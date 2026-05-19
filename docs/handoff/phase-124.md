# Phase 124 — Write-alpha controlled transaction create hardening

Date: 2026-05-19
Status: complete
Previous phase: `docs/handoff/phase-123.md`

## Goal

Harden and complete the first controlled transaction create safety flow for write-alpha only: explicit write flag, copied/disposable fixture, backup, lock, validation, piecash write, audit, and default read-only posture.

## Scope completed

- Started from clean `main` in sync with `origin/main` at `7be432de7403fbe7a97ab1a87a2495245d03e848`.
- Reviewed `AGENTS.md`, `PROJECT_STATUS.md`, and recent handoff files before changing code.
- Inspected existing create/validate/patch route implementation, `GnuCashWriteService`, write DTOs, backup service, and existing write tests.
- Added `_ensure_write_alpha_test_scope(settings)` to the write routes in `apps/api/app/routers/transactions.py`.
  - `POST /books/{book_id}/transactions/validate`
  - `POST /books/{book_id}/transactions`
  - `PATCH /books/{book_id}/transactions/{transaction_id}`
- Preserved the existing default-disabled guard first: with `GNUCASH_WRITES_ENABLED=false`, write routes still 403 before book resolution or write-service construction.
- Added an additional enabled-mode safety gate: even with `GNUCASH_WRITES_ENABLED=true`, routed write-alpha execution requires `APP_ENV=test`; non-test environments return 403 before constructing a write service.
- Added route-level copied/disposable fixture coverage in `apps/api/tests/test_transaction_writes.py`:
  - copies `tests/fixtures/test-book.gnucash.sqlite` into `tmp_path` per test;
  - creates a transaction through the API route with `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`;
  - reloads the disposable book through the read-only service and verifies the created transaction/split state;
  - verifies a pre-write backup file exists;
  - verifies a successful audit log row includes operation, status, transaction id, and backup path;
  - verifies the per-book `.lock` file is not left locked after success;
  - verifies validation failures are audited as failed attempts with no backup path and no lock leak.
- Updated controlled-write documentation/status:
  - `docs/v0.2-controlled-writes.md` now labels Phase 124 write-alpha route execution as test-environment-only copied/disposable fixture evidence.
  - `PROJECT_STATUS.md` now marks completion through Phase 124 and preserves default read-only positioning.
  - `CHANGELOG.md` records the Phase 124 safety hardening.

## Non-goals preserved

- No default write enablement.
- No real-book dogfood and no production-book write safety claim.
- No edit/delete/import/scheduled/account-write capability.
- No frontend write UI change.
- No release publication, tag creation, GitHub release, package, or uploaded artifact.
- No real/private book, app DB, backup, `.env`, screenshot, CSV export, secret, token, key, cert, private path, account name, transaction description, memo, amount, or personal financial data committed.

## Verification run

Targeted write-alpha tests:

```bash
cd apps/api && pytest tests/test_transaction_writes.py tests/test_write_integration.py -q
```

Result: passed — `73 passed, 28 warnings in 22.61s`.

Full backend regression suite:

```bash
cd apps/api && pytest -q
```

Result: passed — `361 passed, 28 warnings in 135.56s`.

Config/default/safety checks:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
cd apps/api && python - <<'PY'
from app.config import Settings
settings = Settings()
print(f"Settings.gnucash_writes_enabled={settings.gnucash_writes_enabled}")
PY
python - <<'PY'
import subprocess, sys
paths = subprocess.check_output(['git','diff','--name-only'], text=True).splitlines()
blocked_suffixes = ('.gnucash', '.gnucash.sqlite', '.db', '.sqlite', '.sqlite3', '.env', '.csv', '.png', '.jpg', '.jpeg', '.webp')
blocked_names = {'app.db'}
bad = [p for p in paths if p.split('/')[-1] in blocked_names or p.endswith(blocked_suffixes) or '/backups/' in p or '/screenshots/' in p]
print('changed_files=' + ','.join(paths))
print('sensitive_changed_files=' + (','.join(bad) if bad else 'none'))
if bad:
    sys.exit(1)
PY
```

Results:

- Docker Compose config validation: passed with no output.
- `git diff --check`: passed with no output.
- Config default proof: `Settings.gnucash_writes_enabled=False`.
- Sensitive changed-file scan: `sensitive_changed_files=none`.

Frontend checks/build were not run because Phase 124 touched no frontend code, routes, styles, or web dependencies.

## Safety notes

- `GNUCASH_WRITES_ENABLED=false` remains the default in code and runtime config expectations.
- Enabled write-alpha route execution is additionally restricted to `APP_ENV=test`.
- The new enabled create-route evidence uses only a copied disposable synthetic fixture under pytest `tmp_path`.
- Backup, lock, validation, piecash write, and audit are verified for the first controlled create route in test scope only.
- Remaining BLOCKED gaps before any real-user write enablement: maintainer review, broader supported-version write compatibility evidence, documented recovery/review procedure, explicit concurrency/error-path expansion, and explicit later authorization.

## Files changed

- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_writes.py`
- `docs/v0.2-controlled-writes.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-124.md`
