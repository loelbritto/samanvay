# Stage 1 implementation and verification

Status: **G1 ready to close**, 27 October 2026 (Asia/Kolkata). Supporting review and actual native Chrome200% checks are complete. This document describes the fixture-only `?preview=1` reference, which saves no decisions. The default application now has the separate Stage2 backend described in STAGE2_PERSISTENCE.md. Earlier interrupted attempts below are retained as history.

## Pre-edit inspection and gaps

Inspected PLAN.md, PROJECT_STATE.md, access/workflow/acceptance contracts, tracked/untracked file inventory, ancestor instruction locations and existing traceability tooling. The repository still had no application or dependency files. Stage 0 files were preserved. No complaint records existed in a database to modify. Missing Stage 1 items were the frontend toolchain, every screen, state examples, responsive layout, keyboard flow and control integration inventory.

## Implemented preview

React/TypeScript/Vite supplies Overview, Cases/filtering, intake, case detail, case timeline, institution directory, Pune profile, Nagpur profile, coordination list, evidence comparison, reports/filtering, notification history, settings boundary and explicit simulated state examples. The inspected route set contains 14 screens (one representative case detail/timeline).

The overview puts issue/reason/owner/deadline/action in a short attention queue before illustrative workload counts. The comparison preserves different complainant tokens/receipts in a RELATED illustration, and retains the independent faculty complaint at the Pune institution. Institution identity, relationship proposal, accountable case owner and coordination lead are separate. The Nagpur institution's identifier/city and one-bureau scenario remain distinct. Semantic services and integrations are explicitly not connected. The UI contains no fabricated match score or AI-generated output.

All case-changing controls are disabled with explanations. Intake only checks required fields and explicitly says no case is created or saved. Search/report counts filter the same four fixture records. Navigation, filtering and field checks use transient UI state; no localStorage, sessionStorage or in-memory workflow substitute is implemented. See [BACKEND_GAPS.md](BACKEND_GAPS.md) for every control and its backend dependency.

## Observed verification

- `npm.cmd install --no-fund --no-audit --fetch-retries=0 --fetch-timeout=30000` completed: 24 packages added. Exact direct package versions were inspected with `npm.cmd ls --depth=0`.
- Initial build failed with TS2882 for the CSS side-effect import. Adding `src/vite-env.d.ts` resolved it. The final `npm.cmd run build` passed TypeScript checking and Vite compilation: 23 modules transformed; CSS 20.50 kB and JavaScript 268.65 kB (build output sizes, not performance benchmarks).
- The server bound to `127.0.0.1:5173`. A sandboxed socket attempt was forbidden and the first in-app navigation timed out. Restarting the same loopback-only server outside the sandbox made it reachable in a fresh preview tab. No all-interface binding or security-setting change was used.
- Actual keyboard route: focused Overview heading → Tab to Preview case intake → Tab to Open institution → Enter; then Tab to other-institution link → Tab to Compare evidence → Enter; then Tab to PGRC-014 source link → Tab to View PGRC-014 timeline → Enter. Expected institution/comparison/timeline headings appeared. The initial interactive links showed solid focus outlines.
- Local search `RB-031` returned 1/4 records; PGRC filter returned 2/4; a nonexistent search displayed the empty state; Clear filters restored the list. Empty intake displayed six required-field messages. Filling fictional values displayed 'No case was created or saved'; create and file inputs were disabled.
- Report filters RB + Nagpur displayed one fixture row, pending 1, under review 0, disposed 0. Drill-down displayed 1/4 and RB-031. No database/report/export behavior was tested.
- Loading, empty, error, permission-denied and stale examples rendered. Retry explicitly said no server request was made; stale reload said no database conflict/mutation occurred. Comparison review/lead controls were disabled.
- All 14 routes were captured at **1440×900** and **390×844**. The 28 DOM measurements found no page-wide horizontal overflow and no unlabelled input/select/textarea. Scrollbars leave 1425 or 375 CSS pixels of content on scrolling pages. Case tables intentionally scroll within their labelled, focusable region.
- The initial pass inspected the principal screenshots; the follow-up supporting-screen review and repairs are recorded below. A full accessibility assessment remains outside the observed result.

## Initial zoom attempt

In the initial run, in-app Ctrl+0 and four Ctrl+plus shortcuts left viewport/DPR unchanged (1440×900, DPR approximately 1); this is **not** evidence of 200% zoom. Before native input, Windows Computer Use stopped on URL-confidence policy. No further UI interaction occurred in that run, no Chrome zoom changed, and no policy bypass was used.

## Supporting-screen follow-up and fixes

The resumed review inspected desktop and narrow captures of Cases, intake, institution directory, Nagpur profile, coordination list, case detail, reports, notifications, settings and preview states. Narrow loading/empty/error/denied/stale examples and the remaining narrow institution/timeline captures were also visually inspected.

The mobile Notifications screen had a material flex-layout defect: its acknowledgement button stayed beside the message and squeezed the text into a thin column. The fix makes the message occupy the remaining row width and wraps the button below it. Post-fix text widths were 254 CSS pixels for both mobile messages; the saved full screenshot was inspected and is readable without that compression. Adjacent Nagpur notices now have spacing; one-case/one-bureau wording is singular. Wide tables have an explicit horizontal-scroll hint.

The hinted native ArrowRight table movement initially remained at zero, even after a fresh observation. The table now handles ArrowLeft/ArrowRight/Home/End when its focusable region is the event target; linked controls keep their own key behavior. Observed at 390×844: ArrowRight = 80, End = 512.8, Home = 0 CSS pixels. A scrollable fixed sidebar was added for short viewports, but its actual 200%-zoom use remains unverified.

All 14 routes were captured again in Chrome at 1440×900 and 390×844 after the layout fixes. All 28 scoped DOM observations showed no page-wide horizontal overflow and no unlabelled form controls. `layout-results.json` is the actual captured observation array; `keyboard-table.json` records the successful post-fix key check. A limited Chrome log read returned an empty warning/error list. No exhaustive console or accessibility audit is claimed.

Final `npm.cmd run build` passed TypeScript checking and Vite compilation: 23 modules; CSS 21.23 kB, JS 269.27 kB. These are emitted artifact sizes, not performance/evaluation metrics.

## Resumed zoom attempt and user stop

Chrome tab-directed Ctrl+plus and Ctrl+equal also left the actual normal viewport at 1536×639 with DPR 1.25; no 200% result is inferred. The temporary Chrome viewport override used for responsive checks was reset. Native Chrome access then became available and tab search opened, but a physical Escape key stopped Computer Use during selection of the preview tab. No further browser/desktop interaction occurred after that stop. Browser zoom was never changed, so there is no zoom setting to restore. Actual 200% zoom is the only remaining G1 check.

## Evidence and continuation

[Original command log](evidence/stage1-commands.md), [original browser summary](evidence/stage1-browser-results.json), and PNGs under `docs/evidence/stage1/` are retained. Follow-up results and captures are under `docs/evidence/stage1-completion/`, including its command log. No screen-reader test, automated contrast audit, WCAG certification or representative usability result is claimed.

## Completed actual 200% check

After explicit user authorisation of a Samanvay-only window, native Chrome Ctrl+0 and five Ctrl+plus steps produced the observed **200%** label. Baseline DPR1.25/786×632 became DPR2.5/393×316, with385CSS pixels after the scrollbar. All14reference routes passed page-width/label observations; viewport captures were visually reviewed. The full-page capture API clipped at zoom, so those images were replaced with proper viewport captures. This screenshot limitation is not treated as a reflow pass on its own.

The keyboard route Overview→Pune→comparison→PGRC-014 timeline passed; each action scrolled into view and focus outlines remained visible. The table region responded to ArrowRight80, End502.4 and Home0 CSS pixels. Settings was reachable by Enter. Native Ctrl+0 restored DPR1.25/786×632; temporary QA tab closed. See [raw observations](evidence/stage1-zoom/results.json), native200% proof and14viewport captures in `docs/evidence/stage1-zoom/`.

G1 is ready to close for these scoped browser checks. Screen-reader testing/full accessibility assessment remain unexecuted; no WCAG conformance is claimed. Stage2's persistence gate also passed; next implementation is Stage3. Real policy/production use still requires the decisions in DECISIONS.md.
