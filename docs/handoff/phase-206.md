# Phase 206 — Transaction and scheduled read-only edge-case polish

Date: 2026-05-20
Status: COMPLETE — transaction/scheduled read-only edge cases are clearer and mobile/desktop overflow-safe on synthetic evidence
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 5 only)

## Goal

Harden transaction and scheduled read-only pages for empty, large, many-split, filtered, reconciliation-state, and no-template cases discovered by synthetic fixtures.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-205.md`, and the cycle-1 roadmap file.
- Added a safe scheduled-transaction DTO field `template_reference_status` with only redacted status values: `present_redacted` or `not_present_redacted`.
- Kept scheduled template split amounts, accounts, memos, transaction descriptions, and raw SQL out of the public DTO and UI; no template split/source rows are queried or inferred for no-template cases.
- Updated `/scheduled` to display localized redacted template-reference status and to keep scheduled cards bounded with `min-w-0`/`break-words` layout.
- Hardened long amount display through `Money.svelte` so long Decimal string amounts can wrap inside bounded transaction/split layouts without coercing to `Number()`.
- Preserved many-split transaction detail behavior with mobile cards plus desktop fixed table, reconciliation labels, string/Decimal amounts, and no horizontal scrolling.
- Extended targeted backend tests for no-template scheduled redaction and many-split transaction Decimal/reconciliation-state behavior.
- Extended frontend static route checks for redacted scheduled template status, no-template copy, Money overflow handling, and bounded scheduled cards.
- Ran Docker/Caddy read-only API and browser dogfood against the committed synthetic fixture copied into ignored runtime storage; browser checks passed at `320x720` and `1365x900` with no overflow, hidden write UI, CSV parity, and no screenshot/download/export artifacts.

## Files changed

- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_scheduled_transactions.py`
- `apps/api/tests/test_transactions.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/components/Money.svelte`
- `apps/web/src/lib/components/TransactionSplits.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/scheduled/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/dogfood/phase-206-readonly-edge-case-dogfood.md`
- `docs/handoff/phase-206.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_scheduled_transactions.py tests/test_transactions.py tests/test_transaction_export.py tests/test_transaction_writes.py -q
# passed: 119 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/api && pytest -q
# passed: 480 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed: svelte-check 0 errors/0 warnings; auth route checks passed; build passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --username admin --fixture-path data/books/main.gnucash.sqlite
# passed at 320x720: scheduled/transactions/account flows no overflow, write UI hidden, CSV export parity, no artifacts

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --username admin --fixture-path data/books/main.gnucash.sqlite --viewport-width 1365 --viewport-height 900
# passed at 1365x900 with the same no-overflow/hidden-write/no-artifact checks

SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py --api-base-url http://127.0.0.1:8080/api --username admin
# passed: validate/create/PATCH/DELETE disabled-write probes returned 403

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default in rendered Docker Compose config for API and web.
- No scheduled transaction writes, next-run prediction, template split exposure, import/export expansion, currency conversion, or real/private screenshots/exports were added.
- Amounts remain serialized and rendered as strings/Decimal-derived strings; no `Number()` conversion was added for money paths.
- Filters remain URL-only display controls; no localStorage/sessionStorage financial persistence was added.
- Docker dogfood used only the committed synthetic fixture copied into ignored `data/books/main.gnucash.sqlite`; runtime copy/app DB were removed after teardown.
- No real/private book, app DB, backup, `.env`, screenshot, export, token, key, cert, raw private path, account name, memo, amount, or private financial data was committed.

## Risks / follow-up

- Scheduled transaction metadata remains intentionally summary-only. The app still does not calculate next occurrences or expose/edit template splits.
- Browser dogfood is local synthetic evidence only; it does not establish real/private-book safety or broad GnuCash Desktop/backend compatibility.
- CSV export remains the existing synchronous, capped read-only export; this phase only preserved visible parity/cap/no-conversion messaging.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
