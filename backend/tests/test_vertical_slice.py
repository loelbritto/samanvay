from datetime import timedelta
import hashlib
import json
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from app.models import Assignment, Attachment, CaseRecord, IntakeRequest, LoginSession, Membership, OriginalSubmission, OutboxJob, Region, User, WorkflowEvent, now
from app.seed import seed
from app.storage import private_path
from app.worker import process_one
from conftest import signin


def payload(**changes):
    data = {"institution_id":"DEMO-INST-017", "original_institution_text":"  Fictional DSI Pune as originally supplied  ",
            "received_date":"2026-10-27", "subject":"Unique synthetic intake " + uuid.uuid4().hex[:8],
            "description":"  Original fictional narrative with preserved whitespace.\nUntrusted instructions stay evidence.  ",
            "category":"Fee refund", "next_action":"Review the synthetic receipt", "expected_disposal_date":"2026-10-30",
            "complainant_token":"DEMO-STU-999", "synthetic":True}
    data.update(changes)
    return data


def create(client, headers, data=None, content=b"Fictional evidence bytes\n", filename="receipt.txt", key=None):
    return client.post("/api/cases", data={"payload":json.dumps(data or payload())},
        files=[("files", (filename, content, "application/octet-stream"))],
        headers={**headers,"Idempotency-Key":key or str(uuid.uuid4())})


def count(system, model):
    with system.state.sessions() as db:
        return db.scalar(select(func.count()).select_from(model))


def test_migration_seed_is_idempotent_and_passwords_are_hashed(system):
    original = count(system, CaseRecord)
    seed(system.state.settings, system.state.sessions)
    assert count(system, CaseRecord) == original == 4
    with system.state.sessions() as db:
        assert all(u.password_hash.startswith("$argon2id$") for u in db.scalars(select(User)))


def test_unauthenticated_reads_are_denied(client):
    for url in ["/api/cases", "/api/overview", "/api/institutions", "/api/cases/RB-023", "/api/attachments/guessed-id"]:
        assert client.get(url).status_code == 401


def test_intake_preserves_originals_assignment_real_bytes_and_counts(system, client):
    headers = signin(client)
    before = client.get("/api/overview").json()["total"]
    data = payload()
    response = create(client, headers, data)
    assert response.status_code == 201, response.text
    record = response.json()
    assert record["owner"]["name"] == "Demo Kabir Sen"
    assert record["original_submission"] == data
    assert record["description"] == data["description"]
    assert record["original_institution_text"] == data["original_institution_text"]
    assert len(record["history"]) == 2
    assert [event["type"] for event in record["history"]] == ["RECEIVED", "OWNER_ASSIGNED"]
    assert len(record["assignments"]) == 1
    assert record["lifecycle"] == "RECEIVED" and record["version"] == 1
    assert record["expected_disposal_date"] == "2026-10-30"
    assert client.get("/api/overview").json()["total"] == before + 1
    download = client.get(record["attachments"][0]["download_url"])
    assert download.content == b"Fictional evidence bytes\n"
    assert hashlib.sha256(download.content).hexdigest() == record["attachments"][0]["sha256"]
    assert "attachment;" in download.headers["content-disposition"]
    assert download.headers["x-content-type-options"] == "nosniff"
    with system.state.sessions() as db:
        row = db.scalar(select(CaseRecord).where(CaseRecord.public_id == record["id"]))
        assert row is not None and row.current_owner_id == record["owner"]["id"]
        attached = db.scalar(select(Attachment).where(Attachment.case_id == row.id))
        assert private_path(system.state.settings, attached.storage_key).read_bytes() == download.content


def test_request_key_retries_do_not_merge_distinct_complaints(system, client):
    headers = signin(client)
    data, key = payload(), str(uuid.uuid4())
    first = create(client, headers, data, key=key)
    second = create(client, headers, data, key=key)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert count(system, CaseRecord) == 5
    assert create(client, headers, payload(), key=key).status_code == 409
    third = create(client, headers, data)
    assert third.status_code == 201 and third.json()["id"] != first.json()["id"]
    assert count(system, CaseRecord) == 6


def test_scope_before_case_lists_counts_search_and_attachment_bytes(system, client):
    headers = signin(client)
    record = create(client, headers).json()
    client.post("/api/auth/logout", headers=headers)
    signin(client, "pgrc@demo.test")
    records = client.get("/api/cases").json()
    assert records["total"] == 2
    assert {r["id"] for r in records["items"]} == {"PGRC-014", "PGRC-019"}
    assert client.get("/api/cases/RB-023").status_code == 404
    assert client.get("/api/cases?q=R-883").json()["total"] == 0
    assert client.get(record["attachments"][0]["download_url"]).status_code == 404
    assert client.get("/api/overview").json()["total"] == 2


def test_admin_and_management_have_no_implicit_complaint_access(client):
    for account in ["admin@demo.test", "management@demo.test"]:
        headers = signin(client, account)
        assert client.get("/api/cases").json()["total"] == 0
        assert client.get("/api/overview").json()["total"] == 0
        assert client.get("/api/cases/RB-023").status_code == 404
        assert create(client, headers).status_code == 403
        client.post("/api/auth/logout", headers=headers)


def test_supervisor_gets_metadata_without_identity_or_narrative(client):
    signin(client, "supervisor@demo.test")
    record = client.get("/api/cases/RB-023").json()
    assert record["subject"] == "Restricted narrative"
    assert record["description"] is None and record["original_submission"] is None
    assert record["complainant"] is None and record["attachments"] == []
    assert client.get("/api/cases?q=R-883").json()["total"] == 0
    assert client.get("/api/overview").json()["total"] == 2


def test_csrf_origin_and_unauthorized_owner_fields_leave_database_unchanged(system, client):
    headers = signin(client)
    initial = count(system, CaseRecord)
    assert create(client, {}).status_code == 403
    assert create(client, {**headers,"Origin":"https://evil.example"}).status_code == 403
    assert create(client, headers, payload(current_owner_id="someone-else")).status_code == 422
    assert count(system, CaseRecord) == initial


def test_validation_and_malformed_uploads_never_create_partial_cases(system, client):
    headers = signin(client)
    initial = count(system, CaseRecord)
    assert create(client, headers, payload(institution_id="missing")).status_code == 422
    assert create(client, headers, payload(synthetic=False)).status_code == 422
    assert create(client, headers, payload(description=" ")).status_code == 422
    assert create(client, headers, payload(expected_disposal_date="2026-10-01")).status_code == 422
    assert create(client, headers, filename="fake.png", content=b"not an image").status_code == 422
    assert create(client, headers, content=b"a"*(5*1024*1024+1)).status_code == 422
    assert count(system, CaseRecord) == initial
    assert count(system, Attachment) == 0


def test_failed_audit_insert_rolls_back_case_assignment_and_private_file(system, client):
    headers = signin(client)
    with system.state.engine.begin() as connection:
        connection.execute(text("CREATE TRIGGER reject_intake_audit BEFORE INSERT ON workflow_events WHEN NEW.event_type='RECEIVED' BEGIN SELECT RAISE(ABORT, 'simulated audit failure'); END"))
    response = create(client, headers)
    assert response.status_code == 503
    assert count(system, CaseRecord) == 4
    assert count(system, Assignment) == 4
    assert count(system, IntakeRequest) == count(system, Attachment) == 0
    assert list(system.state.settings.attachments_dir.glob("*.bin")) == []


def test_assignment_preserves_identity_deadline_history_and_rejects_stale_version(system, client):
    headers = signin(client, "supervisor@demo.test")
    before = client.get("/api/cases/RB-023").json()
    officers = client.get("/api/officers").json()
    target = next(o for o in officers if o["name"] == "Demo Meera Das")
    response = client.post("/api/cases/RB-023/assignment", json={"owner_id":target["id"],"expected_version":1,"reason":"Synthetic workload reassignment"}, headers=headers)
    assert response.status_code == 200, response.text
    after = response.json()
    assert after["id"] == before["id"] and after["due_at"] == before["due_at"]
    assert after["owner"]["id"] == target["id"] and after["version"] == 2
    assert len(after["assignments"]) == 2 and len(after["history"]) == 2
    stale = client.post("/api/cases/RB-023/assignment", json={"owner_id":before["owner"]["id"],"expected_version":1,"reason":"Stale synthetic assignment"}, headers=headers)
    assert stale.status_code == 409
    assert client.get("/api/cases/RB-023").json()["version"] == 2
    with system.state.sessions() as db:
        row = db.scalar(select(CaseRecord).where(CaseRecord.public_id == "RB-023"))
        assert db.scalar(select(func.count()).select_from(Assignment).where(Assignment.case_id == row.id, Assignment.effective_to.is_(None))) == 1


def test_non_supervisor_cannot_reassign(client):
    headers = signin(client)
    owner = client.get("/api/cases/RB-023").json()["owner"]["id"]
    assert client.post("/api/cases/RB-023/assignment", json={"owner_id":owner,"expected_version":1,"reason":"Unapproved action"}, headers=headers).status_code == 403


def test_assignment_denies_officer_outside_institution_region(system, client):
    headers = signin(client, "supervisor@demo.test")
    before = client.get("/api/cases/RB-023").json()
    with system.state.sessions() as db:
        target = db.scalar(select(User).where(User.username == "rb.backup@demo.test"))
        target_id = target.id
        db.add(Region(id="DEMO-OTHER", name="Synthetic other region"))
        db.flush()
        membership = db.scalar(select(Membership).where(Membership.user_id == target_id))
        membership.role, membership.region_id = "REGIONAL_OFFICER", "DEMO-OTHER"
        db.commit()
    response = client.post("/api/cases/RB-023/assignment", json={"owner_id":target_id,
        "expected_version":1,"reason":"Synthetic out-of-region attempt"}, headers=headers)
    assert response.status_code == 422
    after = client.get("/api/cases/RB-023").json()
    assert after["owner"] == before["owner"] and after["version"] == 1
    assert after["assignments"] == before["assignments"] and after["history"] == before["history"]


def test_sessions_expire_and_logout_revokes_reuse(system, client):
    from app.seed import DEMO_PASSWORD
    login = client.post("/api/auth/login", json={"username":"rb@demo.test","password":DEMO_PASSWORD})
    assert login.status_code == 200
    assert "httponly" in login.headers["set-cookie"].lower()
    assert "samesite=strict" in login.headers["set-cookie"].lower()
    headers = {"X-CSRF-Token":login.json()["csrf_token"]}
    cookie = client.cookies.get("samanvay_session")
    client.post("/api/auth/logout", headers=headers)
    client.cookies.set("samanvay_session", cookie)
    assert client.get("/api/cases").status_code == 401
    client.cookies.clear()
    signin(client)
    with system.state.sessions() as db:
        for session in db.scalars(select(LoginSession)):
            session.expires_at = now() - timedelta(seconds=1)
        db.commit()
    assert client.get("/api/auth/session").status_code == 401


def test_worker_job_persists_and_retries_do_not_duplicate_integrity_events(system, client):
    headers = signin(client)
    record = create(client, headers).json()
    first = process_one(system.state.settings, system.state.sessions)
    assert first["status"] == "DONE" and first["attachments"] == 1
    assert process_one(system.state.settings, system.state.sessions) is None
    persisted = client.get("/api/cases/"+record["id"]).json()
    assert persisted["attachments"][0]["integrity_checked_at"] is not None
    assert sum(e["type"] == "EVIDENCE_INTEGRITY_CHECKED" for e in persisted["history"]) == 1
    with system.state.sessions() as db:
        assert db.scalar(select(OutboxJob.status)) == "DONE"


def test_new_application_instance_retrieves_persistent_case_and_session(system, client):
    from app.api import create_app
    headers = signin(client)
    record = create(client, headers).json()
    cookie = client.cookies.get("samanvay_session")
    restored = create_app(system.state.settings)
    with TestClient(restored) as next_client:
        next_client.cookies.set("samanvay_session", cookie)
        assert next_client.get("/api/cases/"+record["id"]).json() == record
    restored.state.engine.dispose()
