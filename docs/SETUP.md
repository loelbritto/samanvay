# Verified local setup

Windows PowerShell; inspected Node25.8.2/npm11.11.1 and Python3.12.14. Exact npm/Python versions are pinned in lockfiles. Fresh installations, frontend build, migration, seed and backend startup were actually checked; logs: evidence/stage9/clean-*.log and clean-dependencies.json. No paid key is needed. Use synthetic data only.

From repository root:

```powershell
& 'C:\Users\loelb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv backend/.venv
& '.\backend\.venv\Scripts\python.exe' -m pip install -r backend/requirements.lock
cd frontend
npm.cmd ci --no-fund --no-audit
npm.cmd run build
cd ../backend
& '.\.venv\Scripts\python.exe' -m alembic upgrade head
& '.\.venv\Scripts\python.exe' -m app.seed
cd ..
```

Use separate terminals from repository root:

```powershell
.\scripts\run-service.ps1 -Service api
.\scripts\run-service.ps1 -Service frontend
.\scripts\run-service.ps1 -Service worker
```

The verified helper starts loopback API8000/UI5173 and the durable worker using `.local-data`. Ctrl+C stops the owned process; restart with the same directory. Do not delete database/WAL/private evidence. Seed is add-only. `.env.example` describes process variables; the application does not auto-load an env file. API environments are limited to demo/test.

All **nine** synthetic accounts use `DemoOnly-Stage2!`:

| Account | Local scope |
| --- | --- |
| rb@demo.test | Assigned RB cases and self-owned intake |
| rb.backup@demo.test | Assigned RB cases, including Nagpur seed |
| pgrc@demo.test | Assigned PGRC cases and intake |
| supervisor@demo.test | RB metadata, eligible assignment and explicit workflow delegations |
| pgrc.supervisor@demo.test | PGRC metadata/assignment and explicit workflow delegations |
| regional@demo.test | Western-region scoped intake/owned cases |
| coordinator@demo.test | Explicit institution metadata and pair/coordination grants; N/I seed scope separate from A |
| management@demo.test | No implicit case access; explicit rehearsal scope is Pune M only |
| admin@demo.test | Technical policy/demo operations; no implicit complaint access |

Opaque sessions/CSRF are stored server-side; Argon2id hashes; HttpOnly/SameSiteStrict cookies expire after8hours of host time. Secure cookies are disabled for loopback HTTP. Isolated contexts use distinct cookie realms; restore revokes copied sessions. No account/grant-management UI or production identity-provider integration is claimed.

## Separate synthetic run, backup and recovery

From backend, `python -m app.demo new --key <unique-nonsecret-run-key>` creates a new marked context under `.demo-contexts`; the same key reuses its persistent state. This is an idempotent non-destructive reset: old complaints/contexts remain intact. Use the returned context ID:

```powershell
# From repository root, each command in a separate terminal
.\scripts\run-service.ps1 -Service api -ContextId demo-5f5a439bfd2ea5ede367507b
.\scripts\run-service.ps1 -Service frontend -ContextId demo-5f5a439bfd2ea5ede367507b
.\scripts\run-service.ps1 -Service worker -ContextId demo-5f5a439bfd2ea5ede367507b
```

These exact context commands were exercised with API8001/UI5174 and actual stop/restart. Only one isolated context may occupy those ports at once. The primary context remains separate.

From backend:

```powershell
& '.\.venv\Scripts\python.exe' -m app.demo audit-storage --context-id demo-5f5a439bfd2ea5ede367507b
& '.\.venv\Scripts\python.exe' -m app.demo backup --context-id demo-5f5a439bfd2ea5ede367507b
# Substitute the returned backup ID and a NEW non-secret restore key:
& '.\.venv\Scripts\python.exe' -m app.demo restore --backup-id backup-RETURNED_ID --key my-new-recovery-run
```

The last line is a substitution template. Actual recovery evidence identifies the used backup/context. Backup uses SQLite's backup API plus verified private-file copies, integrity/FK checks and a manifest. Restore verifies hashes into a NEW context; the source is preserved. Storage audit reports missing/changed/unreferenced files without deleting. No arbitrary configured production database reset is supported.

## Checks

`npm.cmd run build` in frontend; `python -m pytest -q` in backend. Evidence runs use unique validated workspace `--basetemp` directories and JUnit outputs, preserving existing data. In the managed sandbox TestClient needs loopback socket permission; a restricted run hung during Windows event-loop socket creation, then the permitted repeat passed. This is not an application assertion failure.

`scripts/check-clean-dependencies.ps1` installs/builds in a new preserved directory; `scripts/repeat_and_recover.py` exercises a new context plus recovery; `evaluation/generate.py` checks/freezes the synthetic corpus; `evaluation/run.py` emits a new immutable measured run. Source traceability is separately audited by `scripts/verify_phase0.py --verify-originals`.
