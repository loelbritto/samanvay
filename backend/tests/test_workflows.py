from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from app.models import AccessGrant, Assignment, CaseRecord, Resolution, Transfer, User, WorkflowEvent, now
from app.workflows import expire_transfers
from conftest import signin


def action(client, headers, kind, version, **values):
    return client.post('/api/cases/RB-023/actions', headers=headers, json={
        'action':kind, 'expected_version':version, 'reason':'Synthetic workflow verification', **values})


def target(client):
    return next(u for u in client.get('/api/workflow-targets').json() if u['bureau']=='PGRC')


def initiate(client, headers, version=1):
    officer=target(client)
    response=client.post('/api/cases/RB-023/transfers',headers=headers,json={
        'expected_version':version,'target_owner_id':officer['id'],'target_bureau_id':'PGRC',
        'reason':'Synthetic receiving bureau verification','expires_at':(now()+timedelta(days=1)).isoformat()})
    assert response.status_code==201,response.text
    return response.json()


def test_information_cycles_require_latest_answer_and_preserve_original(client):
    h=signin(client)
    original=client.get('/api/cases/RB-023').json()['original_submission']
    # The seed starts UNDER_REVIEW.
    response=action(client,h,'REQUEST_INFORMATION',1,text='Provide the original synthetic receipt',next_action='Wait for receipt')
    assert response.status_code==200 and response.json()['lifecycle']=='AWAITING_INFORMATION'
    assert action(client,h,'REVIEW',2).status_code==422
    assert action(client,h,'INFORMATION',2,text='Synthetic receipt response supplied').status_code==200
    assert action(client,h,'REVIEW',3).json()['lifecycle']=='UNDER_REVIEW'
    assert action(client,h,'REQUEST_INFORMATION',4,text='Provide the missing synthetic date',next_action='Wait for date').status_code==200
    assert action(client,h,'REVIEW',5).status_code==422
    response=action(client,h,'AMEND',5,text='Corrected synthetic narrative; original remains intact')
    assert response.status_code==200 and response.json()['original_submission']==original
    assert len(response.json()['actions'])==6-1


def test_disposal_reopening_scoped_authority_retains_resolutions(system,client):
    h=signin(client)
    assert action(client,h,'DISPOSE',1,text='Synthetic resolution record').status_code==403
    client.post('/api/auth/logout',headers=h)
    h=signin(client,'supervisor@demo.test')
    assert action(client,h,'DISPOSE',1,text='short').status_code==422
    disposed=action(client,h,'DISPOSE',1,text='Synthetic resolution with documented administrative outcome')
    assert disposed.status_code==200 and disposed.json()['lifecycle']=='DISPOSED'
    assert len(disposed.json()['resolutions'])==1
    assert action(client,h,'ESCALATE',2).status_code==422
    client.post('/api/auth/logout',headers=h)
    h=signin(client,'management@demo.test')
    assert action(client,h,'REOPEN',2,next_action='Review appeal').status_code==404
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        user=db.scalar(select(User).where(User.username=='management@demo.test'))
        db.add(AccessGrant(user_id=user.id,case_id=case.id,data_class='M',reason='Synthetic explicit reopening metadata scope',granted_by=user.id))
        db.commit()
    reopened=action(client,h,'REOPEN',2,next_action='Review synthetic appeal')
    assert reopened.status_code==200 and reopened.json()['lifecycle']=='UNDER_REVIEW'
    assert len(reopened.json()['resolutions'])==1
    assert reopened.json()['owner']==disposed.json()['owner']


def test_transfer_reject_then_accept_preserves_deadline_identity_and_one_owner(system,client):
    h=signin(client)
    before=client.get('/api/cases/RB-023').json()
    t=initiate(client,h)
    assert client.get('/api/cases/RB-023').json()['owner']==before['owner']
    assert client.post('/api/transfers/'+t['id']+'/decision',headers=h,json={'action':'ACCEPT','expected_version':2,'transfer_version':1,'reason':'Unapproved source acceptance'}).status_code==404
    client.post('/api/auth/logout',headers=h)
    h=signin(client,'pgrc@demo.test')
    assert client.get('/api/cases/RB-023').status_code==404
    rejected=client.post('/api/transfers/'+t['id']+'/decision',headers=h,json={'action':'REJECT','expected_version':2,'transfer_version':1,'reason':'Synthetic rejection retains source'})
    assert rejected.status_code==200 and rejected.json()['status']=='REJECTED'
    client.post('/api/auth/logout',headers=h)
    h=signin(client)
    t=initiate(client,h,3)
    client.post('/api/auth/logout',headers=h)
    h=signin(client,'pgrc@demo.test')
    accepted=client.post('/api/transfers/'+t['id']+'/decision',headers=h,json={'action':'ACCEPT','expected_version':4,'transfer_version':1,'reason':'Synthetic receiving officer accepts'})
    assert accepted.status_code==200 and accepted.json()['status']=='ACCEPTED'
    after=client.get('/api/cases/RB-023').json()
    assert after['id']==before['id'] and after['due_at']==before['due_at'] and after['lifecycle']==before['lifecycle']
    assert after['owner']['bureau']=='PGRC' and after['version']==5
    assert after['original_submission']==before['original_submission'] and len(after['assignments'])==2
    assert sum(a['to'] is None for a in after['assignments'])==1
    assert client.post('/api/transfers/'+t['id']+'/decision',headers=h,json={'action':'ACCEPT','expected_version':5,'transfer_version':2,'reason':'Repeated acceptance must fail'}).status_code==409


def test_cancel_expiry_boundary_and_disposal_while_transfer_pending(system,client):
    h=signin(client)
    t=initiate(client,h)
    client.post('/api/auth/logout',headers=h)
    supervisor=signin(client,'supervisor@demo.test')
    assert action(client,supervisor,'DISPOSE',2,text='Synthetic resolution cannot skip transfer').status_code==422
    with system.state.sessions() as db:
        transfer=db.get(Transfer,t['id'])
        expiry=transfer.expires_at
    from app.auth import utc
    assert expire_transfers(system.state.sessions,utc(expiry)-timedelta(microseconds=1))==0
    assert expire_transfers(system.state.sessions,utc(expiry))==1
    assert expire_transfers(system.state.sessions,utc(expiry)+timedelta(seconds=1))==0
    assert client.get('/api/cases/RB-023').json()['owner']['name']=='Demo Kabir Sen'
    t=initiate(client,supervisor,3)
    r=client.post('/api/transfers/'+t['id']+'/decision',headers=supervisor,json={'action':'CANCEL','expected_version':4,'transfer_version':1,'reason':'Synthetic source cancellation'})
    assert r.status_code==200 and r.json()['status']=='CANCELLED'


def test_transfer_audit_failure_rolls_back_acceptance_owner_and_intervals(system,client):
    h=signin(client);t=initiate(client,h)
    client.post('/api/auth/logout',headers=h);h=signin(client,'pgrc@demo.test')
    with system.state.engine.begin() as db:
        db.execute(text("CREATE TRIGGER reject_transfer_audit BEFORE INSERT ON workflow_events WHEN NEW.event_type='TRANSFER_ACCEPTED' BEGIN SELECT RAISE(ABORT, 'simulated failure'); END"))
    r=client.post('/api/transfers/'+t['id']+'/decision',headers=h,json={'action':'ACCEPT','expected_version':2,'transfer_version':1,'reason':'Synthetic rollback test'})
    assert r.status_code==503
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        assert case.version==2 and case.current_bureau_id=='RB'
        assert db.get(Transfer,t['id']).status=='PENDING'
        assert db.scalar(select(func.count()).select_from(Assignment).where(Assignment.case_id==case.id))==1


def test_two_simultaneous_commands_have_one_winner(system):
    barrier=Barrier(2)
    def send(value):
        with TestClient(system,raise_server_exceptions=False) as c:
            h=signin(c);barrier.wait()
            return action(c,h,'NEXT_ACTION',1,next_action=value).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes=list(pool.map(send,['Synthetic next action alpha','Synthetic next action beta']))
    assert sorted(codes)==[200,409]
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        assert case.version==2
        assert db.scalar(select(func.count()).select_from(WorkflowEvent).where(WorkflowEvent.case_id==case.id))==2


def test_two_simultaneous_transfer_decisions_have_one_winner(system,client):
    h=signin(client);t=initiate(client,h);barrier=Barrier(2)
    def send(value):
        with TestClient(system,raise_server_exceptions=False) as c:
            headers=signin(c,'pgrc@demo.test');barrier.wait()
            return c.post('/api/transfers/'+t['id']+'/decision',headers=headers,json={'action':value,'expected_version':2,'transfer_version':1,'reason':'Synthetic racing transfer decision'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes=list(pool.map(send,['ACCEPT','REJECT']))
    assert sorted(codes)==[200,409]
    with system.state.sessions() as db:
        case=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        assert case.version==3
        assert db.scalar(select(func.count()).select_from(Assignment).where(Assignment.case_id==case.id,Assignment.effective_to.is_(None)))==1
