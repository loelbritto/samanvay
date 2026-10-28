# Stage 1 remaining-check follow-up

27 October 2026, Asia/Kolkata. This log records actual commands and browser observations. Stage 1 is not ready to close because actual 200% zoom remains unverified.

## Commands actually executed

From the project root: Get-Location, git status --short, `rg --files -g 'AGENTS.md' -g '!node_modules' -g '!dist'`, and Get-Content on PROJECT_STATE.md, PLAN.md, DECISIONS.md, docs/STAGE1_UI.md, docs/ACCEPTANCE.md, the browser-results/progress JSON, existing frontend source/package files and traceability scripts. No AGENTS.md was returned by the workspace search. Get-Process node returned no visible process in the sandbox; this was not evidence that port 5173 was free.

From `frontend/`:

```powershell
npm.cmd run dev
npm.cmd run build
```

The attempted second dev server exited 1 with 'Port 5173 is already in use'; the existing preview was reachable and reused. No process was killed and no server binding was broadened. The build was run after the layout changes and again after explicit table keyboard handling. Both passed. Final output: 23 modules transformed, CSS 21.23 kB (gzip 5.36), JS 269.27 kB (gzip 80.23), HTML 0.61 kB. No packages, backend features or data were added.

## Browser and visual checks actually performed

CUA opened the local Chrome preview and inspected its current source. Existing desktop/narrow captures of all ten supporting screens were reviewed using the file-image tool. This found the mobile notification compression defect, singular/plural wording and adjacent-notice spacing. Those issues were fixed in frontend source.

Chrome viewport controls set 1440×900 and 390×844. All 14 known routes were revisited and captured at each size. The actual DOM arrays were saved immediately to layout-results.json: 28 observations, all with page width within client width and no unlabelled input/select/textarea. Mobile notification text widths after repair were 254 CSS pixels. Five narrow simulated-state captures were saved and visually inspected.

ArrowRight table movement initially remained zero. After adding explicit region key handling, the browser check observed ArrowRight 80 → End 512.7999877929688 → Home 0; keyboard-table.json stores the result. The corrected mobile Notifications screenshot was captured and inspected. A limited warning/error log request returned `[]`.

Chrome tab-directed Ctrl+plus and Ctrl+equal did not change viewport/DPR (1536×639, DPR 1.25). The responsive viewport override was reset. Native Chrome was inspected with current URL controls available; Ctrl+Shift+A opened tab search. During selection of the local preview, Computer Use reported a physical Escape key stop. No further browser/desktop interaction occurred, and no 200% zoom setting was applied or verified. No alternative automation bypass was used.

An inline standard-library script was executed with the bundled Python to update the requirement-progress overlay, retain the original browser summary with a follow-up reference, inventory PNG headers/SHA-256 values, and write results.json/capture-manifest.json. Observed: 33 follow-up PNGs, 28/28 scoped layout observations, successful keyboard scrolling, Stage 1 ready-to-close false. These are file/observation records, not browser-zoom or application-persistence proof.

The following commands were actually executed from the root:

```powershell
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/capture_requirements.py --prompt 'C:\Users\loelb\.codex\attachments\b3eb387c-2580-4e62-8120-b06d96c6c118\Pasted text.txt' --guide 'C:\Users\loelb\Downloads\SIH_26264_Research_and_Build_Guide.docx'
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/verify_phase0.py --verify-originals --output docs/evidence/stage1-completion/traceability.json
```

Observed exit 0: 66 source clauses and 532 guide paragraphs preserved; 24 planning/source-coverage checks passed, zero failed. Original reference hashes/extraction reproduced. Historical evidence was retained. This audit does not pass G1 or the application acceptance scenarios.

## Changed implementation files

- `frontend/src/styles.css`: notification wrapping, adjacent notice spacing, short-sidebar scrolling and narrow table hint styling.
- `frontend/src/components.tsx`: scroll hint with accessible description and explicit Arrow/Home/End table-region handling.
- `frontend/src/screens/Institutions.tsx`: correct singular/plural case and bureau counts.

Also updated PROJECT_STATE.md, PLAN.md, DECISIONS.md, REQUIREMENTS.md, docs/STAGE1_UI.md, docs/ACCEPTANCE.md, docs/BACKEND_GAPS.md and requirement progress/map; added follow-up captures and evidence. Existing source references, historical evidence and all complaint fixtures were preserved.
