"""Reconcile current prototype documentation; preserve historical evidence and source text."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(name, text):
    (ROOT/name).write_text(text.strip()+'\n', encoding='utf-8')


def main():
    write('README.md', r'''
# Samanvay

Student prototype for institution complaint coordination. All people, complaints, receipts, institutions and identifiers are synthetic. No official AICTE integration, deployment or endorsement exists.

**Stages 1–9 have passed their bounded local technical checks.** The application persists intake/private evidence, ownership, workflow actions, transfer acceptance, disposal/reopening, identity review, coordination plans, reviewed relationships, in-app notifications and scoped reports. Institution identity, complaint relationships, case ownership and coordination responsibility remain separate. No complaint merge/delete endpoint exists. All prior contexts are preserved.

Read [current results and limits](PROJECT_STATE.md), [setup](docs/SETUP.md), [demo runbook](docs/DEMO_RUNBOOK.md), [module/data-flow guide](docs/MODULE_GUIDE.md), [acceptance evidence](docs/ACCEPTANCE.md), and [phase ledger](docs/PHASES_3_TO_9.md). [Requirement traceability](REQUIREMENTS.md) retains the supplied clauses without claiming official authority.

After setup, from the repository root, use separate PowerShell terminals:

```powershell
.\scripts\run-service.ps1 -Service api
.\scripts\run-service.ps1 -Service frontend
.\scripts\run-service.ps1 -Service worker
```

Open http://127.0.0.1:5173/. Synthetic login `rb@demo.test`, password `DemoOnly-Stage2!`. These public demo accounts and HTTP cookies are only for this loopback prototype. The rehearsed isolated context uses http://127.0.0.1:5174/ and coordinator account `coordinator@demo.test` with the same password; see the runbook for restart commands.

The database is on-disk **SQLite**, managed by SQLAlchemy/Alembic. PostgreSQL was not verified. The lexical/rule matcher provides suggestions requiring authorised review; no semantic model or LLM is connected. A measured character-vector experiment showed no retrieval gain and is disabled in the application. The frozen synthetic evaluation is not evidence of real complaint accuracy.

Human usability/label review and official competition/policy inputs remain unverified. Production HTTPS, PostgreSQL, antivirus and external integrations remain outside the completed local technical scope. The illustrative reference at `?preview=1` is separately labelled and saves nothing.
''')
    write('PROJECT_STATE.md', '''
# Project state

Release `samanvay-local-20261027`, captured 27 October 2026, Asia/Kolkata. **Stages 1–9 local technical implementation and checks are complete.** This is a synthetic student prototype; independent human evaluation, official alignment and production readiness are not established. [Final evidence summary](docs/evidence/stage9/release-summary.json) and [acceptance index](docs/ACCEPTANCE.md) define the precise scope.

## Implemented

React/TypeScript frontend; FastAPI, SQLAlchemy/Alembic and persistent SQLite; Argon2id/password sessions/CSRF; private evidence bytes; original payloads and checksums; scoped intake/search/counts; assignments; review/information/amendment/deadline/escalation; transfer request/accept/reject/cancel/expiry; resolution/disposal/reopening; append-only application audit and optimistic versions. Business mutations and audit/outbox commit together.

Confirmed institution identity, relationship decisions, assignment intervals and coordination plans are separate tables. Confirmed cross-bureau active cases generate coordination even when INDEPENDENT. Ambiguous names require identity review; Pune and Nagpur remain distinct. Suggestions never merge, close or transfer a complaint. Material source changes create linked reviews; final decisions survive workflow-only changes to unchanged evidence.

Persistent in-app scheduling/delivery/acknowledgement, policy versions, scoped reports/CSV/HTML print, bounded matching, strict optional-adapter validation, input/body caps, role/surface checks, storage audits, safe new demo contexts and verified backup/restore are implemented. Optional character vectors remain research-only after measured comparison; no semantic service is connected.

## Observed evidence

- Final full backend run: **72 tests passed**, one Starlette/httpx dependency deprecation warning. Final print/report follow-up: **7 passed**, same warning. No failed assertions remain in those runs. JUnit files are under docs/evidence/.
- Final TypeScript/Vite build passed: 31 modules, CSS 22.49 kB and JS 340.80 kB. Fresh lockfile npm install/build and fresh Python install/migrate/seed/startup passed in a separate dependency-check directory.
- Original workspace retains **five** complaints, including the Stage2 UI-created record and private bytes; its clock offset stays zero. The isolated browser rehearsal created four new complaints plus four seed records, **eight** total. Actual API/UI/worker stop and restart retained the same records, session, owners, originals, attachment hashes, group plan, decisions and notification states.
- Browser performed PGRC/RB intake, real file uploads, review/information request, pending/accepted transfer, RELATED and INDEPENDENT review controls, coordination lead/next action, clock advance, overdue acknowledgement and seven-row management CSV/print. These are fictional authorised-role exercises by the agent, not independent human annotation.
- An automated second rehearsal in another context passed with three new cases/seven total, application-instance restart and six-row scoped metadata export. Actual backup/restore of the eight-case browser context retained rows/originals/history/private hashes in a new context; source records were unchanged and **zero complaints/files were deleted**.
- Stage1 actual native Chrome200% label, doubled DPR and14route checks are preserved. Current live narrow/desktop and keyboard observations are in stage9/browser-final.json. These are scoped observations, not WCAG certification.
- Frozen evaluation:32institutions,240cases,528labelled pairs,98identity queries.168held-out generated-policy pairs matched their synthetic labels;98identity expectations passed. Retrieval40queries:recall@1=.6,recall@3=1 for both methods. Character vectors showed no gain and were slower. Raw classifications/rankings/errors/timings/source hashes are preserved. These metrics do not establish real-world or multilingual semantic accuracy.

## Remaining limits and human input

Official PS identifier/text/year, round/template/deadline, the separately cited missing brief and approved operational policies remain unverified. Independent difficult-label review and unfamiliar-user comprehension were requested; the user delegated choices, so neither study is claimed. The roughly three-minute narration is a target, not a measured successful live run duration.

No PostgreSQL/RLS deployment, HTTPS/public deployment, real malware scanning, official/email integration, semantic/LLM service, national-scale load result, screen-reader/WCAG certification or production penetration test is established. Access logging is best effort during database failure; business audit is mandatory. Local database administrators can tamper with local files. Reports describe current-state received-date cohorts and period events, not reconstructed historical state. Orphan audits report and preserve extra files rather than deleting them.

No further coding phase is required for this local release. The next gate is **human/stakeholder validation**: confirm official constraints, approve policy/access scopes, review difficult labels and run the short narration with an unfamiliar teammate before a real pilot/submission. No real-data deployment is authorised or claimed.

See docs/CHANGES_AND_COMMANDS.md for changed files, commands actually run, corrected failures and exact evidence. Historical Stage1/Stage2 evidence is retained; Git has no initial commit, so a commit-based diff/version is unavailable. Private contexts, dependencies and builds remain ignored.
''')
    write('docs/SETUP.md', r'''
# Verified local setup

Windows PowerShell; inspected Node25.8.2/npm11.11.1 and Python3.12.14. Exact npm/Python versions are pinned in lockfiles. Fresh installations, frontend build, migration, seed and backend startup were actually checked; logs: evidence/stage9/clean-*.log and clean-dependencies.json. No paid key is needed. Use synthetic data only.

From repository root:

```powershell
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv backend/.venv
& '.\backend\.venv\Scripts\python.exe' -m pip install -r backend/requirements.lock
cd frontend
npm.cmd ci --no-fund --no-audit
npm.cmd run build
cd ../backend
& '.\.venv\Scripts\python.exe' -m alembic upgrade head
& '.\.venv\Scripts\python.exe' -m app.seed
cd ..
```

Use separate terminals from repository root:

```powershell
.\scripts\run-service.ps1 -Service api
.\scripts\run-service.ps1 -Service frontend
.\scripts\run-service.ps1 -Service worker
```

The verified helper starts loopback API8000/UI5173 and the durable worker using `.local-data`. Ctrl+C stops the owned process; restart with the same directory. Do not delete database/WAL/private evidence. Seed is add-only. `.env.example` describes process variables; the application does not auto-load an env file. API environments are limited to demo/test.

All **nine** synthetic accounts use `DemoOnly-Stage2!`:

| Account | Local scope |
| --- | --- |
| rb@demo.test | Assigned RB cases and self-owned intake |
| rb.backup@demo.test | Assigned RB cases, including Nagpur seed |
| pgrc@demo.test | Assigned PGRC cases and intake |
| supervisor@demo.test | RB metadata, eligible assignment and explicit workflow delegations |
| pgrc.supervisor@demo.test | PGRC metadata/assignment and explicit workflow delegations |
| regional@demo.test | Western-region scoped intake/owned cases |
| coordinator@demo.test | Explicit institution metadata and pair/coordination grants; N/I seed scope separate from A |
| management@demo.test | No implicit case access; explicit rehearsal scope is Pune M only |
| admin@demo.test | Technical policy/demo operations; no implicit complaint access |

Opaque sessions/CSRF are stored server-side; Argon2id hashes; HttpOnly/SameSiteStrict cookies expire after8hours of host time. Secure cookies are disabled for loopback HTTP. Isolated contexts use distinct cookie realms; restore revokes copied sessions. No account/grant-management UI or production identity-provider integration is claimed.

## Separate synthetic run, backup and recovery

From backend, `python -m app.demo new --key <unique-nonsecret-run-key>` creates a new marked context under `.demo-contexts`; the same key reuses its persistent state. This is an idempotent non-destructive reset: old complaints/contexts remain intact. Use the returned context ID:

```powershell
# From repository root, each command in a separate terminal
.\scripts\run-service.ps1 -Service api -ContextId demo-5f5a439bfd2ea5ede367507b
.\scripts\run-service.ps1 -Service frontend -ContextId demo-5f5a439bfd2ea5ede367507b
.\scripts\run-service.ps1 -Service worker -ContextId demo-5f5a439bfd2ea5ede367507b
```

These exact context commands were exercised with API8001/UI5174 and actual stop/restart. Only one isolated context may occupy those ports at once. The primary context remains separate.

From backend:

```powershell
& '.\.venv\Scripts\python.exe' -m app.demo audit-storage --context-id demo-5f5a439bfd2ea5ede367507b
& '.\.venv\Scripts\python.exe' -m app.demo backup --context-id demo-5f5a439bfd2ea5ede367507b
# Substitute the returned backup ID and a NEW non-secret restore key:
& '.\.venv\Scripts\python.exe' -m app.demo restore --backup-id backup-RETURNED_ID --key my-new-recovery-run
```

The last line is a substitution template. Actual recovery evidence identifies the used backup/context. Backup uses SQLite's backup API plus verified private-file copies, integrity/FK checks and a manifest. Restore verifies hashes into a NEW context; the source is preserved. Storage audit reports missing/changed/unreferenced files without deleting. No arbitrary configured production database reset is supported.

## Checks

`npm.cmd run build` in frontend; `python -m pytest -q` in backend. Evidence runs use unique validated workspace `--basetemp` directories and JUnit outputs, preserving existing data. In the managed sandbox TestClient needs loopback socket permission; a restricted run hung during Windows event-loop socket creation, then the permitted repeat passed. This is not an application assertion failure.

`scripts/check-clean-dependencies.ps1` installs/builds in a new preserved directory; `scripts/repeat_and_recover.py` exercises a new context plus recovery; `evaluation/generate.py` checks/freezes the synthetic corpus; `evaluation/run.py` emits a new immutable measured run. Source traceability is separately audited by `scripts/verify_phase0.py --verify-originals`.
''')
    write('docs/MODULE_GUIDE.md', '''
# Module and data-flow guide

Release samanvay-local-20261027. Proposed team responsibilities are modules, not invented named team members. Exact schema is backend/app/models.py and Alembic migrations; exact authority is backend policies/workflows. This guide describes the implemented synthetic local build.

| Module | Files | Responsibility / verification |
| --- | --- | --- |
| UI/auth/intake | frontend/src/LiveApp.tsx, api.ts, screens/LiveScreens.tsx | Password sign-in, scoped reads, multipart intake, real server success/error, history/409 reload; vertical-slice tests and UI rehearsal |
| Workflow | backend/app/workflows.py; frontend/src/screens/WorkflowScreens.tsx | Source state/authority/reason/version, actions/resolutions/transfers, one accountable owner; race/rollback tests |
| Identity/coordination | backend/app/coordination.py; CoordinationScreens.tsx | Exact IDs/aliases/city conflicts, review provenance, independent cross-bureau condition, separate lead/reviews, retained decisions |
| Matching | backend/app/matching.py | Scope-first bounded candidate set, explicit facts/contradictions/UNKNOWN, cited suggestions; optional strict adapter validator; no connected model |
| Scheduling/operations | backend/app/scheduling.py, worker.py; OperationsScreens.tsx | Persisted dedup notifications, leases/recovery/acknowledgement, policy versions, isolated context time |
| Reports | backend/app/reporting.py | Single scoped population, filters/denominators/ageing/period events, escaped CSV/HTML print |
| Security/storage | auth.py, policies.py, storage.py, request_limits.py, security_audit.py | M/N/I/A and capability checks, private generated keys/type signatures/body caps, session/CSRF, minimal significant access records |
| Persistence/operations | models.py, database.py, migrations/, seed.py, demo.py, scripts/run-service.ps1 | SQLite transactions, immutable originals, add-only seed, new contexts, verified private backup/restore |
| Research | evaluation/generate.py, run.py, corpus-v1/, README.md | Frozen isolated gold/splits, held-out raw results and comparison; synthetic-only limitations |

Browser form → authenticated API → validated role/capability and data class → expected-version conditional write → case/assignment/action/audit/outbox transaction → response. Private bytes use a generated server-side storage key and independent download checks. A worker consumes persistent jobs, refreshes deterministic coordination, schedules/delivers in-app notifications and checks evidence hashes. No external communication is made.

CaseRecord links canonical institution, current owner and bureau. OriginalSubmission and Attachment retain the original evidence; Assignment records time intervals. IdentityDecision retains correction/provenance; RelationshipSuggestion and RelationshipDecision retain pair-specific evidence and review; CoordinationGroup/GroupParticipant/GroupReview retain institutional responsibility independently. A pair decision cannot change case ownership or lifecycle. A group lead cannot accept a transfer.

Matcher inputs contain permitted source text/structured facts; scores rank evidence and are not probabilities. Different students/receipts in one refund incident normally yield RELATED; same incident/request/person/receipt may yield DUPLICATE; distinct faculty issue INDEPENDENT; insufficient/conflicting facts UNKNOWN. Backend authority is required even when a suggestion is correct. No LLM/semantic cache is required; the research-only character cache is versioned and reproducible but disabled on the web after no gain.

Reports apply authorisation before filters, rows, snippets and counts. Pending = lifecycle other than DISPOSED; UNDER_REVIEW/overdue are overlapping pending subsets. Overdue means due_at < context time, excluding missing deadlines. Received dates are Asia/Kolkata half-open intervals. Cohort disposal rate uses currently disposed / received cohort. Period distinct disposals / new receipts may exceed100% when clearing backlog; monthly/quarterly event views are distinct. Current-state reports do not reconstruct past states.

The local access matrix is a proposal requiring stakeholder validation. Public synthetic credentials, SQLite and loopback HTTP are the verified scope. See BACKEND_GAPS.md before considering real data or deployment.
''')
    write('docs/DEMO_RUNBOOK.md', r'''
# Synthetic demonstration and recovery runbook

Release `samanvay-local-20261027`; actual captures dated27October2026, Asia/Kolkata. Capture filenames/hashes and source/build evidence are indexed in evidence/stage9/release-manifest.json. No Git commit exists. All people/receipts/incidents are fictional; no AICTE service, email or semantic model is connected.

## Open the rehearsed build

API8001/UI5174/worker are running with `demo-5f5a439bfd2ea5ede367507b`. Open http://127.0.0.1:5174/; sign in `coordinator@demo.test` / `DemoOnly-Stage2!`. To restart use the three context-specific commands in SETUP.md. Stage9 evidence proves a real stop/restart, preserving browser session, cases, files, plan and alerts. Do not advance this context's clock again merely to replay the same alert: it is already120hours ahead. Use a new marked context for a new live run.

For a clean run from backend: `python -m app.demo new --key <new-run-key>`; keep the returned ID. The same key reuses the context and retains its records. Stop only your owned isolated services, then pass that ID to run-service.ps1. Seed creates four synthetic cases and nine users. No destructive reset exists. The Settings operation can create another context, but starting its service still requires the documented helper. Each context uses a separate cookie name.

## Proposed three-minute narration

This is a presentation target, not a measured three-minute successful run; verification and file uploads took longer. Keep backup captures available rather than relying on panel links/video playback.

| Target segment | Screen / observable claim |
| --- | --- |
| 0:00–0:25 | Overview → Pune institution: several bureaus need coordination; case owners remain separate |
| 0:25–0:55 | PGRC synthetic refund intake and real receipt; RB paraphrase with original “DSI Pune” text and different student/receipt. Canonical Pune ID is explicitly selected, never inferred from an abbreviation without review |
| 0:55–1:30 | Evidence review: separate student receipts → RELATED. Faculty wage issue → INDEPENDENT. Show exact sources, conflicts/missing facts, reviewer reason/history. Semantic matching unavailable; baseline works |
| 1:30–2:00 | PLANNED institutional coordination: Demo Meera Das coordinates. Refund DEMO-79D983D2A10B stays owned by Demo Kabir Sen/RB; PGRC cases stay with Demo Ananya Rao. Next action: coordinate separate responses while each owner handles their own complaint |
| 2:00–2:25 | Timeline shows receipt, actions and transfer. Source remains owner during pending transfer; acceptance changes the same case's owner without resetting its deadline. Nagpur DEMO-INST-044 is a different institution and is not in the Pune group |
| 2:25–2:45 | Isolated admin clock/worker → persisted overdue alert → recipient acknowledgement. No host time/other-context deadline changed |
| 2:45–3:00 | Management's explicit Pune M-only report: seven rows, no narratives/identity/private evidence. Actual CSV and HTML print agree |

Completed browser record IDs: PGRC refund DEMO-E80508228652; RB refund DEMO-79D983D2A10B; independent faculty DEMO-436C0703134C; accepted transfer DEMO-80AE1D9C9F27. Four initial seed cases remain; total8. Original workspace remains5. The automated repeat created3more in another7case context and passed a fresh application-instance restart. Actual browser service restart evidence is separate from that automated repeat.

## Answers supported by the build

- Differentiator: one institution timeline plus cited pair comparison and explicit coordination lead; same institution never implies duplicate.
- Wrong match: reject/defer with a reason. Final review persists for unchanged evidence; materially changed evidence links a new review rather than erasing the prior decision.
- Ownership: one current assignment; a pending transfer leaves the source accountable. Group lead is a separate institutional responsibility.
- Privacy: scope-first API/search/counts/export and separately protected attachment bytes; administration gives no case access. Public demo accounts are synthetic only.
- Offline: installed local app/core rules need no paid model key; fresh dependency installation needs its package sources. No tested universal offline installer is claimed.
- Results:240generated cases/32institutions; generated-policy results are artificial. Both retrieval methods had recall@3=1 on40queries; vectors added no gain, so baseline is selected. No real accuracy claim.
- Integration: in-app database notifications and private local files are real. No official/email/semantic integration is simulated as a working external service.

## Backup and human gate

Actual backup `backup-ad79d704a15f43f980ab2e4c5078bfab` restored into `demo-30691bac975725b4bf3ef891`. Rows/originals/history/private hashes matched and source records remained unchanged; copied sessions are revoked on restore. The backup remains private under .demo-contexts/backups. No complaint or file was deleted. Storage audit is non-destructive.

Backup views include coordinated-plan-viewport.png, related-review.png, intake-pgrc.png, transfer-source-pending.png, transfer-accepted.png, management-report.png, printable-report.png and mobile captures in evidence/stage9. Captures show the real build and synthetic labels; virtual Nov1timestamps are explicitly caused by the isolated clock, while capture date is Oct27.

The user delegated judgement instead of supplying comprehension answers. Expected reading: Meera coordinates Pune, Kabir owns the RB refund, separate owners prepare their responses, and two students/different receipts for the same incident are RELATED. These are design expectations, not observations of an unfamiliar teammate. Independent label/usability review and official template/policy approval remain human gates. No selection outcome is promised.
''')
    write('docs/BACKEND_GAPS.md', '''
# Current limitations after local Stages 1–9

The persistent workspace implements all planned local technical slices. The separate `?preview=1` reference remains fixture-only and saves nothing; disabled reference controls are intentional. Historical preview/persistence gap ledgers remain in STAGE1_UI.md and STAGE2_PERSISTENCE.md. They are not the current backend status.

| Area | Verified local implementation | Remaining boundary |
| --- | --- | --- |
| Database/state | SQLite migrations, originals, versioned atomic business audit, one current assignment, persistent jobs | PostgreSQL/RLS actual-role checks and production load/concurrency not verified |
| Authentication/access | Password hash/session/CSRF, M/N/I/A grants, capability delegation, nine-role negative surface matrix | Public demo accounts/HTTP only; no production identity provider, account/grant admin UI or stakeholder-approved policy |
| Workflow | Review/info/amend, transfer accept/reject/cancel/expiry, escalation/disposal/reopen and concurrency/rollback | Illustrative authority/deadline rules require real institutional approval; no official import connector |
| Coordination/matching | Separate institutional plan, four relationship labels, sticky review, bounded baseline, strict adapter validation | No live semantic/LLM; statistical vector experiment disabled after no gain; no national-scale indexed retrieval or multilingual semantics claim |
| Evidence | Generated private keys, size/type/signature/body caps, authenticated bytes, checksums, non-destructive storage audit | No real antivirus/full document sandbox; filesystem/DB hard-crash atomicity and production object store unverified |
| Notifications/reports | Durable in-app delivery/ack/leases/dedup, same scheduler, scoped CSV/print/filter denominators | No external email/official service; reports use current state rather than reconstructing historical state |
| Operations | Separate new contexts, context cookie realms, actual restart, verified SQLite/file backup/restore, fresh dependencies | No HTTPS/public deployment, tamper-proof audit, disaster-recovery SLA or unattended cleanup; old records/extra files preserved |
| Evaluation/UI | Frozen synthetic corpus/raw metrics, actual browser intake/restart/keyboard/layout and historical native200% | No independent difficult-label/comprehension study, screen-reader/WCAG certification, real-world accuracy or production penetration test |
| Official alignment | Source clauses/guide fully inventoried; explicit unresolved inputs | Official PS/year/template/deadline, missing cited brief and approved policies remain unverified |

No material failed application assertion remains in the final72test run or7report follow-up. A dependency deprecation warning remains. Restricted TestClient socket startup was retried with permitted loopback access; the repeat passed. A browser approval timeout was retried successfully and did not establish an unsafe action. See CHANGES_AND_COMMANDS.md and the release evidence summary.
''')
    # Keep the original design tables but remove outdated implementation claims.
    replacements = {
        'docs/DATA_MODEL.md': ('# Persistent model and design contract', 'The local schema now implements institutions/aliases, original submissions, cases/complainant tokens, attachments, assignment intervals, actions/resolutions/transfers, identity decisions, coordination groups/participants/reviews, relationship suggestions/decisions, grants, sessions, audit/outbox, policy/clock/notifications and versioned research cache. Exact names/constraints are in backend/app/models.py and migrations. The tables below retain the design vocabulary: institution_resolution maps to IdentityDecision/CaseRecord, relationship_review to RelationshipSuggestion/RelationshipDecision, coordination_group to CoordinationGroup, assignment_history to Assignment. Optional production contact fields/import connectors are not implied. See MODULE_GUIDE.md and final evidence.'),
        'docs/ACCESS_MATRIX.md': ('# Access policy and implemented local scope', 'This proposed policy is enforced through central policies.py plus scoped workflow/coordination capabilities. Owners/class grants, region/bureau metadata, separate pair/coordination authority, transfer receiver and disposal/reopen delegations, reports/bytes and administrator separation are implemented. A nine-role negative surface matrix passed in Stage7/9. Rehearsal scope explicitly grants Pune M-only to management and N/I to the coordinator without A; administration still grants no complaint access. The table is a design policy requiring stakeholder approval; broad account/grant administration is not implemented.'),
        'docs/WORKFLOWS.md': ('# Workflows and calculations', 'The command tables describe the implemented local workflow policy: intake/assignment, review/information/amendment, deadline/escalation, transfer request/accept/reject/cancel/expiry, resolution/disposal/reopening, human pair/identity/group decisions and scheduling/reporting. Every command checks authority, permitted source state, inputs and expected versions; business audit/outbox commits atomically. Invalid/stale/racing commands have executable rollback/race evidence. External communication/import adapters remain unconnected. Exact contracts are backend/app/workflows.py, coordination.py, scheduling.py and reporting.py.')
    }
    for name, (heading, intro) in replacements.items():
        chunks = (ROOT/name).read_text(encoding='utf-8').split('\n\n', 2)
        write(name, heading+'\n\n'+intro+'\n\n'+chunks[2])
    name = ROOT/'docs/ACCESS_MATRIX.md'
    text = name.read_text(encoding='utf-8').replace('Password hashing library and exact session settings will be selected and tested during Stage 2.', 'Argon2id and eight-hour server-side sessions with HttpOnly/SameSiteStrict local cookies are implemented; secure-cookie deployment remains unverified.').replace('Stage 7 must test every role × surface above, including direct guessed IDs and attachment bytes. Stage 2 must already deny unauthenticated and out-of-scope reads/writes.', 'Stage7/9 tests exercised every seeded role across direct case/bytes/search/matching/notifications/counts/exports, including expired/no sessions.').replace('Metadata grants, transfer receiving authority and who can approve disposal/reopening remain proposed (Q04–Q07).', 'Implemented synthetic delegations remain policy proposals requiring real stakeholder approval (Q04–Q07).')
    name.write_text(text, encoding='utf-8')
    name = ROOT/'docs/DATA_MODEL.md'
    name.write_text(name.read_text(encoding='utf-8').replace('Actual HTTP contracts and concurrency evidence must be implemented in Stage 2/3, not inferred from this text.', 'HTTP/concurrency evidence is in stage9-tests.xml; documentation alone is not runtime evidence.'), encoding='utf-8')
    name = ROOT/'docs/WORKFLOWS.md'
    name.write_text(name.read_text(encoding='utf-8').replace("Intake requires confirmed institution selection in Stage 2's minimal path; broader imports may preserve UNRESOLVED/AMBIGUOUS identity until Stage 4 human review.", 'Intake requires explicit canonical selection; ambiguous alias/location evidence requires authorised identity review. No broad external import adapter is connected.'), encoding='utf-8')
    name = ROOT/'PLAN.md'
    old = name.read_text(encoding='utf-8')
    name.write_text('# Execution status\n\nStages1–9 local technical gates passed; source/policy and human-study limits remain explicit. The user authorised all remaining phases on27October2026. Each slice was inspected, implemented and checked before moving on. See PROJECT_STATE.md, docs/PHASES_3_TO_9.md and docs/ACCEPTANCE.md for current evidence.\n\nThe original plan below is retained as the historical design/sequence, not a current feature-status report. Proposed PostgreSQL was replaced by verified local SQLite (D24); all later local modules now exist. Independent human review and official alignment remain unverified.\n\n'+old, encoding='utf-8')
    name = ROOT/'DECISIONS.md'
    name.write_text(name.read_text(encoding='utf-8')+'''

## Final execution decisions, 27 October 2026

Earlier stage-specific availability statements above are historical. Current evidence is in PROJECT_STATE.md.

| ID | Implemented decision | Evidence / boundary |
| --- | --- | --- |
| D27 | User authorised completion of Stages3–9; retain phase gates | PHASES_3_TO_9.md records pre-edit gaps and checks; no external/production authorisation inferred |
| D28 | Keep baseline, disable web character-vector option | Frozen identical-heldout comparison showed equal recall and slower vector timing; retain research runner/cache for reproducibility; no semantic model connected |
| D29 | Current-state cohort reports and separately counted period events | Report tests distinguish cohort rate from disposal/new-receipt ratio; no historical-state reconstruction claim |
| D30 | New marked context is the non-destructive reset | Same key reuses state; new key creates a separate context. No complaint/context deletion; distinct sessions and isolated business clock |
| D31 | Verify SQLite backup plus private bytes and restore into a new context | Actual eight-case source and restored rows/history/hashes match; copied sessions revoked; source preserved |
| D32 | Terminal pair decisions survive workflow-only version changes when evidence is unchanged | Source content fingerprint is compared; material changes create linked review; regression passed |
| D33 | Record delegated human checks as unperformed | User chose “do whatever sounds vest fit”; no comprehension answer or independent label annotation was supplied. Agent exercise of authorised synthetic controls is not a human study |
| D34 | Use same-tab printable report and safe return link | Actual IAB print rendered seven scoped metadata rows and returned to filters; browser/report tests passed |
| D35 | Define release by source hashes/capture dates | No Git initial commit; release-manifest.json records real files/captures without invented revision IDs |
''', encoding='utf-8')
    name = ROOT/'docs/PHASES_3_TO_9.md'
    old = name.read_text(encoding='utf-8')
    old = old.split('\n## Stages 5–9\n')[0]
    name.write_text(old+'''

## Stage 9 — local technical gate passed

Implemented guarded new contexts/session realms, CLI and marked-context settings operations, private SQLite+file backup/restore, non-destructive storage audit, verified service helper, fresh dependency check, complete browser/automated repeat and module/demo guides. Human comprehension/independent-label evidence remains explicitly unperformed, following the user's delegated-choice reply.

Final full suite72passed; seven-report-test follow-up passed; TypeScript/Vite31modules passed. Fresh npm ci/build and fresh pinned Python install/pip-check/migrate/seed/startup passed. Actual browser intake created4separate records, transfer source/acceptance, pairRELATED/INDEPENDENT and institutionalPLANNED lead/next action,120hour isolated clock/worker/acknowledgement and7rowM-onlyCSV/print. Actual UI/API/worker stop/restart preserved8records/session/history/bytes/decisions/plan/notifications. Original5records and zero clock offset remained. A second automated7case context passed creation/review/plan/clock/export/newapplication restart. Actual8case backup/restore matched rows/originals/history/private hashes in a new context; source unchanged, zero deletions.

Fixed a terminal-decision stale-state bug exposed by workflow-only version changes, rendered preserved identity history, hardened worker retry behavior and corrected print navigation/filter return. A fresh-type-build failure was fixed with pinned Node types earlier; final build passes. Restricted TestClient socket initialization hung and was interrupted; the permitted loopback repeat passed. Browser auto-review timed out once and the documented retry succeeded. No unfinished failed application assertion remains. Dependency warning, missing external/official/human evidence and production gaps are documented rather than labelled complete.

See evidence/stage9/release-summary.json, browser-final.json, ui-rehearsal.json, before/after-restart.json, repeat-recovery.json, clean-dependencies.json and docs/CHANGES_AND_COMMANDS.md. Actual native200% proof remains the Stage1 checkpoint; live Stage9 narrow/desktop/keyboard evidence is separate. Proposed3minute narration was prepared; no timed3minute success is claimed.
''', encoding='utf-8')
    print('Current release documentation reconciled; historical evidence preserved')


if __name__ == '__main__':
    main()
