# Project state

**Current: 28 October 2026 identity and workspace revision.** Custom two-part S logo, six vector concepts, outlined Manrope wordmarks, self-hosted type, warm ivory/teal interface, earliest-due case focus and an interactive view of saved shared institution plans are implemented. Compact/full selection and focus handling were corrected in source review. Build and 18 frontend tests passed; 20 static colour pairs passed. Existing complaint/domain records and private bytes are unchanged, as are backend source hashes. No backend regression rerun or browser result is claimed for this frontend-only pass.

**Browser acceptance is OPEN.** Saved origin policy remains unresolved; current desktop/mobile/supporting-screen rendering, keyboard flow and actual 200% zoom remain unverified. Next: restore effective tool access, capture and review the live screens, then rehearse mutations in a separate synthetic context. Previous browser results are historical. The prototype remains synthetic, with no official integration or SIH judging claim.

[Current changes and evidence](docs/BRAND_REDESIGN_20261028.md) · [Architecture revision](docs/ARCHITECTURE_REDESIGN_20261028.md) · [Design system](DESIGN.md).

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
