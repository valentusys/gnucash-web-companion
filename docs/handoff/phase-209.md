# Phase 209 — Default-read-only full dogfood refresh

Date: 2026-05-21
Status: COMPLETE — default-read-only Docker/Caddy API and browser dogfood passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 8 only)

## Goal

Re-run a full default-read-only Docker/Caddy API and browser dogfood after Phases 202–208 to prove the safe default still works.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-208.md`, and the cycle-1 roadmap file.
- Used only the committed synthetic fixture `apps/api/tests/fixtures/test-book.gnucash.sqlite`, copied into ignored runtime data as `data/books/main.gnucash.sqlite` for the smoke.
- Validated rendered Compose config with dummy local values and confirmed `GNUCASH_WRITES_ENABLED: "false"` for both API and web.
- Ran Docker/Caddy default-read-only API smoke through health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports summary, scheduled transaction metadata, write-alpha audit summary, and disabled validate/create/PATCH/DELETE probes returning 403.
- Ran browser dogfood at mobile `320x720` and desktop `1280x900`, covering login, protected redirect, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV fetch, hidden write UI, auth-cookie no-readability, no-overflow checks, and no screenshot/download/CSV artifacts.
- Extended `scripts/smoke/read-only-api-smoke.py` to pin scheduled transaction and audit-summary read-only coverage for this and future full dogfood passes.
- Tore down Docker/Caddy, removed the ignored runtime fixture copy, removed dummy local `.env`, and restored the pre-existing ignored local app DB that had been moved aside before the smoke.
- Updated `CHANGELOG.md`, `PROJECT_STATUS.md`, and dogfood evidence doc `docs/dogfood/phase-209-default-readonly-dogfood.md`.

## Files changed

- `scripts/smoke/read-only-api-smoke.py`
- `docs/dogfood/phase-209-default-readonly-dogfood.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-209.md`

## Verification summary

Commands/results:

```text
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
15:      GNUCASH_WRITES_ENABLED: "false"
65:      GNUCASH_WRITES_ENABLED: "false"

python3 -m py_compile scripts/smoke/read-only-api-smoke.py
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api python3 scripts/smoke/read-only-api-smoke.py
# passed: health/login/books/accounts/transactions/detail/CSV/reports/scheduled/audit-summary and validate/create/PATCH/DELETE 403 probes

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --password <dummy-local-password> --fixture-path data/books/main.gnucash.sqlite --viewport-width 320 --viewport-height 720
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --password <dummy-local-password> --fixture-path data/books/main.gnucash.sqlite --viewport-width 1280 --viewport-height 900
# passed

cd apps/api && pytest -q
# passed: 481 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```

Post-teardown runtime hygiene:

- `data/books`: no non-placeholder entries.
- `data/backups`: no non-placeholder entries.
- `data/locks`: no non-placeholder entries.
- `data/app/app.db`: pre-existing ignored local app DB restored; not staged.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write-enabled run was performed.
- No real/private/only-copy book was used.
- No release/tag/package/image was published.
- No `.env`, app DB, backup, screenshot, export, token, key, cert, raw private path, account name, memo, amount, runtime book, or private financial data was staged or committed.

## Risks / follow-up

- This is default-read-only evidence only; it does not add write-alpha evidence and does not claim production/security/real-private-book write safety.
- The restored ignored `data/app/app.db` predates this phase and remains untracked local state.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
