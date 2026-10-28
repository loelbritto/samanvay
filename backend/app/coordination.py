"""Deterministic institution coordination, explicit identity and human pair review."""
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .auth import Principal, get_db, mutation, principal, utc
from .models import (CaseRecord, Complainant, CoordinationGroup, GroupParticipant, GroupReview, IdentityDecision,
    Institution, InstitutionAlias, OutboxJob, RelationshipDecision, RelationshipSuggestion, User, WorkflowEvent, now)
from .policies import can_read, load_case, visible_cases
from .schemas import StrictInput
from .workflows import capability, change_case


def normal(value):
    return ' '.join(re.sub(r'[^\w\s]', ' ', unicodedata.normalize('NFKC', value).casefold()).split())


def lookup_identity(db, supplied, city=''):
    text, location = normal(supplied), normal(city)
    institutions = list(db.scalars(select(Institution)))
    exact = next((i for i in institutions if i.id.casefold() == supplied.strip().casefold()), None)
    candidates = []
    for i in institutions:
        names = [i.name, i.name+' '+i.city] + list(db.scalars(select(InstitutionAlias.alias).where(InstitutionAlias.institution_id==i.id)))
        matched = i is exact or any(text == normal(name) for name in names)
        if matched:
            candidates.append({'id':i.id, 'name':i.name, 'city':i.city, 'city_conflict':bool(location and location != normal(i.city)),
                'basis':'exact identifier' if i is exact else 'normalised name or recorded alias; human confirmation required'})
    usable = [c for c in candidates if not c['city_conflict']]
    selected = usable[0]['id'] if len(usable)==1 else None
    status = 'EXACT_ID' if exact and selected==exact.id else 'REVIEW_REQUIRED' if selected else 'AMBIGUOUS' if candidates else 'UNRESOLVED'
    return {'status':status, 'selected_candidate':selected, 'candidates':candidates, 'human_confirmation_required':status!='EXACT_ID', 'synthetic':True}


def refresh_coordination(db):
    records = list(db.scalars(select(CaseRecord).where(CaseRecord.identity_status.in_(['CONFIRMED_SELECTION','CONFIRMED_HUMAN']))))
    groups = {g.institution_id:g for g in db.scalars(select(CoordinationGroup))}
    by_institution = {}
    for case in records:
        by_institution.setdefault(case.institution_id, []).append(case)
    changed = 0
    for institution_id in set(by_institution) | set(groups):
        cases = by_institution.get(institution_id, [])
        active = len({c.current_bureau_id for c in cases if c.lifecycle!='DISPOSED'}) >= 2
        source_fingerprint=hashlib.sha256(json.dumps(sorted((c.id,c.version) for c in cases)).encode()).hexdigest()
        group = groups.get(institution_id)
        if group is None:
            if not active:
                continue
            group = CoordinationGroup(institution_id=institution_id,source_fingerprint=source_fingerprint)
            db.add(group); db.flush()
            db.add(GroupReview(group_id=group.id,actor_id=None,action='DETECTED',reason='Confirmed institution has active cases in multiple current bureaus; no relationship claim',payload={},version=1))
            changed += 1
        elif group.condition_active != active or group.source_fingerprint != source_fingerprint:
            next_version=group.version+1
            next_state='REVIEW_REQUIRED' if active and not group.condition_active and group.state=='RESOLVED' else group.state
            updated=db.execute(update(CoordinationGroup).where(CoordinationGroup.id==group.id,CoordinationGroup.version==group.version).values(
                condition_active=active,source_fingerprint=source_fingerprint,version=next_version,state=next_state).execution_options(synchronize_session=False))
            if updated.rowcount!=1:raise HTTPException(409,'Coordination sources changed concurrently; retry deterministic refresh.')
            db.refresh(group)
            db.add(GroupReview(group_id=group.id,actor_id=None,action='CONDITION_CHANGED',reason='Deterministic concurrent-bureau condition re-evaluated; human work retained',payload={'active':active},version=next_version))
            changed += 1
        for case in cases:
            if not db.scalar(select(GroupParticipant.id).where(GroupParticipant.group_id==group.id,GroupParticipant.case_id==case.id)):
                db.add(GroupParticipant(group_id=group.id,case_id=case.id))
    db.flush()
    return changed


def process_domain_one(sessions):
    with sessions() as db:
        job=db.scalar(select(OutboxJob).where(OutboxJob.kind=='DOMAIN_CHANGED',OutboxJob.status=='PENDING').order_by(OutboxJob.available_at).limit(1))
        if not job:return None
        changed=db.execute(update(OutboxJob).where(OutboxJob.id==job.id,OutboxJob.status=='PENDING').values(status='RUNNING',attempts=OutboxJob.attempts+1).execution_options(synchronize_session=False))
        if changed.rowcount!=1:db.rollback();return None
        refresh_coordination(db)
        job.status='DONE';job.completed_at=now()
        db.commit()
        return {'job':job.id,'kind':'DOMAIN_CHANGED','status':'DONE'}


def pair_authorized(db,actor,left,right):
    return left.institution_id==right.institution_id and capability(db,actor,'REVIEW_PAIR',left) and all(can_read(db,actor,c,k) for c in [left,right] for k in ['M','N','I'])


def fingerprint(db,left,right,include_versions=True,include_facts=True):
    values=[]
    for c in [left,right]:
        identity=db.scalar(select(Complainant).where(Complainant.case_id==c.id))
        from .models import Attachment
        value={'id':c.id,'version':c.version if include_versions else None,'institution':c.institution_id,'text':c.description,'subject':c.subject,'category':c.category,'token':identity.synthetic_token if identity else None,
            'attachments':sorted(db.scalars(select(Attachment.sha256).where(Attachment.case_id==c.id)))}
        if include_facts:value['facts']=c.facts
        values.append(value)
    return hashlib.sha256(json.dumps(values,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def make_suggestion(db,left,right,method='HUMAN_SOURCE_REVIEW',label='UNKNOWN',evidence=None):
    left,right=sorted([left,right],key=lambda c:c.id)
    digest=fingerprint(db,left,right)
    content_digest=fingerprint(db,left,right,False)
    for old in db.scalars(select(RelationshipSuggestion).where(RelationshipSuggestion.left_id==left.id,RelationshipSuggestion.right_id==right.id)):
        old_digest=content_digest
        if not old.evidence.get('fingerprint_version') and not any((left.facts or {}).values()) and not any((right.facts or {}).values()):
            old_digest=fingerprint(db,left,right,False,False)
        if old.evidence.get('source_content_fingerprint')==old_digest and db.scalar(select(RelationshipDecision.id).where(RelationshipDecision.suggestion_id==old.id,RelationshipDecision.action.in_(['CONFIRM','REJECT']))):
            return old
    existing=db.scalar(select(RelationshipSuggestion).where(RelationshipSuggestion.left_id==left.id,RelationshipSuggestion.right_id==right.id,RelationshipSuggestion.fingerprint==digest,RelationshipSuggestion.method==method))
    if existing:return existing
    previous=db.scalar(select(RelationshipSuggestion).where(RelationshipSuggestion.left_id==left.id,RelationshipSuggestion.right_id==right.id).order_by(RelationshipSuggestion.created_at.desc()).limit(1))
    evidence=dict(evidence or {'supporting':[],'conflicting':[],'missing':['No automated method applied; authorised human evidence review required']})
    evidence['source_content_fingerprint']=content_digest
    evidence['fingerprint_version']=2
    row=RelationshipSuggestion(left_id=left.id,right_id=right.id,left_version=left.version,right_version=right.version,
        fingerprint=digest,method=method,proposed_label=label,evidence=evidence,previous_id=previous.id if previous else None)
    db.add(row);db.flush();return row


def suggestion_view(db,actor,row):
    left,right=db.get(CaseRecord,row.left_id),db.get(CaseRecord,row.right_id)
    if not pair_authorized(db,actor,left,right):
        raise HTTPException(404,'Pair evidence unavailable. Ask an authorised coordinator to review.')
    decisions=list(db.scalars(select(RelationshipDecision).where(RelationshipDecision.suggestion_id==row.id).order_by(RelationshipDecision.created_at)))
    final=any(d.action in {'CONFIRM','REJECT'} for d in decisions)
    include_facts=bool(row.evidence.get('fingerprint_version'))
    content_unchanged=row.evidence.get('source_content_fingerprint')==fingerprint(db,left,right,False,include_facts)
    if not include_facts and (any((left.facts or {}).values()) or any((right.facts or {}).values())):content_unchanged=False
    versions_changed=[left.version,right.version]!=[row.left_version,row.right_version]
    stale=not content_unchanged or (not final and versions_changed)
    return {'id':row.id,'left':left.public_id,'right':right.public_id,'left_version':row.left_version,'right_version':row.right_version,
        'current_versions':[left.version,right.version],'fingerprint':row.fingerprint,'method':row.method,'proposed_label':row.proposed_label,
        'evidence':row.evidence,'previous_id':row.previous_id,'version':row.version,'stale':stale,
        'workflow_versions_changed':versions_changed,'decision_applies_to_unchanged_evidence':final and content_unchanged,
        'decisions':[{'action':d.action,'label':d.label,'reason':d.reason,'actor':db.get(User,d.actor_id).display_name,'at':utc(d.created_at).isoformat()} for d in decisions],
        'sources':[{'id':c.public_id,'version':c.version,'subject':c.subject,'description':c.description,'category':c.category,
            'institution_id':c.institution_id,'complainant_token':db.scalar(select(Complainant.synthetic_token).where(Complainant.case_id==c.id))} for c in [left,right]],'synthetic':True}


class IdentityInput(StrictInput):
    institution_id:str
    expected_version:int=Field(ge=1)
    reason:str=Field(min_length=5,max_length=1000)
    provenance:str=Field(min_length=5,max_length=1000)
    alias:str=Field(default='',max_length=180)
    acknowledge_conflict:bool=False


class PairInput(StrictInput):
    left:str
    right:str


class ReviewInput(StrictInput):
    action:Literal['CONFIRM','REJECT','DEFER']
    label:Literal['DUPLICATE','RELATED','INDEPENDENT','UNKNOWN']|None=None
    expected_version:int=Field(ge=1)
    left_version:int=Field(ge=1)
    right_version:int=Field(ge=1)
    fingerprint:str
    reason:str=Field(min_length=5,max_length=2000)


class GroupInput(StrictInput):
    state:Literal['IN_REVIEW','PLANNED','RESOLVED','DEFER']
    expected_version:int=Field(ge=1)
    reason:str=Field(min_length=5,max_length=2000)
    next_action:str=Field(min_length=3,max_length=500)
    lead_id:str|None=None
    due_at:datetime|None=None


def group_view(db,actor,g):
    participants=list(db.scalars(select(CaseRecord).join(GroupParticipant,GroupParticipant.case_id==CaseRecord.id).where(GroupParticipant.group_id==g.id)))
    # A partial viewer must not infer hidden participation from a group alert/count.
    if not participants or not all(can_read(db,actor,c,'M') for c in participants):return None
    institution=db.get(Institution,g.institution_id)
    return {'id':g.id,'institution_id':institution.id,'institution':institution.name+', '+institution.city,'label':'Shared institution — coordination required',
        'condition_active':g.condition_active,'state':g.state,'version':g.version,'lead':db.get(User,g.lead_id).display_name if g.lead_id else None,
        'lead_id':g.lead_id,'lead_bureau':g.lead_bureau_id,'next_action':g.next_action,'due_at':utc(g.due_at).isoformat() if g.due_at else None,
        'can_review':capability(db,actor,'COORDINATE',institution_id=g.institution_id),
        'cases':[{'id':c.public_id,'owner':db.get(User,c.current_owner_id).display_name,'bureau':c.current_bureau_id,'lifecycle':c.lifecycle,'current_institution_id':c.institution_id,'historical_participation':c.institution_id!=g.institution_id,'due_at':utc(c.due_at).isoformat() if c.due_at else None} for c in participants],
        'reviews':[{'action':r.action,'reason':r.reason,'at':utc(r.created_at).isoformat(),'actor':db.get(User,r.actor_id).display_name if r.actor_id else 'Deterministic coordination service','version':r.version} for r in db.scalars(select(GroupReview).where(GroupReview.group_id==g.id).order_by(GroupReview.created_at))]}


def register_coordination(app,serialize):
    @app.get('/api/identity/lookup')
    def lookup(q:str='',city:str='',actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        return lookup_identity(db,q[:500],city[:100])

    @app.post('/api/cases/{public_id}/identity')
    def identity(public_id:str,data:IdentityInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        case=load_case(db,actor,public_id)
        target=db.get(Institution,data.institution_id)
        if not capability(db,actor,'IDENTITY',case) or not can_read(db,actor,case,'N'):
            raise HTTPException(403,'Scoped identity delegation and narrative access are required.')
        if not target or not capability(db,actor,'IDENTITY',institution_id=target.id):
            raise HTTPException(422,'The selected institution is outside identity delegation.')
        conflicts=[i.city for i in db.scalars(select(Institution)) if normal(i.city) in normal(case.original_institution_text) and i.city!=target.city]
        if conflicts and not data.acknowledge_conflict:
            raise HTTPException(422,'Original location conflicts with this identity. Explicitly acknowledge and explain the evidence.')
        old=case.institution_id
        change_case(db,case,data.expected_version,actor.user.id,'IDENTITY_CONFIRMED',data.reason,institution_id=target.id,identity_status='CONFIRMED_HUMAN')
        db.add(IdentityDecision(case_id=case.id,previous_institution_id=old,institution_id=target.id,original_text=case.original_institution_text,
            reason=data.reason,provenance=data.provenance,actor_id=actor.user.id,case_version=data.expected_version+1))
        if data.alias and not db.scalar(select(InstitutionAlias.id).where(InstitutionAlias.institution_id==target.id,InstitutionAlias.alias==data.alias)):
            db.add(InstitutionAlias(institution_id=target.id,alias=data.alias,provenance=data.provenance,confirmed_by=actor.user.id))
        db.commit();db.expire_all()
        return serialize(db,actor,load_case(db,actor,public_id),detail=True)

    @app.get('/api/coordination')
    def groups(actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        return [view for g in db.scalars(select(CoordinationGroup)) if (view:=group_view(db,actor,g)) is not None]

    @app.post('/api/coordination/{group_id}/review')
    def group_review(group_id:str,data:GroupInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        refresh_coordination(db)
        db.expire_all()
        g=db.get(CoordinationGroup,group_id)
        if not g or not group_view(db,actor,g):raise HTTPException(404,'Coordination item unavailable.')
        if not capability(db,actor,'COORDINATE',institution_id=g.institution_id):raise HTTPException(403,'Scoped coordination delegation required.')
        if g.version!=data.expected_version:raise HTTPException(409,'Coordination sources changed. Reload and compare before reviewing.')
        transitions={'REVIEW_REQUIRED':{'IN_REVIEW','DEFER'},'IN_REVIEW':{'PLANNED','DEFER'},'PLANNED':{'IN_REVIEW','RESOLVED','DEFER'},'RESOLVED':{'IN_REVIEW','DEFER'}}
        if data.state not in transitions[g.state]:raise HTTPException(422,'Invalid coordination state transition.')
        if data.due_at and data.due_at.tzinfo is None:raise HTTPException(422,'Deadline needs a UTC offset.')
        lead=db.get(User,data.lead_id) if data.lead_id else None
        if data.state=='PLANNED' and (not lead or not lead.active):raise HTTPException(422,'A plan needs an active named coordination lead.')
        from .models import Membership
        target_institution=db.get(Institution,g.institution_id)
        from sqlalchemy import or_
        bureau=db.scalar(select(Membership.bureau_id).where(Membership.user_id==lead.id,Membership.bureau_id.is_not(None),
            Membership.role.in_(['RB_OFFICER','PGRC_OFFICER','REGIONAL_OFFICER','BUREAU_SUPERVISOR']),
            or_(Membership.region_id.is_(None),Membership.region_id==target_institution.region_id))) if lead else None
        if lead and not bureau:raise HTTPException(422,'Choose an active eligible coordination officer and bureau in this institution scope.')
        changed=db.execute(update(CoordinationGroup).where(CoordinationGroup.id==g.id,CoordinationGroup.version==data.expected_version).values(
            state=g.state if data.state=='DEFER' else data.state,next_action=data.next_action,lead_id=lead.id if lead else g.lead_id,
            lead_bureau_id=bureau if lead else g.lead_bureau_id,due_at=data.due_at,version=data.expected_version+1).execution_options(synchronize_session=False))
        if changed.rowcount!=1:db.rollback();raise HTTPException(409,'Coordination changed. Reload and compare.')
        db.add(GroupReview(group_id=g.id,actor_id=actor.user.id,action=data.state,reason=data.reason,payload=data.model_dump(mode='json'),version=data.expected_version+1))
        db.commit();db.expire_all();return group_view(db,actor,db.get(CoordinationGroup,g.id))

    @app.get('/api/institutions/{institution_id}/timeline')
    def timeline(institution_id:str,actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        cases=list(db.scalars(select(CaseRecord).where(CaseRecord.institution_id==institution_id,visible_cases(actor))))
        return {'cases':[serialize(db,actor,c) for c in cases],'events':[{'case_id':c.public_id,'type':e.event_type,'at':utc(e.occurred_at).isoformat(),
            'reason':e.reason if can_read(db,actor,c,'N') else 'Details restricted','owner':db.get(User,c.current_owner_id).display_name,'bureau':c.current_bureau_id}
            for c in cases for e in db.scalars(select(WorkflowEvent).where(WorkflowEvent.case_id==c.id).order_by(WorkflowEvent.occurred_at))]}

    @app.post('/api/relationships/source-review',status_code=201)
    def source_review(data:PairInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        left,right=load_case(db,actor,data.left),load_case(db,actor,data.right)
        if left.id==right.id or not pair_authorized(db,actor,left,right):raise HTTPException(404,'Pair unavailable for review.')
        row=make_suggestion(db,left,right);db.commit();return suggestion_view(db,actor,row)

    @app.get('/api/relationships')
    def suggestions(actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        return [suggestion_view(db,actor,r) for r in db.scalars(select(RelationshipSuggestion).order_by(RelationshipSuggestion.created_at.desc()))
            if pair_authorized(db,actor,db.get(CaseRecord,r.left_id),db.get(CaseRecord,r.right_id))]

    @app.post('/api/relationships/{suggestion_id}/decision')
    def decision(suggestion_id:str,data:ReviewInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        row=db.get(RelationshipSuggestion,suggestion_id)
        if not row:raise HTTPException(404,'Review unavailable.')
        view=suggestion_view(db,actor,row)
        if view['stale'] or data.fingerprint!=row.fingerprint or [data.left_version,data.right_version]!=[row.left_version,row.right_version]:
            raise HTTPException(409,'Evidence changed. Create a new review; prior decisions remain.')
        terminal=db.scalar(select(RelationshipDecision.id).where(RelationshipDecision.suggestion_id==row.id,RelationshipDecision.action.in_(['CONFIRM','REJECT'])))
        if terminal:raise HTTPException(409,'A final decision already exists for this evidence; it is preserved.')
        if data.action=='CONFIRM' and data.label is None:raise HTTPException(422,'Choose a relationship label for confirmation.')
        changed=db.execute(update(RelationshipSuggestion).where(RelationshipSuggestion.id==row.id,RelationshipSuggestion.version==data.expected_version).values(version=data.expected_version+1).execution_options(synchronize_session=False))
        if changed.rowcount!=1:db.rollback();raise HTTPException(409,'Review changed. Reload and compare.')
        db.add(RelationshipDecision(suggestion_id=row.id,action=data.action,label=data.label if data.action=='CONFIRM' else None,
            reason=data.reason,actor_id=actor.user.id,suggestion_version=data.expected_version+1))
        db.commit();db.expire_all();return suggestion_view(db,actor,db.get(RelationshipSuggestion,row.id))
