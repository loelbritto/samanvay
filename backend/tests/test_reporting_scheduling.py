import csv
from datetime import timedelta
import io
import json
from pathlib import Path
import uuid
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from app.auth import utc
from app.config import ROOT,Settings
from app.models import CaseRecord,DemoContext,Notification,User,WorkflowEvent,now
from app.scheduling import context_now,deliver_one,run_scheduler
from conftest import signin


def total(db):return db.scalar(select(func.count()).select_from(Notification))


def test_deadline_before_at_after_and_escalation_deduplicate_across_restart(system):
    due=now()+timedelta(hours=2)
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'));case.due_at=due;case_id=case.id
        rb=db.scalar(select(User.id).where(User.username=='rb@demo.test'));db.commit()
    def count(kind):
        with system.state.sessions() as db:return db.scalar(select(func.count()).select_from(Notification).where(Notification.case_id==case_id,Notification.user_id==rb,Notification.kind==kind))
    run_scheduler(system.state.sessions,due-timedelta(microseconds=1));assert count('APPROACHING_DEADLINE')==1 and count('OVERDUE')==0
    run_scheduler(system.state.sessions,due);assert count('OVERDUE')==0
    run_scheduler(system.state.sessions,due+timedelta(microseconds=1));assert count('OVERDUE')==1
    run_scheduler(system.state.sessions,due+timedelta(hours=24)-timedelta(microseconds=1))
    with system.state.sessions() as db:assert db.get(CaseRecord,case_id).escalation_level==0
    at=due+timedelta(hours=24);run_scheduler(system.state.sessions,at)
    with system.state.sessions() as db:
        case=db.get(CaseRecord,case_id);assert case.escalation_level==1 and utc(case.due_at)==due
        event=db.scalar(select(WorkflowEvent).where(WorkflowEvent.case_id==case_id,WorkflowEvent.event_type=='POLICY_ESCALATION'))
        assert utc(event.occurred_at)==at
        before=total(db)
    from app.api import create_app
    restarted=create_app(system.state.settings)
    assert run_scheduler(restarted.state.sessions,at)['created']==0
    with restarted.state.sessions() as db:assert total(db)==before and db.get(CaseRecord,case_id).escalation_level==1
    restarted.state.engine.dispose()


def test_persistent_delivery_acknowledgement_and_revoked_case_scope(system,client):
    h=signin(client);run_scheduler(system.state.sessions)
    rows=client.get('/api/notifications').json();assert rows and all(r['state']=='PENDING' for r in rows)
    notification=rows[0]
    assert client.post('/api/notifications/'+notification['id']+'/acknowledge',headers=h).status_code==409
    for _ in range(100):
        if deliver_one(system.state.sessions) is None:break
    assert client.post('/api/notifications/'+notification['id']+'/acknowledge',headers=h).json()['state']=='ACKNOWLEDGED'
    assert client.post('/api/notifications/'+notification['id']+'/acknowledge',headers=h).status_code==200
    client.post('/api/auth/logout',headers=h);h=signin(client,'pgrc@demo.test')
    assert client.post('/api/notifications/'+notification['id']+'/acknowledge',headers=h).status_code==404
    client.post('/api/auth/logout',headers=h);h=signin(client,'supervisor@demo.test')
    target=next(r for r in client.get('/api/officers').json() if r['name']=='Demo Meera Das')
    assert client.post('/api/cases/RB-023/assignment',headers=h,json={'owner_id':target['id'],'expected_version':1,'reason':'Synthetic scope revocation verification'}).status_code==200
    client.post('/api/auth/logout',headers=h);signin(client)
    assert client.get('/api/notifications').json()==[]


def test_filters_rows_csv_print_and_autocomplete_use_same_scope(system,client):
    h=signin(client,'coordinator@demo.test')
    params={'institution':'DEMO-INST-017','region':'DEMO-WEST','bureau':'PGRC'}
    report=client.get('/api/reports',params=params).json()
    listing=client.get('/api/cases',params=params).json()
    export=client.get('/api/reports/csv',params=params)
    rows=list(csv.DictReader(io.StringIO(export.content.decode('utf-8-sig'))))
    assert report['total']==listing['total']==len(report['rows'])==len(rows)==2
    assert {r['id'] for r in rows}=={r['id'] for r in report['rows']}=={r['id'] for r in listing['items']}
    assert report['pending']+report['disposed']==report['total'] and sum(report['dimensions']['status'].values())==2
    assert client.get('/api/reports',params={'category':'Infrastructure'}).json()['total']==0  # no narrative grant to RB-031
    assert client.get('/api/reports',params={'received_from':'2026-10-23','received_to':'2026-10-23'}).status_code==422
    assert len(client.get('/api/search/suggestions',params={'q':'Pune'}).json())==3
    printable=client.get('/api/reports/print',params=params)
    assert printable.status_code==200 and 'PGRC-014' in printable.text and 'RB-031' not in printable.text
    client.post('/api/auth/logout',headers=h);signin(client,'admin@demo.test')
    assert client.get('/api/reports').json()['total']==0
    assert client.get('/api/search/suggestions',params={'q':'Pune'}).json()==[]
    assert len(list(csv.DictReader(io.StringIO(client.get('/api/reports/csv').content.decode('utf-8-sig')))))==0


def test_export_formula_and_print_html_are_escaped(system,client):
    signin(client)
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        case.subject='=HYPERLINK("https://example.invalid","synthetic")';case.next_action='<script>alert("synthetic")</script>';db.commit()
    row=list(csv.DictReader(io.StringIO(client.get('/api/reports/csv').content.decode('utf-8-sig'))))[0]
    assert row['subject'].startswith("'=")
    printed=client.get('/api/reports/print').text
    assert '<script>' not in printed and '&lt;script&gt;' in printed


def test_disposal_counts_cohort_and_throughput_are_distinct(system,client):
    from app.reporting import INDIA
    today=now().astimezone(INDIA).date();h=signin(client)
    data={'institution_id':'DEMO-INST-017','original_institution_text':'Synthetic Pune','received_date':today.isoformat(),
        'subject':'Synthetic new receipt for report denominator','description':'A fictional new complaint for the reporting cohort.',
        'category':'Other','next_action':'Review synthetic intake','complainant_token':'DEMO-REPORT-NEW','synthetic':True}
    assert client.post('/api/cases',headers={**h,'Idempotency-Key':uuid.uuid4().hex},data={'payload':json.dumps(data)}).status_code==201
    client.post('/api/auth/logout',headers=h);h=signin(client,'pgrc.supervisor@demo.test')
    for case in ['PGRC-014','PGRC-019']:
        assert client.post('/api/cases/'+case+'/actions',headers=h,json={'action':'DISPOSE','expected_version':1,'reason':'Synthetic backlog resolution','text':'Documented synthetic administrative resolution'}).status_code==200
    client.post('/api/auth/logout',headers=h);signin(client,'coordinator@demo.test')
    report=client.get('/api/reports',params={'received_from':today.isoformat(),'received_to':(today+timedelta(days=1)).isoformat()}).json()
    assert report['missing_deadline']==1
    assert report['total']==1 and report['cohort_disposal_rate']==0 and report['period_distinct_disposals']==2
    assert report['disposal_to_receipt_ratio']==2.0 and report['monthly'] and report['quarterly']


def test_policy_admin_requires_role_and_versions_and_clock_is_guarded(client):
    h=signin(client);body={'expected_version':1,'approaching_hours':24,'escalation_hours':48,'auto_escalate':False,'reason':'Synthetic policy administration test'}
    assert client.post('/api/settings/policy',headers=h,json=body).status_code==403
    client.post('/api/auth/logout',headers=h);h=signin(client,'admin@demo.test')
    assert client.post('/api/settings/policy',headers=h,json=body).status_code==200
    assert client.post('/api/settings/policy',headers=h,json=body).status_code==409
    assert client.post('/api/demo/clock',headers=h,json={'expected_version':1,'advance_seconds':86400,'reason':'Synthetic guard test'}).status_code==403
    assert not client.get('/api/settings').json()['clock_enabled']


def test_isolated_clock_keeps_host_other_context_and_stored_deadlines_unchanged(system,monkeypatch):
    from app.api import create_app
    from app.seed import seed
    context='test-'+uuid.uuid4().hex;directory=ROOT/'.demo-contexts'/context
    assert not directory.exists() and directory.resolve().is_relative_to((ROOT/'.demo-contexts').resolve())
    with monkeypatch.context() as env:
        env.setenv('SAMANVAY_DATA_DIR',str(directory));env.setenv('SAMANVAY_ENV','test')
        command.upgrade(Config(str(ROOT/'backend/alembic.ini')),'head')
    settings=Settings(directory,'test',demo_controls=True,context_id=context)
    isolated=create_app(settings);seed(settings,isolated.state.sessions)
    with isolated.state.sessions() as db:before={c.id:c.due_at for c in db.scalars(select(CaseRecord))}
    wall_before=now()
    with TestClient(isolated) as c:
        h=signin(c,'admin@demo.test')
        r=c.post('/api/demo/clock',headers=h,json={'expected_version':1,'advance_seconds':86400,'reason':'Synthetic isolated clock test'})
        assert r.status_code==200,r.text
        assert r.json()['host_clock_changed'] is False and r.json()['stored_deadlines_changed'] is False
        assert c.get('/api/settings').json()['clock_offset_seconds']==86400
    assert (now()-wall_before).total_seconds()<30
    with isolated.state.sessions() as db:assert {c.id:c.due_at for c in db.scalars(select(CaseRecord))}==before
    with system.state.sessions() as db:assert db.scalar(select(DemoContext)).clock_offset_seconds==0
    isolated.state.engine.dispose()
