"""Persistent illustrative policy, per-database demo time, and scoped in-app delivery."""
from datetime import timedelta
import hashlib
import json
import time
from pathlib import Path
from types import SimpleNamespace
from fastapi import Depends, HTTPException, Request
from pydantic import Field
from sqlalchemy import or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .auth import Principal, get_db, mutation, principal, utc
from .config import ROOT
from .coordination import group_view, pair_authorized, refresh_coordination
from .models import (AdministrativeEvent, AdministrativePolicy, CaseRecord, CoordinationGroup, DemoContext,
    Membership, Notification, RelationshipSuggestion, SchedulerEffect, Transfer, User, WorkflowEvent, now)
from .policies import can_read
from .schemas import StrictInput
from .workflows import change_case, expire_transfers, receiving


def context_now(db):
    context=db.scalar(select(DemoContext))
    return now()+timedelta(seconds=context.clock_offset_seconds if context and context.synthetic else 0)


def is_admin(actor):
    return any(m.role=='SYSTEM_ADMIN' for m in actor.memberships)


def require_demo_controls(settings,db):
    context=db.get(DemoContext,settings.context_id)
    allowed=(ROOT/'.demo-contexts').resolve()
    data=settings.data_dir.resolve()
    marker=data/'SYNTHETIC_CONTEXT.json'
    if not settings.demo_controls or settings.environment not in {'demo','test'} or not data.is_relative_to(allowed) or data==allowed or not context or not context.synthetic:
        raise HTTPException(403,'Demo clock/reset require an explicitly enabled, marked isolated context under .demo-contexts; the normal workspace is protected.')
    try:mark=json.loads(marker.read_text(encoding='utf-8'))
    except (OSError,ValueError):raise HTTPException(403,'Isolated synthetic context marker is missing or invalid.')
    if mark!={'context_id':context.id,'synthetic':True}:raise HTTPException(403,'Context marker does not match the database.')
    return context


def notification_allowed(db,actor,n):
    if n.user_id!=actor.user.id:return False
    if n.case_id:
        case=db.get(CaseRecord,n.case_id)
        if not case or not can_read(db,actor,case,'M'):return False
    if n.group_id:
        group=db.get(CoordinationGroup,n.group_id)
        if not group or not group_view(db,actor,group):return False
    if n.suggestion_id:
        s=db.get(RelationshipSuggestion,n.suggestion_id)
        if not s or not pair_authorized(db,actor,db.get(CaseRecord,s.left_id),db.get(CaseRecord,s.right_id)):return False
    if n.transfer_id:
        t=db.get(Transfer,n.transfer_id)
        if not t or not (receiving(actor,t) or actor.user.id in {t.source_owner_id,t.requester_id} or any(m.role=='BUREAU_SUPERVISOR' and m.bureau_id==t.source_bureau_id for m in actor.memberships)):return False
    return True


def notify(db,actor,policy,kind,title,key,at,case=None,group=None,suggestion=None,transfer=None):
    digest=hashlib.sha256((actor.user.id+':'+str(policy.version)+':'+key).encode()).hexdigest()
    if db.scalar(select(Notification.id).where(Notification.dedup_key==digest)):return 0
    db.add(Notification(user_id=actor.user.id,case_id=case.id if case else None,group_id=group.id if group else None,
        suggestion_id=suggestion.id if suggestion else None,transfer_id=transfer.id if transfer else None,kind=kind,title=title,dedup_key=digest,policy_version=policy.version,created_at=at,available_at=at))
    db.flush();return 1


def run_scheduler(sessions,at=None):
    for attempt in range(3):
        try:return _run_scheduler(sessions,at)
        except (SQLAlchemyError,HTTPException) as error:
            if isinstance(error,HTTPException) and error.status_code!=409:raise
            if attempt==2:raise
            time.sleep(.025*(attempt+1))


def _run_scheduler(sessions,at=None):
    # The same routine serves the real worker, clock control and deterministic boundary tests.
    with sessions() as db:instant=at or context_now(db)
    expired=expire_transfers(sessions,instant)
    created=escalated=0
    with sessions() as db:
        policy=db.get(AdministrativePolicy,'DEMO_DEFAULT')
        if not policy:return {'created':0,'escalated':0,'expired':expired}
        cases=list(db.scalars(select(CaseRecord)))
        for c in cases:
            if c.lifecycle=='DISPOSED' or not c.due_at or not policy.auto_escalate:continue
            if instant>=utc(c.due_at)+timedelta(hours=policy.escalation_hours) and instant>utc(c.due_at):
                key=f'escalation:{c.id}:due{c.due_version}:policy{policy.version}'
                if not db.get(SchedulerEffect,key):
                    db.add(SchedulerEffect(key=key,created_at=instant));db.flush()
                    change_case(db,c,c.version,None,'POLICY_ESCALATION',policy.label,business_at=instant,escalation_level=c.escalation_level+1)
                    db.flush();db.refresh(c);escalated+=1
        refresh_coordination(db)
        groups=list(db.scalars(select(CoordinationGroup)))
        suggestions=list(db.scalars(select(RelationshipSuggestion)))
        transfers=list(db.scalars(select(Transfer)))
        actors=[SimpleNamespace(user=u,memberships=list(db.scalars(select(Membership).where(Membership.user_id==u.id)))) for u in db.scalars(select(User).where(User.active.is_(True)))]
        for actor in actors:
            for c in cases:
                if not can_read(db,actor,c,'M'):continue
                if c.lifecycle!='DISPOSED':
                    created+=notify(db,actor,policy,'PENDING_ACTION','A permitted case has a pending next action',f'pending:{c.id}:{c.version}',instant,case=c)
                    if c.due_at:
                        delta=utc(c.due_at)-instant
                        if timedelta(0)<=delta<=timedelta(hours=policy.approaching_hours):
                            created+=notify(db,actor,policy,'APPROACHING_DEADLINE','A permitted case is approaching its illustrative deadline',f'approaching:{c.id}:due{c.due_version}',instant,case=c)
                        if instant>utc(c.due_at):
                            created+=notify(db,actor,policy,'OVERDUE','A permitted case is overdue under the illustrative policy',f'overdue:{c.id}:due{c.due_version}',instant,case=c)
                for e in db.scalars(select(WorkflowEvent).where(WorkflowEvent.case_id==c.id,WorkflowEvent.event_type.in_(['ESCALATE','POLICY_ESCALATION','TRANSFER_REQUESTED','TRANSFER_ACCEPTED','TRANSFER_REJECTED','TRANSFER_CANCELLED','TRANSFER_EXPIRED']))):
                    created+=notify(db,actor,policy,'ESCALATION' if 'ESCALAT' in e.event_type else 'TRANSFER','A permitted workflow event requires attention',f'event:{e.id}',instant,case=c)
            for g in groups:
                if g.condition_active and group_view(db,actor,g):created+=notify(db,actor,policy,'COORDINATION','Shared institution — coordination required',f'group:{g.id}:{g.version}',instant,group=g)
            for s in suggestions:
                if pair_authorized(db,actor,db.get(CaseRecord,s.left_id),db.get(CaseRecord,s.right_id)):
                    created+=notify(db,actor,policy,'RELATIONSHIP_REVIEW','A potential relationship needs authorised evidence review',f'suggestion:{s.id}',instant,suggestion=s)
            for t in transfers:
                if receiving(actor,t) or actor.user.id in {t.source_owner_id,t.requester_id} or any(m.role=='BUREAU_SUPERVISOR' and m.bureau_id==t.source_bureau_id for m in actor.memberships):
                    created+=notify(db,actor,policy,'TRANSFER','A named transfer has a recorded request or decision',f'transfer:{t.id}:{t.version}',instant,transfer=t)
        db.commit()
    return {'created':created,'escalated':escalated,'expired':expired}


def deliver_one(sessions,at=None):
    with sessions() as db:
        instant=at or context_now(db)
        eligible=or_(Notification.state=='PENDING',(Notification.state=='DELIVERING')&(Notification.lease_until<instant))
        n=db.scalar(select(Notification).where(eligible,Notification.available_at<=instant,Notification.attempts<5).order_by(Notification.created_at).limit(1))
        if not n:return None
        claimed=db.execute(update(Notification).where(Notification.id==n.id,eligible).values(state='DELIVERING',lease_until=instant+timedelta(minutes=2),attempts=Notification.attempts+1).execution_options(synchronize_session=False))
        if claimed.rowcount!=1:db.rollback();return None
        db.commit()
        # In-app delivery has no external side effect. A crashed lease is retried.
        db.execute(update(Notification).where(Notification.id==n.id,Notification.state=='DELIVERING',Notification.lease_until==instant+timedelta(minutes=2)).values(state='DELIVERED',delivered_at=instant,lease_until=None))
        db.commit();return {'id':n.id,'state':'DELIVERED','integration':'in-app database only'}


class PolicyInput(StrictInput):
    expected_version:int=Field(ge=1)
    approaching_hours:int=Field(ge=0,le=720)
    escalation_hours:int=Field(ge=1,le=720)
    auto_escalate:bool
    reason:str=Field(min_length=5,max_length=1000)


class ClockInput(StrictInput):
    expected_version:int=Field(ge=1)
    advance_seconds:int=Field(ge=0,le=90*86400)
    reason:str=Field(min_length=5,max_length=1000)


def register_scheduling(app):
    @app.get('/api/notifications')
    def notifications(actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        return [{'id':n.id,'kind':n.kind,'title':n.title,'state':n.state,'created_at':utc(n.created_at).isoformat(),
            'delivered_at':utc(n.delivered_at).isoformat() if n.delivered_at else None,'acknowledged_at':utc(n.acknowledged_at).isoformat() if n.acknowledged_at else None,
            'case_id':db.get(CaseRecord,n.case_id).public_id if n.case_id else None,'group_id':n.group_id,'suggestion_id':n.suggestion_id,'transfer_id':n.transfer_id,'policy_version':n.policy_version}
            for n in db.scalars(select(Notification).where(Notification.user_id==actor.user.id).order_by(Notification.created_at.desc())) if notification_allowed(db,actor,n)]

    @app.post('/api/notifications/{notification_id}/acknowledge')
    def acknowledge(notification_id:str,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        n=db.get(Notification,notification_id)
        if not n or not notification_allowed(db,actor,n):raise HTTPException(404,'Notification unavailable.')
        if n.state not in {'DELIVERED','ACKNOWLEDGED'}:raise HTTPException(409,'In-app delivery has not completed yet.')
        if n.state!='ACKNOWLEDGED':n.state='ACKNOWLEDGED';n.acknowledged_at=context_now(db)
        db.commit();return {'id':n.id,'state':n.state}

    @app.get('/api/settings')
    def settings(request:Request,actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        p=db.get(AdministrativePolicy,'DEMO_DEFAULT');c=db.scalar(select(DemoContext))
        try:require_demo_controls(request.app.state.settings,db);clock=True
        except HTTPException:clock=False
        return {'policy':{'version':p.version,'approaching_hours':p.approaching_hours,'escalation_hours':p.escalation_hours,'auto_escalate':p.auto_escalate,'label':p.label},
            'can_administer':is_admin(actor),'context_id':c.id if c else None,'clock_version':c.clock_version if c else None,
            'clock_enabled':clock,'as_of':context_now(db).isoformat(),'clock_offset_seconds':c.clock_offset_seconds if c else 0,'integration':'in-app database only; no external email'}

    @app.post('/api/settings/policy')
    def policy(data:PolicyInput,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        if not is_admin(actor):raise HTTPException(403,'Technical policy administration required; it does not grant complaint access.')
        changed=db.execute(update(AdministrativePolicy).where(AdministrativePolicy.id=='DEMO_DEFAULT',AdministrativePolicy.version==data.expected_version).values(
            approaching_hours=data.approaching_hours,escalation_hours=data.escalation_hours,auto_escalate=data.auto_escalate,version=data.expected_version+1))
        if changed.rowcount!=1:db.rollback();raise HTTPException(409,'Policy changed. Reload and compare.')
        db.add(AdministrativeEvent(actor_id=actor.user.id,kind='POLICY_CHANGED',reason=data.reason,payload=data.model_dump(mode='json')))
        db.commit();return {'version':data.expected_version+1,'synthetic':True}

    @app.post('/api/demo/clock')
    def clock(data:ClockInput,request:Request,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        if not is_admin(actor):raise HTTPException(403,'Isolated demo clock requires technical administration.')
        context=require_demo_controls(request.app.state.settings,db)
        changed=db.execute(update(DemoContext).where(DemoContext.id==context.id,DemoContext.clock_version==data.expected_version).values(
            clock_offset_seconds=context.clock_offset_seconds+data.advance_seconds,clock_version=data.expected_version+1))
        if changed.rowcount!=1:db.rollback();raise HTTPException(409,'Clock changed. Reload and compare.')
        db.add(AdministrativeEvent(actor_id=actor.user.id,kind='DEMO_CLOCK_ADVANCED',reason=data.reason,payload=data.model_dump(mode='json')))
        db.commit()
        result=run_scheduler(request.app.state.sessions)
        return {'context_id':context.id,'host_clock_changed':False,'stored_deadlines_changed':False,'scheduler':'Executed in isolated synthetic context; complaint counts are not disclosed to technical administration'}

    @app.post('/api/settings/run-worker')
    def batch(request:Request,actor:Principal=Depends(mutation)):
        if not is_admin(actor):raise HTTPException(403,'Technical operation requires administration.')
        run_scheduler(request.app.state.sessions)
        for _ in range(100):
            if deliver_one(request.app.state.sessions) is None:break
        return {'status':'Persisted in-app scheduler/delivery batch completed','external_messages_sent':False}
