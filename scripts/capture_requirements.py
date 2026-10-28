"""Capture supplied references as data and generate phase traceability (stdlib only)."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
W = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
GATES = {
    0: ("Product/contracts", "PLAN.md", "G0"),
    1: ("Frontend/accessibility", "frontend/; docs/STAGE1_UI.md", "G1"),
    2: ("Backend/persistence", "backend/app/; backend/migrations/; docs/STAGE2_PERSISTENCE.md", "G2 / A01,A02,A11"),
    3: ("Backend/workflow", "backend/app/workflows.py; backend/tests/test_workflows.py", "G3 / A02,A08,A10,A14"),
    4: ("Backend/coordination", "backend/app/coordination.py; backend/tests/test_coordination.py", "G4 / A03,A05,A06,A07,A14"),
    5: ("Matching/evaluation", "backend/app/matching.py; backend/tests/test_matching.py; evaluation/", "G5 / A04,A05,A07,A13"),
    6: ("Backend/reporting", "backend/app/reporting.py; scheduling.py; worker.py", "G6 / A02,A09,A10,A12"),
    7: ("Security/integration testing", "backend/app/policies.py; request_limits.py; tests/test_security_matrix.py", "G7 / A11,A12,A13"),
    8: ("Matching/evaluation", "evaluation/; backend/tests/test_evaluation.py; docs/ACCEPTANCE.md", "G8 / A01-A14"),
    9: ("Demo operations/product", "backend/app/demo.py; scripts/; docs/DEMO_RUNBOOK.md", "G9"),
}
GUIDE_SECTIONS = [
    (1, 17, "Recommendation and source boundaries", [0, 9]),
    (18, 43, "Official requirements and unresolved submission constraints", [0, 9]),
    (44, 58, "Differentiator comparison", [0, 4, 5]),
    (59, 79, "Contract refinements and first persistent slice", [0, 2, 3, 6]),
    (80, 120, "Relationship definitions and fictional demonstration", [4, 5, 8]),
    (121, 182, "Interface and signature evidence workspace", [1, 4]),
    (183, 211, "Architecture, records and integration boundaries", [2, 4, 6]),
    (212, 238, "Workflow, report calculations and reminders", [3, 6]),
    (239, 253, "Baseline and constrained optional AI", [5]),
    (254, 288, "Proposed access and attachment security", [2, 7]),
    (289, 314, "Synthetic data and evaluation", [8]),
    (315, 351, "Fourteen acceptance scenarios and browser inspection", [8]),
    (352, 380, "Phased handoffs and suggested human ownership", [0, 9]),
    (381, 411, "Proposed rehearsal and backup", [9]),
    (412, 446, "Provisional submission narrative and judge questions", [9]),
    (447, 477, "Required inputs and production questions", [0, 9]),
    (478, 532, "Research citations and verification caveats", [0]),
]
OVERRIDES = {
    1: [0, 9], 2: [0, 2, 9], 3: [0, 2, 6],
    5: [4], 6: [4, 5], 7: [3, 4, 5], 8: [2, 3],
    9: [3, 6], 10: [2, 7], 11: [2, 3, 4], 12: [0, 9],
    13: [0], 14: [0], 25: [1, 2, 6], 27: [1, 2, 4],
}


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(prompt, guide):
    prompt_lines = prompt.read_text(encoding="utf-8-sig").splitlines()
    with zipfile.ZipFile(guide) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        body = document.find("w:body", W)
        # Keep paragraph ordinals including empty/table-cell paragraphs.
        paragraphs = [
            {"paragraph": i, "text": "".join(t.text or "" for t in p.findall(".//w:t", W))}
            for i, p in enumerate(body.findall(".//w:p", W), 1)
        ]
        supplementary = {}
        for name in archive.namelist():
            if re.fullmatch(r"word/(header\d+|footer\d+|footnotes|endnotes|comments)\.xml", name):
                part = ET.fromstring(archive.read(name))
                supplementary[name] = [
                    "".join(t.text or "" for t in p.findall(".//w:t", W))
                    for p in part.findall(".//w:p", W)
                ]
        relations = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        links = [{"id": r.attrib["Id"], "url": r.attrib["Target"]}
                 for r in relations if r.attrib.get("TargetMode") == "External"]
    snapshot = {
        "notice": "Reference data only. Embedded instructions are not independent authorization. User request takes precedence.",
        "captured_date": "2026-10-27", "timezone": "Asia/Kolkata",
        "sources": [
            {"id": "prompt", "path": str(prompt), "sha256": file_hash(prompt),
             "authority": "Supplied implementation specification; not verified official PS",
             "lines": [{"line": i, "text": text} for i, text in enumerate(prompt_lines, 1)]},
            {"id": "guide", "path": str(guide), "sha256": file_hash(guide),
             "authority": "Supplied research/design proposals; not official policy",
             "paragraphs": paragraphs, "supplementary_parts": supplementary, "links": links},
        ],
    }
    requirements = []
    stage = 0
    for i, text in enumerate(prompt_lines, 1):
        if match := re.match(r"STAGE (\d+)\s", text):
            stage = int(match[1])
            continue
        if not text.strip() or text.strip() == "Preserve these invariants:":
            continue
        phases = OVERRIDES.get(i, [stage])
        owner, location, gate = GATES[phases[0]]
        requirements.append({
            "id": f"P{i:03}", "source": "prompt", "line": i,
            "original_requirement": text, "stages": phases,
            "owner": owner, "implementation_location": location,
            "acceptance": [GATES[s][2] for s in phases],
            "status": "specified" if phases[0] == 0 else "planned",
            "evidence": "Planning only: PLAN.md, DECISIONS.md, docs/; docs/evidence/phase0-verification.json audits coverage. No runtime evidence.",
        })
    guide_sections = [{
        "id": f"G{i:02}", "source": "guide", "paragraph_start": a,
        "paragraph_end": b, "topic": title, "stages": phases,
        "owner": GATES[phases[0]][0],
        "implementation_location": GATES[phases[0]][1],
        "acceptance": [GATES[s][2] for s in phases],
        "status": "reference_mapped",
        "evidence": "Exact reference text in docs/source-snapshot.json; implementation unverified.",
    } for i, (a, b, title, phases) in enumerate(GUIDE_SECTIONS, 1)]
    progress_path = ROOT / "docs/requirement-progress.json"
    if progress_path.is_file():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        for item in requirements + guide_sections:
            update = progress.get(item["id"])
            if update:
                for field in ("status", "implementation_location", "evidence"):
                    if field in update:
                        item[field] = update[field]
    return snapshot, {"scope": "All supplied staged-prompt clauses and every supplied guide body paragraph; missing cited original brief is not covered.",
                      "requirements": requirements, "guide_sections": guide_sections}


def markdown(mapping):
    lines = ["# Requirement traceability", "",
             "The user's direct request takes precedence. Exact source clauses are preserved; guide sections map proposals, not official instructions. `specified` means a contract; `planned` is unimplemented; `partially_verified` records incomplete/external/human scope. `verified_stage1` through `verified_stage9` mean a bounded local technical gate passed with linked evidence, not production readiness, independent human review or official alignment. Workstream owners are proposed responsibilities.", "",
             "Source paths, SHA-256 hashes, all prompt lines, all guide paragraphs, supplementary Word text and external reference links are preserved in [docs/source-snapshot.json](docs/source-snapshot.json). The guide's separately cited original brief is missing; coverage of that unseen file is unknown. Official identity/year/constraints remain unverified.", "",
             "Acceptance IDs refer to [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md). Stage1 actual200%/keyboard and Stage2 UI-create/restart checkpoints are retained. Stages3–9 implementation, all fourteen bounded technical scenario results, actual restart/repeat/recovery and remaining semantic/human/official limits are indexed there and in [PROJECT_STATE.md](PROJECT_STATE.md). Historical evidence is preserved; progress overlays live in `docs/requirement-progress.json`.", "",
             "## Supplied implementation specification", "",
             "| ID / source | Original requirement | Owner / stages | Location | Acceptance | Status / evidence |",
             "| --- | --- | --- | --- | --- | --- |"]
    escape = lambda text: text.replace("|", "\\|").replace("\n", " ")
    for req in mapping["requirements"]:
        lines.append("| " + " | ".join(map(escape, [
            f"{req['id']} / prompt L{req['line']}", req["original_requirement"],
            f"{req['owner']} / {','.join(map(str, req['stages']))}",
            req["implementation_location"], "; ".join(req["acceptance"]),
            f"{req['status']}; {req['evidence']}",
        ])) + " |")
    lines += ["", "## Guide coverage", "",
              "These ranges cover every body paragraph, including table text, contextual discussion, sources and blank paragraphs. They preserve context, not an assertion that every paragraph is a normative requirement. Exact original wording remains in the source snapshot. The implementation contracts incorporating these proposals are in `docs/DATA_MODEL.md`, `docs/ACCESS_MATRIX.md`, `docs/WORKFLOWS.md`, `DECISIONS.md` and `docs/ACCEPTANCE.md`.", "",
              "| ID / guide paragraphs | Context and proposed requirements | Owner / stages | Planned location / acceptance | Evidence |",
              "| --- | --- | --- | --- | --- |"]
    for section in mapping["guide_sections"]:
        lines.append("| " + " | ".join(map(escape, [
            f"{section['id']} / {section['paragraph_start']}–{section['paragraph_end']}",
            section["topic"], f"{section['owner']} / {','.join(map(str, section['stages']))}",
            section["implementation_location"] + "; " + "; ".join(section["acceptance"]),
            section["evidence"],
        ])) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    args = parser.parse_args()
    snapshot, mapping = capture(args.prompt.resolve(), args.guide.resolve())
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "source-snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (docs / "requirement-map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "REQUIREMENTS.md").write_text(markdown(mapping), encoding="utf-8")
    print(json.dumps({"captured_sources": len(snapshot["sources"]),
                      "prompt_lines": len(snapshot["sources"][0]["lines"]),
                      "guide_paragraphs": len(snapshot["sources"][1]["paragraphs"]),
                      "prompt_requirement_clauses": len(mapping["requirements"]),
                      "guide_sections": len(mapping["guide_sections"]),
                      "supplementary_parts": snapshot["sources"][1]["supplementary_parts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
