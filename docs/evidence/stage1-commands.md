# Stage 1 actual commands and observations

Date: 27 October 2026 (Asia/Kolkata). Project root: `C:\Users\loelb\OneDrive\Documents\ChatGPT\sih`. Commands below were actually run; browser operations are identified separately.

## Inspection

```powershell
Get-Location
git status --short
rg --files -g '!node_modules' -g '!__pycache__' -g '!package-lock.json'
Get-Content -LiteralPath PLAN.md -Raw
Get-Content -LiteralPath PROJECT_STATE.md -Raw
Get-Content -LiteralPath docs\ACCESS_MATRIX.md -Raw
Get-Content -LiteralPath docs\ACCEPTANCE.md -Raw
Get-Content -LiteralPath docs\WORKFLOWS.md -Raw
Get-Content -LiteralPath scripts\capture_requirements.py -TotalCount 85
Get-Content -LiteralPath .gitignore -Raw
```

Ancestor `AGENTS.md` candidates from `C:\AGENTS.md` through the workspace were checked with Test-Path/Get-Content; none returned. Computer-use SKILL.md, guidance.md, api.md and confirmations.md were read before the native-browser attempt. CUA local-web-development, viewport and browser-troubleshooting documentation was read through its documented APIs.

## Dependency discovery and install

Initial metadata command (`npm.cmd view` for react, react-dom, vite, typescript, plugin-react and type packages) produced no output while sandboxed and was interrupted. The following was rerun outside the sandbox, with no source-policy change:

```powershell
npm.cmd view react version --fetch-retries=0 --fetch-timeout=15000
npm.cmd view vite version engines --json --fetch-retries=0 --fetch-timeout=15000
npm.cmd view typescript version --fetch-retries=0 --fetch-timeout=15000
npm.cmd view @vitejs/plugin-react version engines --json --fetch-retries=0 --fetch-timeout=15000
npm.cmd view @types/react version --fetch-retries=0 --fetch-timeout=15000
npm.cmd view @types/react-dom version --fetch-retries=0 --fetch-timeout=15000
npm.cmd config get registry
npm.cmd cache ls react --parseable
```

Observed registry `https://registry.npmjs.org/`; React 19.3.1, Vite 8.3.5, TypeScript 7.0.2, plugin-react 6.1.2, type packages 19.3.0. Vite/plugin engines returned `^20.19.0 || >=22.12.0`. Existing system Node v25.8.2/npm 11.11.1 were used for this repo build. Bundled node_modules inspection found Playwright packages but no React/Vite/TypeScript packages. Official React and Vite setup pages were read through the web tool; no template generator was run.

In `frontend/`:

```powershell
npm.cmd install --no-fund --no-audit --fetch-retries=0 --fetch-timeout=30000
npm.cmd run build
npm.cmd run dev
```

Install completed outside sandbox: 24 packages added in 25 seconds. First build failed with TS2882 (CSS side-effect import type missing). After adding `src/vite-env.d.ts`, build passed: TypeScript check plus 23 modules transformed. Dev server started on loopback `http://127.0.0.1:5173/`.

## Local connection recovery

```powershell
(Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -TimeoutSec 10).StatusCode
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object LocalAddress,State,OwningProcess
```

Sandboxed Invoke-WebRequest reported a forbidden socket access. The first in-app browser attempt timed out. The sandboxed dev session was interrupted, then **the same `npm.cmd run dev` command** was run outside sandbox, still bound to 127.0.0.1. A new in-app tab then loaded the preview. The previous error tab could not navigate because of its data-URL policy; no policy was bypassed.

After the final CSS spacing/focus adjustment, in `frontend/`:

```powershell
npm.cmd run build
npm.cmd ls --depth=0
```

Observed final build passed: 23 modules, CSS 20.50 kB (gzip 5.22 kB), JS 268.65 kB (gzip 79.99 kB), HTML 0.61 kB. `npm ls` listed exactly the seven pinned direct packages. These are build artifact sizes, not a runtime benchmark or security audit. Dependency audit, backend tests and server/database setup were not run.

## Browser operations actually performed

CUA created local preview tabs, set the in-app viewport to 1440×900 and 390×844, captured PNGs, measured DOM widths/form labels and exercised the controls listed in stage1-browser-results.json. Keyboard input used Tab/Return along the main four-screen route; selected links showed solid focus outlines. All 14 known routes were captured at both sizes. No external form, account, integration, message or file upload was submitted.

In-app Ctrl+0 and four Ctrl+plus inputs did not change viewport/DPR, so actual zoom was not verified. A named Chrome QA tab was opened. Before native input, CUA stopped because it could not determine the browser URL reliably for policy enforcement. No further browser/desktop interaction occurred. That check remains outstanding; supporting screenshot visual review and console/accessibility audits are also explicitly limited in STAGE1_UI.md.

## Traceability continuation

The following root-directory commands were executed after the progress overlay was added:

```powershell
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/capture_requirements.py --prompt 'C:\Users\loelb\.codex\attachments\b3eb387c-2580-4e62-8120-b06d96c6c118\Pasted text.txt' --guide 'C:\Users\loelb\Downloads\SIH_26264_Research_and_Build_Guide.docx'
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/verify_phase0.py --verify-originals --output docs/evidence/stage1-traceability.json
Get-Content -LiteralPath REQUIREMENTS.md -TotalCount 9
rg -n 'P02[2-8] /|G06 /' REQUIREMENTS.md
git status --short
```

Observed exit 0 for capture and audit: 2 sources, 77 prompt lines, 532 guide paragraphs, 66 clauses; 24 planning checks and zero failures. Seven Stage 1 prompt clauses and guide section G06 now carry `partially_verified` plus exact implementation/evidence locations. Original hashes/text remain unchanged. Historical `phase0-verification.json` is retained; this is a separate current traceability report. The audit is rerun after the final evidence-log/script changes so its artifact hashes match delivered planning documents.

An inline standard-library Python script was also actually run with the bundled Python: it enumerated `docs/evidence/stage1/*.png`, read PNG dimensions with `struct.unpack('>II', data[16:24])`, and wrote filename/dimensions/byte-count/SHA-256 to `docs/evidence/stage1-captures.json`. Observed: **30 PNG files, 3,048,873 bytes total** (28 route/viewport images plus intake-validation and stale-state captures). This inventories existing screenshots; it does not render or modify images, or establish a missing browser check.

`git status --short` reports the project files as untracked because no initial commit exists. No Git commit, backend test, real external message, official integration, AI metric or complete G1 pass is claimed.
