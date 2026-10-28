# Remaining-phase execution ledger

The user authorised completion of all remaining phases on 27 October 2026. Each gate is implemented and checked before moving on. Source documents remain reference requirements; no external integration, real-data use or official-policy authority follows from this request.

## Stage 3 — workflow gate passed

Pre-edit gaps: no review/information, disposal/reopening, transfer lifecycle or simultaneous command tests. Added workflow/capability/transfer/action/resolution tables and migration84165027696e; workflows.py; explicit synthetic supervisor delegations; action and transfer UI; scoped transfer inbox. Originals, identity and deadlines remain preserved. New audit/outbox rows commit with commands. Invalid source state, authority, evidence or versions reject without mutation. Disposal while transfer pending is rejected. Named receivers accept/reject; sources cancel; expiry retains source; acceptance atomically closes/opens one assignment interval.

Executed: Alembic revision/autogeneration and upgrade; add-only `app.seed`; `pytest` with fresh checked workspace basetemp and `--junitxml ../docs/evidence/stage3-tests.xml`; `npm.cmd run build`; owned loopback API restart. **23 tests passed, one dependency deprecation warning**. Tests include two simultaneous edits, competing accept/reject, expiry boundary and audit-failure rollback. Frontend TypeScript/Vite passed (28 modules). Browser saved a NEXT_ACTION on DEMO-20BF09829C05, now version2 with retained original/history; capture `docs/evidence/stage3/workflow.png`. Prior Stage2 evidence remains a historical checkpoint.

Stage3 does not send external information requests. Action text is recorded locally; a separate communication action is not simulated. Deadline/transfer limits are labelled illustrative, not statutory. Database/admin tampering resistance is not claimed.

## Stage 4 — identity / coordination / human-review gate passed

Missing persistent institution-resolution review, coordination groups/lead decisions/timeline and sticky relationship review. These are next. Detection must depend on confirmed identity and concurrent current bureaus even when cases are independent. Group metadata grants, pair evidence grants and individual ownership remain separate.

Implemented these gaps in coordination.py, models/migrationd3dda6dae075, explicit scoped synthetic coordinator grants, institution identity/timeline and coordination/evidence-review UI. Original identity text survives a corrected canonical selection. Concurrent bureau conditions and retained group work are separate; explicit metadata grants do not grant N/I/A. Pair review requires separate delegation and M/N/I access to both sources. Confirm/reject/defer decisions are append-only; terminal decisions remain for unchanged content across method reruns; changed content creates a linked review.

Executed migration/seed, integrity/domain worker once, owned API restart, full pytest and frontend build. **29 tests passed, one dependency warning** (`stage4-tests.xml`); TypeScript/Vite passed,29modules. Browser coordinator created/rejected a source review, reloaded and observed the same rejection with decision disabled (`stage4/browser.json`, rejected-review.png). Tests verify independent complaints retain coordination, ambiguous cities/aliases require review, corrected identities preserve original/provenance, group lead never changes case owners, inactive condition retains work, and forbidden viewers receive no pair/group disclosures.

## Stage 5 — matching gate passed (35 tests, one dependency warning; frontend build passed)

No candidate retrieval, explainable baseline, optional local vector comparison, strict model-output/citation validation or measured matching evaluation exists yet. No semantic model is connected. The next slice will add bounded authorised retrieval and suggestion-only evidence with explicit unavailable semantic status.

Implemented matching.py, structured optional incident facts and migrationabe1be3f646d, candidate retrieval UI, lexical-rules-v1 and cached hashed-character-ngrams-128-v1 comparison. Candidate selection applies M/N/I scope and confirmed institution before a50record bound; disposed cases remain eligible. DUPLICATE/RELATED/INDEPENDENT/UNKNOWN outputs cite exact excerpts/structured fields, conflicts and missing facts. Scores are ranking signals. Inputs over8000characters retain first/last4000 and flag truncation. The character encoder is statistical, not semantic AI; English rules and multilingual limitations are explicit. No paid/model dependency is required.

Strict optional-adapter validation rejects invented IDs/excerpts/field values/versions and action fields. Failure returns unavailable while rules/coordination continue. No actual semantic/LLM adapter is connected. Stage8 will compare the optional encoder on frozen synthetic inputs; no improvement is claimed now. Backward-compatible fingerprint handling preserves Stage4 rejections after schema changes. Browser retrieval returned2authorised candidates and retained the earlier REJECT (`stage5/browser.json`, matching.png). Final test/build results are recorded in stage5-tests.xml and the command output.

## Stage 6 — scheduling / reporting gate passed

Persistent notifications/delivery/acknowledgement, scheduled deadline policy, isolated demo clock, full scoped filter/report/CSV/print and administrative policy versions remain missing. These are next after the matching tests pass.

Implemented these gaps in scheduling.py/reporting.py, models/migration9be862270eb9, OperationsScreens and full list filters/pagination. Notifications retain pending/delivered/acknowledged state and leases; repeated runs/restarts deduplicate. Named transfer recipients have limited transfer notices without complaint narrative access. Illustrative approaching/overdue/escalation rules are versioned and audited. Clock controls require administrator plus an explicitly enabled marked database under .demo-contexts; host time, stored deadlines and other contexts remain unchanged. Business event timestamps follow context time; sessions retain wall-clock expiry.

One scoped query supplies list/report/CSV/print populations. Filters include names/IDs, bureau, region, permitted category, lifecycle and half-open received dates. Reports distinguish lifecycle partitions, current cohort disposal rates, period disposals/new receipts, ageing, monthly/quarterly activity and separately authorised relationship measures. CSV formula prefixes and print HTML escaping were tested. No backdated historical-state reconstruction is claimed.

Executed migration/seed, worker once and continuous worker, owned API restart, full pytest and frontend build. **42 tests passed, one dependency warning**, including before/at/after deadlines, repeated scheduler/restart, delivery/acknowledgement/revocation, export/population agreement, throughput200% example, policy conflicts and actual isolated-clock guard/isolation. A timestamp inconsistency was fixed and the42tests rerun with an exact business-event timestamp assertion. Browser reports showed5scoped rows and export links; notification acknowledgement persisted; normal-workspace clock guard was visible (`stage6/browser.json`, captures). Build passed,31modules.

## Stage 7 — scoped security / resilience audit passed

The assembled surfaces now need a role-by-surface negative matrix, actual unknown-length body protection, storage/path checks, significant access records, database uniqueness constraints and auxiliary resilience checks. Production certification, antivirus and PostgreSQL are outside this local prototype gate and will remain explicit limits.

Implemented request_limits.py, security_audit.py, migration2b8ec33456f0, SQL uniqueness for current assignments/pending transfers, constant-cost unknown-user password verification, explicit UI pair-delegation availability and Vite private-path restrictions. Access records hash resource paths and omit narratives/query terms/cookies/bytes. Business audit remains mandatory/transactional; auxiliary access logging is best effort during database failure. Chunked/unknown-length bodies are counted before parsing, capped16MiB; upload caps remain separate.

**60 tests passed, one dependency warning** (`stage7-tests.xml`), including the nine-role matrix across direct case/bytes/search/autocomplete/matching/notifications/counts/CSV/print, expired sessions/grants, malformed multi-file requests, physical ownership constraints, persistent login throttle, simultaneous scheduler dedup and crashed delivery/integrity lease recovery. Actual matrix is `stage7/surface-matrix.json`. Build initially failed because Node types were absent for Vite configuration; installed exact @types/node26.6.5 and build passed (31modules). An automatic build-review timeout was retried once successfully; it was not a safety rejection.

Running-service smoke script `scripts/verify_running_security.py` passed: unauthenticated surfaces401, wrong-origin login403, existing private SQLite/backend files via Vite403, all5complaints retained, private-byte checksum and significant-access records verified. See `stage7/running-security.json`. No PostgreSQL/RLS, antivirus, tamper-proofing or production security certification is claimed.

## Stage 8 — reproducible synthetic evaluation gate passed

No frozen200–300case corpus, grouped splits/isolated labels, held-out comparison, raw error/latency results or complete acceptance mapping exists yet. The next slice generates a labelled synthetic research corpus independently from the working demo and measures both implemented methods on identical held-out inputs. Difficult-label independent human review remains an explicit unperformed item until someone supplies it.

Added evaluation/generate.py and run.py, immutable corpus-v1 (240cases,32institutions,528pairs,98identity queries), evaluator-only labels and family/template split groups, known/unseen held-out galleries, actual raw classifications/rankings/errors/timings and source/input hashes. `evaluation/README.md` explains the artificial structured-fact benchmark and limits. Both commands ran twice; frozen hashes remained identical. The final comparison selected the baseline: both methods recall@1=.6/recall@3=1 on40queries; the optional cached character encoder had no gain.168held-out pair labels and98identity expectations matched the generated policy; this does not establish real accuracy or semantic understanding. No live semantic model is connected.

Fixed bounded API preselection so explicit incident references can retain older disposed cases ahead of newer noise; tested55new unrelated records with the50candidate cap. Category/shared-incident contradictions now remainUNKNOWN. **62 tests passed, one dependency warning** (`stage8-tests.xml`). Independent human label review and representative usability remain unperformed; no human study is fabricated. The final fourteen-scenario evidence index will also include Stage9's clean-context/restart rehearsal.

## Stage 9 — current pre-edit gaps

Need non-destructive idempotent reset by creating a separate marked context, context-specific sessions, verified backup/restore, exact startup helpers, full clean-context rehearsal/restart/repeat, actual final captures/layout/keyboard review, module guide and evidence/requirements reconciliation. Every earlier complaint/context must remain preserved. Official submission constraints and human comprehension/label review still require actual human evidence.


## Stage 9 — local technical gate passed

Implemented guarded new contexts/session realms, CLI and marked-context settings operations, private SQLite+file backup/restore, non-destructive storage audit, verified service helper, fresh dependency check, complete browser/automated repeat and module/demo guides. Human comprehension/independent-label evidence remains explicitly unperformed, following the user's delegated-choice reply.

Final full suite72passed; seven-report-test follow-up passed; TypeScript/Vite31modules passed. Fresh npm ci/build and fresh pinned Python install/pip-check/migrate/seed/startup passed. Actual browser intake created4separate records, transfer source/acceptance, pairRELATED/INDEPENDENT and institutionalPLANNED lead/next action,120hour isolated clock/worker/acknowledgement and7rowM-onlyCSV/print. Actual UI/API/worker stop/restart preserved8records/session/history/bytes/decisions/plan/notifications. Original5records and zero clock offset remained. A second automated7case context passed creation/review/plan/clock/export/newapplication restart. Actual8case backup/restore matched rows/originals/history/private hashes in a new context; source unchanged, zero deletions.

Fixed a terminal-decision stale-state bug exposed by workflow-only version changes, rendered preserved identity history, hardened worker retry behavior and corrected print navigation/filter return. A fresh-type-build failure was fixed with pinned Node types earlier; final build passes. Restricted TestClient socket initialization hung and was interrupted; the permitted loopback repeat passed. Browser auto-review timed out once and the documented retry succeeded. No unfinished failed application assertion remains. Dependency warning, missing external/official/human evidence and production gaps are documented rather than labelled complete.

See evidence/stage9/release-summary.json, browser-final.json, ui-rehearsal.json, before/after-restart.json, repeat-recovery.json, clean-dependencies.json and docs/CHANGES_AND_COMMANDS.md. Actual native200% proof remains the Stage1 checkpoint; live Stage9 narrow/desktop/keyboard evidence is separate. Proposed3minute narration was prepared; no timed3minute success is claimed.
