# Delivered changes and actual verification

## 28 October live UI redesign

See [complete changed-file, command and results report](REDESIGN_20261028.md). Nine frontend source files and the package test script were added/updated; presentation logic tests and read-only preservation/static contrast scripts were added. No backend source changed. Final build passed (34 modules, CSS 43.56 kB, JS 356.13 kB); 10 frontend logic tests and 72 backend tests passed with one existing dependency warning. Sixteen static colour pairs pass 4.5:1. Both existing contexts retain identical domain records and private bytes. Browser inspection was rejected by the saved origin permission despite user approval; no new layout/keyboard/200% claim is made. Current evidence is under `docs/evidence/redesign-20261028/`. Historical release results follow.

Release samanvay-local-20261027. This repository has no initial commit; `git status --short` lists the project as untracked. A commit-based changed-file diff cannot be produced. The phase ledger records pre-edit gaps and additions at each gate; release-manifest.json inventories delivered source/build files and actual capture hashes. Private databases, files, test contexts, dependencies and dist are ignored.

## Files changed across Stages3–9

- Backend: app/models.py, api.py, auth.py, config.py, worker.py and migration environment; new workflows.py, coordination.py, matching.py, scheduling.py, reporting.py, request_limits.py, security_audit.py and demo.py. Alembic revisions84165027696e, d3dda6dae075, abe1be3f646d,9be862270eb9 and2b8ec33456f0 add workflows/coordination/facts/scheduling/security constraints. Existing initial migration and original records are retained.
- Frontend: src/LiveApp.tsx, api.ts, styles.css, screens/LiveScreens.tsx; new WorkflowScreens.tsx, CoordinationScreens.tsx and OperationsScreens.tsx; vite.config.ts and package lock/Node types. PreviewApp/reference remains labelled and separate. Final clarity fix replaces editable-looking completed pair-review fields with an explanation that the final decision is retained.
- Tests: test_workflows.py, test_coordination.py, test_matching.py, test_reporting_scheduling.py, test_security_matrix.py, test_evaluation.py and test_demo_operations.py; updated fixtures/evidence writer. Existing vertical-slice tests remain. Final added regression exercises DEFER→REJECT plus blocked overwrite/history preservation.
- Research: evaluation/generate.py, run.py, README.md and frozen corpus-v1 inputs/isolated labels/splits/hash manifest; immutable measured runs under docs/evidence/stage8.
- Operations: scripts/run-service.ps1, check-clean-dependencies.ps1, check_clean_runtime.py, verify_running_security.py, verify_full_rehearsal.py, repeat_and_recover.py, reconcile_release_docs.py, summarize_release.py; updated capture_requirements.py/verify_phase0.py.
- Documentation/evidence: README, PLAN, DECISIONS, PROJECT_STATE, REQUIREMENTS; DATA_MODEL, ACCESS_MATRIX, WORKFLOWS, ACCEPTANCE, SETUP, BACKEND_GAPS, PHASES_3_TO_9, MODULE_GUIDE, DEMO_RUNBOOK and this report; requirement maps/progress; JUnit files; actual browser/restart/repeat/recovery/dependency/evaluation records and screenshots. Original source-snapshot text/hashes remain unchanged.

## Commands actually run

The following command families were executed in their indicated directories. Unique basetemp directories and generated IDs are recorded in evidence/tool outputs; no database was cleared. Source inspection also used `rg`, `Get-Content`, directory listings and `git status --short`. These inspection commands do not constitute tests.

| Directory / command | Observed result |
| --- | --- |
| backend: `.venv/Scripts/python.exe -m alembic upgrade head`; `-m app.seed` after migrations | Success; add-only seed retains complaints/edits |
| backend: `.venv/Scripts/python.exe -m pytest --basetemp <fresh validated workspace path> --junitxml ../docs/evidence/stageN-tests.xml -q` at each phase |23/29/35/42/60/62 tests passed at Stages3/4/5/6/7/8; Stage9 final result in release-summary/JUnit. One TestClient/httpx deprecation warning |
| backend: `pytest tests/test_reporting_scheduling.py --basetemp <fresh path> --junitxml ../docs/evidence/stage9-print-tests.xml -q` |7passed after printable report navigation change |
| frontend: `npm.cmd install --save-dev --save-exact @types/node@26.6.5`; `npm.cmd run build` | Missing Node types fixed; final TypeScript/Vite31module build passed |
| root: `.\scripts\run-service.ps1 -Service api`, `-Service worker`; original frontend already running | Loopback main API8000/UI5173/worker; persistent5cases retained |
| root: `.\scripts\run-service.ps1 -Service api -ContextId demo-5f5a439bfd2ea5ede367507b` and corresponding frontend/worker commands | Loopback8001/5174/worker started, stopped with Ctrl+C and actually restarted; API PID23352→12356, Vite6956→2052 |
| backend: `python -m app.demo new --key rehearsal-20261027-final-v1` | First new marked context; later same-key execution returned reused:true, previous contexts preserved |
| root: `python scripts/verify_full_rehearsal.py before-clock`, `before-restart`, `after-restart` |8cases and originals/files verified;120hour isolated offset, unchanged owners/deadlines, same restart snapshots, main5/offset0, managementCSV7 |
| root: `python scripts/verify_running_security.py` | Actual unauthenticated API401; wrong-origin403; existing private/backend Vite paths403;5original cases and private hash preserved |
| root: `.\scripts\check-clean-dependencies.ps1` | Actual fresh npm ci/build, fresh Python venv/pinned install/pip-check/migration/seed/startup all passed; logs preserved |
| root: `python evaluation/generate.py` repeatedly; `python evaluation/run.py` repeatedly | Frozen corpus hashes unchanged; final run20261027T164828Z-1236c289, raw results retained; baseline selected |
| root: `python scripts/repeat_and_recover.py` | Actual eight-case private backup/restore, source unchanged; second7case context creation/review/plan/clock/ack/export/newapp restart passed. No deletes |
| backend: `python -m app.demo audit-storage --context-id demo-5f5a439bfd2ea5ede367507b`; `python -m app.demo audit-storage` | Actual missing/changed/unreferenced-file results saved separately; no deletions |
| root: `python scripts/reconcile_release_docs.py`; `python scripts/summarize_release.py`; `python scripts/capture_requirements.py --prompt <supplied path> --guide <supplied path>`; `python scripts/verify_phase0.py --verify-originals --output docs/evidence/stage9/source-coverage.json` | Documentation generation, evidence aggregation and original-source audit; final output files record success/failure. These commands do not rerun application tests |

`python` above denotes backend/.venv/Scripts/python.exe, with relative path adapted to the shown directory. The fresh-runtime helper also used the inspected bundled Python3.12.14. Browser actions used CUA, not shell browser automation: real file chooser uploads, Enter navigation/submission, CSV download, current scoped screenshots, DOM layout/label checks and table keys. Actual native200% proof is the preserved Stage1 checkpoint; current Stage9 browser observations are separate and labelled.

## Corrected failures and remaining limits

The build initially lacked Node type definitions; the exact pinned dependency fixed it. Rehearsal exposed workflow-only version changes incorrectly marking final unchanged-evidence decisions stale; content fingerprints and a regression fixed it. Print opened an inaccessible new-tab flow; same-tab HTML plus safe filter return was implemented and browser-verified. Completed pair reviews displayed misleading editable fields; final wording was repaired and inspected. Worker transient failures now preserve/retry durable jobs.

Two restricted repeat-script attempts stalled before a first request while Windows created an event-loop socket; they were interrupted, their contexts preserved, and the permitted loopback run passed. A browser automatic approval review timed out once; the allowed retry succeeded. An early documentation-generator quoting error was corrected before it wrote documents. Failed full-page screenshot attempts produced no artifact; only saved capture files are indexed. Wrong/missing inspection filenames and unsupported initial locators were corrected, and no success was inferred from those attempts.

No unfinished failed assertion remains in the final successful evidence. One dependency warning remains. Human comprehension/independent labels, official constraints/policies, live semantic/official/email integration, PostgreSQL, antivirus and production deployment/security/scale remain unverified as detailed in PROJECT_STATE.md. No additional coding stage is needed for the bounded local release; stakeholder and unfamiliar-user validation is the next gate.
