from sqlalchemy import select
from fastapi.testclient import TestClient
from app.models import CaseRecord, CoordinationGroup, IdentityDecision, InstitutionAlias, RelationshipDecision, User
from app.coordination import make_suggestion, process_domain_one, refresh_coordination
from conftest import signin


def source(client,h,left='PGRC-014',right='RB-023'):
    r=client.post('/api/relationships/source-review',headers=h,json={'left':left,'right':right})
    assert r.status_code==201,r.text
    return r.json()


def review(client,h,row,kind='REJECT',label=None):
    return client.post('/api/relationships/'+row['id']+'/decision',headers=h,json={
        'action':kind,'label':label,'expected_version':row['version'],'left_version':row['left_version'],
        'right_version':row['right_version'],'fingerprint':row['fingerprint'],'reason':'Synthetic authorised evidence decision'})


def test_exact_identity_location_collision_and_aliases_require_human_review(client):
    signin(client)
    assert client.get('/api/identity/lookup',params={'q':'DEMO-INST-017'}).json()['status']=='EXACT_ID'
    ambiguous=client.get('/api/identity/lookup',params={'q':'Demo Suryavan Institute'}).json()
    assert ambiguous['status']=='AMBIGUOUS' and len(ambiguous['candidates'])==2
    alias=client.get('/api/identity/lookup',params={'q':'DSI Pune'}).json()
    assert alias['selected_candidate']=='DEMO-INST-017' and alias['human_confirmation_required']
    conflict=client.get('/api/identity/lookup',params={'q':'DEMO-INST-017','city':'Nagpur'}).json()
    assert conflict['selected_candidate'] is None and conflict['candidates'][0]['city_conflict']


def test_identity_confirmation_preserves_original_and_alias_provenance(system,client):
    h=signin(client,'coordinator@demo.test')
    before=client.get('/api/cases/PGRC-014').json()
    data={'institution_id':'DEMO-INST-044','expected_version':1,'reason':'Synthetic conflicting location checked by authorised reviewer',
        'provenance':'Synthetic signed campus note DEMO-NOTE-22','alias':'DSI reviewed Nagpur','acknowledge_conflict':False}
    assert client.post('/api/cases/PGRC-014/identity',headers=h,json=data).status_code==422
    data['acknowledge_conflict']=True
    r=client.post('/api/cases/PGRC-014/identity',headers=h,json=data)
    assert r.status_code==200,r.text
    after=r.json()
    assert after['institution_id']=='DEMO-INST-044' and after['original_institution_text']==before['original_institution_text']
    assert after['original_submission']==before['original_submission'] and after['owner']==before['owner']
    assert after['identity_history'][0]['provenance']==data['provenance']
    with system.state.sessions() as db:
        decision=db.scalar(select(IdentityDecision))
        assert decision.previous_institution_id=='DEMO-INST-017' and decision.provenance==data['provenance']
        assert db.scalar(select(InstitutionAlias).where(InstitutionAlias.alias==data['alias'])).provenance==data['provenance']


def test_independent_relationship_does_not_remove_coordination_or_change_owners(client):
    h=signin(client,'coordinator@demo.test')
    groups=client.get('/api/coordination').json()
    assert len(groups)==1 and groups[0]['condition_active'] and groups[0]['institution_id']=='DEMO-INST-017'
    before=[(c['id'],c['owner']) for c in groups[0]['cases']]
    row=source(client,h,'PGRC-019','RB-023')
    r=review(client,h,row,'CONFIRM','INDEPENDENT')
    assert r.status_code==200 and r.json()['decisions'][-1]['label']=='INDEPENDENT'
    after=client.get('/api/coordination').json()[0]
    assert after['condition_active'] and [(c['id'],c['owner']) for c in after['cases']]==before
    assert 'duplicate' not in after['label'].lower()


def test_rejection_sticky_across_method_rerun_restart_and_changed_evidence(system,client):
    h=signin(client,'coordinator@demo.test');row=source(client,h)
    assert review(client,h,row).status_code==200
    assert source(client,h)['id']==row['id']
    with system.state.sessions() as db:
        left=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='PGRC-014'))
        right=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='RB-023'))
        same=make_suggestion(db,left,right,method='DIFFERENT_METHOD_RETRY')
        assert same.id==row['id'];db.commit()
    from app.api import create_app
    restarted=create_app(system.state.settings)
    with TestClient(restarted) as c:
        h2=signin(c,'coordinator@demo.test')
        assert source(c,h2)['decisions'][0]['action']=='REJECT'
    restarted.state.engine.dispose()
    with TestClient(system) as owner:
        headers=signin(owner)
        assert owner.post('/api/cases/RB-023/actions',headers=headers,json={'action':'AMEND','expected_version':1,
            'reason':'Synthetic material source change','text':'New synthetic receipt and conflicting date details added for renewed review'}).status_code==200
    assert review(client,h,row,'CONFIRM','DUPLICATE').status_code==409
    new=source(client,h)
    assert new['id']!=row['id'] and new['previous_id']==row['id'] and new['decisions']==[]
    with system.state.sessions() as db:
        assert db.scalar(select(RelationshipDecision).where(RelationshipDecision.suggestion_id==row['id'])).action=='REJECT'


def test_group_state_version_lead_and_inactive_condition_keep_history(system,client):
    h=signin(client,'coordinator@demo.test');g=client.get('/api/coordination').json()[0]
    owners=[c['owner'] for c in g['cases']]
    def save(state,version,lead=None):
        return client.post('/api/coordination/'+g['id']+'/review',headers=h,json={'state':state,'expected_version':version,
            'reason':'Synthetic coordination plan review','next_action':'Compare responses without replacing case owners','lead_id':lead})
    assert save('PLANNED',1).status_code==422
    r=save('IN_REVIEW',1);assert r.status_code==200
    assert save('DEFER',1).status_code==409
    lead=client.get('/api/workflow-targets').json()[0]['id']
    r=save('PLANNED',2,lead);assert r.status_code==200 and r.json()['lead_id']==lead
    r=save('RESOLVED',3,lead);assert r.status_code==200
    assert [c['owner'] for c in r.json()['cases']]==owners
    with system.state.sessions() as db:
        for c in db.scalars(select(CaseRecord).where(CaseRecord.current_bureau_id=='PGRC')):
            c.lifecycle='DISPOSED';c.version+=1
        db.flush();refresh_coordination(db);db.commit()
    retained=client.get('/api/coordination').json()[0]
    assert not retained['condition_active'] and retained['state']=='RESOLVED'
    assert len(retained['cases'])==3 and len(retained['reviews'])==5


def test_metadata_group_does_not_grant_narratives_pairs_or_other_viewer_counts(client):
    h=signin(client)
    assert client.get('/api/coordination').json()==[]
    assert client.get('/api/relationships').json()==[]
    assert client.post('/api/relationships/source-review',headers=h,json={'left':'PGRC-014','right':'RB-023'}).status_code==404
    assert len(client.get('/api/institutions/DEMO-INST-017/timeline').json()['cases'])==1
    client.post('/api/auth/logout',headers=h);h=signin(client,'coordinator@demo.test')
    nagpur=client.get('/api/cases/RB-031').json()
    assert nagpur['description'] is None and nagpur['attachments']==[] and nagpur['complainant'] is None
    assert client.post('/api/relationships/source-review',headers=h,json={'left':'RB-031','right':'PGRC-014'}).status_code==404


def test_deferred_pair_can_be_reviewed_then_rejected_without_erasing_history(client):
    h=signin(client,'coordinator@demo.test')
    row=source(client,h)
    deferred=review(client,h,row,'DEFER')
    assert deferred.status_code==200
    current=source(client,h)
    assert current['id']==row['id'] and current['version']==row['version']+1
    assert current['decisions'][0]['action']=='DEFER'
    final=review(client,h,current,'REJECT')
    assert final.status_code==200
    again=source(client,h)
    assert [d['action'] for d in again['decisions']]==['DEFER','REJECT']
    assert review(client,h,again,'CONFIRM','RELATED').status_code==409
    assert source(client,h)['decisions']==again['decisions']
