# Synthetic demonstration and recovery runbook

Release `samanvay-local-20261027`; actual captures dated27October2026, Asia/Kolkata. Capture filenames/hashes and source/build evidence are indexed in evidence/stage9/release-manifest.json. No Git commit exists. All people/receipts/incidents are fictional; no AICTE service, email or semantic model is connected.

## Open the rehearsed build

API8001/UI5174/worker are running with `demo-5f5a439bfd2ea5ede367507b`. Open http://127.0.0.1:5174/; sign in `coordinator@demo.test` / `DemoOnly-Stage2!`. To restart use the three context-specific commands in SETUP.md. Stage9 evidence proves a real stop/restart, preserving browser session, cases, files, plan and alerts. Do not advance this context's clock again merely to replay the same alert: it is already120hours ahead. Use a new marked context for a new live run.

For a clean run from backend: `python -m app.demo new --key <new-run-key>`; keep the returned ID. The same key reuses the context and retains its records. Stop only your owned isolated services, then pass that ID to run-service.ps1. Seed creates four synthetic cases and nine users. No destructive reset exists. The Settings operation can create another context, but starting its service still requires the documented helper. Each context uses a separate cookie name.

## Proposed three-minute narration

This is a presentation target, not a measured three-minute successful run; verification and file uploads took longer. Keep backup captures available rather than relying on panel links/video playback.

| Target segment | Screen / observable claim |
| --- | --- |
| 0:00–0:25 | Overview → Pune institution: several bureaus need coordination; case owners remain separate |
| 0:25–0:55 | PGRC synthetic refund intake and real receipt; RB paraphrase with original “DSI Pune” text and different student/receipt. Canonical Pune ID is explicitly selected, never inferred from an abbreviation without review |
| 0:55–1:30 | Evidence review: separate student receipts → RELATED. Faculty wage issue → INDEPENDENT. Show exact sources, conflicts/missing facts, reviewer reason/history. Semantic matching unavailable; baseline works |
| 1:30–2:00 | PLANNED institutional coordination: Demo Meera Das coordinates. Refund DEMO-79D983D2A10B stays owned by Demo Kabir Sen/RB; PGRC cases stay with Demo Ananya Rao. Next action: coordinate separate responses while each owner handles their own complaint |
| 2:00–2:25 | Timeline shows receipt, actions and transfer. Source remains owner during pending transfer; acceptance changes the same case's owner without resetting its deadline. Nagpur DEMO-INST-044 is a different institution and is not in the Pune group |
| 2:25–2:45 | Isolated admin clock/worker → persisted overdue alert → recipient acknowledgement. No host time/other-context deadline changed |
| 2:45–3:00 | Management's explicit Pune M-only report: seven rows, no narratives/identity/private evidence. Actual CSV and HTML print agree |

Completed browser record IDs: PGRC refund DEMO-E80508228652; RB refund DEMO-79D983D2A10B; independent faculty DEMO-436C0703134C; accepted transfer DEMO-80AE1D9C9F27. Four initial seed cases remain; total8. Original workspace remains5. The automated repeat created3more in another7case context and passed a fresh application-instance restart. Actual browser service restart evidence is separate from that automated repeat.

## Answers supported by the build

- Differentiator: one institution timeline plus cited pair comparison and explicit coordination lead; same institution never implies duplicate.
- Wrong match: reject/defer with a reason. Final review persists for unchanged evidence; materially changed evidence links a new review rather than erasing the prior decision.
- Ownership: one current assignment; a pending transfer leaves the source accountable. Group lead is a separate institutional responsibility.
- Privacy: scope-first API/search/counts/export and separately protected attachment bytes; administration gives no case access. Public demo accounts are synthetic only.
- Offline: installed local app/core rules need no paid model key; fresh dependency installation needs its package sources. No tested universal offline installer is claimed.
- Results:240generated cases/32institutions; generated-policy results are artificial. Both retrieval methods had recall@3=1 on40queries; vectors added no gain, so baseline is selected. No real accuracy claim.
- Integration: in-app database notifications and private local files are real. No official/email/semantic integration is simulated as a working external service.

## Backup and human gate

Actual backup `backup-ad79d704a15f43f980ab2e4c5078bfab` restored into `demo-30691bac975725b4bf3ef891`. Rows/originals/history/private hashes matched and source records remained unchanged; copied sessions are revoked on restore. The backup remains private under .demo-contexts/backups. No complaint or file was deleted. Storage audit is non-destructive.

Backup views include coordinated-plan-viewport.png, related-review.png, intake-pgrc.png, transfer-source-pending.png, transfer-accepted.png, management-report.png, printable-report.png and mobile captures in evidence/stage9. Captures show the real build and synthetic labels; virtual Nov1timestamps are explicitly caused by the isolated clock, while capture date is Oct27.

The user delegated judgement instead of supplying comprehension answers. Expected reading: Meera coordinates Pune, Kabir owns the RB refund, separate owners prepare their responses, and two students/different receipts for the same incident are RELATED. These are design expectations, not observations of an unfamiliar teammate. Independent label/usability review and official template/policy approval remain human gates. No selection outcome is promised.
