from datetime import timedelta
import io
import csv
import json
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func,select
from sqlalchemy.exc import IntegrityError
from app.models import AccessGrant,Assignment,CaseRecord,LoginAttempt,OutboxJob,SecurityAudit,User,WorkflowEvent,now
from app.storage import private_path
from app.worker import process_one
from app.scheduling import run_scheduler,deliver_one
from conftest import signin,SURFACE_RESULTS


def create_private(client,h):
    payload={'institution_id':'DEMO-INST-017','original_institution_text':'Synthetic campus identity','received_date':'2026-10-27',
        'subject':'DEMO-SECRET-NARRATIVE-ONLY-OWNER','description':'Synthetic private narrative must not appear in metadata exports or matching.',
        'category':'Other','next_action':'DEMO-SECRET-NEXT-ACTION','complainant_token':'DEMO-PRIVATE-TOKEN','synthetic':True}
    r=client.post('/api/cases',headers={**h,'Idempotency-Key':uuid.uuid4().hex},data={'payload':json.dumps(payload)},
        files=[('files',('private.txt',b'Synthetic private evidence bytes','text/plain'))])
    assert r.status_code==201,r.text
    return r.json()


@pytest.mark.parametrize('account,metadata,narrative',[
    ('rb@demo.test',True,True),('rb.backup@demo.test',False,False),('pgrc@demo.test',False,False),
    ('supervisor@demo.test',True,False),('pgrc.supervisor@demo.test',False,False),('regional@demo.test',False,False),
    ('coordinator@demo.test',True,False),('management@demo.test',False,False),('admin@demo.test',False,False)])
def test_every_role_across_case_bytes_search_matching_notifications_counts_exports(system,client,account,metadata,narrative):
    h=signin(client);record=create_private(client,h);run_scheduler(system.state.sessions)
    owner_notifications=client.get('/api/notifications').json();private_notice=next(n for n in owner_notifications if n['case_id']==record['id'])
    client.post('/api/auth/logout',headers=h);h=signin(client,account)
    detail=client.get('/api/cases/'+record['id']);download=client.get(record['attachments'][0]['download_url'])
    secret_search=client.get('/api/cases',params={'q':'DEMO-SECRET-NARRATIVE-ONLY-OWNER'}).json()
    autocomplete=client.get('/api/search/suggestions',params={'q':'DEMO-SECRET-NARRATIVE-ONLY-OWNER'}).json()
    report=client.get('/api/reports').json();listing=client.get('/api/cases').json()
    csv_response=client.get('/api/reports/csv');csv_rows=list(csv.DictReader(io.StringIO(csv_response.content.decode('utf-8-sig'))))
    printed=client.get('/api/reports/print').text
    matching=client.post('/api/cases/'+record['id']+'/matching',headers=h,json={'expected_version':1})
    acknowledge=client.post('/api/notifications/'+private_notice['id']+'/acknowledge',headers=h)
    assert detail.status_code==(200 if metadata else 404)
    if metadata:
        body=detail.json();assert body['description'] is not None if narrative else body['description'] is None
        assert bool(body['complainant'])==narrative and bool(body['attachments'])==narrative
    assert download.status_code==(200 if narrative else 404)
    assert secret_search['total']==int(narrative) and len(autocomplete)==int(narrative)
    assert report['total']==listing['total']==len(report['rows'])==len(csv_rows)
    assert ('DEMO-SECRET-NARRATIVE-ONLY-OWNER' in csv_response.text)==narrative
    assert ('DEMO-SECRET-NEXT-ACTION' in printed)==narrative
    assert matching.status_code in {403,404}
    if account!='rb@demo.test':assert acknowledge.status_code==404
    notifications=client.get('/api/notifications').json()
    assert all('DEMO-SECRET-NARRATIVE' not in json.dumps(n) for n in notifications)
    SURFACE_RESULTS.append({'account':account,'direct_case':detail.status_code,'private_bytes':download.status_code,
        'secret_search_count':secret_search['total'],'autocomplete_count':len(autocomplete),'authorised_total':report['total'],
        'csv_rows':len(csv_rows),'matching_status':matching.status_code,'other_recipient_ack_status':acknowledge.status_code,
        'passed':True})


def test_expired_or_missing_session_denies_every_new_read_surface(client,system):
    urls=['/api/reports','/api/reports/csv','/api/reports/print','/api/notifications','/api/transfers',
          '/api/matching/status','/api/relationships','/api/coordination','/api/identity/lookup?q=DSI','/api/search/suggestions?q=receipt','/api/settings']
    assert all(client.get(url).status_code==401 for url in urls)
    signin(client)
    from app.models import LoginSession
    with system.state.sessions() as db:
        for session in db.scalars(select(LoginSession)):session.expires_at=now()-timedelta(seconds=1)
        db.commit()
    assert all(client.get(url).status_code==401 for url in urls)


def test_actual_unknown_length_body_limit_and_negative_length_leave_state_unchanged(system,client):
    h=signin(client)
    with system.state.sessions() as db:before=db.scalar(select(func.count()).select_from(CaseRecord))
    def stream():
        for _ in range(257):yield b'x'*(64*1024)
    r=client.post('/api/cases',headers={**h,'Content-Type':'application/json'},content=stream())
    assert r.status_code==413,r.text
    assert client.post('/api/auth/login',headers={'Content-Length':'-1'},content=b'').status_code==400
    with system.state.sessions() as db:assert db.scalar(select(func.count()).select_from(CaseRecord))==before


def test_private_paths_malformed_many_files_and_auxiliary_audit_never_record_content(system,client):
    h=signin(client);record=create_private(client,h)
    for value in ['../../outside','C:\\Windows\\system.ini','00.bin','a'*48+'.bin/..']:
        with pytest.raises(ValueError):private_path(system.state.settings,value)
    assert client.get(record['attachments'][0]['download_url']).content==b'Synthetic private evidence bytes'
    many=client.post('/api/cases',headers={**h,'Idempotency-Key':uuid.uuid4().hex},data={'payload':json.dumps(record['original_submission'])},
        files=[('files',(f'part{i}.txt',b'Synthetic file bytes','text/plain')) for i in range(4)])
    assert many.status_code==422
    assert client.get('/private-evidence/guess.bin').status_code==404
    with system.state.sessions() as db:
        audits=list(db.scalars(select(SecurityAudit)))
        assert any(a.operation=='EVIDENCE_ACCESS' and a.status==200 for a in audits)
        assert all(len(a.resource_hash)==64 and 'SECRET' not in a.operation for a in audits)


def test_expired_grants_do_not_enable_metadata_or_narrative_filtering(system,client):
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        user=db.scalar(select(User).where(User.username=='pgrc@demo.test'))
        db.add(AccessGrant(user_id=user.id,case_id=case.id,data_class='M',expires_at=now()-timedelta(seconds=1),reason='Expired synthetic grant',granted_by=user.id))
        db.add(AccessGrant(user_id=user.id,case_id=case.id,data_class='N',reason='Narrative grant does not imply metadata',granted_by=user.id));db.commit()
    signin(client,'pgrc@demo.test')
    assert client.get('/api/cases/RB-023').status_code==404
    assert client.get('/api/cases',params={'q':'R-883'}).json()['total']==0


def test_database_enforces_one_current_assignment(system):
    with system.state.sessions() as db:
        existing=db.scalar(select(Assignment))
        db.add(Assignment(case_id=existing.case_id,owner_id=existing.owner_id,bureau_id=existing.bureau_id,assigned_by=existing.assigned_by,reason='Synthetic invalid second current interval'))
        with pytest.raises(IntegrityError):db.flush()
        db.rollback()


def test_signin_throttle_persists_then_recovers_after_its_own_window(system,client):
    for _ in range(10):assert client.post('/api/auth/login',json={'username':'rb@demo.test','password':'wrong-synthetic-password'}).status_code==401
    assert client.post('/api/auth/login',json={'username':'rb@demo.test','password':'DemoOnly-Stage2!'}).status_code==429
    with system.state.sessions() as db:
        for attempt in db.scalars(select(LoginAttempt)):attempt.window_start=now()-timedelta(minutes=6)
        db.commit()
    assert signin(client)


def test_crashed_integrity_worker_lease_is_reclaimed_without_duplicate_event(system,client):
    h=signin(client);record=create_private(client,h)
    with system.state.sessions() as db:
        job=db.scalar(select(OutboxJob).where(OutboxJob.kind=='EVIDENCE_INTEGRITY'))
        job.status='RUNNING';job.lease_until=now()-timedelta(seconds=1);job.attempts=1;db.commit()
    assert process_one(system.state.settings,system.state.sessions)['status']=='DONE'
    assert process_one(system.state.settings,system.state.sessions) is None
    assert sum(e['type']=='EVIDENCE_INTEGRITY_CHECKED' for e in client.get('/api/cases/'+record['id']).json()['history'])==1


def test_simultaneous_scheduler_runs_retry_without_alert_flood(system):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.models import Notification
    barrier=Barrier(2);at=now()
    def run(_):barrier.wait();return run_scheduler(system.state.sessions,at)
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,[1,2]))
    with system.state.sessions() as db:
        rows=list(db.scalars(select(Notification)))
        assert rows and len({n.dedup_key for n in rows})==len(rows)
        assert sum(r['created'] for r in results)==len(rows)
    assert run_scheduler(system.state.sessions,at)['created']==0


def test_notification_delivery_recovers_crashed_lease_without_recreating_notice(system):
    from app.models import Notification
    run_scheduler(system.state.sessions)
    with system.state.sessions() as db:
        n=db.scalar(select(Notification).order_by(Notification.created_at).limit(1));notice_id=n.id
        n.state='DELIVERING';n.lease_until=now()-timedelta(seconds=1);n.attempts=1;db.commit()
        count=db.scalar(select(func.count()).select_from(Notification))
    delivered=deliver_one(system.state.sessions)
    assert delivered['id']==notice_id and delivered['state']=='DELIVERED'
    with system.state.sessions() as db:
        assert db.get(Notification,notice_id).attempts==2
        assert db.scalar(select(func.count()).select_from(Notification))==count
