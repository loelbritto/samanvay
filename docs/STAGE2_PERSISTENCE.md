# Stage 2 implementation and verification

**G2 ready to close for the synthetic local prototype**, 27 October 2026, Asia/Kolkata. G1's remaining actual-browser zoom check also passed. No later-stage integration, AI metric or production-readiness claim follows.

## Inspection and implemented slice

Inspected Stage 0 contracts, Stage 1 source/screens/control inventory, project state, requirements and tool availability before editing. The project had no backend, migrations, authentication, private objects or worker. The preview's disabled operations were preserved at `?preview=1`. The default workspace now uses authenticated API data and shows explicit unavailability for future workflows.

Persistent SQLite via SQLAlchemy/Alembic stores institutions/aliases and synthetic provenance, regions/bureaus, users/memberships, sessions/login throttling, cases, protected complainant tokens, original JSON/hash, attachment metadata, assignment intervals, workflow events, class grants, idempotent intake requests and integrity jobs. Canonical identity does not replace original supplied text. Name similarity grants no authority. Original payload/bytes and separate complaint IDs survive implemented actions. No complaint merge/delete route exists.

Intake validates fields/synthetic markers; the signed-in eligible officer becomes the initial owner. Received date and illustrative end-of-day disposal boundary are UTC instants displayed in Asia/Kolkata. Success follows commit. Case/original/complainant/assignment/events/outbox metadata commit together. A simulated failed audit insert proves rollback and private-file cleanup on handled exceptions. Separate request keys retain separate complaints even with identical content; an identical retry key returns its prior intake.

Private files have generated keys outside the public frontend, extension/signature/UTF-8 checks and limits of three files, 5 MiB each. Downloads check metadata and attachment permissions separately. Passwords use Argon2id; hashed opaque session tokens, expiry/logout, CSRF and origin checks exist. Owner/class grants and own-bureau supervisor metadata remain separate; management/admin roles reveal no cases by default. Supervisor reassignment checks reason/current version/eligible bureau and region, atomically retains intervals/events, and preserves ID/deadline. This is a limited early Stage 3 slice.

The outbox worker verifies evidence checksums, retains job state and avoids duplicate integrity events on repeat processing. It is not an AI, notification or official integration worker.

## Observed results

| Check | Result / evidence |
| --- | --- |
| Backend suite | 16 passed, 1 Starlette/httpx deprecation warning; [JUnit](evidence/stage2-tests.xml) |
| Frontend compilation | TypeScript/Vite passed; 27 modules, CSS 22.31 kB, JS 300.53 kB. Emitted sizes are not performance metrics |
| UI intake | Created `DEMO-20BF09829C05` with original synthetic text/token and real 117-byte upload; RB count 1 → 2; [proof](evidence/stage2/ui-intake.json) |
| Actual process restart | API/frontend stopped/restarted; same browser session/case/owner/history/file survived; [UI](evidence/stage2/ui-after-restart.json), [API/DB/file](evidence/stage2/after-restart-api.json) |
| File integrity | SHA-256 `d2403f506e0bb0c5342f1b3eae55d70965d680bca827f3cfa993b8d13fae4832`; API bytes, metadata and private file agree |
| Negative reads | No session 401; unrelated PGRC case/file 404; admin overview 0. Tests cover management, supervisor field redaction, scoped search/counts and expiry |
| Supervisor browser flow | RB-023 assigned to Demo Meera Das (v2), restored to Demo Kabir Sen (v3), with distinct reasons/history; [UI](evidence/stage2/assignment-ui.json) |
| Live layouts | Ten routes × desktop/narrow = 20 scoped overflow/label passes; [raw results](evidence/stage2/layout-results.json) and actual captures |
| Stage 1 actual zoom | Native Chrome 200%, DPR doubled, 14 screens/captures reviewed; keyboard path/table passed; normal zoom restored; [raw results](evidence/stage1-zoom/results.json) |

Same-time history events could initially sort ownership before receipt by random ID. Ordering now includes version transitions; a regression asserts RECEIVED then OWNER_ASSIGNED. Out-of-region reassignment was fixed and negatively tested. Long hashes now wrap on narrow detail screens.

## Failures and limits

The first seed command from the root failed to import `app`; running from `backend/` succeeded. Initial sandbox pytest runs failed temp permissions or blocked loopback/event-loop setup; the final suite used a fresh validated workspace-only temp directory outside the sandbox. One dependency deprecation warning remains. Earlier native Chrome checks were stopped/rejected for shared-window privacy/concurrent input. After the user authorised a Samanvay-only window, actual zoom succeeded. Chrome full-page captures clipped at zoom; those images were replaced with reviewed viewport captures. No unrelated-window screenshot is included in evidence.

PostgreSQL was not connected/tested; SQLite is an explicit persistent local substitute (D24). Public demo credentials/HTTP cookies, no malware scan, no hard-crash orphan-file reconciliation, incomplete unknown-length total-body protection, no backup restoration and no comprehensive role-by-surface/concurrent race audit remain limits. Per-file caps and exception cleanup do not prove crash-proof filesystem/database atomicity. Original records are immutable through implemented APIs; a local database administrator can still modify them. No tamper-proof/WORM claim is made.

A01 passed. A02 only creation/count changes passed; disposal/reopening are absent. A11 only current case/search/count/file/session surfaces were exercised. A14 stale assignment rejection passed; racing commands/transfer concurrency remain unexecuted. A03–A10/A12/A13 need later features. Four seed cases plus one browser-created case are not an evaluation corpus; no accuracy/F1/latency study or real-world safety claim exists.

## Changed files and continuation

Added `backend/app/{__init__,api,auth,config,database,main,models,policies,schemas,seed,storage,worker}.py`; Alembic configuration, migration environment/template/revision `19512be41395`; pinned requirements, synthetic seed JSON, pytest configuration/fixtures/tests. Added `.env.example`; ignored private/generated state. Added `frontend/src/{PreviewApp,LiveApp}.tsx`, `api.ts`, `screens/LiveScreens.tsx`; changed App, Vite proxy and styles. Preserved Stage 1 reference screens/fixtures.

Added this handoff, SETUP.md, `scripts/verify_stage2_restart.py`, tests/restart/layout/capture evidence and command log. Updated README, PLAN, DECISIONS, PROJECT_STATE, source-preserving traceability/progress tooling and data/access/workflow/acceptance/backend-gap docs. Original snapshot text/historical evidence remain intact. [Manifest](evidence/stage2/capture-manifest.json) identifies checked source/evidence hashes; Git has no initial commit.

Next: Stage 3 review/information requests, source-state/authority/version checks, atomic accepted transfer, expiry/reject/cancel, escalation, disposal/reopening and concurrent commands. No further implementation is implied by closure. No human input is needed for the next synthetic slice when requested; official scope and real policies still need Q01–Q11 before real use.
