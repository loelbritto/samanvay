from pathlib import Path
import sys
from sqlalchemy import select
from app.models import AccessGrant,CaseRecord,Complainant,User,now
from conftest import signin

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from evaluation.generate import build
from evaluation.run import audit_splits


def test_corpus_has_complete_isolated_labels_and_disjoint_families_templates():
    data=build()
    assert len(data['institutions.json'])==32 and len(data['cases.json'])==240
    audit=audit_splits(data['cases.json'],data['labels.json'],data['splits.json'])
    assert audit['passed'] and audit['labels_isolated'] and audit['unseen_institutions']==16
    assert {p['label'] for p in data['labels.json']}=={'DUPLICATE','RELATED','INDEPENDENT','UNKNOWN'}
    assert any(c['institution_id'] is None for c in data['cases.json'])
    assert any('grant admin' in c['description'] for c in data['cases.json'])


def test_bounded_preselection_prioritises_explicit_reference_over_newer_noise_and_keeps_disposed(system,client):
    h=signin(client,'coordinator@demo.test')
    with system.state.sessions() as db:
        coordinator=db.scalar(select(User).where(User.username=='coordinator@demo.test'))
        owner=db.scalar(select(User).where(User.username=='rb@demo.test'))
        old=db.scalar(select(CaseRecord).where(CaseRecord.public_id=='PGRC-014'));old.lifecycle='DISPOSED'
        for index in range(55):
            c=CaseRecord(public_id=f'DEMO-NOISE-{index:03}',institution_id='DEMO-INST-017',original_institution_text='Synthetic Pune',
                received_at=now(),subject='A separate synthetic campus question',description='Unrelated synthetic text without the referenced incident.',
                category='Other',current_owner_id=owner.id,current_bureau_id='RB',next_action='Review independent synthetic question')
            db.add(c);db.flush();db.add(Complainant(case_id=c.id,synthetic_token=f'DEMO-NOISE-{index}'))
            for kind in ['N','I']:db.add(AccessGrant(user_id=coordinator.id,case_id=c.id,data_class=kind,reason='Explicit synthetic retrieval fixture grant',granted_by=coordinator.id))
        db.commit()
    r=client.post('/api/cases/RB-023/matching',headers=h,json={'expected_version':1})
    assert r.status_code==200,r.text
    result=r.json();assert result['candidate_count']==50
    assert any('PGRC-014' in [row['review']['left'],row['review']['right']] for row in result['items'])
