# Phase 199 — Full default-read-only regression dogfood

Date: 2026-05-20
Status: COMPLETE — default read-only Docker/Caddy API and browser dogfood passed; committed/pushed after verification
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 8 only)

## Goal

After Phases 192–198, confirm that the default read-only product path is stable on synthetic/disposable local Docker/Caddy across API, mobile browser, and desktop browser coverage.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-198.md`, cycle-3 roadmap file, Docker Compose config, `.gitignore`, and existing read-only API/browser smoke helpers.
- Copied only the committed synthetic fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite` into ignored runtime data as `data/books/main.gnucash.sqlite`.
- Ran local Docker/Caddy with dummy local-only `.env` values and `GNUCASH_WRITES_ENABLED=false`.
- Ran read-only API smoke through health, login, `/auth/me`, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/PATCH/DELETE probes.
- Ran headless browser dogfood at `320x720` and `1280x900` through login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV fetch, hidden write UI, auth-cookie no-readability, no-overflow, and no-download-artifact checks.
- Stopped Docker/Caddy and removed ignored runtime `.env`, book, and app DB artifacts.
- Documented evidence in `docs/dogfood/phase-199-default-readonly-regression.md`.

## Files changed

- `docs/dogfood/phase-199-default-readonly-regression.md`
- `docs/handoff/phase-199.md`
- `PROJECT_STATUS.md`

## Verification summary

Commands/results:

```text
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api scripts/smoke/read-only-api-smoke.py
# PASS: health/login/books/accounts/transactions/detail/CSV/reports and validate/create/PATCH/DELETE 403 checks

SMOKE_ADMIN_PASSWORD=<dummy-local-password> scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --fixture-path data/books/main.gnucash.sqlite --viewport-width 320 --viewport-height 720
# PASS: mobile browser dogfood, auth cookie not readable, hidden write UI, no horizontal overflow, no downloads

SMOKE_ADMIN_PASSWORD=<dummy-local-password> scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --fixture-path data/books/main.gnucash.sqlite --viewport-width 1280 --viewport-height 900
# PASS: desktop browser dogfood, auth cookie not readable, hidden write UI, no horizontal overflow, no downloads

cd apps/api && pytest tests/test_health.py tests/test_transaction_writes.py -q
# passed

cd apps/api && pytest -q
# passed

cd apps/web && npm run check
# passed

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and was rendered as false for API and web.
- No write-enabled mode was run in this phase.
- Only the committed synthetic fixture was copied into ignored runtime data.
- No real/private/only-copy book was used.
- No `.env`, app DB, runtime book, backup, lock, screenshot, download, raw CSV export, token, key, cert, private path, account name, memo, amount, or private financial data was committed.
- Local dummy `.env`, runtime fixture, and generated app DB were removed after `docker compose down --remove-orphans`.
- No release/tag/package was published.

## Risks / follow-up

- This is synthetic/disposable local pre-alpha evidence only; it is not a production-readiness or security-audit claim.
- Phase 9 write-alpha disposable CRUD/restore dogfood remains separate and was not started in this session.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
