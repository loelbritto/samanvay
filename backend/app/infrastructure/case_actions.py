from dataclasses import asdict
from sqlalchemy import select
from ..auth import utc
from ..domain.case_actions import ActionCommand, ActionDecision, CaseState
from ..models import Attachment, CaseAction, Resolution, Transfer
from ..policies import can_read


class SqlCaseActionRepository:
    """The HTTP boundary authorises the action before constructing this adapter."""
    def __init__(self, db, actor, case):
        self.db, self.actor, self.case = db, actor, case

    def snapshot(self, command: ActionCommand) -> CaseState:
        db, case = self.db, self.case
        def latest(kind):
            return db.scalar(select(CaseAction.case_version).where(
                CaseAction.case_id == case.id, CaseAction.kind == kind)
                .order_by(CaseAction.case_version.desc()).limit(1))
        requested, answered = latest('REQUEST_INFORMATION'), latest('INFORMATION')
        evidence = [db.get(Attachment, key) for key in command.evidence_ids]
        return CaseState(case.lifecycle, utc(case.received_at), case.due_version, case.escalation_level,
            information_received=requested is not None and answered is not None and answered >= requested,
            pending_transfer=db.scalar(select(Transfer.id).where(Transfer.case_id == case.id, Transfer.status == 'PENDING')) is not None,
            evidence_authorised=all(item is not None and item.case_id == case.id and can_read(db, self.actor, case, 'A') for item in evidence))

    def commit(self, command: ActionCommand, decision: ActionDecision) -> None:
        from ..workflows import change_case
        from ..scheduling import context_now
        db, actor, case = self.db, self.actor, self.case
        when = context_now(db)
        try:
            change_case(db, case, command.expected_version, actor.user.id, command.action,
                        command.reason, business_at=when, **decision.changes)
            if decision.record_resolution:
                db.add(Resolution(case_id=case.id, resolution=command.text,
                    evidence_ids=list(command.evidence_ids), disposed_at=when,
                    actor_id=actor.user.id, case_version=command.expected_version + 1))
            payload = asdict(command)
            payload['evidence_ids'] = list(command.evidence_ids)
            payload['due_at'] = command.due_at.isoformat() if command.due_at else None
            db.add(CaseAction(case_id=case.id, kind=command.action, payload=payload,
                actor_id=actor.user.id, case_version=command.expected_version + 1, created_at=when))
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.expire_all()
