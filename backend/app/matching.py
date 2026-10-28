"""Bounded, explainable matching. No model or text is allowed to execute actions."""
from collections import Counter
import hashlib
import math
import re
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import case as sql_case, func, or_, select
from sqlalchemy.orm import Session
from .auth import Principal, get_db, mutation, principal
from .coordination import make_suggestion, normal, pair_authorized, suggestion_view
from .models import CaseRecord, Complainant, EmbeddingCache
from .policies import grants, load_case, visible_cases
from .schemas import StrictInput
from .workflows import capability

BASELINE='lexical-rules-v1.1'
VECTOR='hashed-character-ngrams-128-v1'
LIMIT=50
MAX_CHARS=8000
WORDS={'reimbursement':'refund','reimburse':'refund','repayment':'refund','moneyback':'refund','fees':'fee',
       'cancelled':'cancel','cancellation':'cancel','canceled':'cancel','salary':'salary','wages':'salary','payroll':'salary',
       'unpaid':'pending','delayed':'pending','awaiting':'pending','returned':'refund','student':'student','faculty':'faculty'}


def bounded_text(record):
    value=record.get('subject','')+' '+record.get('description','')
    return value if len(value)<=MAX_CHARS else value[:4000]+' '+value[-4000:]


def tokens(record):
    return {WORDS.get(w,w) for w in normal(bounded_text(record)).split() if len(w)>2}


def facts(record):
    text=bounded_text(record)
    result=dict(record.get('facts') or {})
    for key,pattern in [('incident_reference',r'\b(?:DEMO-BATCH-\d+|INC-[\w-]+)\b'),('receipt_reference',r'\bR-\d+\b'),
                        ('incident_date',r'\b\d{4}-\d{2}-\d{2}\b'),('amount',r'[₹$]\s?[\d,]+')]:
        if not result.get(key):
            match=re.search(pattern,text,re.I)
            if match:result[key]=match.group(0).upper()
    return result


def citation(record,field,value):
    if field in {'description','subject'}:
        return {'case_id':record['id'],'field':field,'excerpt':value}
    return {'case_id':record['id'],'field':field,'value':value}


def assess_pair(left,right):
    a,b=facts(left),facts(right)
    supporting=[];conflicting=[];missing=[]
    same_institution=left.get('institution_id')==right.get('institution_id') and bool(left.get('institution_id'))
    for key in ['incident_reference','incident_date','receipt_reference','amount','remedy']:
        av,bv=a.get(key),b.get(key)
        if av and bv:
            destination=supporting if normal(str(av))==normal(str(bv)) else conflicting
            for record,value in [(left,av),(right,bv)]:
                raw=(record.get('facts') or {}).get(key)
                if raw:destination.append(citation(record,'facts.'+key,str(value)))
                elif str(value).casefold() in record.get('description','').casefold():
                    # Preserve the exact original excerpt, including its case.
                    start=record['description'].casefold().index(str(value).casefold())
                    destination.append(citation(record,'description',record['description'][start:start+len(str(value))]))
        else:missing.append(key+' is not present in both sources')
    category_a,category_b=normal(left.get('category','')),normal(right.get('category',''))
    independent=category_a!=category_b and {category_a,category_b}.issubset({'fee refund','faculty grievance','infrastructure'})
    contradiction=any(a.get(k) and b.get(k) and normal(str(a[k]))!=normal(str(b[k])) for k in ['incident_date','incident_reference','amount','remedy'])
    same_incident=bool(a.get('incident_reference') and normal(a['incident_reference'])==normal(b.get('incident_reference','')))
    same_token=bool(left.get('complainant_token') and left.get('complainant_token')==right.get('complainant_token'))
    same_receipt=bool(a.get('receipt_reference') and normal(a['receipt_reference'])==normal(b.get('receipt_reference','')))
    if not same_institution:
        label='UNKNOWN';missing.append('Confirmed common institution required; name similarity cannot establish it')
    elif independent and not same_incident:
        label='INDEPENDENT'
    elif independent and same_incident:
        label='UNKNOWN';missing.append('Conflicting category and shared-incident evidence require human review')
    elif contradiction:
        label='UNKNOWN';missing.append('Conflicting explicit incident/date facts require human review')
    elif same_incident and same_token and same_receipt:
        label='DUPLICATE'
    elif same_incident and left.get('complainant_token') and right.get('complainant_token') and not same_token:
        label='RELATED'
    else:
        label='UNKNOWN';missing.append('Insufficient incident/request/complainant agreement to propose a stronger relationship')
    for record in [left,right]:
        supporting += [citation(record,'institution_id',record.get('institution_id','')),citation(record,'category',record.get('category',''))]
    if same_incident:
        destination=supporting if same_token else conflicting
        for record in [left,right]:destination.append(citation(record,'complainant_token',record.get('complainant_token') or ''))
    overlap=len(tokens(left)&tokens(right))/max(1,len(tokens(left)|tokens(right)))
    score=.25*overlap+.2*(category_a==category_b)+.4*same_incident+.15*same_receipt
    return {'proposed_label':label,'rank_score':round(score,6),'supporting':supporting,'conflicting':conflicting,
        'missing':missing,'method':BASELINE,'score_meaning':'Ranking signal, not a calibrated probability',
        'input_limit':MAX_CHARS,'truncated':len(left.get('subject','')+' '+left.get('description',''))>MAX_CHARS or len(right.get('subject','')+' '+right.get('description',''))>MAX_CHARS}


def vector(record,db=None):
    text=normal(bounded_text(record))
    key=hashlib.sha256((VECTOR+'\n'+text).encode()).hexdigest()
    cached=db.get(EmbeddingCache,key) if db else None
    if cached:return cached.vector
    values=[0.0]*128
    for size in [3,4]:
        for start in range(max(0,len(text)-size+1)):
            gram=text[start:start+size]
            digest=hashlib.blake2b(gram.encode(),digest_size=8).digest()
            values[int.from_bytes(digest[:4],'little')%128]+=1 if digest[4]%2 else -1
    norm=math.sqrt(sum(v*v for v in values)) or 1
    values=[v/norm for v in values]
    if db:db.add(EmbeddingCache(key=key,model=VECTOR,vector=values));db.flush()
    return values


def rank_candidates(query,candidates,method='baseline',db=None):
    rows=[]
    qvector=vector(query,db) if method=='char-vectors' else None
    for candidate in candidates[:LIMIT]:
        assessment=assess_pair(query,candidate)
        score=assessment['rank_score']
        if qvector is not None:
            similarity=sum(a*b for a,b in zip(qvector,vector(candidate,db)))
            score=.75*score+.25*max(0,similarity)
        rows.append({'case_id':candidate['id'],'score':round(score,6),'assessment':assessment})
    return sorted(rows,key=lambda row:(-row['score'],row['case_id']))


def record_input(db,case):
    return {'id':case.public_id,'version':case.version,'institution_id':case.institution_id,'subject':case.subject,
        'description':case.description,'category':case.category,'facts':case.facts,
        'complainant_token':db.scalar(select(Complainant.synthetic_token).where(Complainant.case_id==case.id))}


class EvidenceCitation(BaseModel):
    model_config=ConfigDict(extra='forbid')
    case_id:str
    field:Literal['description','subject','institution_id','category','complainant_token','facts.incident_reference','facts.incident_date','facts.receipt_reference','facts.amount','facts.remedy']
    excerpt:str|None=Field(default=None,max_length=2000)
    value:str|None=Field(default=None,max_length=500)


class AdapterOutput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    proposed_label:Literal['DUPLICATE','RELATED','INDEPENDENT','UNKNOWN']
    source_versions:dict[str,int]
    supporting:list[EvidenceCitation]=Field(min_length=2,max_length=30)
    conflicting:list[EvidenceCitation]=Field(max_length=30)
    missing:list[str]=Field(max_length=20)


def validate_adapter_output(payload,sources):
    output=AdapterOutput.model_validate(payload)
    authorised={s['id']:s for s in sources}
    if output.source_versions!={s['id']:s['version'] for s in sources}:raise ValueError('Invented or stale source versions')
    if {c.case_id for c in output.supporting}!=set(authorised):raise ValueError('Both authorised source cases must support review')
    for c in output.supporting+output.conflicting:
        source=authorised.get(c.case_id)
        if source is None:raise ValueError('Unauthorised citation')
        value=(source.get('facts') or {}).get(c.field.split('.',1)[1]) if c.field.startswith('facts.') else source.get(c.field)
        if c.field in {'description','subject'}:
            if not c.excerpt or c.value is not None or c.excerpt not in (value or ''):raise ValueError('Invented excerpt')
        elif c.excerpt is not None or c.value is None or c.value!=str(value):raise ValueError('Invented structured reference')
    return output.model_dump(mode='json')


def safe_semantic_adapter(adapter,sources):
    if adapter is None:return {'available':False,'reason':'No semantic adapter configured','suggestion':None}
    try:
        validated=validate_adapter_output(adapter(sources),sources)
        return {'available':True,'reason':'Validated suggestion only; authorised review required','suggestion':validated}
    except Exception:
        return {'available':False,'reason':'Semantic adapter failed or returned invalid evidence; rule-based checks remain active','suggestion':None}


class MatchingInput(StrictInput):
    expected_version:int=Field(ge=1)
    method:Literal['baseline','char-vectors']='baseline'


def register_matching(app):
    @app.get('/api/matching/status')
    def status(actor:Principal=Depends(principal)):
        return {'semantic_available':False,'message':'Semantic matching unavailable — rule-based checks active',
            'baseline':BASELINE,'research_encoder':VECTOR,'encoder_is_semantic':False,'enhanced_enabled':False,'default':'baseline',
            'candidate_limit':LIMIT,'input_char_limit':MAX_CHARS,'languages':'English rule vocabulary; character encoder is script agnostic but not a validated multilingual semantic model'}

    @app.post('/api/cases/{public_id}/matching')
    def matching(public_id:str,data:MatchingInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        case=load_case(db,actor,public_id)
        if data.method!='baseline':raise HTTPException(422,'Character-vector comparison is retained in the research harness only: measured retrieval did not improve. Use the baseline.')
        if case.version!=data.expected_version:raise HTTPException(409,'Source changed. Reload before retrieving evidence.')
        if not pair_authorized(db,actor,case,case):
            raise HTTPException(403,'Matching requires delegated pair review and separate source evidence grants.')
        if case.identity_status not in {'CONFIRMED_SELECTION','CONFIRMED_HUMAN'}:raise HTTPException(422,'Confirm institution identity before matching.')
        narrative=or_(CaseRecord.current_owner_id==actor.user.id,CaseRecord.id.in_(grants(actor,'N')))
        identity=or_(CaseRecord.current_owner_id==actor.user.id,CaseRecord.id.in_(grants(actor,'I')))
        source_record=record_input(db,case)
        reference=facts(source_record).get('incident_reference','')
        priority=sql_case((or_(func.lower(CaseRecord.facts['incident_reference'].as_string())==str(reference).casefold(),
            CaseRecord.description.contains(str(reference),autoescape=True)),1),else_=0) if reference else sql_case((CaseRecord.id==case.id,0),else_=0)
        candidates=list(db.scalars(select(CaseRecord).where(CaseRecord.institution_id==case.institution_id,
            CaseRecord.id!=case.id,CaseRecord.identity_status.in_(['CONFIRMED_SELECTION','CONFIRMED_HUMAN']),visible_cases(actor),narrative,identity)
            .order_by(priority.desc(),CaseRecord.created_at.desc(),CaseRecord.id).limit(LIMIT)))
        rows=rank_candidates(source_record,[record_input(db,c) for c in candidates],data.method,db)
        by_id={c.public_id:c for c in candidates};items=[]
        for row in rows:
            suggestion=make_suggestion(db,case,by_id[row['case_id']],method=BASELINE if data.method=='baseline' else BASELINE+'+'+VECTOR,
                label=row['assessment']['proposed_label'],evidence=row['assessment'])
            items.append({'rank_score':row['score'],'review':suggestion_view(db,actor,suggestion)})
        db.commit()
        return {'items':items,'candidate_count':len(items),'bounded_at':LIMIT,'method':data.method,'synthetic':True,
            'semantic_available':False,'message':'Semantic matching unavailable — rule-based checks active','no_case_action_performed':True}
