"""Role-aware case response projection shared by HTTP adapters."""
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from .auth import utc
from .models import Institution, User, OriginalSubmission, Complainant, Attachment, WorkflowEvent, Assignment
from .policies import can_read, can_assign

INDIA = ZoneInfo('Asia/Kolkata')


def deadline_date(value):
    if value is None:
        return None
    local = utc(value).astimezone(INDIA)
    # Date-only intake deadlines are stored as the next IST midnight, exclusive.
    # An officer's explicit daytime deadline belongs to that same calendar date.
    date = local.date() - timedelta(days=1) if local.time() == time.min else local.date()
    return date.isoformat()


def serialize_case(db, actor, case, detail=False):
    inst, owner = db.get(Institution, case.institution_id), db.get(User, case.current_owner_id)
    narrative = can_read(db, actor, case, "N")
    deadline = deadline_date(case.due_at)
    result = {"id": case.public_id, "institution_id": inst.id, "institution_name": inst.name, "city": inst.city,
              "owner": {"id": owner.id, "name": owner.display_name, "bureau": case.current_bureau_id},
              "subject": case.subject if narrative else "Restricted narrative", "category": case.category if narrative else None,
              "lifecycle": case.lifecycle, "received_date": utc(case.received_at).astimezone(INDIA).date().isoformat(),
              "expected_disposal_date": deadline, "due_at": utc(case.due_at).isoformat() if case.due_at else None,
              "next_action": case.next_action if narrative else "Contact the accountable officer",
              "version": case.version, "synthetic": case.synthetic, "can_read_narrative": narrative,
              "can_assign": can_assign(actor, case), "identity_status": case.identity_status,
              "last_action": case.last_action, "last_action_at": utc(case.last_action_at).isoformat(),
              "escalation_level": case.escalation_level, "transfer_state": "NONE", "coordination_lead": None}
    from .models import Transfer
    latest_transfer = db.scalar(select(Transfer).where(Transfer.case_id == case.id).order_by(Transfer.created_at.desc()).limit(1))
    result["transfer_state"] = latest_transfer.status if latest_transfer else "NONE"
    from .workflows import capability
    result['can_review_pair']=narrative and can_read(db,actor,case,'I') and capability(db,actor,'REVIEW_PAIR',case)
    if detail:
        submission = db.scalar(select(OriginalSubmission).where(OriginalSubmission.case_id == case.id))
        result.update(description=case.description if narrative else None,
                      facts=case.facts if narrative else None,
                      original_institution_text=case.original_institution_text if narrative else None,
                      original_submission=submission.payload if narrative and submission else None,
                      original_sha256=submission.sha256 if narrative and submission else None)
        identity = db.scalar(select(Complainant).where(Complainant.case_id == case.id))
        result["complainant"] = {"token": identity.synthetic_token, "contact": identity.contact} if identity and can_read(db, actor, case, "I") else None
        result["attachments"] = [{"id": a.id, "filename": a.original_filename, "size": a.size, "type": a.detected_type,
            "sha256": a.sha256, "integrity_checked_at": utc(a.verified_at).isoformat() if a.verified_at else None,
            "download_url": f"/api/attachments/{a.id}"} for a in db.scalars(select(Attachment).where(Attachment.case_id == case.id))] if can_read(db, actor, case, "A") else []
        events = db.scalars(select(WorkflowEvent).where(WorkflowEvent.case_id == case.id).order_by(WorkflowEvent.occurred_at, WorkflowEvent.before_version, WorkflowEvent.after_version, WorkflowEvent.id))
        result["history"] = [{"id": e.id, "type": e.event_type, "at": utc(e.occurred_at).isoformat(),
            "actor": db.get(User, e.actor_id).display_name if e.actor_id else ("Local integrity worker" if e.event_type=='EVIDENCE_INTEGRITY_CHECKED' else "Deterministic policy worker"),
            "reason": e.reason if narrative else "Details restricted", "before_version": e.before_version, "after_version": e.after_version} for e in events]
        result["assignments"] = [{"owner": db.get(User, a.owner_id).display_name, "bureau": a.bureau_id,
            "from": utc(a.effective_from).isoformat(), "to": utc(a.effective_to).isoformat() if a.effective_to else None,
            "reason": a.reason if narrative else "Details restricted"} for a in db.scalars(select(Assignment).where(Assignment.case_id == case.id).order_by(Assignment.effective_from))]
        from .models import CaseAction, IdentityDecision, Resolution, Transfer
        from .workflows import capability
        result["actions"] = [{"kind": a.kind, "payload": a.payload if narrative else None, "version": a.case_version}
            for a in db.scalars(select(CaseAction).where(CaseAction.case_id == case.id).order_by(CaseAction.case_version))]
        result["resolutions"] = [{"id": r.id, "text": r.resolution if narrative else "Resolution narrative restricted",
            "at": utc(r.disposed_at).isoformat(), "version": r.case_version} for r in db.scalars(select(Resolution).where(Resolution.case_id == case.id).order_by(Resolution.disposed_at))]
        result["pending_transfer"] = db.scalar(select(Transfer.id).where(Transfer.case_id == case.id, Transfer.status == "PENDING"))
        result['identity_history']=[{'previous_institution_id':r.previous_institution_id,'institution_id':r.institution_id,
            'original_text':r.original_text if narrative else None,'reason':r.reason if narrative else 'Details restricted',
            'provenance':r.provenance if narrative else 'Details restricted','actor':db.get(User,r.actor_id).display_name,
            'version':r.case_version} for r in db.scalars(select(IdentityDecision).where(IdentityDecision.case_id==case.id).order_by(IdentityDecision.created_at))]
        result["capabilities"] = {name: capability(db, actor, name, case) for name in ["DISPOSE", "REOPEN", "DEADLINE", "ESCALATE"]}
    return result


