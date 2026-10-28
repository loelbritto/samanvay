from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import hashlib
import json
import uuid
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select
from app.api import create_app
from app.demo import BACKUPS,backup,context_settings,identifier,new_context,rehearsal_grants,restore,storage_audit
from app.models import CaseRecord,CoordinationGroup,RelationshipSuggestion,User
from app.coordination import process_domain_one
from app.scheduling import run_scheduler
from conftest import signin
from test_security_matrix import create_private
from test_workflows import initiate


def isolated():
    result=new_context('test-'+uuid.uuid4().hex)
    settings=context_settings(result['context_id']);return result,create_app(settings)


def test_reset_is_new_context_idempotent_preserves_every_existing_complaint_and_cookie_realm():
    result,app=isolated()
    with TestClient(app) as client:
        h=signin(client);record=create_private(client,h)
        cookie_name=app.state.settings.cookie_name
        assert cookie_name!='samanvay_session' and client.cookies.get(cookie_name)
        client.post('/api/auth/logout',headers=h);h=signin(client,'admin@demo.test')
        body={'run_key':'reset-'+uuid.uuid4().hex,'reason':'Synthetic non-destructive reset verification'}
        first=client.post('/api/demo/new-context',headers=h,json=body)
        second=client.post('/api/demo/new-context',headers=h,json=body)
        assert first.status_code==second.status_code==200
        assert first.json()['context_id']==second.json()['context_id']!=result['context_id'] and second.json()['reused']
        with app.state.sessions() as db:assert db.scalar(select(CaseRecord.id).where(CaseRecord.public_id==record['id']))
        assert context_settings(first.json()['context_id']).cookie_name!=cookie_name
    app.state.engine.dispose()


def test_normal_workspace_production_mode_and_unsafe_keys_are_guarded(client,monkeypatch):
    h=signin(client,'admin@demo.test')
    assert client.post('/api/demo/new-context',headers=h,json={'run_key':'test-'+uuid.uuid4().hex,'reason':'Synthetic guard verification'}).status_code==403
    assert client.post('/api/demo/rehearsal-scope',headers=h,json={'reason':'Synthetic scope guard verification'}).status_code==403
    with pytest.raises(ValueError):identifier('../../unsafe/path')
    with pytest.raises(ValueError):context_settings('../outside')
    with monkeypatch.context() as env:
        env.setenv('SAMANVAY_ENV','production')
        with pytest.raises(ValueError):new_context('test-'+uuid.uuid4().hex)


def test_verified_backup_restore_preserves_case_original_bytes_history_and_source_sessions():
    result,app=isolated();settings=app.state.settings
    with TestClient(app) as client:
        h=signin(client);record=create_private(client,h);old_cookie=client.cookies.get(settings.cookie_name)
        snapshot=backup(settings);assert record['id'] in snapshot['case_ids']
        key='restore-'+uuid.uuid4().hex
        restored=restore(snapshot['backup_id'],key)
        assert restore(snapshot['backup_id'],key)['reused']
        restored_settings=context_settings(restored['context_id']);next_app=create_app(restored_settings)
        with TestClient(next_app) as c:
            c.cookies.set(restored_settings.cookie_name,old_cookie)
            assert c.get('/api/cases/'+record['id']).status_code==401
            signin(c)
            after=c.get('/api/cases/'+record['id']).json()
            assert after==record
            contents=c.get(after['attachments'][0]['download_url']).content
            assert hashlib.sha256(contents).hexdigest()==record['attachments'][0]['sha256']
        next_app.state.engine.dispose()
        assert client.get('/api/cases/'+record['id']).status_code==200 # source session is unchanged
        assert storage_audit(settings)['passed'] and storage_audit(restored_settings)['passed']
    app.state.engine.dispose()


def test_tampered_backup_is_rejected_before_target_creation():
    result,app=isolated();snapshot=backup(app.state.settings)
    manifest=BACKUPS/snapshot['backup_id']/'backup-manifest.json';original=manifest.read_bytes()
    payload=json.loads(original);payload['database_sha256']='0'*64;manifest.write_text(json.dumps(payload),encoding='utf-8')
    key='tamper-'+uuid.uuid4().hex
    try:
        with pytest.raises(ValueError):restore(snapshot['backup_id'],key)
        assert not context_settings(identifier(key)).data_dir.exists()
    finally:manifest.write_bytes(original)
    app.state.engine.dispose()


def test_explicit_rehearsal_scope_keeps_management_metadata_and_attachments_separate():
    result,app=isolated()
    with TestClient(app) as c:
        h=signin(c);record=create_private(c,h);c.post('/api/auth/logout',headers=h)
        h=signin(c,'coordinator@demo.test');assert c.get('/api/cases/'+record['id']).json()['description'] is None
        c.post('/api/auth/logout',headers=h);h=signin(c,'admin@demo.test')
        assert c.post('/api/demo/rehearsal-scope',headers=h,json={'reason':'Explicit synthetic demonstration review scope'}).status_code==200
        assert c.get('/api/reports').json()['total']==0
        c.post('/api/auth/logout',headers=h);h=signin(c,'management@demo.test')
        after=c.get('/api/cases/'+record['id']).json()
        assert after['description'] is None and after['complainant'] is None and after['attachments']==[]
        assert c.get(record['attachments'][0]['download_url']).status_code==404
        c.post('/api/auth/logout',headers=h);signin(c,'coordinator@demo.test')
        assert c.get('/api/cases/'+record['id']).json()['description'] and c.get(record['attachments'][0]['download_url']).status_code==404
    app.state.engine.dispose()


def test_pending_transfer_recipient_receives_notice_without_case_narrative_scope(system,client):
    h=signin(client);t=initiate(client,h);run_scheduler(system.state.sessions)
    client.post('/api/auth/logout',headers=h);signin(client,'pgrc@demo.test')
    assert any(n['transfer_id']==t['id'] and n['kind']=='TRANSFER' for n in client.get('/api/notifications').json())
    assert client.get('/api/cases/RB-023').status_code==404


def test_simultaneous_pair_decisions_have_one_winner(system,client):
    h=signin(client,'coordinator@demo.test')
    row=client.post('/api/relationships/source-review',headers=h,json={'left':'PGRC-014','right':'RB-023'}).json()
    barrier=Barrier(2)
    def send(kind):
        with TestClient(system) as c:
            headers=signin(c,'coordinator@demo.test');barrier.wait()
            return c.post('/api/relationships/'+row['id']+'/decision',headers=headers,json={'action':kind,'label':'RELATED',
                'expected_version':1,'left_version':row['left_version'],'right_version':row['right_version'],'fingerprint':row['fingerprint'],'reason':'Synthetic competing human decisions'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(send,['CONFIRM','REJECT']))
    assert sorted(codes)==[200,409]
    assert len(client.get('/api/relationships').json()[0]['decisions'])==1


def test_unprocessed_material_source_change_blocks_stale_group_plan(system,client):
    h=signin(client)
    assert client.post('/api/cases/RB-023/actions',headers=h,json={'action':'NEXT_ACTION','expected_version':1,'reason':'Synthetic concurrent source update','next_action':'New synthetic administrative action'}).status_code==200
    client.post('/api/auth/logout',headers=h);h=signin(client,'coordinator@demo.test')
    g=client.get('/api/coordination').json()[0]
    response=client.post('/api/coordination/'+g['id']+'/review',headers=h,json={'state':'IN_REVIEW','expected_version':g['version'],
        'reason':'Synthetic stale coordination plan','next_action':'Review current evidence'})
    assert response.status_code==409
    assert process_domain_one(system.state.sessions)['status']=='DONE'
    assert client.get('/api/coordination').json()[0]['version']==g['version']+1


def test_final_review_applies_to_unchanged_evidence_after_workflow_only_version_change(client):
    h=signin(client,'coordinator@demo.test')
    row=client.post('/api/relationships/source-review',headers=h,json={'left':'PGRC-014','right':'RB-023'}).json()
    assert client.post('/api/relationships/'+row['id']+'/decision',headers=h,json={'action':'REJECT','expected_version':1,
        'left_version':row['left_version'],'right_version':row['right_version'],'fingerprint':row['fingerprint'],'reason':'Synthetic final decision on unchanged evidence'}).status_code==200
    client.post('/api/auth/logout',headers=h);h=signin(client)
    assert client.post('/api/cases/RB-023/actions',headers=h,json={'action':'NEXT_ACTION','expected_version':1,
        'reason':'Synthetic workflow-only metadata update','next_action':'Contact the same owner about the existing receipt'}).status_code==200
    client.post('/api/auth/logout',headers=h);h=signin(client,'coordinator@demo.test')
    current=client.post('/api/relationships/source-review',headers=h,json={'left':'PGRC-014','right':'RB-023'}).json()
    assert current['id']==row['id'] and not current['stale'] and current['workflow_versions_changed']
    assert current['decision_applies_to_unchanged_evidence'] and current['decisions'][0]['action']=='REJECT'
