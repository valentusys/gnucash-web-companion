# Phase 210 — Bounded disposable write-alpha CRUD/restore refresh

Date: 2026-05-21
Status: COMPLETE — bounded local write-alpha create/PATCH/DELETE+restore evidence passed, then default read-only reset passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 9 only)

## Scope

Collected one fresh bounded write-alpha evidence pass after cycle-1 hardening using only the committed synthetic fixture copied through an external disposable source into ignored runtime data:

- source fixture class: committed synthetic test fixture copied to a temporary external disposable path
- runtime book class: ignored `data/books` copy
- backup class: ignored `data/backups` artifacts
- app DB class: ignored `data/app` runtime metadata
- lock class: ignored `data/locks` runtime lock file

No real/private/only-copy book was used. No package, image, tag, or release was published.

## Preflight

```text
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-disposable-source>
status=ready; book=<redacted.gnucash.sqlite>; reason=write-alpha copied-book preflight passed without copying or mutation; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
```

A broader `data/backups` preflight target failed closed as expected because the preflight requires a specific ignored backup child class, not the tracked parent directory.

## Write-enabled local runtime

The local Docker/Caddy runtime was started only with explicit local test-write settings:

```text
APP_ENV=test
GNUCASH_WRITES_ENABLED=true
JWT_SECRET=<dummy-local-secret>
APP_ADMIN_PASSWORD=<dummy-local-password>
ORIGIN=http://localhost:8080
```

A fresh ignored runtime copy was prepared from the external disposable source before each route-family smoke. The app metadata DB was runtime-only and ignored.

## Route-family evidence

### Create

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-create-smoke.py
PASS: write-alpha create smoke completed with redacted output
```

Evidence:

- health/books/accounts/read-back routes passed
- validation rejected unbalanced and invalid-account probes safely
- placeholder-style validation probe rejected without a real placeholder account
- exactly one balanced two-split create succeeded on the prepared runtime copy
- backup count increased before mutation response returned
- successful `transaction.create` audit count increased by exactly one
- lock evidence: `stale_released`, not actively held

### PATCH

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-patch-smoke.py
PASS: write-alpha PATCH smoke completed with redacted output
```

Evidence:

- health/books/read-only transaction detail routes passed
- missing-transaction PATCH returned 404 without a new backup
- exactly one metadata/split-memo PATCH succeeded on the prepared runtime copy
- API and runtime SQLite read-back matched synthetic PATCH markers only
- split amount fingerprint was unchanged
- backup count increased before mutation response returned
- successful `transaction.patch` audit count increased by exactly one
- failed safe-error PATCH audit was recorded
- lock evidence: `stale_released`, not actively held

### DELETE + restore

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/write-alpha-delete-restore-smoke.py
PASS: write-alpha DELETE restore smoke completed with redacted output
```

Evidence:

- health/books/read-only transaction detail routes passed before DELETE
- exactly one existing synthetic transaction DELETE succeeded on the prepared runtime copy
- API and runtime SQLite absence checks confirmed the transaction was deleted
- backup count increased by exactly one before mutation response returned
- successful `transaction.delete` audit count increased by exactly one
- backup contained the deleted transaction with matching bounded split fingerprint
- host-readable backup restore proof was performed and restored API read-back passed
- lock evidence: `stale_released`, not actively held

## Reset to default false

After the write-enabled route-family smokes, the stack was stopped and restarted without `GNUCASH_WRITES_ENABLED=true`.

Rendered config check:

```text
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

Read-only API smoke after reset:

```text
SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/read-only-api-smoke.py
PASS: read-only API smoke checks completed
```

Covered health, login, `/auth/me`, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, scheduled transactions, write-alpha audit summary, and validate/create/PATCH/DELETE probes returning 403.

## Cleanup

Post-smoke cleanup stopped Docker/Caddy and removed ignored runtime artifacts:

- ignored runtime book removed
- ignored backup artifacts removed
- ignored stale lock removed
- generated ignored smoke app DB removed
- pre-existing ignored local `data/app/app.db` was restored and remains untracked local state
- no `.env`, backup, book, app DB, token, key, cert, screenshot, export, or raw runtime artifact was staged

The stopped-runtime cleanup helper needed `--via-compose` fallback for root-owned ignored backup artifacts; the fallback removed the backup and stale lock with redacted output.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The write-enabled run was explicit local `APP_ENV=test` only and used disposable synthetic copies in ignored runtime paths. This evidence does not claim production safety, security audit coverage, broad GnuCash compatibility, or safety for real/private/only-copy books.

No raw account names, memos, transaction descriptions, amounts, backup paths, private paths, app DB contents, cookies, tokens, or book artifacts are committed in this evidence.
