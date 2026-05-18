# Phase 63 Audit — Backup/Recovery

## Executive summary

Phase 63 audited backup and recovery documentation against the auditor roadmap. The backup/recovery runbook exists, is conservative, and covers app metadata backups, copied GnuCash SQL book backups, controlled-write pre-write backups, dry-run restore, read-only verification after restore, and explicit limitations.

Verdict: no release-blocking backup/recovery blocker was found. One documentation defect was found: two docs used `docker compose config | grep 'GNUCASH_WRITES_ENABLED=false'`, but current Compose output renders the value as `GNUCASH_WRITES_ENABLED: "false"`. This can make a safe verification command fail even when writes are disabled. The finding is accepted as a safe docs fix in Phase 63 rather than a new GitHub issue.

This phase does not unblock `v0.1.0-readonly` publication because prior blockers #24 and #25 remain open.

## Verdict

Backup/recovery documentation is acceptable for cautious local/private read-only testing after the accepted grep-command docs fix. No Phase 63 backup/recovery blocker remains.

## Blockers

None found in the Phase 63 backup/recovery scope.

Carried forward from previous phases and still release-blocking before any `v0.1.0-readonly` publication:

1. GitHub #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. GitHub #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

## Non-blockers

1. `docs/operations/backup-and-recovery.md` and `docs/deployment/local-secure-deployment.md` used a stale exact grep example for confirming `GNUCASH_WRITES_ENABLED=false`. Actual Compose V2 output observed during this audit is `GNUCASH_WRITES_ENABLED: "false"`. This is a documentation reliability issue, not evidence that writes are enabled. It is safe to fix in Phase 63.
2. There is no restore UI or restore API. This is documented and acceptable for the read-only MVP; recovery remains an operator-run manual procedure.
3. The runbook intentionally does not provide production disaster recovery, off-site/encrypted backup tooling, point-in-time recovery, retention, or live-backup guarantees. This limitation is explicit and not a blocker for the current pre-alpha/read-only posture.

## Phase 63 audit checks

| Roadmap check | Evidence found | Result |
| --- | --- | --- |
| Backing up GnuCash book | `docs/operations/backup-and-recovery.md` documents backing up copied GnuCash books under `data/books/` and keeping authoritative originals outside the repo. README and deployment docs tell users to use copied/disposable books first. | Pass |
| Backing up app metadata DB | Runbook documents `./data/app/app.db` / `/data/app/app.db`, backup frequency, manual copy procedure, and SQLite integrity check. | Pass |
| Backing up before write mode | Runbook documents experimental controlled-write pre-write backups under `data/backups/<book_id>/`, says writes are post-MVP/experimental, and says never use write mode against an only authoritative book. | Pass |
| Restoring a book | Runbook documents dry-run workspace, moving current `data` aside, copying verified backup data back into `data/app`, `data/books`, `data/backups`, and recreating `data/locks`. | Pass with docs-fix finding |
| Verifying restored book can be read | Runbook instructs running the read-only smoke script after restore and lists manual UI verification. Backend `apps/api/tests/test_backup_restore.py` also verifies backup files open read-only and restored copied fixture state is recoverable. | Pass |
| Limitations of backup system | Runbook explicitly says it is not production-grade DR, encrypted/off-site backup, retention/rotation, point-in-time recovery, live-copy consistency, all-version/all-backend compatibility, or safe write-mode guarantee. | Pass |
| No guarantee of production disaster recovery | Runbook line 3 and limitations section explicitly avoid production DR guarantees. README remains pre-alpha/not production-ready. | Pass |

## Product consistency

Checked files and state:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `.env.example`
- `docker-compose.yml`
- `apps/api/app/config.py`
- `apps/api/tests/test_backup_restore.py`
- `docs/operations/backup-and-recovery.md`
- `docs/deployment/local-secure-deployment.md`
- `docs/GNUCASH_SAFETY.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-62.md`
- auditor roadmap Phase 63 entry
- open GitHub issues via `gh issue list`

Findings:

- Public docs still position the project as pre-alpha, self-hosted, read-only by default, and not production-ready/security-audited.
- No inspected backup/recovery doc reframes the project as SaaS, a GnuCash replacement, collaborative accounting, production DR, or safe write-mode software.
- Phase 63 does not publish or approve `v0.1.0-readonly`; #24 and #25 remain release blockers.

## Safety boundary

Findings:

- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- `.env.example` and `docker-compose.yml` keep `GNUCASH_WRITES_ENABLED=false` as the default.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` showed `GNUCASH_WRITES_ENABLED: "false"` for both API and web services during this audit.
- Controlled writes remain documented as experimental/post-MVP only.
- GnuCash Desktop remains documented as the authoritative editor.
- No product code changed in this phase.
- No real GnuCash book, `.env`, app DB, backup, secret, key, cert, real screenshot, or real financial CSV export was added by this phase.

## Release/readme/docs consistency

README and PROJECT_STATUS should be updated to record Phase 63 as a backup/recovery audit and to link the latest audit artifact. This must not imply that v0.1 publication is approved or that production disaster recovery is guaranteed.

CHANGELOG may record the Phase 63 release-facing audit result because backup/recovery posture is relevant to future `v0.1.0-readonly` release notes and release gates.

## GitHub project hygiene

Open issues reviewed via `gh issue list`:

- #26 — CORS origin narrowing visibility.
- #25 — copied/disposable-data runtime smoke/dogfood gate.
- #24 — conservative v0.1 release notes.
- #22, #17, #13, #12, #11 — non-blocking backlog items.

Created: none.

Suggested: none for Phase 63 after the accepted docs fix. Creating an issue for a two-line docs command mismatch would be noise once fixed in this phase.

## Security notes

This was not a professional security audit. It was a backup/recovery documentation audit.

The inspected docs correctly warn that:

- the app is pre-alpha and not production-ready/security-audited;
- operators should use copied/disposable books first;
- authoritative GnuCash originals should remain outside the repo;
- `.env`, app DBs, copied books, backups, screenshots, CSV exports, logs with sensitive values, keys, certs, and real financial data must not be committed or attached to public reports;
- controlled writes are experimental and disabled by default;
- manual backup/restore does not provide production disaster recovery.

## Test/CI notes

Phase 63 is audit/status documentation work with a small safe documentation correction and no product-code changes. Because it reports a backup/recovery readiness verdict, the phase should run and record the standard checks:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

Final check results are recorded in `docs/handoff/phase-63.md`.

## Recommended next actions

1. Do not publish `v0.1.0-readonly` from Phase 63.
2. Apply the accepted docs fix so write-disabled verification commands match Compose V2 output.
3. Update README/PROJECT_STATUS/handoff to record the Phase 63 backup/recovery audit result.
4. Keep #24 and #25 as release blockers before v0.1 publication.
5. Keep backup/recovery language conservative: manual/operator-run, copied/disposable data first, no production DR guarantee.

## Suggested GitHub issues

Created: none.

Suggested: none for Phase 63 after the accepted documentation fix.

Existing release blockers remain:

1. #24 — Prepare conservative v0.1.0-readonly release notes before publication.
2. #25 — Complete v0.1 read-only runtime smoke/dogfood gate on copied or disposable data.

## What not to do next

- Do not publish a `v0.1.0-readonly` tag or GitHub release from Phase 63.
- Do not claim production-grade backup/disaster recovery.
- Do not add restore UI/API or write-scope work in this audit phase.
- Do not enable or expand controlled writes.
- Do not weaken the copied/disposable-book and external-backup guidance.
- Do not commit `.env`, copied books, app DBs, backups, screenshots, CSV exports, secrets, keys, tokens, or certs.
- Do not start Phase 64 without an explicit request.
