# Access policy and implemented local scope

This proposed policy is enforced through central policies.py plus scoped workflow/coordination capabilities. Owners/class grants, region/bureau metadata, separate pair/coordination authority, transfer receiver and disposal/reopen delegations, reports/bytes and administrator separation are implemented. A nine-role negative surface matrix passed in Stage7/9. Rehearsal scope explicitly grants Pune M-only to management and N/I to the coordinator without A; administration still grants no complaint access. The table is a design policy requiring stakeholder approval; broad account/grant administration is not implemented.

Data classes: **M** = approved coordination metadata (case ID, confirmed institution/city, bureau, officer, lifecycle, due date, next administrative action); **N** = narrative/category/source excerpts; **I** = complainant identity/contact/token; **A** = attachment metadata/bytes. Even M may reveal sensitive activity and requires explicit scope. Do not return redacted hidden-case counts, titles or hints that disclose unauthorized existence.

| Role | M visibility | N / I / A visibility | Case commands | Other authority |
| --- | --- | --- | --- | --- |
| RB officer | Assigned/explicitly granted RB cases; approved group metadata by grant | Assigned cases plus explicit class grants; attachments checked separately | Create with self as initial owner; assigned-case review/request-info; request transfer; submit proposed resolution | Review relationship only with explicit pair-review grant; no automatic coordination authority |
| PGRC officer | Assigned/explicitly granted PGRC cases; approved group metadata by grant | Same scoped rule as RB | Same assigned-case commands | Same pair-review restriction |
| Regional officer | Explicit regional case/group scope, intersected with delegation | Explicit case/data-class grants within permitted region | Create/act only as delegated owner; request transfer within delegated scope | No whole-country access from regional role |
| Bureau supervisor | Authorized own-bureau metadata; other bureau metadata by group grant | Explicit case/data-class grants; supervise own bureau without automatic I/A access | Assign eligible own-bureau officer; approve disposal; accept incoming transfer only as named receiver with eligible owner; reject as named receiver | Confirm identity/alias within delegated scope; escalate; grant review within own delegated authority |
| Coordinator capability | Specifically granted group M, in addition to another scoped role | Separate N/I/A grants per participating case | No case ownership, disposal or transfer authority from coordination capability | Confirm/reject/defer pair with review grant and authorized required evidence; appoint/change lead and tasks with group decision grant |
| Senior management / competent authority | Explicit aggregate and metadata scope | Separate per-case N/I/A grants | Authorized reopening/escalation/disposal only with explicit command delegation | Scoped reports; grant/revoke within delegated scope; no implicit universal case access |
| System administrator | Technical/account/policy metadata only | None by administration role | None by administration role | Manage accounts/configuration, audit technical actions; business authority needs separately approved role/grant |
| Background worker | Explicit service processing grants for eligible records | Minimum necessary processing fields | No human decision authority; deterministic group detection, jobs and notifications only | Cannot close/merge/transfer/adjudicate or broaden permissions; all viewer output filtered |

## Command and disclosure checks

| Surface | Required policy application |
| --- | --- |
| Detail, lists, institution timeline | Apply authorized record population and field projection before response; timeline cannot reveal hidden narrative/events |
| Create/update/assignment/transition | Validate role, scope, ownership/delegation, source state, reason/evidence and expected versions in backend |
| Pair review / AI evidence | Pair-review grant plus access to each cited field/version; if evidence is insufficiently permitted, route to authorized reviewer with minimal metadata |
| Coordination detection/display | Internal processing can detect cross-bureau condition; only approved scoped metadata reaches participants; detection does not silently issue content grants |
| Attachment upload/download | Separate case and A permission, content/type/size checks, private storage; no public path/static directory |
| Search/autocomplete/snippets | Apply scope before ranking, pagination, counts or snippets; no existence leaks |
| Dashboard/reports/CSV/print | Same authorized underlying population and field projection; denominator and drill-down agree |
| Notifications | Authorize recipient at creation, delivery and read; revoke visibility when scope changes; do not retain revealing snippets |
| Settings / audit | Technical administrator scope distinct from business policy authority; log significant access/configuration without raw narratives |

Sessions require established password hashing, token expiry/revocation, protected cookies, CSRF protection for cookie mutations, no secrets in logs, and explicit development gating of synthetic demo personas. Argon2id and eight-hour server-side sessions with HttpOnly/SameSiteStrict local cookies are implemented; secure-cookie deployment remains unverified. Any database row-level security is additional and must be tested as the actual application database role; none exists now.

Stage7/9 tests exercised every seeded role across direct case/bytes/search/matching/notifications/counts/exports, including expired/no sessions. Implemented synthetic delegations remain policy proposals requiring real stakeholder approval (Q04–Q07).
