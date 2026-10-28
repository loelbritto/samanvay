# Module and data-flow guide

Current brand pass: `shared/Brand.tsx` owns the custom mark; `design-system/desk.css` owns task-focus and brand components; `features/workspace/InstitutionConnections.tsx` and `connection-model.ts` present authorised saved institution plans without changing ownership. `FocusCase.tsx` uses the supplied context clock. `app/WorkspaceBoundary.tsx` provides load/render recovery. Logo exports and concept gallery are in `frontend/public/brand/`. See [current report](BRAND_REDESIGN_20261028.md).

Current architecture: [28 October report](ARCHITECTURE_REDESIGN_20261028.md). Live session/navigation/shell are in `frontend/src/app/`; case and institution pages are in `features/`; primitives/resource hooks are in `shared/`; `design-system/` owns live tokens/CSS. `screens/LiveScreens.tsx` is a compatibility export file. The static preview loads independently.

`backend/app/domain/case_actions.py` owns pure decisions; `application/case_actions.py` owns the use case and repository port; `infrastructure/case_actions.py` owns SQL persistence. `case_views.py` projects authorised responses; `workspace.py` selects the queue before display pagination. Existing transfer/coordination/reporting services remain in place. The table and browser observations below describe the earlier release.

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
