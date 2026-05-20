# Phase 200 — Write-alpha cycle-3 disposable CRUD/restore dogfood

Date: 2026-05-20
Status: COMPLETE — synthetic/disposable local write-alpha create/PATCH/DELETE route-family smokes passed once per prepared copy; default read-only reset passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 9 only)

## Goal

Collect final cycle-3 write-alpha evidence after helper/UX fixes on synthetic/disposable data only: create, PATCH, DELETE, audit, backup, lock, restore where actually completed, and return the stack to default `GNUCASH_WRITES_ENABLED=false`.

## Scope executed

- Used only the committed synthetic fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite` copied into ignored runtime data as `data/books/main.gnucash.sqlite`.
- Preflighted an external disposable source copy with the write-alpha dogfood preflight helper; output was path-redacted and confirmed external source, ignored runtime class, ignored backup class, and dry-run/no-copy/no-mutation status.
- Ran explicit local-only Docker/Caddy runtime with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` only for write-alpha smokes.
- Reset ignored runtime data and prepared a fresh synthetic runtime copy before each route-family smoke.
- Executed exactly one mutating route-family smoke per prepared copy:
  - create smoke;
  - PATCH smoke;
  - DELETE+restore smoke.
- Inspected audit, backup, and lock evidence through the resilient smoke helpers, including container-side fallback capability. No active lock remained after any route-family smoke.
- Restored only where actually completed: DELETE restore proof completed from a host-readable backup and read-back passed.
- Returned the stack to default write-disabled mode, rendered `GNUCASH_WRITES_ENABLED=false`, ran read-only API smoke, and verified disabled validate/create/PATCH/DELETE probes returned 403.
- Stopped Docker/Caddy, removed ignored runtime artifacts, and removed local dummy `.env`.

## Redacted evidence

### Preflight / config

```text
write-alpha preflight: status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; dry_run=true
write-enabled local config: GNUCASH_WRITES_ENABLED: "true" for API and web only during explicit APP_ENV=test disposable runs
```

The initial preflight attempt using the backup root itself was blocked because the path class was too broad; it was immediately corrected to the ignored `data/backups/write-alpha-dogfood` class. No copy or mutation occurred during the blocked dry-run.

### Create route family

```text
PASS: write-alpha create smoke completed with redacted output
ok: validation rejected unbalanced and invalid account probes
ok: placeholder-style validation probe rejected without using a real placeholder account
ok: exactly one balanced two-split create succeeded
ok: backup count increased before mutation response returned
ok: audit success count increased by exactly one
ok: write lock evidence status=stale_released; active=false
```

### PATCH route family

```text
PASS: write-alpha PATCH smoke completed with redacted output
ok: missing-transaction PATCH returned 404 without a new backup
ok: exactly one metadata/split-memo PATCH succeeded
ok: API read-back matched synthetic PATCH markers only
ok: runtime SQLite read-back matched markers and split amount fingerprint was unchanged
ok: backup count increased before mutation response returned
ok: audit success count increased by exactly one and failed safe-error audit was recorded
ok: write lock evidence status=stale_released; active=false
```

### DELETE route family and restore proof

```text
PASS: write-alpha DELETE restore smoke completed with redacted output
ok: exactly one existing synthetic transaction DELETE succeeded
ok: API and runtime SQLite absence checks confirmed transaction was deleted
ok: backup count increased by exactly one before mutation response returned
ok: audit success count increased by exactly one
ok: backup contained the deleted transaction with matching bounded split fingerprint
ok: restore proof performed on host-readable backup and restored API read-back passed
ok: write lock evidence status=stale_released; active=false
```

### Default-false reset

```text
GNUCASH_WRITES_ENABLED: "false" rendered for API and web after reset
PASS: read-only API smoke checks completed
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
```

### Teardown

```text
data/books: non_placeholder_files=0
data/app: non_placeholder_files=0
data/backups: non_placeholder_files=0
data/locks: non_placeholder_files=0
```

## Verification commands

```text
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-create-smoke.py
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-patch-smoke.py
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
```

Additional final verification is recorded in `docs/handoff/phase-200.md`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was rendered after the write-alpha smokes.
- Write-enabled mode was local-only, explicit, `APP_ENV=test`, and used only ignored disposable runtime copies.
- No real/private/only-copy book was used.
- No write route was expanded and no production write-safety claim is made.
- No release, tag, package, or image was published.
- No raw path, account name, transaction description, memo, amount, cookie, token, app DB row, backup filename, screenshot, export, runtime book, app DB, backup, lock artifact, `.env`, secret, key, or cert was committed.

## Risks / follow-up

- Evidence is synthetic/disposable local pre-alpha write-alpha evidence only; it is not production readiness, a security audit, or a real/private-book write-safety claim.
- Lock files can remain as stale released files after route execution; Phase 200 evidence confirms they were not actively held, and cleanup remains stopped-runtime only.
