"""Read-only persisted rehearsal snapshots around real clock and service restarts."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import time
import httpx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.demo import context_settings


def login(client,username):
    response=client.post('/api/auth/login',json={'username':username,'password':'DemoOnly-Stage2!'})
    assert response.status_code==200


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['before-clock','before-restart','after-restart'])
    args=parser.parse_args();evidence=ROOT/'docs/evidence/stage9'
    proof=json.loads((evidence/'ui-rehearsal.json').read_text(encoding='utf-8'))
    settings=context_settings(proof['context_id']);dbfile=settings.data_dir/'samanvay.sqlite3'
    # Wait only for persisted in-app delivery to settle; no workflow is mutated here.
    if args.phase!='before-clock':
        for _ in range(100):
            with sqlite3.connect('file:'+dbfile.as_posix()+'?mode=ro',uri=True) as db:
                pending=db.execute("SELECT count(*) FROM notifications WHERE state IN ('PENDING','DELIVERING')").fetchone()[0]
            if pending==0:break
            time.sleep(.1)
        assert pending==0,'In-app delivery did not settle'
    with sqlite3.connect('file:'+dbfile.as_posix()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        rows=db.execute('SELECT c.*,u.username FROM cases c JOIN users u ON u.id=c.current_owner_id ORDER BY c.public_id').fetchall()
        expected={'PGRC-014','PGRC-019','RB-023','RB-031'}|{r['id'] for r in proof['created']}
        assert len(rows)==8 and {r['public_id'] for r in rows}==expected
        cases=[]
        for c in rows:
            original=db.execute('SELECT payload,sha256 FROM original_submissions WHERE case_id=?',(c['id'],)).fetchone()
            assert original and hashlib.sha256(json.dumps(json.loads(original['payload']),sort_keys=True,ensure_ascii=False).encode()).hexdigest()==original['sha256']
            history=[dict(e) for e in db.execute('SELECT id,event_type,before_version,after_version FROM workflow_events WHERE case_id=? ORDER BY occurred_at,before_version,after_version,id',(c['id'],))]
            assignments=[dict(a) for a in db.execute('SELECT owner_id,bureau_id,effective_from,effective_to,reason FROM assignment_history WHERE case_id=? ORDER BY effective_from',(c['id'],))]
            assert sum(a['effective_to'] is None for a in assignments)==1
            attachments=[dict(a) for a in db.execute('SELECT id,storage_key,sha256 FROM attachments WHERE case_id=?',(c['id'],))]
            for a in attachments:
                contents=(settings.attachments_dir/a['storage_key']).read_bytes()
                assert hashlib.sha256(contents).hexdigest()==a['sha256']
            cases.append({'id':c['public_id'],'owner_id':c['current_owner_id'],'username':c['username'],'bureau':c['current_bureau_id'],
                'version':c['version'],'lifecycle':c['lifecycle'],'due_at':c['due_at'],'original_sha256':original['sha256'],'history':history,'assignments':assignments,
                'attachments':[{'id':a['id'],'sha256':a['sha256']} for a in attachments]})
        offset=db.execute('SELECT clock_offset_seconds FROM demo_context').fetchone()[0]
        groups=[dict(g) for g in db.execute('SELECT id,institution_id,condition_active,state,lead_id,lead_bureau_id,next_action,version FROM coordination_groups ORDER BY id')]
        decisions=[dict(d) for d in db.execute('SELECT id,suggestion_id,action,label,reason FROM relationship_decisions ORDER BY id')]
        notifications=[dict(n) for n in db.execute('SELECT id,user_id,kind,state,acknowledged_at FROM notifications ORDER BY id')]
        assert len(groups)==1 and groups[0]['condition_active'] and groups[0]['state']=='PLANNED'
        assert {d['label'] for d in decisions if d['action']=='CONFIRM'}=={'RELATED','INDEPENDENT'}
    with sqlite3.connect('file:'+(ROOT/'.local-data/samanvay.sqlite3').as_posix()+'?mode=ro',uri=True) as primary:
        assert primary.execute('SELECT count(*) FROM cases').fetchone()[0]==5
        assert primary.execute('SELECT clock_offset_seconds FROM demo_context').fetchone()[0]==0
    base='http://127.0.0.1:8001'
    with httpx.Client(base_url=base,timeout=15) as client:
        assert client.get('/api/cases').status_code==401
        login(client,'coordinator@demo.test')
        assert client.get('/api/reports').json()['total']==8
        assert any(v['decision_applies_to_unchanged_evidence'] for v in client.get('/api/relationships').json() if v['decisions'])
    for username in sorted({c['username'] for c in cases}):
        with httpx.Client(base_url=base,timeout=15) as client:
            login(client,username)
            for c in cases:
                if c['username']!=username:continue
                record=client.get('/api/cases/'+c['id']).json()
                assert record['original_sha256']==c['original_sha256'] and record['version']==c['version']
                for a in c['attachments']:
                    downloaded=client.get('/api/attachments/'+a['id'])
                    assert downloaded.status_code==200 and hashlib.sha256(downloaded.content).hexdigest()==a['sha256']
    with httpx.Client(base_url=base,timeout=15) as management:
        login(management,'management@demo.test');params={'institution':'DEMO-INST-017'}
        report=management.get('/api/reports',params=params).json()
        export=management.get('/api/reports/csv',params=params)
        exported=list(csv.DictReader(io.StringIO(export.content.decode('utf-8-sig'))))
        assert report['total']==len(exported)==7
        assert {r['id'] for r in report['rows']}=={r['id'] for r in exported}
        assert all(r['subject']=='Restricted narrative' for r in exported)
    result={'phase':args.phase,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'context_id':settings.context_id,
        'case_count':len(cases),'cases':cases,'groups':groups,'decisions':decisions,'notifications':notifications,'clock_offset_seconds':offset,
        'original_context_case_count':5,'original_context_clock_offset':0,'management_csv_count':7,'private_bytes_verified':True}
    if args.phase=='before-clock':assert offset==0
    else:
        before=json.loads((evidence/'before-clock.json').read_text(encoding='utf-8'))
        assert offset==120*3600
        assert {c['id']:(c['owner_id'],c['bureau'],c['due_at'],c['original_sha256']) for c in cases}=={c['id']:(c['owner_id'],c['bureau'],c['due_at'],c['original_sha256']) for c in before['cases']}
        elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(before['observed_at_utc'])).total_seconds()
        assert 0<=elapsed<3600,'Host wall time was not expected to advance by the virtual clock amount'
        result['stored_deadlines_owners_originals_unchanged']=True
        result['wall_elapsed_seconds_since_before_clock']=elapsed
    if args.phase=='after-restart':
        before=json.loads((evidence/'before-restart.json').read_text(encoding='utf-8'))
        for key in ['cases','groups','decisions','notifications','clock_offset_seconds']:assert result[key]==before[key],key
        result['matches_before_restart']=True
    (evidence/(args.phase+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['phase','passed','case_count','clock_offset_seconds','management_csv_count','private_bytes_verified']}))


if __name__=='__main__':main()
