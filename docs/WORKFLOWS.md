# Workflows and calculations

The command tables describe the implemented local workflow policy: intake/assignment, review/information/amendment, deadline/escalation, transfer request/accept/reject/cancel/expiry, resolution/disposal/reopening, human pair/identity/group decisions and scheduling/reporting. Every command checks authority, permitted source state, inputs and expected versions; business audit/outbox commits atomically. Invalid/stale/racing commands have executable rollback/race evidence. External communication/import adapters remain unconnected. Exact contracts are backend/app/workflows.py, coordination.py, scheduling.py and reporting.py.

## Independent dimensions

Lifecycle: RECEIVED, ASSIGNED, UNDER_REVIEW, AWAITING_INFORMATION, DISPOSED. Pending/active = every state except DISPOSED. Owner: exactly one current officer and bureau. Transfer: PENDING, ACCEPTED, REJECTED, CANCELLED, EXPIRED, or no transfer. Escalation: policy-defined level plus event history. Overdue: a computed condition, never a lifecycle. Institution resolution and reviewed complaint relationship are separate again.

## Case commands

| Command | Source → target lifecycle | Authority | Required inputs and effects |
| --- | --- | --- | --- |
| create/import | new → RECEIVED | Officer with intake scope; import requires delegated adapter permission | Received time, original institution text, subject/description/category, eligible initial owner, next action; optional deadline explicitly marked missing; immutable original/evidence provenance; case+assignment+event transaction |
| assign | RECEIVED/ASSIGNED/UNDER_REVIEW/AWAITING_INFORMATION → ASSIGNED | Scoped bureau supervisor | Eligible officer in same bureau, reason, case version; assignment history; cross-bureau movement must use transfer |
| begin/resume review | RECEIVED/ASSIGNED/AWAITING_INFORMATION → UNDER_REVIEW | Current owner or delegated supervisor | Action reason, version; satisfy response validation when resuming information request |
| request information | UNDER_REVIEW → AWAITING_INFORMATION | Current owner or delegated supervisor | Information needed, next action, reason; recorded request; no unapproved external message |
| append information/amendment | Any existing lifecycle → same lifecycle | Current owner/delegated editor with field/evidence permission | Original remains, amendment/evidence provenance, version; disposed records remain disposed unless reopened |
| set next action / due date | Active → same lifecycle | Current owner for next action; supervisor with policy authority for deadline changes | Reason, version, action; policy/version for deadline edits; recompute reminders using new due_version |
| escalate | Active → same lifecycle | Delegated supervisor/competent authority; policy worker may record a configured alert escalation | Level, reason/policy, version; no owner replacement |
| dispose | Active → DISPOSED | Scoped supervisor/competent authority with disposal delegation | Resolution record, reason, permitted evidence references, version; disallow PENDING transfer until resolved/cancelled |
| reopen | DISPOSED → UNDER_REVIEW | Competent authority with scoped reopening delegation | Reason, new next action, explicit due-date policy/review if needed, version; preserve all disposal records |

Intake requires explicit canonical selection; ambiguous alias/location evidence requires authorised identity review. No broad external import adapter is connected. No destructive delete/merge command is proposed. A relationship confirmation never disposes a complaint.

## Transfer commands

| Command | Source transfer → target | Authorized actor and guards | Ownership effect |
| --- | --- | --- | --- |
| initiate | none/terminal → PENDING | Active case owner or delegated supervisor; named eligible target officer/bureau, reason, future expiry if configured, expected case version; one pending transfer maximum | Source stays accountable |
| accept | PENDING → ACCEPTED | Named target officer or named target supervisor with receiving delegation and eligible designated owner; expected case+transfer versions; unexpired and active | One transaction changes owner/bureau, assignment interval, versions, outcome, event and outbox |
| reject | PENDING → REJECTED | Named receiving officer/supervisor, reason, expected versions | Source unchanged |
| cancel | PENDING → CANCELLED | Source requester or source supervisor, reason, expected versions | Source unchanged |
| expire | PENDING → EXPIRED | Database-backed job using explicit policy and isolated context clock; version/lock; at now >= expires_at | Source unchanged; notify appropriate scoped recipient |

Already-terminal transfer commands fail without a second assignment/event; idempotency keys may return the recorded result. Accept/reject/cancel/expiry races have one winner; stale contender gets a conflict. No transfer command changes received time, deadline, lifecycle or case ID. Disposal while pending is rejected. Transfer expiry duration is unconfigured until labelled prototype policy is chosen.

## Identity, relationships and coordination

Resolve an exact selected canonical institution ID first, then normalized name/confirmed alias with address/city evidence. Name-only/abbreviation collisions are AMBIGUOUS and require scoped human confirmation; mismatching code and location needs review rather than silently overriding contradiction. Save original text, candidates, evidence, actor and confirmation provenance.

Relationship outcomes: DUPLICATE (same incident and substantially same complainant/request; synthetic receipt and token support review), RELATED (shared event but different complainants/remedies), INDEPENDENT (same institution, different faculty-salary vs fee-refund issue), UNKNOWN (missing/contradictory incident facts or insufficient evidence). These are proposed annotation policies. No outcome merges or discards cases.

Suggestion → CONFIRM with chosen label, REJECT with reason, or DEFER with missing-information/next-action reason; expected suggestion/source versions required. Review requires authorized pair evidence. Source change marks review evidence stale; same evidence fingerprint and versions cannot reset a rejection. New material evidence creates a new linked review item retaining earlier decisions. Method scores rank candidates and are not calibrated probabilities. Human decisions and generated suggestions are stored separately.

For each confirmed institution, count distinct current bureaus with active cases inside the processing service's authorized scope. At two or more, upsert a unique coordination item labelled **Shared institution — coordination required**, even for INDEPENDENT cases and with semantic services disabled. Unresolved identities, one bureau, and disposed-only participation do not satisfy the rule. Re-evaluate after intake, identity review, accepted transfer, disposal and reopening using persistent jobs. Human-confirmed relationship is not a precondition for this item.

Group review states: REVIEW_REQUIRED → IN_REVIEW → PLANNED → RESOLVED. Explicit scoped coordinator decisions require reason, lead bureau/officer where assigning action, next action/deadline, and group version. DEFER retains review state and records reason/next review time. A coordinator may reopen RESOLVED → IN_REVIEW with reason. When the deterministic condition ceases, set `condition_active=false` and retain participants/review history; do not silently erase or human-resolve outstanding work. A later recurrence reactivates the condition and queues review. Group task owner and case owner remain independent. Detection/relationships do not confer narrative or attachment grants.

## Deadline, notification and reporting definitions

All dates use UTC instants and displayed Asia/Kolkata boundaries. For an inclusive date-only expected disposal date, define due_at as the next local midnight and label that conversion. Overdue is `active AND due_at IS NOT NULL AND due_at < as_of`; exactly at the deadline is not overdue under D13. Approaching is `active AND 0 <= due_at - now <= configured_window`, with window/version explicitly labelled illustrative. Missing dates show 'No deadline set' separately. No invented statutory days, pauses or holidays.

Notification dedup key includes recipient, case/group, event type, policy version, threshold, source version where material, and due-date version. Persist delivery/acknowledgement and leases/attempts. Retry cannot overwrite a review or flood recipients. External email, if built, uses a labelled local test inbox; no real messaging is authorized.

Reports use [start, end) in stated timezone and cutoff. Total = distinct permitted case IDs in stated scope. Pending and disposed partition that population; under-review and overdue overlap pending. Case age = completed elapsed 24-hour days from received_at to as_of for active cases; disposed elapsed time uses resolution time and is separately labelled. Bureau defaults to current owner; event-time reports use assignment history and say so. Accepted transfer event counts are historical measures, not added to lifecycle totals.

Cohort disposal rate = distinct cohort cases currently DISPOSED at cutoff / all distinct cases received in cohort; empty cohort = N/A. Monthly disposals count distinct cases with disposal events in the month, with reopening and repeated events separately reported. Disposals in a period / new receipts in that period is a separate throughput ratio and can exceed 100%. Report filters, drill-down rows, chart counts and CSV/print use one scoped population and documented denominators. Never expose aggregate hidden-record counts.
