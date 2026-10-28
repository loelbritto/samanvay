"""Verify the actual UI-created complaint against API, SQLite row and private bytes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import httpx

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence" / "stage2"
PASSWORD = "DemoOnly-Stage2!"


def signin(client, username):
    response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert response.status_code == 200, response.status_code
    return response.json()["csrf_token"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["before", "after"])
    args = parser.parse_args()
    proof = json.loads((EVIDENCE / "ui-intake.json").read_text(encoding="utf-8"))
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=10) as client:
        for attempt in range(30):
            try:
                if client.get("/api/health").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("Backend did not become available")
        unauth = client.get("/api/cases/" + proof["case_id"]).status_code
        assert unauth == 401
        csrf = signin(client, "rb@demo.test")
        response = client.get("/api/cases/" + proof["case_id"])
        assert response.status_code == 200
        record = response.json()
        assert record["subject"] == proof["subject"]
        assert record["owner"]["name"] == "Demo Kabir Sen"
        assert record["original_institution_text"] == "DSI Pune — original synthetic submission"
        assert len(record["history"]) >= 2 and len(record["assignments"]) == 1
        download = client.get(proof["attachment_link"])
        expected_bytes = (EVIDENCE / "synthetic-upload.txt").read_bytes()
        assert download.status_code == 200 and download.content == expected_bytes
        digest = hashlib.sha256(download.content).hexdigest()
        assert digest == record["attachments"][0]["sha256"]
        overview = client.get("/api/overview").json()
        assert overview["total"] == proof["before_count"] + 1
        client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
        csrf = signin(client, "pgrc@demo.test")
        cross_case = client.get("/api/cases/" + proof["case_id"]).status_code
        cross_attachment = client.get(proof["attachment_link"]).status_code
        assert cross_case == cross_attachment == 404
        client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
        signin(client, "admin@demo.test")
        admin_total = client.get("/api/overview").json()["total"]
        assert admin_total == 0
    db_path = ROOT / ".local-data" / "samanvay.sqlite3"
    with sqlite3.connect("file:" + db_path.as_posix() + "?mode=ro", uri=True) as db:
        row = db.execute("SELECT id,public_id,current_owner_id,version FROM cases WHERE public_id=?", (proof["case_id"],)).fetchone()
        assert row is not None
        events = db.execute("SELECT count(*) FROM workflow_events WHERE case_id=?", (row[0],)).fetchone()[0]
        original_count = db.execute("SELECT count(*) FROM original_submissions WHERE case_id=?", (row[0],)).fetchone()[0]
        assignment_count = db.execute("SELECT count(*) FROM assignment_history WHERE case_id=?", (row[0],)).fetchone()[0]
        key, stored_sha = db.execute("SELECT storage_key,sha256 FROM attachments WHERE case_id=?", (row[0],)).fetchone()
        private_bytes = (ROOT / ".local-data" / "private-evidence" / key).read_bytes()
        assert hashlib.sha256(private_bytes).hexdigest() == digest == stored_sha
        assert original_count == assignment_count == 1 and events == len(record["history"])
    report = {"phase": args.phase, "observed_at_utc": datetime.now(timezone.utc).isoformat(), "case_id": proof["case_id"],
              "subject": record["subject"], "owner": record["owner"], "version": record["version"],
              "history_ids": [e["id"] for e in record["history"]], "history_count": len(record["history"]),
              "sha256": digest, "attachment_bytes": len(expected_bytes), "authorized_count": overview["total"],
              "database_row_found": True, "original_submissions": original_count, "assignment_rows": assignment_count,
              "unauthenticated_status": unauth, "cross_scope_case_status": cross_case, "cross_scope_attachment_status": cross_attachment,
              "administrator_case_count": admin_total, "passed": True}
    if args.phase == "after":
        before = json.loads((EVIDENCE / "before-restart-api.json").read_text(encoding="utf-8"))
        for key in ["case_id", "owner", "version", "sha256", "authorized_count"]:
            assert report[key] == before[key], key
        assert set(report["history_ids"]) == set(before["history_ids"])
        assert [event["type"] for event in record["history"][:2]] == ["RECEIVED", "OWNER_ASSIGNED"]
        report["creation_history_order_verified"] = True
        report["matches_before_restart"] = True
    (EVIDENCE / (args.phase + "-restart-api.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
