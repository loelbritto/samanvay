"""Validate saved scoped evidence, inspect the demo DB read-only, and hash final sources/captures.

This does not rerun browser interactions or substitute for the linked raw results.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/stage2"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    suite = ET.parse(ROOT / "docs/evidence/stage2-tests.xml").getroot().find("testsuite")
    assert int(suite.get("tests")) == 16
    assert all(int(suite.get(key)) == 0 for key in ["errors", "failures", "skipped"])
    zoom = read("docs/evidence/stage1-zoom/results.json")
    assert zoom["actual_browser_zoom_percent"] == 200 and "200%" in zoom["native_label"]
    assert zoom["at200"]["dpr"] == zoom["baseline"]["dpr"] * 2
    assert zoom["restored_to_100_percent"]
    assert len(zoom["screenChecks"]) == 14 and all(row["passed"] for row in zoom["screenChecks"])
    assert zoom["keyboard"][-1]["title"] == "Case timeline"
    assert all(row["visible"] for row in zoom["keyboard"][:-1])
    assert zoom["tableKeys"][0]["scrollLeft"] > 0 and zoom["tableKeys"][-1]["scrollLeft"] == 0
    layouts = read("docs/evidence/stage2/layout-results.json")
    assert len(layouts) == 20 and all(row["passed"] for row in layouts)
    before = read("docs/evidence/stage2/before-restart-api.json")
    after = read("docs/evidence/stage2/after-restart-api.json")
    intake = read("docs/evidence/stage2/ui-intake.json")
    ui = read("docs/evidence/stage2/ui-after-restart.json")
    final_ui = read("docs/evidence/stage2/final-ui.json")
    assert before["passed"] and after["passed"] and after["matches_before_restart"]
    assert ui["passed"] and ui["same_authenticated_browser_session"] and intake["created_through_ui"]
    assert final_ui["history"].index("Received") < final_ui["history"].index("Owner assigned")
    assert "Evidence integrity checked" in final_ui["history"]
    with sqlite3.connect("file:" + (ROOT / ".local-data/samanvay.sqlite3").as_posix() + "?mode=ro", uri=True) as db:
        rows = db.execute("""SELECT c.public_id, c.version, u.display_name,
            (SELECT count(*) FROM original_submissions o WHERE o.case_id=c.id),
            (SELECT count(*) FROM assignment_history a WHERE a.case_id=c.id AND a.effective_to IS NULL),
            (SELECT count(*) FROM assignment_history a WHERE a.case_id=c.id),
            (SELECT count(*) FROM workflow_events e WHERE e.case_id=c.id)
            FROM cases c JOIN users u ON u.id=c.current_owner_id ORDER BY c.public_id""").fetchall()
        assert len(rows) == 5 and all(row[3] == row[4] == 1 for row in rows)
        reassigned = next(row for row in rows if row[0] == "RB-023")
        assert reassigned[1] == 3 and reassigned[2] == "Demo Kabir Sen" and reassigned[5:] == (3, 3)
        reasons = db.execute("""SELECT e.reason FROM workflow_events e JOIN cases c ON c.id=e.case_id
            WHERE c.public_id='RB-023' AND e.event_type='OWNER_REASSIGNED' ORDER BY e.after_version""").fetchall()
        assert len(reasons) == 2
        jobs = db.execute("SELECT status,count(*) FROM outbox_jobs GROUP BY status").fetchall()
    db_audit = {"read_only": True, "passed": True, "preserved_case_count": len(rows),
        "cases": [dict(zip(["id", "version", "owner", "original_rows", "current_assignments", "assignment_rows", "event_rows"], row)) for row in rows],
        "rb023_assignment_reasons": [row[0] for row in reasons], "job_states": dict(jobs)}
    write(EVIDENCE / "database-audit.json", db_audit)
    report = {"observed_at_utc": datetime.now(timezone.utc).isoformat(), "stage1_ready": True, "stage2_ready": True,
        "scope": "Local synthetic G1/G2 gates only; saved browser evidence plus executed API/DB/file checks and pytest. No later-stage/security certification.",
        "tests": 16, "test_failures": 0, "test_warnings": 1, "stage1_zoom_screens": 14, "stage2_layout_observations": 20,
        "ui_case": after["case_id"], "restart_matches": True, "sha256": after["sha256"],
        "evidence": ["../stage2-tests.xml", "../stage1-zoom/results.json", "ui-intake.json", "ui-after-restart.json", "final-ui.json",
                     "before-restart-api.json", "after-restart-api.json", "layout-results.json", "database-audit.json", "../stage2-commands.md"]}
    write(EVIDENCE / "results.json", report)
    sources = [ROOT / name for name in ["README.md", "PLAN.md", "DECISIONS.md", "PROJECT_STATE.md", "REQUIREMENTS.md", ".env.example", ".gitignore",
        "frontend/package.json", "frontend/package-lock.json", "frontend/vite.config.ts", "frontend/tsconfig.json", "backend/alembic.ini", "backend/requirements.in", "backend/requirements.lock", "backend/pytest.ini"]]
    for folder in ["frontend/src", "backend/app", "backend/migrations", "backend/tests", "backend/seeds", "scripts"]:
        sources += [p for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".tsx", ".ts", ".css", ".json", ".mako"}]
    sources += list((ROOT / "docs").glob("*.md")) + list((ROOT / "docs").glob("*.json"))
    captures = list(EVIDENCE.glob("*.png")) + list((ROOT / "docs/evidence/stage1-zoom").glob("*.png"))
    raw = [ROOT / "docs/evidence/stage2-tests.xml"] + [p for p in EVIDENCE.glob("*.json") if p.name not in {"capture-manifest.json", "traceability.json"}] + [ROOT / "docs/evidence/stage1-zoom/results.json"]
    def hashes(paths):
        return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
    write(EVIDENCE / "capture-manifest.json", {"captured_at_utc": report["observed_at_utc"],
        "source_version": "No initial Git commit; source SHA-256 manifest identifies checked version", "synthetic": True,
        "source_sha256": hashes(sources), "capture_sha256": hashes(captures), "raw_evidence_sha256": hashes(raw)})
    print(json.dumps(report))


if __name__ == "__main__":
    main()
