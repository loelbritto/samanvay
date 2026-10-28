# Samanvay identity and workspace revision — 28 October 2026

The user rejected the previous generic appearance and asked for stronger SIH presentation, a better logo and useful creativity. This revision implements a coherent identity and a new view of existing saved coordination data. It does not claim an SIH judging result, official endorsement or production readiness.

## Gaps inspected

The old brand reused the generic coordination icon. The blue/grey shell and uniform queue gave little visual explanation of Samanvay's purpose. Institution plans were available only inside the coordination workflow, and the sign-in screen explained little of the distinction between case ownership and shared coordination. Browser inspection was already blocked by a saved origin policy; that environmental condition has not changed.

## What changed

- **Custom identity:** a two-part S, selected from six original geometric concepts. Its two channels remain separated. The lowercase outlined Manrope wordmark adds a clay period. SVG and transparent PNG exports, provenance and an interactive concept gallery are included.
- **Visual system:** self-hosted Manrope, warm ivory surfaces, light navigation, deep teal task emphasis, consistent controls and a restrained clay brand accent. Fonts are served locally; no Google Fonts browser request is required.
- **Next case:** the earliest-due authorised complaint has a focused owner/next-step view. Other complaints remain below without duplicating that first record. Overdue labels use the API's context clock, not the device clock; closed records are never labelled overdue.
- **Shared plans:** select an authorised institution and see its saved coordination lead and next action connected to bureau-specific complaint-owner lists. Closed and historical participants remain accessible but do not inflate current open counts. Inactive plans are explicitly identified as retained. The selected institution survives compact/full switching, and expansion moves focus into the new view.
- **Useful navigation:** global complaint search, direct navigation to the selected institution plan, and a direct evidence-review link. The sign-in page explains separate complaint ownership with an explicitly labelled illustrative diagram.
- **Recovery:** a failed app module/render now leaves a reload control and a truthful unsaved-change message instead of an empty workspace.

The new shared-plan view consumes the existing `/api/coordination` response. That endpoint withholds a group if the viewer cannot access every participant's metadata. The frontend does not reconstruct partial hidden groups from case lists. Case ownership, institution identity, relationship decisions and coordination leadership remain separate. Automated connections still require authorised human review.

## Research used

The [r/UXDesign dashboard discussion](https://www.reddit.com/r/UXDesign/comments/18liurr/what_important_things_should_i_consider_in/) informed the attention → context → responsible person hierarchy. The [r/UX_Design critique](https://www.reddit.com/r/UX_Design/comments/1o39xrm/just_finished_designing_a_clean_ecommerce/) reinforced clear colour roles and less redundant interface chrome. These are community opinions, not user evaluation or SIH criteria.

The [GOV.UK task-list guidance](https://design-system.service.gov.uk/components/task-list/) supports explicit task names and readable statuses. We borrowed those interaction principles without imitating an official government identity. A [hackathon demo discussion](https://www.reddit.com/r/hackathon/comments/1ttu2wu/we_turned_our_hackathon_demo_into_an_opensource/) inspired showing a real saved workflow as the distinctive demonstration moment; no claimed judging benefit was inferred.

## Verification

- Production TypeScript/Vite build passed: 61 modules; separate historical preview and live assets; four local Manrope font weights.
- **18 frontend tests passed**, including grouping without record loss, retained historical/closed participants, input immutability, independent owners and context-clock overdue logic.
- **20 selected static text/background combinations passed 4.5:1**. This is source-value calculation, not computed browser contrast or certification.
- One Impeccable detector run returned `[]` before the final small recovery/focus/narrow-brand follow-ups; no second detector pass is claimed.
- **11 SVGs** passed XML checks; six distinct concepts and six transparent PNG exports were checked. Selected standalone 16px/128px marks and final wordmark were visually inspected as artwork. This is not website rendering evidence.
- Source review found and resolved lost institution selection and compact-to-full focus handling. The reviewer found no remaining P1/P2 issues in the reviewed source; this is not visual approval.
- Read-only before/after comparison covers both existing contexts, selected complaint/domain history tables and private evidence bytes. See `preservation-result.json` for the observed result. Backend source hashes are compared explicitly in `verification.json`.
- Frontend restarted on 5174 after dependency optimisation; API remains on 8001. Temporary HMR import errors occurred while files were being replaced; the final build passed and the frontend restarted cleanly. No browser reload success is claimed.
- Design-document YAML/JSON parsing and token-reference checks passed: 25 colours, 10 type roles, 19 component tokens and 10 static component previews. The first documentation check failed because `python` was not on PATH; rerunning with `py -3 -` succeeded. These previews describe source and do not establish browser acceptance.

All current evidence is under `docs/evidence/brand-redesign-20261028/`. The earlier 91 backend tests and 24 follow-up checks belong to the preceding architecture revision; they were not rerun for this frontend-only change.

## Commands actually run

```powershell
# Project root
& C:/Users/loelb/.codex/skills/impeccable/scripts/impeccable.cmd context --target frontend/src/LiveApp.tsx
.\backend\.venv\Scripts\python.exe scripts/check-redesign-preservation.py before brand-redesign-20261028
.\backend\.venv\Scripts\python.exe scripts/redesign-brand.py
.\backend\.venv\Scripts\python.exe scripts/check-redesign-contrast.py
& C:/Users/loelb/.codex/skills/impeccable/scripts/impeccable.cmd detect --json frontend/src/LiveApp.tsx frontend/src/shared/Brand.tsx frontend/src/app/Login.tsx frontend/src/app/WorkspaceShell.tsx frontend/src/features/workspace frontend/src/features/cases/CaseList.tsx frontend/src/design-system frontend/src/screens/CoordinationScreens.tsx
.\scripts\run-service.ps1 -Service frontend -ContextId demo-5f5a439bfd2ea5ede367507b
.\backend\.venv\Scripts\python.exe scripts/check-redesign-preservation.py after brand-redesign-20261028
.\backend\.venv\Scripts\python.exe scripts/finalize-brand-evidence.py

# frontend
npm install @fontsource/manrope
npm run typecheck
node --test tests/connections.test.ts
npm run build
npm test
```

Prettier 3 was run on the changed TSX/TS/CSS files; exact file output is retained in `format.txt` and follow-up logs. Read-only inspection used `rg`, `Get-Content`, Git status and listener inventory. The logo task used Python XML validation, the bundled Sharp renderer and a small Python standard-library WOFF glyph extractor to outline the installed Manrope lettering; font provenance and licence are in the brand directory. No operating-system font installation was performed. The one-time `redesign-brand.py` is a source-edit record, not a setup or database migration command.

## Changed files and remaining limits

The exact changed-source comparison, additional test/config/documentation paths and brand-asset inventory are in `changed-files.json`. [Brand rationale](BRAND_IDENTITY_20261028.md) describes the six concepts and export formats. Root `DESIGN.md` and `.impeccable/design.json` describe the implemented system.

**Browser acceptance remains open.** The saved origin block reported in the previous turn was not bypassed or retried without an external permission change. Current desktop/mobile layout, supporting-screen rendering, actual keyboard flow and actual 200% browser zoom remain unverified. The existing browser authorization is recorded, but the tool still needs effective access. Next phase: rendered desktop/mobile review, keyboard and zoom checks, then an isolated synthetic write rehearsal. Independent human clarity/relationship evaluation and official policy alignment remain outstanding.

All complaint records are preserved. No backend integration, model, notification service, new evaluation score or production deployment is claimed. The Impeccable context tool also reported the existing product brief's older metadata schema; that advisory was not treated as permission to replace confirmed product context or expand this task into an interview.
