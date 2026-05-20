# Phase 177 — write-alpha backup and restore drill

Date: 2026-05-20
Status: COMPLETE — disposable backup restore drill passed; no private/real book used
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 6 only)

## Goal

Prove that a disposable write-alpha backup can restore the pre-write book state after a Phase 4-style create mutation.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-176.md`;
  - roadmap file named by the phase contract;
  - Phase 175/176 dogfood evidence, write-alpha create smoke helper, read-only API smoke helper, and backup service behavior.
- Recreated a safe Phase 4-style write-alpha create run from the committed synthetic fixture only because prior runtime backup files were intentionally removed after earlier phases.
- Used the generated pre-write backup from that run, restored it to an ignored disposable path, and restarted the app in read-only/default-write-disabled mode against the restored copy.
- Verified checksum relationship, transaction absence, read-only API smoke, disabled write probes, and file-lock/audit expectations.
- Removed ignored runtime book/app DB/backup/lock artifacts after verification.

## Files changed

- `docs/dogfood/phase-177-write-alpha-backup-restore-drill.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-177.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `GNUCASH_WRITES_ENABLED=true` was used only as an explicit local runtime override with `APP_ENV=test`.
- Runtime, backup, restored book, app DB, and lock paths were under ignored `data/` runtime storage and were removed after the run.
- No real/private/only-copy book was opened or mutated.
- No PATCH or DELETE dogfood was run.
- No release/tag/package was published.
- No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data was committed.

## Verification

Commands run:

```bash
python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy <temporary external synthetic copy>
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/write-alpha-create-smoke.py
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose exec -T api <redacted audit/backup/lock/restore probe>
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose down --remove-orphans
APP_ENV=test GNUCASH_DEFAULT_BOOK_PATH=/data/books/restored-phase177.gnucash.sqlite JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy ORIGIN=http://localhost:8080 docker compose up --build -d
SMOKE_ADMIN_PASSWORD=<local dummy> python3 scripts/smoke/read-only-api-smoke.py
python3 <redacted API transaction-absence probe>
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
APP_ENV=test GNUCASH_DEFAULT_BOOK_PATH=/data/books/restored-phase177.gnucash.sqlite JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down --remove-orphans
```

Results:

- Source preflight passed with redacted summary only: `sha256_12=c8f22b449c49`.
- Exactly one write-alpha create was performed on an ignored disposable runtime copy.
- One pre-write backup was generated under ignored backup storage: `backup_sha256_12=c8f22b449c49`, size `212992` bytes.
- Mutated disposable copy checksum differed: `sha256_12=e502ac9ac38f`.
- Restored copy checksum matched the backup: `sha256_12=c8f22b449c49`; local copy time was `0.43 ms`.
- Transaction-absence probe against the restored read-only deployment returned zero matches for the synthetic create marker.
- Read-only API smoke passed with default writes disabled, including validate/create/PATCH/DELETE probes returning 403.
- Default Compose config still renders `GNUCASH_WRITES_ENABLED: "false"`.
- Lock file behavior is understood: the implementation can leave a stale lock path after release, but an in-container flock probe showed it was not actively held.
- Ignored runtime artifacts were removed from `data/books`, `data/backups`, `data/app/app.db`, and `data/locks`.

## Next

Continue only with the next explicitly requested phase. Do not run UX/API hardening, combined regression dogfood, release-readiness gate, release/tag publication, PATCH dogfood, DELETE dogfood, or private-book disaster recovery unless a later phase explicitly requests it.
