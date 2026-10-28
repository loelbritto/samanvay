"""Durable evidence-integrity jobs only. No matching/coordination/notification integration."""
import argparse
from datetime import timedelta
import hashlib
import time
from sqlalchemy import or_, select, update
from .auth import utc
from .config import Settings
from .database import make_database
from .models import Attachment, CaseRecord, OutboxJob, WorkflowEvent, now
from .storage import private_path


def process_one(settings, sessions):
    with sessions() as db:
        eligible = or_(OutboxJob.status == "PENDING", (OutboxJob.status == "RUNNING") & (OutboxJob.lease_until < now()))
        job = db.scalar(select(OutboxJob).where(eligible, OutboxJob.kind == "EVIDENCE_INTEGRITY", OutboxJob.available_at <= now(), OutboxJob.attempts < 5).order_by(OutboxJob.available_at).limit(1))
        if not job:
            return None
        lease = now() + timedelta(minutes=2)
        claimed = db.execute(update(OutboxJob).where(OutboxJob.id == job.id, eligible, OutboxJob.attempts < 5).values(
            status="RUNNING", lease_until=lease, attempts=OutboxJob.attempts + 1).execution_options(synchronize_session=False))
        if claimed.rowcount != 1:
            db.rollback()
            return None
        db.commit()
        db.expire_all()
        job = db.get(OutboxJob, job.id)
        attachments = list(db.scalars(select(Attachment).where(Attachment.case_id == job.case_id)))
        good = all(private_path(settings, a.storage_key).is_file() and
                   hashlib.sha256(private_path(settings, a.storage_key).read_bytes()).hexdigest() == a.sha256 for a in attachments)
        if not good:
            job.status = "FAILED" if job.attempts >= 5 else "PENDING"
            job.available_at = now() + timedelta(seconds=30)
            job.error_code = "EVIDENCE_UNAVAILABLE_OR_CHANGED"
        else:
            for attachment in attachments:
                attachment.verified_at = now()
            case = db.get(CaseRecord, job.case_id)
            db.add(WorkflowEvent(case_id=case.id, event_type="EVIDENCE_INTEGRITY_CHECKED", actor_id=None,
                reason="Stored evidence checksums verified; this is not malware scanning or evidence adjudication." if attachments else "No attachments to check; no evidence verdict is asserted.",
                before_version=case.version, after_version=case.version))
            job.status, job.completed_at, job.error_code = "DONE", now(), None
        job.lease_until = None
        db.commit()
        return {"job": job.id, "status": job.status, "attachments": len(attachments)}


def main():
    from fastapi import HTTPException
    from sqlalchemy.exc import SQLAlchemyError
    from .coordination import process_domain_one
    from .scheduling import run_scheduler,deliver_one
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    settings = Settings.from_env()
    engine, sessions = make_database(settings)
    try:
        while True:
            try:
                integrity=process_one(settings,sessions)
                domain=process_domain_one(sessions)
                scheduled=run_scheduler(sessions)
                delivered=0
                for _ in range(20):
                    if deliver_one(sessions) is None:break
                    delivered+=1
                if integrity or domain or scheduled['created'] or scheduled['escalated'] or scheduled['expired'] or delivered:
                    print({'integrity':integrity,'domain':domain,'scheduler':scheduled,'in_app_delivered':delivered},flush=True)
            except (SQLAlchemyError,HTTPException,OSError):
                print({'status':'retry_pending','detail':'Temporary database, version or storage failure; persisted jobs retained. No external message sent.'},flush=True)
                if args.once:return 1
            if args.once:return 0
            time.sleep(2)
    finally:engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
