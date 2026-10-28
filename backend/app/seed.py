"""Idempotent seed: add fictional accounts/institutions/cases, never delete or overwrite records."""
from datetime import datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
from sqlalchemy import select
from .auth import hasher
from .config import Settings
from .database import make_database
from .models import AccessGrant, Assignment, Bureau, CapabilityGrant, CaseRecord, Complainant, Institution, InstitutionAlias, Membership, OriginalSubmission, Region, User, WorkflowEvent, new_id, now

DEMO_PASSWORD = "DemoOnly-Stage2!"
ACCOUNTS = [
    ("rb@demo.test", "Demo Kabir Sen", "RB_OFFICER", "RB"),
    ("pgrc@demo.test", "Demo Ananya Rao", "PGRC_OFFICER", "PGRC"),
    ("rb.backup@demo.test", "Demo Meera Das", "RB_OFFICER", "RB"),
    ("supervisor@demo.test", "Demo RB Supervisor", "BUREAU_SUPERVISOR", "RB"),
    ("pgrc.supervisor@demo.test", "Demo PGRC Supervisor", "BUREAU_SUPERVISOR", "PGRC"),
    ("regional@demo.test", "Demo Regional Officer", "REGIONAL_OFFICER", "RB"),
    ("management@demo.test", "Demo Competent Authority", "SENIOR_MANAGEMENT", None),
    ("admin@demo.test", "Demo System Administrator", "SYSTEM_ADMIN", None),
    ("coordinator@demo.test", "Demo Scoped Coordinator", "COORDINATOR", None),
]


def seed(settings, sessions):
    if settings.environment not in {"demo", "test"}:
        raise RuntimeError("Seeding is available only in synthetic demo/test environments.")
    with sessions() as db:
        from .models import DemoContext
        existing_context=db.scalar(select(DemoContext))
        if existing_context and existing_context.id!=settings.context_id:
            raise RuntimeError('Configured context does not match this database; existing records were preserved')
        if db.scalar(select(CaseRecord.id).where(CaseRecord.synthetic.is_(False)).limit(1)):
            raise RuntimeError('Non-synthetic records found; refusing to seed or label this database as a demo')
        if not db.get(Region, "DEMO-WEST"):
            db.add(Region(id="DEMO-WEST", name="Fictional Western Region"))
        for id_, name in [("RB", "Regulation Bureau"), ("PGRC", "Public Grievance Redressal Cell")]:
            if not db.get(Bureau, id_):
                db.add(Bureau(id=id_, name=name))
        db.flush()
        users = {}
        for username, name, role, bureau in ACCOUNTS:
            user = db.scalar(select(User).where(User.username == username))
            if not user:
                user = User(id=new_id(), username=username, display_name=name, password_hash=hasher.hash(DEMO_PASSWORD))
                db.add(user)
                db.flush()
                db.add(Membership(user_id=user.id, role=role, bureau_id=bureau, region_id="DEMO-WEST" if role == "REGIONAL_OFFICER" else None))
            users[username] = user
        db.flush()
        for id_, city in [("DEMO-INST-017", "Pune"), ("DEMO-INST-044", "Nagpur")]:
            if not db.get(Institution, id_):
                db.add(Institution(id=id_, name="Demo Suryavan Institute", city=city, region_id="DEMO-WEST"))
                db.flush()
                db.add(InstitutionAlias(institution_id=id_, alias="DSI " + city,
                    provenance="Authored synthetic fixture; not an official institution identity verification.", confirmed_by=users["supervisor@demo.test"].id))
        for account, bureau in [("supervisor@demo.test", "RB"), ("pgrc.supervisor@demo.test", "PGRC")]:
            for permission in ["DISPOSE", "DEADLINE", "ESCALATE"]:
                if not db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id == users[account].id,
                    CapabilityGrant.capability == permission, CapabilityGrant.scope_id == bureau)):
                    db.add(CapabilityGrant(user_id=users[account].id, capability=permission, scope_type="BUREAU", scope_id=bureau,
                        reason="Explicit illustrative synthetic supervisor delegation; not an official policy"))
        for bureau in ["RB", "PGRC"]:
            if not db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id == users["management@demo.test"].id,
                CapabilityGrant.capability == "REOPEN", CapabilityGrant.scope_id == bureau)):
                db.add(CapabilityGrant(user_id=users["management@demo.test"].id, capability="REOPEN", scope_type="BUREAU", scope_id=bureau,
                    reason="Synthetic reopening delegation; separate metadata grant still required"))
        db.flush()
        records = json.loads((Path(__file__).parents[1] / "seeds" / "synthetic-cases.json").read_text(encoding="utf-8"))
        for record in records:
            if db.scalar(select(CaseRecord.id).where(CaseRecord.public_id == record["id"])):
                continue
            owner = users[record["account"]]
            received = datetime.fromisoformat(record["received"] + "T00:00:00+05:30")
            case = CaseRecord(id=new_id(), public_id=record["id"], institution_id=record["institution"],
                original_institution_text=record["original_institution_text"], received_at=received.astimezone(timezone.utc),
                subject=record["subject"], description=record["description"], category=record["category"],
                lifecycle=record["lifecycle"], current_owner_id=owner.id, current_bureau_id=record["bureau"],
                next_action=record["next_action"], due_at=(datetime.fromisoformat(record["due"] + "T00:00:00+05:30") + timedelta(days=1)).astimezone(timezone.utc))
            db.add(case)
            db.flush()
            encoded = json.dumps(record, sort_keys=True, ensure_ascii=False).encode()
            db.add_all([OriginalSubmission(case_id=case.id, payload=record, sha256=hashlib.sha256(encoded).hexdigest()),
                Complainant(case_id=case.id, synthetic_token=record["token"]),
                Assignment(case_id=case.id, owner_id=owner.id, bureau_id=record["bureau"], assigned_by=owner.id, reason="Authored synthetic seed assignment"),
                WorkflowEvent(case_id=case.id, event_type="SYNTHETIC_SEED", actor_id=owner.id,
                    reason="Fictional demonstration record imported by seed command; original fixture retained.", before_version=0, after_version=1)])
        from .models import AdministrativePolicy,DemoContext
        if not db.get(AdministrativePolicy,'DEMO_DEFAULT'):db.add(AdministrativePolicy(id='DEMO_DEFAULT'))
        if not db.get(DemoContext,settings.context_id):db.add(DemoContext(id=settings.context_id))
        coordinator=users['coordinator@demo.test']
        for institution_id in ['DEMO-INST-017','DEMO-INST-044']:
            for permission in ['CASE_METADATA','COORDINATE','REVIEW_PAIR','IDENTITY']:
                if not db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id==coordinator.id,CapabilityGrant.capability==permission,CapabilityGrant.scope_type=='INSTITUTION',CapabilityGrant.scope_id==institution_id)):
                    db.add(CapabilityGrant(user_id=coordinator.id,capability=permission,scope_type='INSTITUTION',scope_id=institution_id,reason='Explicit synthetic demo institution delegation; separate narrative/identity grants required'))
        for case in db.scalars(select(CaseRecord).where(CaseRecord.public_id.in_(['PGRC-014','PGRC-019','RB-023']))):
            for data_class in ['N','I']:
                if not db.scalar(select(AccessGrant.id).where(AccessGrant.user_id==coordinator.id,AccessGrant.case_id==case.id,AccessGrant.data_class==data_class)):
                    db.add(AccessGrant(user_id=coordinator.id,case_id=case.id,data_class=data_class,reason='Explicit synthetic pair-review evidence delegation',granted_by=users['supervisor@demo.test'].id))
        db.flush()
        from .coordination import refresh_coordination
        refresh_coordination(db)
        db.commit()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "SYNTHETIC_DEMO.txt").write_text("Local synthetic Samanvay data. No official integration. Seeding never resets/deletes cases.\n", encoding="utf-8")
    from .config import ROOT
    if settings.demo_controls and settings.data_dir.resolve().is_relative_to((ROOT/'.demo-contexts').resolve()):
        marker=settings.data_dir/'SYNTHETIC_CONTEXT.json'
        value={'context_id':settings.context_id,'synthetic':True}
        if marker.exists() and json.loads(marker.read_text(encoding='utf-8'))!=value:raise RuntimeError('Existing context marker mismatch; refusing to overwrite')
        marker.write_text(json.dumps(value),encoding='utf-8')


def main():
    settings = Settings.from_env()
    _, sessions = make_database(settings)
    seed(settings, sessions)
    print("Synthetic seed complete; existing records preserved. Demo password: " + DEMO_PASSWORD)
    print("Accounts: " + ", ".join(a[0] for a in ACCOUNTS))


if __name__ == "__main__":
    main()
