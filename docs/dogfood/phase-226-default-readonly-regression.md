# Phase 226 — Default read-only regression after write-alpha remediation

Date: 2026-05-21
Status: PASS — full Docker/Caddy default-read-only synthetic regression passed after write-alpha backup/evidence remediation
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 5 only)

## Scope

This phase verified that the Phase 222–225 write-alpha backup/evidence remediation did not regress the default read-only product path.

The run used only:

- committed synthetic fixture source: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- ignored runtime copy: `data/books/phase-226-synthetic.gnucash.sqlite`;
- Docker/Caddy with `GNUCASH_WRITES_ENABLED=false` for API and web;
- dummy local-only admin credentials and JWT secret placeholders;
- no write-enabled run.

No real/private or only-copy book was used. No screenshot, raw CSV download/export artifact, runtime book, app DB, backup, `.env`, token, cookie, key, cert, private path, account name, memo, amount, or private financial data is committed here.

## Rendered default-read-only config

Docker Compose config validation passed with dummy local-only placeholders. Rendered service environment showed writes disabled in both API and web services:

```text
api: GNUCASH_WRITES_ENABLED: "false"
web: GNUCASH_WRITES_ENABLED: "false"
```

## API smoke evidence

`SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py` passed against `http://localhost:8080/api`.

Covered checks:

- `/health` returned `status=ok`;
- login/auth and `/auth/me` passed;
- `/books` discovered and `/books/{bookId}` verified the default book;
- accounts endpoint passed;
- transactions list passed;
- transaction detail passed;
- CSV export fetch succeeded in memory and validated headers without saving a raw CSV artifact;
- reports summary passed;
- scheduled transaction metadata passed without unsafe template/source fields;
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

`SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py` passed at both required viewports.

### Mobile viewport

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

### Desktop viewport

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

The browser helper fetched CSV through `fetch(..., { credentials: 'same-origin' })`, checked HTTP 200 and CSV headers, and did not allow downloads or persist an export artifact.

## Cleanup / no-artifact check

After smoke, Docker Compose was stopped and stopped-runtime cleanup ran:

```text
before cleanup: books=1, app=1, backups=0, locks=0
cleanup removed ignored runtime artifacts
final dry-run: books=0, app=0, backups=0, locks=0
```

Only tracked documentation/status changes were left for this phase; untracked `.hermes/` remained excluded.

## Safety result

- `GNUCASH_WRITES_ENABLED=false` remained the default and rendered runtime value.
- No write-enabled run was performed.
- `APP_ENV=test` was not weakened or required for this read-only smoke.
- Runtime used a committed synthetic fixture copied into ignored `data/books/`.
- Dummy local-only secrets/passwords are redacted in committed docs.
- No raw runtime book, app DB, backup, screenshot, download, export, `.env`, token, key, cert, or private data artifact is committed.

## Verification summary

Passed:

- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-226-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config --quiet`
- rendered Compose grep for `GNUCASH_WRITES_ENABLED: "false"` in API and web services
- Docker/Caddy default-read-only startup with committed synthetic fixture copied into ignored runtime storage
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py`
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --viewport-width 320 --viewport-height 720`
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --viewport-width 1280 --viewport-height 900`
- stopped-runtime cleanup and final no-artifact dry-run

Standard checks are recorded in `docs/handoff/phase-226.md`.

## Release impact

The default read-only regression path is green after the write-alpha backup/evidence remediation. This phase does not publish a release, does not enable writes, and does not claim production/security readiness or real/private-book write safety. Later roadmap phases still need operator-facing blocker-closure UX, fresh-clone/upgrade smokes, final release-candidate dogfood, and a final release gate before any publication decision.
