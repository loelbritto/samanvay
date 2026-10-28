# Actual Stage 1 closure / Stage 2 commands and observations

27 October 2026, PowerShell. Relative paths start at the repository unless cwd is specified. This is an execution log; setup reinstall instructions are not silently counted as executed. Python 3.12.14, Node 25.8.2/npm 11.11.1; dependency pins/freeze are in the repository.

| Actual command / action | Observation |
| --- | --- |
| `rg --files`; `Get-Content` contracts/source/state/evidence; `git status --short`; runtime/PostgreSQL inventory | Existing Stage 1 inspected; backend absent; no initial commit; no verified PostgreSQL server |
| Bundled Python `-m venv backend/.venv` | Local environment created |
| Initial package installation and `-m pip freeze` | Backend/test packages installed and frozen; exact original pip argument list was not retained. Requirements files record actual installed pins |
| Root: venv Python `-m pip install --no-index -r backend/requirements.lock`; `-m pip check` | Every pin already satisfied; no broken requirements. Pip warned it could not remove four sandbox temporary directories; they were left untouched outside the project. No clean-machine reinstall claimed |
| Venv Python `-m alembic -c backend/alembic.ini revision --autogenerate`; `-m alembic -c backend/alembic.ini upgrade head` | Migration generated/reviewed; SQLite tables created; revision19512be41395 retained. Original message text is in its header |
| Root cwd: venv Python `-m app.seed` | ModuleNotFoundError; corrected cwd |
| `backend/`: `.venv/Scripts/python.exe -m app.seed` | Eight accounts/two institutions/four cases; add-only idempotency tested |
| Initial sandbox pytest runs | Temp-directory permission errors, then blocked loopback/event-loop setup; interrupted; not passes |
| Final guarded pytest below | **16 passed, 1 warning in 44.85 s**, stage2-tests.xml; previous 15-test passes predated region regression |
| `frontend/`: `npm.cmd run build` | Final TypeScript/Vite passed, 27 modules; CSS 22.31 kB/JS 300.53 kB |
| `backend/`: `.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log` | Loopback API, owned session stopped/restarted; final PID29120 includes region fix |
| `frontend/`: `npm.cmd run dev` | Loopback Vite5173, stopped/restarted for G2; prior exact Vite workspace/command verified before stopping PID |
| `backend/`: `.venv/Scripts/python.exe -m app.worker --once` | One persisted job DONE, one file; integrity event retained |
| Root: `backend/.venv/Scripts/python.exe scripts/verify_stage2_restart.py before`, then `... after` | API/scoped reads plus read-only SQLite/private-byte comparison passed; after check repeated after region fix |
| CUA UI sign-in/intake/file upload/refresh; actual API and UI stop/restart/reload | Same ID/owner/original/history/session/bytes/count retained; browser intake used actual form |
| CUA supervisor assignment/restore; ten routes at1440×900/390×844 | Both changes retained; 20 scoped layout/label observations passed |
| Authorised isolated Chrome native Ctrl+0, five Ctrl+plus steps | Native200% label/DPR1.25→2.5; 14route checks/captures and keyboard/table passed. Ctrl+0 restored; temporary QA tab closed |
| Root: venv Python `scripts/capture_requirements.py --prompt <original-prompt-path> --guide <original-docx-path>`; `scripts/summarize_stage2.py`; `scripts/verify_phase0.py --verify-originals --output docs/evidence/stage2/traceability.json` | Sources recaptured without changing original text;66clauses/532paragraphs covered;25planning/source checks passed. Summary also reads demo DB without mutation and hashes sources/captures |

From `backend/`, the final temporary path was freshly generated and checked because pytest may clear its basetemp target:

```powershell
$stage2TestRoot = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path '..\.local-data'))
$stage2TestPath = Join-Path $stage2TestRoot ('pytest-' + [guid]::NewGuid().ToString('N'))
if (-not $stage2TestPath.StartsWith($stage2TestRoot + [System.IO.Path]::DirectorySeparatorChar) -or (Test-Path -LiteralPath $stage2TestPath)) { throw 'Unsafe or existing pytest temporary directory' }
& '.\.venv\Scripts\python.exe' -m pytest --basetemp $stage2TestPath --junitxml '..\docs\evidence\stage2-tests.xml' -q
```

Computer-use checks used documented CUA APIs/native zoom/read-only DOM. Earlier shared-window inspection/input was rejected/interrupted; the user then authorised a Samanvay-only window. No security bypass or unrelated-site action was used. Full-page zoom captures clipped and were replaced with viewport captures. Final source coverage, database audit and manifest results are in their JSON artifacts. Planning/source checks remain separate from the 16 application tests.
