# Phase 114 — Synthetic browser dogfood refresh

Date: 2026-05-19
Status: complete
Related roadmap item: analyst Phase 9
Related GitHub issues: #11, #12, #13, #38
PM brief: `docs/handoff/phase-114-pm-brief.md`

## Summary

Phase 114 implemented the analyst roadmap synthetic browser dogfood refresh. The phase added durable local browser dogfood tooling, ran Docker/Caddy against a synthetic/disposable fixture with writes disabled, verified core read-only UI/API paths, and recorded redacted evidence.

This was not personal-book dogfood and does not close #38.

## PM decision

Proceed with synthetic/disposable Docker/Caddy dogfood only. Cover the recent read-only UI surfaces practically: login/protected redirects, dashboard, accounts, books, scheduled awareness, transaction filters, account detail, transaction detail, CSV export, and disabled write probes. Do not publish a release, enable writes, use private books, or commit runtime artifacts.

## Implementation

Added durable smoke tooling:

- `scripts/smoke/read-only-browser-dogfood.py`
  - launches headless Chromium locally;
  - talks to Chrome DevTools Protocol with a tiny standard-library WebSocket client;
  - logs into the app through the real `/login` page;
  - verifies the auth cookie is not visible to `document.cookie`;
  - checks authenticated dashboard/accounts/books/scheduled pages;
  - checks account-detail and transaction-detail navigation;
  - checks a transaction-filtered URL and confirms the CSV export link preserves active filters;
  - fetches the CSV export through the authenticated browser/proxy route in memory only;
  - denies downloads and verifies no screenshot/download/CSV files were created.

Recorded dogfood evidence:

- `docs/dogfood/phase-114-synthetic-browser-dogfood.md`
  - runtime setup and safe synthetic fixture class;
  - Docker/API health evidence;
  - API smoke results;
  - browser dogfood results;
  - safety/limitation notes.

Updated status/docs:

- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-114-pm-brief.md`
- `docs/handoff/phase-114.md`

## Runtime dogfood result

Runtime setup:

- Docker/Caddy URL: `http://127.0.0.1:18080`.
- Runtime fixture: ignored local copy at `data/books/main.gnucash.sqlite`.
- Source class: committed synthetic/disposable fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`.
- Fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`.
- Web container internal API URL for dogfood: `http://api:8000`.

API smoke passed:

```text
read-only API smoke: target=http://127.0.0.1:18080/api
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
PASS: read-only API smoke checks completed
```

Browser dogfood passed:

```text
read-only browser dogfood: target=http://127.0.0.1:18080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
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

The filtered CSV route returned zero rows for the chosen synthetic filter combination, but the dogfood objective passed: the UI export link preserved the active filters, the authenticated proxy route returned CSV headers/metadata successfully, and no write or artifact side effect occurred.

## Safety

- `GNUCASH_WRITES_ENABLED=false` remained the runtime and documented default.
- No write endpoint/service behavior was changed.
- No personal/private GnuCash book was used or searched for.
- No screenshots, CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, cookies, certs, keys, private paths, account names from real data, transaction descriptions from real data, memos, real amounts, or personal financial data were committed.
- No release/tag/package was published.
- No production-readiness, security-audited, hosted-SaaS, broad compatibility, family-wallet, collaborative-accounting, or personal-book dogfood success claim was added.
- Money logic was not changed; no float money logic or fake currency conversion was added.

## Verification

Passed:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

APP_ADMIN_PASSWORD=dummy SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://127.0.0.1:18080/api scripts/smoke/read-only-api-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:18080 --fixture-path data/books/main.gnucash.sqlite
# passed

cd apps/api && pytest -q
# 349 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

git diff --check
# passed
```

## Files changed

- `scripts/smoke/read-only-browser-dogfood.py`
- `docs/dogfood/phase-114-synthetic-browser-dogfood.md`
- `docs/handoff/phase-114-pm-brief.md`
- `docs/handoff/phase-114.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## GitHub

- Updated #11 with Phase 114 synthetic dogfood evidence: https://github.com/valentusys/gnucash-web-companion/issues/11#issuecomment-4483046173
- Updated #12 with Phase 114 synthetic dogfood evidence: https://github.com/valentusys/gnucash-web-companion/issues/12#issuecomment-4483046445
- Updated #13 with Phase 114 synthetic dogfood evidence: https://github.com/valentusys/gnucash-web-companion/issues/13#issuecomment-4483046696
- Updated #38 to confirm Phase 114 does not satisfy personal copied-book dogfood: https://github.com/valentusys/gnucash-web-companion/issues/38#issuecomment-4483046845
- Keep #38 open/blocked because this phase did not use a personal copied GnuCash SQL book.

## Commit/push

- Commit: pending at handoff creation time; final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
