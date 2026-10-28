# Persistent model and design contract

The local schema now implements institutions/aliases, original submissions, cases/complainant tokens, attachments, assignment intervals, actions/resolutions/transfers, identity decisions, coordination groups/participants/reviews, relationship suggestions/decisions, grants, sessions, audit/outbox, policy/clock/notifications and versioned research cache. Exact names/constraints are in backend/app/models.py and migrations. The tables below retain the design vocabulary: institution_resolution maps to IdentityDecision/CaseRecord, relationship_review to RelationshipSuggestion/RelationshipDecision, coordination_group to CoordinationGroup, assignment_history to Assignment. Optional production contact fields/import connectors are not implied. See MODULE_GUIDE.md and final evidence.

## Records and boundaries

| Entity | Important fields / links | Required invariant |
| --- | --- | --- |
| demo_context | id, synthetic marker, environment, isolated clock offset | Real contexts cannot use demo clock/reset routes |
| institution | id, canonical identifier, name, city, region_id, version, synthetic | Pune DEMO-INST-017 and Nagpur DEMO-INST-044 are different rows |
| institution_alias | institution_id, raw/normalized alias, location, provenance, confirmed_by/at, version | Model/name similarity cannot silently confirm an alias |
| institution_resolution | case_id, original text/identifier, candidates, outcome, confirmed identity, evidence, reviewer, time, version | UNRESOLVED/AMBIGUOUS/CONFIRMED are explicit; original institution text is retained |
| bureau / region | id, display name, synthetic | Allocation is an illustrative policy |
| user / role_membership | id, password hash, active state; role, bureau, region, validity | Scoped memberships; administration is separate from case access |
| session | token hash, user_id, expiry, revocation, CSRF protection metadata | Secure cookie/session design; no frontend role dropdown authentication |
| case_record | immutable id/public_id, source ID, received_at, original institution text, confirmed institution_id nullable, subject, description, category, incident dates, lifecycle, current_owner_id, current_bureau_id, last_action/at, next_action, due_at, due_version, escalation_level, version, synthetic, context_id | Exactly one accountable owner; no transfer/relationship/overdue value hidden in lifecycle |
| case_submission / amendment | case_id, immutable original payload; append-only corrected payload, reason, author/time, version | Original narrative and prior versions remain; no destructive merge |
| complainant | id, case_id, synthetic identity/token, restricted contact fields | Separate protected data class; excluded from ordinary logs and metadata projections |
| attachment | id, case_id, generated storage key, original filename, detected type, size, SHA-256, created_by/at, scan/status | Private immutable bytes; separately authorized download; size/type/signature validation |
| assignment_history | case_id, owner/bureau, effective_from/to, reason, actor, transfer_id nullable | Current owner agrees with last assignment interval; report event-time ownership retained |
| workflow_event | case_id, event type, before/after versions, actor, reason, structured changes, occurred_at | Append-only through APIs; committed with case change |
| information_request | case_id, request text, requested_by/at, response/evidence refs, status | Responses append records; external sending is not implied |
| resolution | case_id, disposal version, reason, evidence refs, authority, time | Reopening preserves every earlier resolution |
| transfer | case_id, source owner/bureau, target officer/bureau, request reason/time, status, expected versions, outcome actor/reason/time, expires_at | At most one PENDING per case; owner changes only on atomic acceptance |
| escalation_event | case_id, policy/version, level, reason, actor/job, time | Escalation does not change owner/lifecycle automatically |
| relationship_suggestion | canonical ordered case pair, proposed label, source versions, evidence fingerprint, rule/model version, supporting/conflicting/missing facts, status, prior_suggestion_id | Unique same pair/version/fingerprint/method; historical disposed candidates allowed |
| relationship_review | suggestion_id, CONFIRM/REJECT/DEFER, confirmed label nullable, reason, actor/time, version | Reviewed relationship is distinct from identity and coordination; no case deletion |
| coordination_group | institution_id, condition_active, review state, lead bureau/officer nullable, next action/due_at, version | One current group per institution/context; deterministic detection does not appoint lead or confer evidence access |
| coordination_participant / review / task | group_id, case_id, joined/left; decision reason/actor/time; task owner/bureau/action/due/state/version | Case ownership remains independent; membership/events retained when condition ceases |
| access_grant | principal, resource, data class, operations, scope, expiry, granted_by/reason | Case relationship/group membership does not itself grant narrative/identity/attachment access |
| deadline_policy | version, configured windows, scope, effective dates, synthetic/proposed flag | No invented official period; deadline edits record reason and due_version |
| notification / delivery / acknowledgement | recipient, type, authorized minimal payload, resource refs, dedup key, policy/due versions, delivery state, attempts, acknowledged_at | No alert floods on retries/restart; permission rechecked on delivery/read |
| outbox_job | event key, source entity/version, type, payload refs, available_at, lease, attempts, result/error | Durable retry with unique idempotency keys; no narrative in ordinary job logs |
| source_import | source adapter/type, external id, content hash, provenance, synthetic, import key | Unique source+external-id+revision; never imply official integration |
| model_cache / evaluation_label | model/input/source versions, cached result; separate ground truth corpus/split | Labels unavailable to matcher; no metric until measured |

## Transaction and storage contracts

Create-case transaction validates the session/scope, institution selection, required fields and owner, inserts original submission, case, complainant, initial assignment, audit event and outbox entry, then commits before reporting success. Evidence uploads first enter private staging; commit attachment metadata only after durable object creation and validation. A failed transaction must not expose orphan bytes; a persistent cleanup job can remove unattached staging objects. Persistent files are not stored in an ephemeral build directory.

Every update carries an expected entity version. Use a conditional write/row lock and a transaction covering coupled case, assignment, transfer, review, event and outbox records. A stale version returns 409 with authorized reload/compare details. Invalid input returns 422; forbidden commands return 403; inaccessible object reads use a consistent non-disclosing 404 policy; unauthenticated requests return 401. No partial success on audit failure. HTTP/concurrency evidence is in stage9-tests.xml; documentation alone is not runtime evidence.

Transfer acceptance locks/checks both case and pending transfer, validates target authority and eligible target owner, changes the current owner/bureau and assignment interval, marks ACCEPTED, records audit/outbox and versions together. Unique constraints prevent multiple pending transfers; no deadline/received_at/ID rewrite. Bulk operations must not bypass version/audit policy.

Institution identity can change only through a versioned identity review preserving previous resolution and provenance. Re-evaluate affected coordination/suggestions via outbox. A rejected suggestion at the same source versions/fingerprint remains rejected; changed input creates a new review item linked to the earlier one. Human-reviewed facts are never overwritten by a worker.

Scoped views derive timelines from events/assignments/reviews and disclose only permitted fields. Internal processing access is separately granted and cannot bypass response projection. Audit is append-only through application APIs, not absolutely tamper-proof against a privileged database operator.
