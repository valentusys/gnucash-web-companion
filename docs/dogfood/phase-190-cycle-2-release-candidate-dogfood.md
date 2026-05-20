# Phase 190 — cycle-2 release-candidate dogfood

Date: 2026-05-20
Status: COMPLETE — combined default read-only and bounded write-alpha release-candidate dogfood completed without release publication
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 9 only)

## Scope

This phase gathered final practical evidence after cycle-2 Phases 183–189. It used only the committed synthetic fixture copied into ignored runtime paths:

- source fixture: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- runtime book class: ignored `data/books/main.gnucash.sqlite`;
- app DB/backup/lock classes: ignored `data/app/`, `data/backups/`, and `data/locks/`;
- default read-only runs: `APP_ENV=test` with default `GNUCASH_WRITES_ENABLED=false`;
- write-alpha runs: explicit local-only `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true`.

No private, real, or only-copy book was used. No raw book, app DB, backup, `.env`, token, key, cert, screenshot, CSV export, account name, transaction description, memo, amount, private path, or private financial data is committed.

## Default read-only Docker/Caddy dogfood

Default rendered Compose config was checked before the read-only run:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

Local Docker/Caddy was started with the default write-disabled configuration against the synthetic runtime copy.

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
fixture: filename=test-book.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
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

Browser dogfood result at desktop viewport `1280x900`:

```text
read-only browser dogfood: target=http://localhost:8080
fixture: filename=test-book.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: mobile_viewport: 1280x900
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

Because cycle-2 changed or revalidated the write-alpha restore, PATCH, DELETE, audit-summary, and regression evidence paths, this phase ran bounded write-alpha smokes for the touched create/PATCH/DELETE route family. Each write-enabled run was local-only, synthetic/disposable, separate from the default read-only runs, and started with explicit rendered config:

```text
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://localhost:8080 docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "true"
65:      GNUCASH_WRITES_ENABLED: "true"
```

Create smoke:

- `scripts/smoke/write-alpha-create-smoke.py` reached the known host-side root-owned lock-file readability limitation after the route completed.
- The helper was not rerun, to avoid creating a second transaction.
- Container-side redacted inspection confirmed:
  - app DB existed;
  - one `transaction.create` audit row had `result=success`;
  - the audit row had a transaction id and backup evidence;
  - one backup file existed;
  - one lock file existed but `lock_active_hold=False`.

PATCH smoke on a fresh disposable runtime copy:

- `scripts/smoke/write-alpha-patch-smoke.py` reached the same host-side lock-file readability limitation after the route completed.
- Container-side redacted inspection confirmed:
  - one safe missing-transaction `transaction.patch` failed audit row without backup evidence;
  - one successful `transaction.patch` audit row with transaction id and backup evidence;
  - one backup file existed;
  - one lock file existed but `lock_active_hold=False`.

DELETE smoke on a fresh disposable runtime copy:

- `python3 scripts/smoke/write-alpha-delete-restore-smoke.py` executed the DELETE route, then stopped at host-side backup-file readability during the helper's restore proof.
- The helper was not rerun.
- Container-side redacted inspection confirmed:
  - one successful `transaction.delete` audit row with transaction id and backup evidence;
  - one backup file existed;
  - one lock file existed but `lock_active_hold=False`.

Interpretation: create/PATCH/DELETE route execution, audit, backup, and lock-release evidence were collected from synthetic/disposable runtime data only. Host-side root-owned runtime file readability remains an operator workflow limitation already documented by prior phases; it did not show an active lock hold and did not require a rerun.

## Return to default read-only posture

After the explicit write-alpha runs, the stack was stopped, ignored runtime data was cleaned, the synthetic fixture was recopied, and the stack was restarted without `GNUCASH_WRITES_ENABLED=true`. Rendered Compose config again showed the default false values:

```text
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"
```

A final default read-only API smoke passed, including validate/create/PATCH/DELETE probes returning 403.

## Teardown and artifact hygiene

After verification:

- Docker/Caddy containers and the Compose network were stopped/removed;
- ignored runtime book/app DB/backups/locks were removed with a one-shot container because runtime files can be root-owned;
- final runtime file listing under `data/books`, `data/app`, `data/backups`, and `data/locks` showed zero non-placeholder runtime files;
- `.hermes/` remained untracked/ignored and was not staged;
- no raw screenshot/download/CSV/book/backup/app DB artifact was committed.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains the default. The only write-enabled runs were explicit, local, `APP_ENV=test`, synthetic/disposable, and temporary. This phase did not publish a release/tag and does not claim production readiness, a security audit, broad Desktop compatibility, or write safety for real/private/only-copy books.

## Final repository checks

```text
cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py tests/test_write_lock.py tests/test_write_alpha_smoke_lock_evidence.py -q
86 passed

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"

git diff --check
passed

sensitive tracked-file hygiene scan
passed
```
