from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from .models import AccessGrant, CapabilityGrant, CaseRecord, Membership, now


def grants(actor, data_class):
    return select(AccessGrant.case_id).where(AccessGrant.user_id == actor.user.id,
        AccessGrant.data_class == data_class,
        or_(AccessGrant.expires_at.is_(None), AccessGrant.expires_at > now()))


def visible_cases(actor):
    supervisor_bureaus = [m.bureau_id for m in actor.memberships if m.role == "BUREAU_SUPERVISOR"]
    return or_(CaseRecord.current_owner_id == actor.user.id,
               CaseRecord.id.in_(grants(actor, "M")),
               CaseRecord.institution_id.in_(select(CapabilityGrant.scope_id).where(CapabilityGrant.user_id == actor.user.id,
                   CapabilityGrant.capability == "CASE_METADATA", CapabilityGrant.scope_type == "INSTITUTION")),
               CaseRecord.current_bureau_id.in_(supervisor_bureaus))


def can_read(db, actor, case, data_class):
    if case.current_owner_id == actor.user.id:
        return True
    if data_class == "M" and can_assign(actor, case):
        return True
    if data_class == "M" and db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id == actor.user.id,
        CapabilityGrant.capability == "CASE_METADATA", CapabilityGrant.scope_type == "INSTITUTION", CapabilityGrant.scope_id == case.institution_id)):
        return True
    return db.scalar(select(AccessGrant.id).where(AccessGrant.case_id == case.id,
        AccessGrant.user_id == actor.user.id, AccessGrant.data_class == data_class,
        or_(AccessGrant.expires_at.is_(None), AccessGrant.expires_at > now()))) is not None


def can_assign(actor, case):
    return any(m.role == "BUREAU_SUPERVISOR" and m.bureau_id == case.current_bureau_id for m in actor.memberships)


def intake_membership(actor):
    allowed = [m for m in actor.memberships if m.role in {"RB_OFFICER", "PGRC_OFFICER", "REGIONAL_OFFICER"} and m.bureau_id]
    if len(allowed) != 1:
        raise HTTPException(403, "This account has no unambiguous intake assignment.")
    return allowed[0]


def load_case(db, actor, public_id):
    case = db.scalar(select(CaseRecord).where(CaseRecord.public_id == public_id, visible_cases(actor)))
    if case is None:
        raise HTTPException(404, "Case not found or not available in your scope.")
    return case
