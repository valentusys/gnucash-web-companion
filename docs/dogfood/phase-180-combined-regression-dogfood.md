# Phase 180 — combined read-only plus write-alpha regression dogfood

Date: 2026-05-20
Status: COMPLETE — combined regression pass completed without release publication
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 9 only)

## Scope

This phase re-ran the combined regression dogfood after the Phase 175–179 write-alpha dogfood and safety fixes, while preserving the default read-only posture.

It used only the committed synthetic fixture copied into ignored runtime paths:

- source fixture: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- runtime book class: ignored `data/books/main.gnucash.sqlite`;
- app DB/backup/lock classes: ignored `data/app/`, `data/backups/`, and `data/locks/`;
- read-only runs: `APP_ENV=test` with default `GNUCASH_WRITES_ENABLED=false`;
- write-alpha run: `APP_ENV=test` plus explicit local-only `GNUCASH_WRITES_ENABLED=true`.

No private, real, or only-copy book was used. No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data is committed.

## Default read-only Docker/Caddy dogfood

Default rendered Compose config was checked before the read-only run:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

Local Docker/Caddy was then started with the default write-disabled configuration. `/api/health` reported `writes_enabled=false` and the default synthetic book was present/readable.

API smoke result:

```text
read-only API smoke: target=http://localhost:8080/api
ok: API health
ok: login
ok: /auth/me
ok: default book discovered via /books and verified at /books/1
ok: accounts endpoint
ok: transactions endpoint
ok: transaction detail endpoint
ok: CSV export endpoint
ok: reports summary
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
PASS: read-only API smoke checks completed
```

Browser dogfood result at mobile viewport `320x720`:

```text
read-only browser dogfood: target=http://localhost:8080
ok: mobile_viewport: 320x720
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: dashboard: /dashboard loaded; write UI hidden
ok: accounts: /accounts loaded; write UI hidden
ok: books: /books loaded; write UI hidden
ok: scheduled: /scheduled loaded; write UI hidden
ok: account_detail: first account detail loaded
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: transaction_detail: first transaction detail loaded
ok: csv_export: status=200 total=0 truncated=false
ok: no_artifacts: no screenshots/downloads/CSV files written
PASS: read-only browser dogfood completed
```

The API smoke covered disabled validate/create/PATCH/DELETE probes and all returned HTTP 403 with read-only/write-disabled detail.

## Explicit write-alpha disposable smoke

Because Phases 175–179 included write-alpha dogfood changes/fixes, this phase also ran the synthetic/disposable write-alpha smoke with an explicit writes-enabled override.

Explicit write-alpha rendered Compose config:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "true"
65:      GNUCASH_WRITES_ENABLED: "true"
```

`/api/health` reported `writes_enabled=true` only for this explicit local run.

`scripts/smoke/write-alpha-create-smoke.py` executed the validation and create path against the disposable runtime book. The helper reached its final host-side lock-file readability check and hit the known Docker/root-owned lock-file limitation from the phase-execution runbook:

```text
FAIL: lock file is not readable by this smoke user; run from the API container or fix permissions
```

No rerun was performed to avoid creating a second transaction. Container-side redacted inspection showed the already-executed write-alpha operation succeeded and the remaining lock file was not actively held:

```text
app_db_exists True
audit_rows 1
audit transaction.create {'action': 'transaction.create', 'transaction_id': '<redacted>', 'timestamp': '2026-05-20T03:25:04.533194+00:00', 'request_summary': {'date': '2026-05-20', 'description': 'Write-alpha create smoke disposable transaction', 'split_count': 2, 'currencies': ['SEK']}, 'backup_path': '<redacted>', 'result': 'success'}
backup_files 1
lock_files 1
lock_active_hold False
```

Interpretation: the disposable write-alpha create smoke succeeded through validation, create, read-back, backup, and audit checks; only the host-side stale-lock readability probe was blocked by container file ownership. Lock release was verified from inside the API container without printing raw paths.

## Return to default read-only posture

After the explicit write-alpha run, the stack was stopped and restarted without `GNUCASH_WRITES_ENABLED=true`. Rendered Compose config again showed the default false values:

```text
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

`/api/health` reported `writes_enabled=false`, and a second read-only API smoke passed against the disposable runtime book with validate/create/PATCH/DELETE probes returning 403.

## Teardown and artifact hygiene

After verification:

- Docker/Caddy containers and the Compose network were stopped/removed;
- ignored runtime book/app DB/backups/locks were removed;
- final runtime file listing under `data/` showed only placeholder `.gitkeep` content;
- `.hermes/` remained untracked/ignored and was not staged;
- no raw screenshot/download/CSV/book/backup/app DB artifact was committed.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The only write-enabled run was explicit, local, `APP_ENV=test`, synthetic/disposable, and temporary. This phase did not publish a release/tag and does not claim production readiness, broad Desktop compatibility, or write safety for real/private/only-copy books.
