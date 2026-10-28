"""Audit Stage 0 planning artifacts. This does not run application acceptance tests."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from capture_requirements import capture, markdown

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = ["README.md", "PLAN.md", "DECISIONS.md", "PROJECT_STATE.md", "REQUIREMENTS.md",
                 "docs/DATA_MODEL.md", "docs/ACCESS_MATRIX.md", "docs/WORKFLOWS.md",
                 "docs/ACCEPTANCE.md", "docs/evidence/phase0-commands.md"]


def audit(verify_originals=False):
    checks = []

    def check(name, condition, detail):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    for path in REQUIRED_DOCS:
        file = ROOT / path
        check("document:" + path, file.is_file() and file.stat().st_size > 0, "Required planning artifact exists and is nonempty")
    snapshot = json.loads((ROOT / "docs/source-snapshot.json").read_text(encoding="utf-8"))
    mapping = json.loads((ROOT / "docs/requirement-map.json").read_text(encoding="utf-8"))
    source_prompt, source_guide = snapshot["sources"]
    expected = {line["line"] for line in source_prompt["lines"]
                if line["text"].strip() and not re.match(r"STAGE \d+\s", line["text"])
                and line["text"].strip() != "Preserve these invariants:"}
    actual = [req["line"] for req in mapping["requirements"]]
    check("complete_prompt_coverage", set(actual) == expected and len(actual) == len(set(actual)),
          {"expected_clauses": len(expected), "mapped_clauses": len(actual), "missing": sorted(expected - set(actual))})
    source_lines = {item["line"]: item["text"] for item in source_prompt["lines"]}
    check("verbatim_requirement_text", all(req["original_requirement"] == source_lines.get(req["line"]) for req in mapping["requirements"]),
          "Every mapped original clause equals its source snapshot line")
    check("owner_stage_location_acceptance_evidence", all(
        req.get("owner") and req.get("stages") and all(type(stage) is int and 0 <= stage <= 9 for stage in req["stages"])
        and req.get("implementation_location") and req.get("acceptance") and req.get("evidence")
        for req in mapping["requirements"] + mapping["guide_sections"]), "Every clause/guide section has traceability fields")
    check("honest_maturity_statuses", all(req["status"] in ({"specified", "planned", "partially_verified"} | {f"verified_stage{i}" for i in range(1,10)}) for req in mapping["requirements"]),
          "Statuses distinguish contracts, partial scope and evidence-gated local stage passes")
    if any(req["status"].startswith("verified_stage") for req in mapping["requirements"]):
        stage_results = json.loads((ROOT / "docs/evidence/stage2/results.json").read_text(encoding="utf-8"))
        check("local_stage_evidence_present", stage_results.get("stage1_ready") and stage_results.get("stage2_ready"),
              "Stage gate summary links actual zoom/layout/keyboard, JUnit, UI intake and API/DB/file restart evidence; this audit does not rerun them")
    if any(req["status"] in {f"verified_stage{i}" for i in range(3,10)} for req in mapping["requirements"]):
        release = json.loads((ROOT / "docs/evidence/stage9/release-summary.json").read_text(encoding="utf-8"))
        check("later_local_gate_evidence_present", release.get("technical_gates_passed") and release.get("independent_human_review_performed") is False,
              "Final summary verifies bounded runtime evidence and explicitly records missing human review; this source audit does not rerun the application")
    covered = Counter(p for section in mapping["guide_sections"] for p in range(section["paragraph_start"], section["paragraph_end"] + 1))
    expected_paras = {p["paragraph"] for p in source_guide["paragraphs"]}
    check("complete_guide_context_coverage", set(covered) == expected_paras and all(count == 1 for count in covered.values()),
          {"body_paragraphs": len(expected_paras), "covered_once": sum(v == 1 for v in covered.values())})
    check("generated_markdown_current", (ROOT / "REQUIREMENTS.md").read_text(encoding="utf-8") == markdown(mapping),
          "Readable requirement table matches machine-readable map")

    # These are document-presence/consistency checks, not executable policy/security tests.
    model = (ROOT / "docs/DATA_MODEL.md").read_text(encoding="utf-8")
    workflow = (ROOT / "docs/WORKFLOWS.md").read_text(encoding="utf-8")
    access = (ROOT / "docs/ACCESS_MATRIX.md").read_text(encoding="utf-8")
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    plan = (ROOT / "PLAN.md").read_text(encoding="utf-8")
    acceptance = (ROOT / "docs/ACCEPTANCE.md").read_text(encoding="utf-8")
    check("separate_concepts_documented", all(name in model for name in [
        "institution_resolution", "assignment_history", "relationship_review", "coordination_group"]),
        "Four distinct proposed persistence concepts are documented")
    check("lifecycle_and_transfer_documented", all(state in workflow for state in [
        "RECEIVED", "ASSIGNED", "UNDER_REVIEW", "AWAITING_INFORMATION", "DISPOSED",
        "PENDING", "ACCEPTED", "REJECTED", "CANCELLED", "EXPIRED"]),
        "Lifecycle and transfer states have distinct documented command tables")
    check("role_matrix_documented", all(role in access for role in [
        "RB officer", "PGRC officer", "Regional officer", "Bureau supervisor",
        "Coordinator capability", "Senior management", "System administrator", "Background worker"]),
        "All proposed roles and separate service authority are included")
    check("fourteen_scenarios_documented", all(f"| A{i:02} |" in acceptance for i in range(1, 15)),
        "Fourteen scenario definitions are present; runtime results are reported separately by scope")
    check("uncertainty_and_next_slice_documented", all(token in decisions for token in ["Q01", "Q11", "403"])
          and "Stage 1" in plan and "missing" in plan.lower(),
          "Official uncertainty, missing source and next UI slice are explicit")
    if verify_originals:
        paths = [Path(source["path"]) for source in snapshot["sources"]]
        check("original_files_available", all(path.is_file() for path in paths), "Original files are available for this audit")
        if all(path.is_file() for path in paths):
            fresh_snapshot, fresh_mapping = capture(*paths)
            check("original_hashes_and_extraction", fresh_snapshot == snapshot,
                  "Original SHA-256 hashes and full extracted text/links equal captured snapshot")
            check("reproducible_mapping", fresh_mapping == mapping,
                  "Regenerating source classification yields identical traceability data")
    else:
        checks.append({"name": "original_files_not_rechecked", "passed": True,
                       "detail": "Portable snapshot-only audit; use --verify-originals to verify original files", "scope_note": True})
    failures = [check for check in checks if not check["passed"]]
    artifacts = REQUIRED_DOCS + [".gitignore", "scripts/capture_requirements.py", "scripts/verify_phase0.py",
                                "docs/source-snapshot.json", "docs/requirement-map.json",
                                "docs/requirement-progress.json"]
    artifact_hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                       for path in artifacts if (ROOT / path).is_file()}
    return {"phase": 0, "scope": "Planning/source coverage audit only; no application acceptance tests",
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
            "originals_rechecked": verify_originals,
            "checks": checks, "passed": not failures,
            "check_count": len(checks), "failure_count": len(failures),
            "prompt_clause_count": len(actual), "guide_paragraph_count": len(expected_paras),
            "artifact_sha256": artifact_hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-originals", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.verify_originals)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Stage 0 audit could not complete: {exc}", file=sys.stderr)
        return 1
    if args.output:
        output = args.output.resolve()
        if not output.is_relative_to(ROOT):
            parser.error("Evidence output must be inside this workspace")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["phase", "scope", "passed", "check_count", "failure_count", "prompt_clause_count", "guide_paragraph_count"]}))
    for check in report["checks"]:
        if not check["passed"]:
            print("FAIL: " + check["name"] + " " + json.dumps(check["detail"]))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
