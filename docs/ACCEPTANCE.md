# Acceptance gates and evidence

**Current: 28 October 2026 identity and workspace revision.** Custom two-part S logo, six vector concepts, outlined Manrope wordmarks, self-hosted type, warm ivory/teal interface, earliest-due case focus and an interactive view of saved shared institution plans are implemented. Compact/full selection and focus handling were corrected in source review. Build and 18 frontend tests passed; 20 static colour pairs passed. Existing complaint/domain records and private bytes are unchanged, as are backend source hashes. No backend regression rerun or browser result is claimed for this frontend-only pass.

**Browser acceptance is OPEN.** Saved origin policy remains unresolved; current desktop/mobile/supporting-screen rendering, keyboard flow and actual 200% zoom remain unverified. Next: restore effective tool access, capture and review the live screens, then rehearse mutations in a separate synthetic context. Previous browser results are historical. The prototype remains synthetic, with no official integration or SIH judging claim.

[Current report](BRAND_REDESIGN_20261028.md).

All fourteen scenarios below have executable evidence for the bounded synthetic local implementation. The observed-results index at the end maps each scenario to actual tests/browser/restart records. No live semantic model, independent human study, official alignment or production certification is claimed. Source audits, browser observations, automated tests and synthetic evaluation remain distinct evidence types.

## Stage gates

G0: complete supplied-source inventory and source hashes; map every non-heading staged-prompt line and guide section; separate official unknowns/design proposals; document model, permissions, transitions, ownership, conflicts and next small slice. Run `scripts/verify_phase0.py` and inspect its evidence output. This only verifies planning artifacts, not implementation or stakeholder approval.

G1: actual browser screenshots at 1440×900, 390×844 and 200% zoom; keyboard Overview → institution → evidence → timeline; readable labels/focus/overflow and loading/empty/error/retry/permission/stale states. Inventory every backend-pending control. No simulated persistent action success.

G1 status: **ready to close**. Desktop/narrow/supporting screens and actual native Chrome200% were inspected;14zoom routes passed scoped overflow/labels, focused keyboard actions scrolled into view and table keys worked. Zoom restored. See docs/STAGE1_UI.md and evidence/stage1-zoom/results.json. This is not a full accessibility certification.

G2 status: **ready to close for the local synthetic slice**. UI-created DEMO-20BF09829C05 survived actual API/frontend restart with the same original/owner/history/session/private bytes and actual counts. API/SQLite/file agreement and forbidden reads passed.16pytest tests passed with one dependency warning. See STAGE2_PERSISTENCE.md, evidence/stage2-tests.xml and evidence/stage2/after-restart-api.json. SQLite/public demo HTTP limits remain explicit.

G2–G9: use the corresponding PLAN.md stage gate and requirement records. Each feature needs an implemented test/manual procedure, command, environment, observed result and evidence location. Stage 7 audits authorization across all surfaces; security is required when each surface is introduced.

## Fourteen core scenarios from the available guide

| ID | Scenario / implementation stage | Expected observable result and necessary evidence |
| --- | --- | --- |
| A01 | Persistence / 2 | UI-create a unique synthetic case/evidence; refresh; stop/restart API and UI; authenticated API/UI retrieve same ID, owner and history; direct database row and byte checksum agree |
| A02 | Database totals / 2,3,6 | Create/dispose/reopen changes actual scoped query counts; verify stored rows, drill-down and mutually exclusive lifecycle totals |
| A03 | Shared institution / 4 | Two unrelated active cases at confirmed Pune institution in different bureaus produce one coordination item with no duplicate label; one-bureau/disposed-only/ambiguous counterexamples do not |
| A04 | Paraphrased duplicate / 5 | Same synthetic incident/request retrieves paraphrase with inspectable authorized references; record method/source versions; no automatic case action |
| A05 | Independent complaint / 4,5 | Faculty complaint remains INDEPENDENT while Pune institution coordination persists and every case/evidence survives |
| A06 | Name collision / 4 | Pune DEMO-INST-017 and Nagpur DEMO-INST-044 remain distinct; city/code contradictions and abbreviations trigger human review |
| A07 | Officer decision / 4,5 | Confirm/reject/defer reason, actor and source versions persist across refresh, repeated worker runs and restart; changed evidence creates linked stale/new review |
| A08 | Transfer / 3 | Rejection/expiry/cancel keep source; acceptance atomically assigns one target owner with same ID/deadline and complete history; unauthorized/racing accept fails |
| A09 | Reminder / 6 | Just before/at/after configured threshold creates one persisted scoped notification; repeat job/restart/acknowledge proves dedup and delivery state |
| A10 | Escalation / 3,6 | Just before/at/after due_at follows D13 and explicit policy; worker restart preserves result; no silent ownership change; isolated clock does not alter host/other context |
| A11 | Direct access / 2,7 | Every role attempts forbidden case and attachment IDs with authenticated/expired/no session; backend denies bytes/fields and leaves state unchanged |
| A12 | Export scope / 6,7 | CSV and printable report match authorized filters, records, fields and denominators; no hidden-row counts or sensitive snippets |
| A13 | AI failure / 5 | Disabled/failing semantic service displays unavailable state; baseline and deterministic coordination remain usable; unsafe/invented citations rejected; injection text remains evidence |
| A14 | Concurrent edit / 3,4 | Two commands at same version yield one success and one clear 409; no partial audit, lost decision or double transfer assignment; reload/compare route works |

Additional checks: original submission survives corrections; imported external IDs/idempotency preserved; session protections and malformed/type-signature/oversized uploads; worker leases/retries; no access implied by relationship/group membership/admin; demo clock/reset unavailable outside isolated demo; all visible controls work or show honest unavailability; labelled evaluation labels/splits cannot leak to matching inputs.

## Evaluation and release evidence

Stage8 generated and froze32fictional institutions,240synthetic cases,528pair labels and98identity queries. Family/template splits are isolated from model-visible cases; held-out retrieval galleries and unseen-institution inputs are preserved. The latest measured run is identified by evidence/stage8/latest.json, with raw classifications/rankings/errors, support/confusion/UNKNOWN, hardware and first/warm-pass latency.168held-out generated-policy pairs matched their labels;98identity expectations passed. Both retrieval methods measured recall@1=.6 and recall@3=1 on40queries; optional character vectors had no gain and are disabled in the application. No live semantic model or independently reviewed gold labels exist; these artificial metrics do not establish real accuracy. Failed HTTP/UI operations are documented separately rather than turned into an invented aggregate end-to-end accuracy metric.

Stage 9 requires an actual clean-reset/restart rehearsal, exact verified startup commands, labelled synthetic credentials, guarded reset, capture date/version on actual screenshots/video, team comprehension observations and unresolved limitations. Approximately three minutes is a proposed rehearsal length, not a verified official limit. Official template overrides provisional pitch packaging when available.

## Observed local results index

All test references below resolve in backend/tests and final JUnit evidence. Earlier phase JUnit files retain their historical counts. The final full suite and print follow-up counts are recorded in evidence/stage9/release-summary.json. These tests ran against separate synthetic databases; actual browser intake/service restart is separately evidenced.

| ID | Observed result and evidence | Scope |
| --- | --- | --- |
| A01 | stage9/ui-rehearsal.json, before/after-restart.json, service-processes-before/after.json:8same cases, session, originals, history and attachment hashes after actual API/UI/worker stop/restart. Stage2 original UI-created record retained | Passed local persistence |
| A02 | test_intake_preserves_originals_assignment_real_bytes_and_counts; test_disposal_counts_cohort_and_throughput_are_distinct; test_disposal_reopening_scoped_authority_retains_resolutions; actual management7rows/CSV | Passed scoped create/dispose/reopen/report counts |
| A03 | test_independent_relationship_does_not_remove_coordination_or_change_owners; test_group_state_version_lead_and_inactive_condition_keep_history; actual PLANNED Pune group | Passed deterministic multi-bureau condition; all cases retained |
| A04 | test_four_labels_paraphrase_contradictions_and_unknown_are_explainable; test_authorised_bounded_matching_includes_disposed_and_never_changes_case; evaluation raw held-out rankings | Passed baseline paraphrase/cited evidence; no live semantic claim |
| A05 | Actual faculty DEMO-436C0703134C / refund DEMO-79D983D2A10B confirmed INDEPENDENT while institutional plan stays active; test_independent_relationship_does_not_remove_coordination_or_change_owners | Passed separate relationship/coordination |
| A06 | test_exact_identity_location_collision_and_aliases_require_human_review; identity confirmation/provenance test;98synthetic identity expectations; browser directory shows distinct Pune/Nagpur | Passed exact/alias/city ambiguity policy |
| A07 | test_rejection_sticky_across_method_rerun_restart_and_changed_evidence; test_final_review_applies_to_unchanged_evidence_after_workflow_only_version_change; test_deferred_pair_can_be_reviewed_then_rejected_without_erasing_history; actual two final reviews retained after restart | Passed review/history/retry/staleness; fictional reviewer controls exercised by agent |
| A08 | test_transfer_reject_then_accept_preserves_deadline_identity_and_one_owner; test_cancel_expiry_boundary_and_disposal_while_transfer_pending; test_transfer_audit_failure_rolls_back_acceptance_owner_and_intervals; actual pending/accepted screenshots | Passed transfer lifecycle, recipient authority, atomic assignment/history |
| A09 | test_deadline_before_at_after_and_escalation_deduplicate_across_restart; test_persistent_delivery_acknowledgement_and_revoked_case_scope; crashed lease recovery; browser acknowledgement/restart | Passed persisted in-app reminders; no email |
| A10 | test_isolated_clock_keeps_host_other_context_and_stored_deadlines_unchanged; threshold/escalation test; actual120hour offset with unchanged owners/deadlines and primary contextoffset0 | Passed illustrative policy and isolated clock |
| A11 | Nine-role test_every_role_across_case_bytes_search_matching_notifications_counts_exports; no/expired session, expired grants, private path/upload/body-limit tests; actual running-security.json | Passed tested negative matrix; no production audit claim |
| A12 | test_filters_rows_csv_print_and_autocomplete_use_same_scope; formula/HTML escaping; disposal denominator tests; actual downloaded7rowM-onlyCSV and rendered HTML print/return link | Passed tested population/field/filter scope |
| A13 | test_strict_adapter_rejects_invented_excerpts_ids_versions_and_tool_calls; test_injection_is_source_data_and_outage_does_not_disable_coordination; actual semantic-unavailable notice | Passed disabled adapter, simulated adapter exception and unsafe-output/injection checks. No actual external model outage was induced |
| A14 | test_two_simultaneous_commands_have_one_winner; test_two_simultaneous_transfer_decisions_have_one_winner; test_simultaneous_pair_decisions_have_one_winner; stale group-source/physical ownership constraints | Passed one winner/409, rollback and current-source reload safeguards |

G3–G7 have passing implementation/race/surface checks. G8 has a reproducible frozen synthetic evaluation and the scenario index above; independent gold review is unperformed. G9 has an actual clean-context browser run and actual service restart, an automated second-context repeat/new-application restart, fresh dependency/startup checks, actual private backup/restore and module/runbook/capture hashes. Human comprehension and a measured three-minute run remain unperformed. The user delegated choices; no human-study result was invented. Local technical gates may close with those limits recorded; official/pilot approval remains a separate human gate.
