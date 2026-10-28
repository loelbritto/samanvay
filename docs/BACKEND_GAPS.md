# Current limitations after local Stages 1–9

28 October architecture update: case actions now have separate domain, application and SQL adapter boundaries; the queue covers the full authorised population before limiting display. Transfer, identity, scheduling, matching and reporting retain their existing service modules. This is an incremental modular-monolith refactor, not a completed production architecture migration. Current browser acceptance is OPEN because saved origin policy still blocks inspection. The historical browser checks below do not validate the new interface. See [current report](ARCHITECTURE_REDESIGN_20261028.md).

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
