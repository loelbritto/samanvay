# Stage 0 commands and observed evidence

Date: 27 October 2026, Asia/Kolkata. Working directory: `C:\Users\loelb\OneDrive\Documents\ChatGPT\sih`. No package install, app startup, database connection or application test was run.

## Initial project inspection

These commands were actually executed through PowerShell:

```powershell
Get-Location
rg --files -g 'AGENTS.md' -g 'package.json' -g 'README*' -g '*plan*' -g '*phase*' -g 'pyproject.toml' -g 'requirements*.txt' -g 'docker-compose*' -g 'prisma/schema.prisma' -g '.env.example' -g 'SKILL.md' -g '!node_modules' -g '!.git'
git status --short
Get-ChildItem -Force | Select-Object Mode,Name
git rev-parse --is-inside-work-tree
git log -1 --format='%h %s'
git ls-files
git status --porcelain=v1
Get-ChildItem -Force .git | Select-Object Name
git diff --stat
```

Observed: working directory matched the supplied workspace; only `.git` existed; `rg --files` found no matching files (exit 1); Git recognized a repository, no tracked files/status changes existed, and log failed because `master` had no commits. This is the pre-edit gap assessment, not a failed application test.

```powershell
$paths = @('C:\AGENTS.md','C:\Users\AGENTS.md','C:\Users\loelb\AGENTS.md','C:\Users\loelb\OneDrive\AGENTS.md','C:\Users\loelb\OneDrive\Documents\AGENTS.md','C:\Users\loelb\OneDrive\Documents\ChatGPT\AGENTS.md','C:\Users\loelb\OneDrive\Documents\ChatGPT\sih\AGENTS.md')
foreach ($path in $paths) { if (Test-Path -LiteralPath $path) { Write-Output $path; Get-Content -LiteralPath $path -Raw } }
```

Observed: no applicable instruction file was returned from those locations.

## Runtime inspection

```powershell
Get-Command python,python3,py,node,npm,docker,psql,git,rg -ErrorAction SilentlyContinue | Select-Object Name,Source
node --version
npm.cmd --version
py --list
git --version
$PSVersionTable.PSVersion.ToString()
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' --version
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' --version
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "import importlib.util,json; print(json.dumps({name: importlib.util.find_spec(name) is not None for name in ['fastapi','sqlalchemy','alembic','psycopg','docx']},sort_keys=True))"
```

Observed: system Node v25.8.2/npm 11.11.1, Git 2.49.0.windows.1, PowerShell 7.6.5. `py --list`: `No installed Pythons found!`. Python/python3/docker/psql were not returned by PATH inspection. Both CIM requests reported access unavailable. Bundled runtime: Python 3.12.14, Node v24.19.0; `docx: true`, `fastapi/sqlalchemy/alembic/psycopg: false` in bundled import discovery. No database connection was attempted.

The workspace dependency loader was called successfully to discover bundled paths. Skills were read from the supplied documents skill package using `Get-Content`, including `SKILL.md` and `tasks/read_review.md`. No Word file was created or edited; no layout quality is asserted.

## Reference reading and official verification

The pasted file was read with `Get-Content -Raw`, line-numbered output and tail output. The Word guide was read using `.NET System.IO.Compression.ZipFile`, `word/document.xml`, the WordprocessingML namespace, all body `w:p`/`w:t` nodes, and `word/_rels/document.xml.rels`; body ranges 1–180 and 181–291 were then read separately to recover tool-output truncation. Remaining paragraphs through 532 were visible in the initial extraction. File hashes were obtained using `Get-FileHash -Algorithm SHA256` for both supplied paths. The capture script below repeats complete extraction reproducibly and includes supplementary Word parts.

Observed source hashes:

- Guide: `D588805278A5EF017E9B9F0F3B8345FBA4A719B6261BD12294CEE1A1EC2F5B20`
- Staged prompt: `14B7877B81955F971B70EF689E162E8DE1DD0C9D7C876A13BABEF0E6229CC589`

Web-tool requests (actual tool operations, not shell commands): open `https://www.sih.gov.in/sih2026PS`; open `https://www.sih.gov.in/letters/SIH2026-Guidelines-College-SPOC.pdf`; search `site:sih.gov.in "26264" "Institution"`. Both opens returned 403; search returned no results. This does not verify official scope or absence of a statement. No external message or restricted system operation was attempted.

## Phase verification

```powershell
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/capture_requirements.py --prompt 'C:\Users\loelb\.codex\attachments\b3eb387c-2580-4e62-8120-b06d96c6c118\Pasted text.txt' --guide 'C:\Users\loelb\Downloads\SIH_26264_Research_and_Build_Guide.docx'
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/verify_phase0.py --verify-originals --output docs/evidence/phase0-verification.json
Get-Content -LiteralPath REQUIREMENTS.md -TotalCount 25
Get-Content -LiteralPath REQUIREMENTS.md | Select-Object -Last 24
git status --short
rg --files -g '!__pycache__'
```

Observed source capture exit 0: 2 sources, 77 prompt lines, 532 guide body paragraphs, 66 requirement clauses, 17 guide coverage sections; supplementary footer `Samanvay research guide  |  ` preserved. No header/footnote/endnote/comment parts were returned. Planning audit exit 0: 24 checks, 0 failures, original hashes/full extraction and generated mapping reproduced. The exact original text equals the snapshot; requirement statuses are only specified/planned. Required docs, separate proposed concepts, role matrix and fourteen scenario definitions are present. This does not execute or verify application behavior. The audit is rerun after final documentation edits so raw evidence hashes refer to the delivered planning files.

The generated requirement table and file inventory were inspected. Git lists all deliverables as untracked because the repository has no initial commit; no commit or application feature is claimed.
