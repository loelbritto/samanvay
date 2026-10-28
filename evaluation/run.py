"""Measure actual held-out synthetic outputs; never sends labels/splits to a method."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.auth import hasher
from app.config import Settings
from app.coordination import lookup_identity
from app.database import make_database
from app.matching import BASELINE,VECTOR,assess_pair,rank_candidates
from app.models import Base,EmbeddingCache,Institution,InstitutionAlias,Region,User
from sqlalchemy import func,select

CORPUS=ROOT/'evaluation/corpus-v1'
CLASSES=['DUPLICATE','RELATED','INDEPENDENT','UNKNOWN']


def read(name):return json.loads((CORPUS/name).read_text(encoding='utf-8'))


def audit_splits(cases,labels,splits):
    ids={c['id'] for c in cases};mapping=splits['case_split']
    assert ids==set(mapping) and len(ids)==len(cases)==240
    assert all(len({mapping[i] for i in members})==1 for group in ['generation_families','generation_templates'] for members in splits[group].values())
    assert all(mapping[p['left']]==mapping[p['right']]==p['split'] for p in labels)
    assert all(not any(key in c for key in ['label','split','generation_family','template','gold']) for c in cases)
    dev_institutions={c['institution_id'] for c in cases if mapping[c['id']]=='development'}
    unseen=set(splits['unseen_institution_ids']);assert not dev_institutions & unseen
    assert all(c['institution_id'] in unseen or c['institution_id'] is None for c in cases if mapping[c['id']]=='heldout-unseen')
    return {'passed':True,'case_count':240,'family_template_disjoint':True,'labels_isolated':True,'unseen_institutions':len(unseen)}


def classification(rows):
    matrix={gold:{pred:0 for pred in CLASSES} for gold in CLASSES}
    for r in rows:matrix[r['gold']][r['predicted']]+=1
    metrics={}
    for label in CLASSES:
        tp=matrix[label][label];fp=sum(matrix[g][label] for g in CLASSES if g!=label);fn=sum(matrix[label][p] for p in CLASSES if p!=label)
        precision=tp/(tp+fp) if tp+fp else 0;recall=tp/(tp+fn) if tp+fn else 0
        metrics[label]={'support':sum(matrix[label].values()),'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0}
    return {'n':len(rows),'per_class':metrics,'macro_f1':statistics.mean(v['f1'] for v in metrics.values()),'confusion_matrix':matrix,
        'unknown_coverage':sum(r['predicted']=='UNKNOWN' for r in rows)/len(rows) if rows else 0,
        'errors':sum(r['gold']!=r['predicted'] for r in rows)}


def latency(samples):
    values=sorted(samples)
    return {'n':len(values),'median_ms':statistics.median(values) if values else None,'p95_ms':values[min(len(values)-1,int(.95*len(values)))] if values else None,'total_ms':sum(values)}


def main():
    freeze=read('freeze.json')
    for name,digest in freeze['sha256'].items():assert hashlib.sha256((CORPUS/name).read_bytes()).hexdigest()==digest
    cases=read('cases.json');labels=read('labels.json');splits=read('splits.json');institutions=read('institutions.json')
    split_audit=audit_splits(cases,labels,splits);by_id={c['id']:c for c in cases}
    heldout=[p for p in labels if p['split'].startswith('heldout')]
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    directory=ROOT/'.demo-contexts'/('eval-cache-'+run_id);assert not directory.exists()
    engine,sessions=make_database(Settings(directory,'test'));Base.metadata.create_all(engine)
    with sessions() as db:
        db.add_all([Region(id='DEMO-WEST',name='Fictional west'),Region(id='DEMO-EAST',name='Fictional east')])
        reviewer=User(username='inactive-evaluation-directory@demo.test',display_name='Synthetic directory fixture',password_hash=hasher.hash('DemoOnly-Stage2!'),active=False)
        db.add(reviewer);db.flush()
        for i in institutions:
            db.add(Institution(id=i['id'],name=i['name'],city=i['city'],region_id=i['region']));db.flush()
            for alias in i['aliases']:db.add(InstitutionAlias(institution_id=i['id'],alias=alias,provenance='Generated synthetic canonical directory; no official verification',confirmed_by=reviewer.id))
        db.commit()
    raw_class=[];class_samples=[]
    for p in heldout:
        started=time.perf_counter_ns();result=assess_pair(by_id[p['left']],by_id[p['right']]);elapsed=(time.perf_counter_ns()-started)/1e6
        class_samples.append(elapsed);raw_class.append({'left':p['left'],'right':p['right'],'split':p['split'],'gold':p['label'],'predicted':result['proposed_label'],'evidence':result,'elapsed_ms':elapsed})
    positives=defaultdict(set)
    for p in heldout:
        if p['label'] in {'DUPLICATE','RELATED'}:positives[p['left']].add(p['right']);positives[p['right']].add(p['left'])
    queries=[by_id[key] for key in sorted(positives)]
    retrieval={};raw_retrieval=[]
    for method in ['baseline','char-vectors']:
        passes={};cache_counts=[]
        for mode in ['first-pass','warm-repeat']:
            samples=[];recall={1:[],3:[]};errors=0
            with sessions() as db:
                cache_before=db.scalar(select(func.count()).select_from(EmbeddingCache))
                for query in queries:
                    fold=splits['case_split'][query['id']]
                    gallery=[c for c in cases if c['id']!=query['id'] and c['institution_id']==query['institution_id'] and splits['case_split'][c['id']]==fold]
                    started=time.perf_counter_ns()
                    ranked=rank_candidates(query,gallery,method,db if method=='char-vectors' else None)
                    db.commit();elapsed=(time.perf_counter_ns()-started)/1e6;samples.append(elapsed)
                    ranks=[r['case_id'] for r in ranked]
                    for k in recall:recall[k].append(len(set(ranks[:k])&positives[query['id']])/len(positives[query['id']]))
                    if not set(ranks)&positives[query['id']]:errors+=1
                    raw_retrieval.append({'method':method,'pass':mode,'query_id':query['id'],'split':fold,'gallery_ids':[c['id'] for c in gallery],
                        'expected_counterparts':sorted(positives[query['id']]),'ranking':ranked,'elapsed_ms':elapsed})
                cache_after=db.scalar(select(func.count()).select_from(EmbeddingCache))
            passes[mode]={'latency':latency(samples),'recall_at_1':statistics.mean(recall[1]),'recall_at_3':statistics.mean(recall[3]),
                'queries_without_retrieved_counterpart':errors,'cache_rows_before':cache_before,'cache_rows_after':cache_after}
        retrieval[method]=passes
    identity_rows=[]
    identity_gold={g['id']:g for g in read('identity-labels.json')}
    with sessions() as db:
        for q in read('identity-queries.json'):
            truth=identity_gold[q['id']];result=lookup_identity(db,q['q'],q['city'])
            identity_rows.append({'query_id':q['id'],'split':truth['split'],'expected_status':truth['expected_status'],'expected_id':truth['expected_id'],
                'actual_status':result['status'],'actual_id':result['selected_candidate'],
                'passed':truth['expected_status']==result['status'] and truth['expected_id']==result['selected_candidate']})
    baseline=retrieval['baseline']['warm-repeat'];enhanced=retrieval['char-vectors']['warm-repeat']
    keep=enhanced['recall_at_3']>baseline['recall_at_3'] and enhanced['recall_at_1']>=baseline['recall_at_1']
    summary={'run_id':run_id,'observed_at_utc':datetime.now(timezone.utc).isoformat(),'synthetic_only':True,'corpus_freeze':freeze,
        'split_audit':split_audit,'classification':classification(raw_class),'classification_by_split':{fold:classification([r for r in raw_class if r['split']==fold]) for fold in ['heldout-known','heldout-unseen']},
        'classification_latency':latency(class_samples),'retrieval':retrieval,'identity_matching':{'n':len(identity_rows),'correct':sum(r['passed'] for r in identity_rows),'errors':[r for r in identity_rows if not r['passed']]},
        'comparison':{'classifier_shared':True,'baseline':BASELINE,'enhanced':BASELINE+'+'+VECTOR,'retain_enhanced_as_default':keep,'selected_default':'char-vectors' if keep else 'baseline',
            'rule':'Require strict recall@3 gain and no recall@1 loss; otherwise keep baseline. No improvement is inferred from equal synthetic scores.'},
        'hardware':{'platform':platform.platform(),'machine':platform.machine(),'processor_identifier':os.environ.get('PROCESSOR_IDENTIFIER','unavailable'),'logical_cpus':os.cpu_count(),'python':platform.python_version()},
        'measurement_scope':'In-process classification and bounded retrieval on preloaded JSON. Optional vector timing includes SQLite cache queries/commit; excludes HTTP/UI/model startup. First pass starts with an empty vector cache but later queries can hit it; warm-repeat reuses cache.',
        'limitations':['Explicit structured facts and small generated galleries make this an artificial benchmark; not real complaint accuracy.',
            'Gold policy labels were generated, not independently human-reviewed. No semantic model/LLM is connected; character vectors are statistical.',
            'This is a single-machine sample, not a national-scale or multilingual semantic performance claim.'],
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'evaluation/generate.py',ROOT/'backend/app/matching.py',ROOT/'backend/app/coordination.py']}}
    output=ROOT/'docs/evidence/stage8'/run_id;output.mkdir(parents=True)
    for name,value in [('summary.json',summary),('classification-raw.json',raw_class),('retrieval-raw.json',raw_retrieval),('identity-raw.json',identity_rows),
        ('false-positives-negatives.json',[r for r in raw_class if r['gold']!=r['predicted']])]:
        (output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'docs/evidence/stage8/latest.json').write_text(json.dumps({'run_id':run_id,'summary':str((output/'summary.json').relative_to(ROOT)).replace('\\','/')},indent=2)+'\n',encoding='utf-8')
    engine.dispose()
    print(json.dumps({'run_id':run_id,'classification':summary['classification'],'retrieval':retrieval,'identity_correct':summary['identity_matching']['correct'],
        'identity_n':len(identity_rows),'selected_default':summary['comparison']['selected_default'],'output':str(output)}))


if __name__=='__main__':main()
