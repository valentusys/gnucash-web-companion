# Phase 230 — Cycle 3 release-candidate dogfood pack

Date: 2026-05-21
Status: PASS — final release-candidate dogfood evidence is green for a later `v0.2.5-writealpha` attempt, subject to Phase 10 release gate and explicit publication authorization.
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 9 only)

## Scope

This phase produced the final release-candidate evidence pack after the backup/audit remediation cycle.

Covered:

- full Docker/Caddy default-read-only API smoke with `GNUCASH_WRITES_ENABLED=false`;
- full Docker/Caddy browser dogfood at mobile `320x720` and desktop `1280x900` with `GNUCASH_WRITES_ENABLED=false`;
- separate explicit local-only write-alpha create, PATCH, and DELETE smokes with `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` on ignored synthetic/disposable runtime copies;
- DELETE backup restore proof;
- reset to default `GNUCASH_WRITES_ENABLED=false` and disabled-write API smoke after write-alpha runs;
- stopped-runtime cleanup/no-artifact checks.

Non-goals preserved: no new feature work, no release publication, no real/private/only-copy book, no broad compatibility claim, no production/security/write-safety claim.

## Inputs and safety boundaries

The runs used only:

- committed synthetic fixture source: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- external temporary disposable copies for write-alpha provenance;
- ignored runtime copies under `data/books/`;
- ignored app DB, backup, and lock storage under `data/`;
- dummy local-only admin password and JWT secret values, redacted here;
- Docker/Caddy with explicit env values per run.

`GNUCASH_WRITES_ENABLED=false` remained the default before and after write-alpha. Write-alpha was enabled only for bounded local `APP_ENV=test` route-family smokes. `APP_ENV=test` gating was not weakened.

No raw runtime book, app DB, backup, lock, `.env`, screenshot, CSV download/export, token, key, cert, private path, account name, memo, amount, or private financial data is committed.

## Default-read-only Docker/Caddy evidence

Rendered config validation passed with dummy local-only placeholders and the committed synthetic fixture copied into ignored runtime storage:

```text
api: GNUCASH_WRITES_ENABLED: "false"
web: GNUCASH_WRITES_ENABLED: "false"
```

`SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py` passed against Docker/Caddy.

Covered checks:

- `/health` returned `status=ok`;
- login/auth and `/auth/me` passed;
- `/books` discovered and `/books/{bookId}` verified the default book;
- accounts endpoint passed;
- transactions list and transaction detail passed;
- CSV export fetch succeeded in memory without saving a raw CSV artifact;
- reports summary passed;
- scheduled transaction metadata passed;
- write-alpha audit summary passed as read-only app-metadata endpoint;
- disabled write probes returned 403 for validate, create, PATCH, and DELETE.

Result:

```text
PASS: read-only API smoke checks completed
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
```

## Browser dogfood evidence

`SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080` passed at both required viewports.

Mobile viewport:

```text
viewport=320x720
PASS: login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV fetch, hidden write UI, auth cookie not readable from document.cookie, no horizontal overflow, no screenshots/downloads/CSV artifacts
```

Observed no-overflow examples:

```text
dashboard: scrollWidth=320 clientWidth=320
accounts: scrollWidth=320 clientWidth=320
books: scrollWidth=320 clientWidth=320
scheduled: scrollWidth=320 clientWidth=320
transactions_filters: scrollWidth=320 clientWidth=320
transaction_detail: scrollWidth=320 clientWidth=320
```

Desktop viewport:

```text
viewport=1280x900
PASS: login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV fetch, hidden write UI, auth cookie not readable from document.cookie, no horizontal overflow, no screenshots/downloads/CSV artifacts
```

Observed no-overflow examples:

```text
dashboard: scrollWidth=1265 clientWidth=1265
accounts: scrollWidth=1265 clientWidth=1265
books: scrollWidth=1265 clientWidth=1265
scheduled: scrollWidth=1265 clientWidth=1265
transactions_filters: scrollWidth=1265 clientWidth=1265
transaction_detail: scrollWidth=1280 clientWidth=1280
```

## Write-alpha evidence matrix

Each route family used a fresh external temporary disposable copy and a fresh ignored runtime copy under `data/books/main.gnucash.sqlite`. The preflight helper reported the same committed synthetic fixture checksum prefix for each external disposable copy and did not copy, open with piecash, or mutate the candidate during preflight.

```text
status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; size_bytes=212992; sha256_12=c8f22b449c49; dry_run=true
```

| Route family | Successful routed write | Read-back / restore evidence | Backup evidence | Audit evidence | Expected failed probes | Lock evidence | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| create | exactly one balanced two-split create succeeded | API read-back passed | backup count increased by exactly one before mutation response returned | success audit count increased by exactly one | unbalanced, invalid-account, and placeholder-style validation probes rejected before mutation | stale-released, not active | PASS |
| PATCH | exactly one metadata/split-memo PATCH succeeded | API and runtime SQLite read-back matched synthetic markers; split amount fingerprint unchanged | backup count increased by exactly one before mutation response returned | success audit count increased by exactly one and failed safe-error audit was recorded | missing-transaction PATCH returned 404 without a new backup | stale-released, not active | PASS |
| DELETE | exactly one existing synthetic transaction DELETE succeeded | API/runtime absence checks passed; host-readable backup restore and restored API read-back passed | backup count increased by exactly one before mutation response returned | success audit count increased by exactly one | no extra DELETE failure probe; successful DELETE was not rerun | stale-released, not active | PASS |

DELETE restore proof:

```text
ok: backup contained the deleted transaction with matching bounded split fingerprint
ok: restore proof performed on host-readable backup and restored API read-back passed
```

No write-alpha anomaly appeared. No successful mutation was rerun after evidence collection.

## Default false reset and cleanup

After write-alpha route-family smokes, Docker/Caddy was reset to default disabled writes with the committed synthetic fixture copied into ignored runtime storage.

Rendered reset config:

```text
api: GNUCASH_WRITES_ENABLED: "false"
web: GNUCASH_WRITES_ENABLED: "false"
```

Reset read-only API smoke passed again:

```text
PASS: read-only API smoke checks completed
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
ok: delete endpoint is write-disabled
```

Stopped-runtime cleanup removed ignored runtime artifacts after each write-alpha run and after final reset. Final no-artifact dry-run:

```text
books=0, app=0, backups=0, locks=0
```

## Commands run

```bash
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-230-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-230-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-230-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --viewport-width 320 --viewport-height 720
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --viewport-width 1280 --viewport-height 900
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-create-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-create-smoke.py
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-PATCH-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-patch-smoke.py
python3 apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan --dry-run --confirm-disposable-copy --runtime-book data/books/main.gnucash.sqlite --backup-dir data/backups/write-alpha-dogfood <external-DELETE-disposable-copy>
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> APP_ENV=test GNUCASH_WRITES_ENABLED=true ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite docker compose up -d
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://127.0.0.1:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-230-reset-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config --quiet
SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED --execute --via-compose
python3 scripts/ops/runtime-cleanup.py --ack I_CONFIRM_RUNTIME_STOPPED
```

## Release input for Phase 10

Release-candidate dogfood verdict: green input for Phase 10.

Phase 10 must still run the full release gate, update release artifacts, confirm tag/release absence, verify exact pushed commit/CI as required, and publish only if explicitly authorized and all gates remain green. This phase did not create a tag or GitHub release.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains default. `APP_ENV=test` was not weakened. Write-alpha evidence is limited to synthetic/disposable ignored runtime copies. No real/private/only-copy book was used. No release, tag, package, image, production/security claim, broad compatibility claim, or real/private-book write-safety claim was added.
