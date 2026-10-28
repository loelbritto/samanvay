"""Human-authorised workflow commands. Every change is versioned and audited."""
from datetime import datetime, timedelta, timezone
from typing import Literal
from fastapi import Depends, HTTPException
from pydantic import Field
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session
from .auth import Principal, get_db, mutation, principal, utc
from .models import (Assignment, Attachment, CapabilityGrant, CaseAction, CaseRecord, Institution,
                     Membership, OutboxJob, Resolution, Transfer, User, WorkflowEvent, now)
from .policies import can_assign, can_read, load_case
from .schemas import FactsInput, StrictInput


def capability(db, actor, name, case=None, institution_id=None):
    scopes = [("CASE", case.id), ("BUREAU", case.current_bureau_id), ("INSTITUTION", case.institution_id)] if case else [("INSTITUTION", institution_id)]
    return db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id == actor.user.id,
        CapabilityGrant.capability == name,
        or_(*[(CapabilityGrant.scope_type == kind) & (CapabilityGrant.scope_id == key) for kind, key in scopes]))) is not None


def owner_or_supervisor(actor, case):
    return case.current_owner_id == actor.user.id or can_assign(actor, case)


def eligible(db, user_id, bureau, institution_id):
    user = db.get(User, user_id)
    institution = db.get(Institution, institution_id)
    membership = db.scalar(select(Membership).where(Membership.user_id == user_id, Membership.bureau_id == bureau,
        Membership.role.in_(["RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"]),
        or_(Membership.region_id.is_(None), Membership.region_id == institution.region_id)))
    return user is not None and user.active and membership is not None


def change_case(db, case, expected, actor_id, kind, reason, business_at=None, **values):
    if case.version != expected:
        raise HTTPException(409, "Case changed. Reload and compare before submitting again.")
    from .scheduling import context_now
    when = business_at or context_now(db)
    changed = db.execute(update(CaseRecord).where(CaseRecord.id == case.id, CaseRecord.version == expected).values(
        **values, version=expected + 1, last_action=kind.replace("_", " ").title(), last_action_at=when).execution_options(synchronize_session=False))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Case changed. Reload and compare before submitting again.")
    db.add(WorkflowEvent(case_id=case.id, event_type=kind, actor_id=actor_id, reason=reason,
        before_version=expected, after_version=expected+1, occurred_at=when))
    db.add(OutboxJob(case_id=case.id, kind="DOMAIN_CHANGED", dedup_key=f"domain:{case.id}:{expected+1}"))


class ActionInput(StrictInput):
    action: Literal["REVIEW", "REQUEST_INFORMATION", "INFORMATION", "NEXT_ACTION", "DEADLINE", "ESCALATE", "DISPOSE", "REOPEN", "AMEND"]
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=5, max_length=2000)
    text: str = Field(default="", max_length=20000)
    next_action: str = Field(default="", max_length=500)
    due_at: datetime | None = None
    evidence_ids: list[str] = Field(default_factory=list, max_length=10)
    facts: FactsInput | None = None


class TransferInput(StrictInput):
    expected_version: int = Field(ge=1)
    target_owner_id: str
    target_bureau_id: str
    reason: str = Field(min_length=5, max_length=1000)
    expires_at: datetime


class TransferDecision(StrictInput):
    action: Literal["ACCEPT", "REJECT", "CANCEL"]
    expected_version: int = Field(ge=1)
    transfer_version: int = Field(ge=1)
    reason: str = Field(min_length=5, max_length=1000)


def transfer_view(db, transfer):
    case = db.get(CaseRecord, transfer.case_id)
    return {"id": transfer.id, "case_id": case.public_id, "case_version": case.version,
        "source_owner": db.get(User, transfer.source_owner_id).display_name, "source_owner_id": transfer.source_owner_id, "source_bureau": transfer.source_bureau_id,
        "target_owner_id": transfer.target_owner_id, "target_owner": db.get(User, transfer.target_owner_id).display_name,
        "target_bureau": transfer.target_bureau_id, "status": transfer.status, "version": transfer.version,
        "expires_at": utc(transfer.expires_at).isoformat(), "reason": transfer.reason,
        "response_reason": transfer.response_reason}


def receiving(actor, transfer):
    return actor.user.id == transfer.target_owner_id or any(m.role == "BUREAU_SUPERVISOR" and m.bureau_id == transfer.target_bureau_id for m in actor.memberships)


def expire_transfers(sessions, at=None):
    count = 0
    with sessions() as db:
        from .scheduling import context_now
        at=at or context_now(db)
        for t in db.scalars(select(Transfer).where(Transfer.status == "PENDING", Transfer.expires_at <= at)):
            case = db.get(CaseRecord, t.case_id)
            updated = db.execute(update(Transfer).where(Transfer.id == t.id, Transfer.status == "PENDING", Transfer.version == t.version).values(
                status="EXPIRED", version=t.version+1, responded_at=at, response_reason="Illustrative transfer expiry reached").execution_options(synchronize_session=False))
            if updated.rowcount != 1:
                continue
            change_case(db, case, case.version, None, "TRANSFER_EXPIRED", "Source owner retained at transfer expiry",business_at=at)
            count += 1
        db.commit()
    return count


def register_workflows(app, serialize):
    @app.get("/api/workflow-targets")
    def targets(actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        return [{"id": u.id, "name": u.display_name, "bureau": m.bureau_id, "region": m.region_id}
            for u, m in db.execute(select(User, Membership).join(Membership, Membership.user_id == User.id).where(
                User.active.is_(True), Membership.role.in_(["RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"])))]

    @app.get("/api/transfers")
    def transfers(actor: Principal = Depends(principal), db: Session = Depends(get_db)):
        rows = db.scalars(select(Transfer).order_by(Transfer.created_at.desc()))
        return [transfer_view(db, t) for t in rows if receiving(actor, t) or t.source_owner_id == actor.user.id or
            any(m.role == "BUREAU_SUPERVISOR" and m.bureau_id == t.source_bureau_id for m in actor.memberships)]

    @app.post("/api/cases/{public_id}/actions")
    def action(public_id: str, data: ActionInput, actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        case = load_case(db, actor, public_id)
        a = data.action
        supervisor = can_assign(actor, case)
        if a == "REOPEN":
            allowed = any(m.role == "SENIOR_MANAGEMENT" for m in actor.memberships) and capability(db, actor, "REOPEN", case)
        elif a == "DISPOSE":
            allowed = supervisor and capability(db, actor, "DISPOSE", case)
        elif a in {"ESCALATE", "DEADLINE"}:
            allowed = supervisor and capability(db, actor, "DEADLINE" if a == "DEADLINE" else "ESCALATE", case)
        else:
            allowed = owner_or_supervisor(actor, case) and can_read(db, actor, case, "N")
        if not allowed:
            raise HTTPException(403, "This command requires a scoped authorised role and delegation.")
        from .application.case_actions import execute_case_action
        from .domain.case_actions import ActionCommand, RuleViolation
        from .infrastructure.case_actions import SqlCaseActionRepository
        command = ActionCommand(**{**data.model_dump(),
            'evidence_ids': tuple(data.evidence_ids),
            'facts': data.facts.model_dump(mode='json') if data.facts is not None else None})
        try:
            execute_case_action(SqlCaseActionRepository(db, actor, case), command)
        except RuleViolation as error:
            raise HTTPException(422, str(error)) from error
        return serialize(db, actor, load_case(db, actor, public_id), detail=True)

    @app.post("/api/cases/{public_id}/transfers", status_code=201)
    def initiate(public_id: str, data: TransferInput, actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        case = load_case(db, actor, public_id)
        if not owner_or_supervisor(actor, case):
            raise HTTPException(403, "Only source ownership or authorised supervision can request transfer.")
        if case.lifecycle == "DISPOSED" or data.target_bureau_id == case.current_bureau_id or not eligible(db, data.target_owner_id, data.target_bureau_id, case.institution_id):
            raise HTTPException(422, "Choose an eligible officer in another bureau for an active case.")
        from .scheduling import context_now
        instant=context_now(db)
        if data.expires_at.tzinfo is None or data.expires_at <= instant or data.expires_at > instant+timedelta(days=30):
            raise HTTPException(422, "Choose an explicit future expiry within the illustrative 30-day maximum.")
        if db.scalar(select(Transfer.id).where(Transfer.case_id == case.id, Transfer.status == "PENDING")):
            raise HTTPException(409, "A transfer is already pending.")
        change_case(db, case, data.expected_version, actor.user.id, "TRANSFER_REQUESTED", data.reason)
        transfer = Transfer(case_id=case.id, source_owner_id=case.current_owner_id, source_bureau_id=case.current_bureau_id,
            requester_id=actor.user.id, target_owner_id=data.target_owner_id, target_bureau_id=data.target_bureau_id,
            reason=data.reason, expires_at=data.expires_at)
        db.add(transfer)
        db.commit()
        db.expire_all()
        return transfer_view(db, transfer)

    @app.post("/api/transfers/{transfer_id}/decision")
    def decide(transfer_id: str, data: TransferDecision, actor: Principal = Depends(mutation), db: Session = Depends(get_db)):
        t = db.get(Transfer, transfer_id)
        if not t:
            raise HTTPException(404, "Transfer unavailable.")
        case = db.get(CaseRecord, t.case_id)
        source = actor.user.id == t.requester_id or can_assign(actor, case)
        if not (source if data.action == "CANCEL" else receiving(actor, t)):
            raise HTTPException(404, "Transfer unavailable.")
        from .scheduling import context_now
        if t.status != "PENDING" or t.version != data.transfer_version or utc(t.expires_at) <= context_now(db) or case.lifecycle == "DISPOSED":
            raise HTTPException(409, "Transfer changed, expired or is no longer pending. Reload before deciding.")
        if case.current_owner_id != t.source_owner_id or case.current_bureau_id != t.source_bureau_id:
            raise HTTPException(409, "Source assignment changed. Cancel and request a fresh transfer.")
        values = {}
        status = {"ACCEPT":"ACCEPTED", "REJECT":"REJECTED", "CANCEL":"CANCELLED"}[data.action]
        if data.action == "ACCEPT":
            if not eligible(db, t.target_owner_id, t.target_bureau_id, case.institution_id):
                raise HTTPException(422, "Receiving officer is no longer eligible.")
            values.update(current_owner_id=t.target_owner_id, current_bureau_id=t.target_bureau_id)
        change_case(db, case, data.expected_version, actor.user.id, "TRANSFER_"+status, data.reason, **values)
        updated = db.execute(update(Transfer).where(Transfer.id == t.id, Transfer.status == "PENDING", Transfer.version == data.transfer_version).values(
            status=status, version=t.version+1, response_reason=data.reason, responded_at=context_now(db)).execution_options(synchronize_session=False))
        if updated.rowcount != 1:
            db.rollback()
            raise HTTPException(409, "Another decision won. Reload the transfer.")
        if data.action == "ACCEPT":
            when = context_now(db)
            db.execute(update(Assignment).where(Assignment.case_id == case.id, Assignment.effective_to.is_(None)).values(effective_to=when))
            db.add(Assignment(case_id=case.id, owner_id=t.target_owner_id, bureau_id=t.target_bureau_id,
                assigned_by=actor.user.id, reason=data.reason, effective_from=when))
        db.commit()
        db.expire_all()
        return transfer_view(db, t)
