# Decisions and unresolved policies

All policies below are **student-prototype proposals requiring stakeholder approval for real use**. They are not official AICTE rules. Engineering may proceed with labelled synthetic data.

| ID | Decision | Reason / boundary |
| --- | --- | --- |
| D01 | Start at Stage 0; finish one stage per requested increment | Empty repository; no existing working architecture |
| D02 | Keep institution resolution, complaint relationship, case assignment and coordination assignment as separate records | Same institution never proves duplication; coordination never transfers ownership |
| D03 | Preserve original submissions, IDs, attachment objects and previous decisions | Corrections append amendments/events; no complaint merge/delete endpoint is planned |
| D04 | Every case has an accountable officer and bureau from creation | Intake officer is initial owner; permission-checked reassignment/accepted transfer changes that owner |
| D05 | Pending/active means lifecycle other than DISPOSED | UNDER_REVIEW is a subset; transfer, escalation and overdue are independent dimensions |
| D06 | Source owner remains until an authorized receiver accepts a transfer | Reject/cancel/expiry preserve source owner, case ID, received time and due time |
| D07 | Confirmed institution + active cases in at least two distinct current bureaus creates a coordination item | Deterministic, independent of relationship label, evidence similarity or model availability |
| D08 | A relationship suggestion has a separate reviewed decision and source versions/fingerprint | Rejection survives retries/restart; material new evidence makes a new item referencing prior decisions |
| D09 | AI is optional and suggestion-only; no tool/action permissions | Validate evidence references and schema in backend; no automatic adjudication, case merge, disposal, transfer or permission change |
| D10 | Deny by default; separate metadata, narrative, identity and attachment grants | Administrator and management roles do not imply unrestricted complaint access |
| D11 | Case mutations, audit, versions and persistent outbox entries commit atomically | Rollback leaves no partial business change or misleading success |
| D12 | Store UTC instants; display/report in Asia/Kolkata with explicit cutoff | Reporting intervals are half-open [start, end); no official working-day policy assumed |
| D13 | Overdue = active and due_at < as_of; equality is not yet overdue | Null due_at is 'No deadline set', excluded from overdue/approaching counts and shown separately |
| D14 | No fixed official disposal period; illustrative rules must carry a policy version and synthetic label | Deadline windows/pauses/extensions need authorized policy validation |
| D15 | Cohort disposal rate uses distinct currently disposed cases in a received-date cohort / all distinct cases in cohort | Empty denominator displays N/A; reopened cases are pending at cutoff |
| D16 | Default stack is React/TypeScript + FastAPI + PostgreSQL + private files + database jobs | Versions and database availability await implementing-phase verification; no installed framework claim |
| D17 | Stage 1 is a labelled preview; workflow success requires backend transaction from Stage 2 onward | No local-state decision/create success can be presented as a working workflow |
| D18 | Reset/time travel are explicit isolated synthetic-demo operations | Require environment guard plus database demo marker/allowlist; no arbitrary database reset or host-time edits |
| D19 | No external integration is implemented | Synthetic import/local test inbox, if later built, must show adapter type, source and delivery state |
| D20 | Use incident-family/template grouped evaluation and a separate unseen-institution set | No cross-split incident leakage; held-out query still has its matching gallery case |
| D21 | Stage 1 uses React 19.3.1, TypeScript 7.0.2, Vite 8.3.5 with exact lockfile | Installed from npm; actual build evidence in docs/evidence/stage1-commands.md; no backend dependencies added |
| D22 | G1 required actual 200% zoom; this gate is now satisfied | Earlier attempts were interrupted/rejected. After Samanvay-only-window authorisation, native Chrome showed 200%, DPR doubled, 14 screens and keyboard flow passed; zoom restored. Historical attempts remain recorded |
| D23 | Make narrow notifications wrap actions below their content and give tables explicit keyboard scrolling | Supporting review found squeezed notification text and nonmoving ArrowRight input; verified the fixes without adding workflow state |

| D24 | Stage 2 uses persistent SQLite through SQLAlchemy/Alembic for the loopback demo | PostgreSQL18 files were found but no usable initdb/pg_ctl/server credentials/connection were verified. SQLite is a deliberate local architecture change, not an in-memory substitute or PostgreSQL claim. PostgreSQL migration/concurrency must be tested before deployment |
| D25 | Separate persistent workspace from fixture-only reference with `?preview=1` | Default UI requires real server sign-in and commit; the reference preserves later-screen illustrations with no saves. Public demo accounts/HTTP cookies are local-only; no production environment is supported |
| D26 | Complete G1/G2 after the user requested Stages1–2 | Native200% and 14screen keyboard/reflow checks close G1. UI intake, actual service restart, DB/file agreement, scoped denial and 16passing tests close the bounded G2; later workflow/security/evaluation gates remain open |

## Unresolved inputs

| ID | Question / missing evidence | Effect and responsible human |
| --- | --- | --- |
| Q01 | Exact official PS 26264 title/text, competition year and current clarification | Product lead/SPOC obtains authorized page/export; engineering scope remains provisional |
| Q02 | Current template/version, submission format, deadline, duration, judging weights and AI disclosure rules | SPOC supplies round instructions; do not invent limits or weights |
| Q03 | Missing brief cited by guide as `Pasted text(20261027-110839).txt` | Team provides it if distinct; no claim of coverage of unseen requirements |
| Q04 | Who may see cross-bureau metadata, identities and evidence; regional boundaries | Authorized stakeholder approves matrix/grants before real data |
| Q05 | Who may confirm identity/aliases, relationships and coordination lead | Proposed scoped supervisor/coordinator; human authority must be validated |
| Q06 | Receiving officer vs receiving supervisor acceptance, delegation, transfer expiry/cancellation policy | Prototype restricts to named target supervisor assigning an eligible officer, or named target officer; validate before pilot |
| Q07 | Disposal/reopening authority, evidence, retention and any pause/extension rules | Proposed supervisor/competent authority; no statutory timetable or retention invented |
| Q08 | Relationship annotation policy, complainant tokenization and multilingual requirements | Domain reviewers validate DUPLICATE/RELATED/INDEPENDENT/UNKNOWN and language coverage |
| Q09 | Approved integration APIs, identifiers, import provenance and permitted data | No restricted systems queried; adapters remain proposed |
| Q10 | Team members, time budget and machine memory | Team assigns named owners to workstreams; OS/memory CIM access was denied |
| Q11 | PostgreSQL installation/connection and compatible dependency versions | Implementer verifies before Stage 2; not a Stage 0 or labelled UI blocker |

## Official-source verification attempt

On 27 October 2026 (Asia/Kolkata), browser retrieval of the [SIH problem portal](https://www.sih.gov.in/sih2026PS) and [2026 College SPOC guideline PDF](https://www.sih.gov.in/letters/SIH2026-Guidelines-College-SPOC.pdf) returned HTTP 403. A `site:sih.gov.in "26264" "Institution"` search returned no results. These observations establish an access limitation, not that a statement or competition is absent. No authoritative identifier/year/title/submission constraints were confirmed. The guide's research and any independent mirror are not substituted for official confirmation.


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
