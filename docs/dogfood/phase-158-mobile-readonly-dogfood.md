# Phase 158 — Mobile read-only account/transaction dogfood

Date: 2026-05-19
Status: passed on synthetic/disposable data
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 7/10 only)

## Summary

Phase 158 used narrow-width synthetic browser dogfood to pin one concrete mobile read-only UX issue in the account/transaction flows: CSV export and related transaction-page action links did not explicitly guarantee a 44px touch target on narrow screens.

The fix keeps transaction/account export and empty-state recovery actions as touch-friendly `inline-flex min-h-11` controls. The browser dogfood helper now runs at a mobile/narrow viewport by default, checks for horizontal overflow on read-only dashboard/accounts/books/scheduled/account-detail/transactions/transaction-detail pages, verifies visible CSV export actions are at least 44px tall, and uses the mobile transaction card path when opening a transaction detail.

No screenshots, downloads, raw CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, keys, certs, private paths, or private financial data were committed.

## Scope completed

- Ran the current browser dogfood at a 320x720 viewport against local Docker/Caddy with the committed synthetic fixture copied in ignored runtime data.
- Fixed touch-target sizing for:
  - `/transactions` CSV export action;
  - `/transactions` write-mode entry point when explicitly enabled in future test-only contexts;
  - `/transactions` filtered empty-state clear-filters action;
  - `/transactions` empty-state review-books action;
  - `/accounts/[id]` account-scoped CSV export action.
- Extended `scripts/smoke/read-only-browser-dogfood.py` with:
  - `--viewport-width` / `--viewport-height` options, defaulting to 320x720;
  - Chrome device metrics override for narrow mobile dogfood;
  - horizontal-overflow assertions for the covered read-only pages;
  - CSV export touch-target height assertions;
  - mobile-card transaction detail navigation.
- Extended frontend route checks to pin the new touch-target classes.

## Runtime setup used for this pass

- Runtime origin: `http://127.0.0.1:8080`
- Runtime fixture filename: `main.gnucash.sqlite`
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`
- Viewport: `320x720`
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`
- Secrets: dummy local-only values passed via environment; values were not printed.
- Note: the ignored local `data/app/app.db` was temporarily moved aside so the dummy admin password could seed a disposable smoke database, then restored after Docker shutdown.

## Evidence

Browser dogfood passed:

```text
read-only browser dogfood: target=http://127.0.0.1:8080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: mobile_viewport: 320x720
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: mobile_no_overflow: dashboard: scrollWidth=320 clientWidth=320
ok: dashboard: /dashboard loaded; write UI hidden
ok: mobile_no_overflow: accounts: scrollWidth=320 clientWidth=320
ok: accounts: /accounts loaded; write UI hidden
ok: mobile_no_overflow: books: scrollWidth=320 clientWidth=320
ok: books: /books loaded; write UI hidden
ok: mobile_no_overflow: scheduled: scrollWidth=320 clientWidth=320
ok: scheduled: /scheduled loaded; write UI hidden
ok: mobile_no_overflow: account_detail: scrollWidth=320 clientWidth=320
ok: account_detail: first account detail loaded
ok: mobile_no_overflow: transactions_filters: scrollWidth=320 clientWidth=320
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: mobile_no_overflow: transaction_detail: scrollWidth=320 clientWidth=320
ok: transaction_detail: first transaction detail loaded
ok: csv_export: status=200 total=0 truncated=false
ok: no_artifacts: no screenshots/downloads/CSV files written
PASS: read-only browser dogfood completed
```

## Acceptance criteria result

- Narrow-viewport browser check exists and passed: yes.
- Specific mobile issue fixed and pinned by tests: yes, transaction/account export and recovery actions now explicitly keep touch-friendly 44px targets.
- Account/transaction flows covered: yes, `/accounts`, account detail, `/transactions`, and transaction detail were checked at 320px width.
- Horizontal overflow check covered by dogfood: yes, covered read-only pages reported `scrollWidth=320 clientWidth=320`.
- Write UI remained hidden with default writes-disabled runtime: yes.

## Limitations

- Evidence is local synthetic/disposable dogfood only.
- This is not a production deployment hardening claim and not a security audit.
- No release, tag, package, Docker image, binary, real/private book, or private data artifact was published.

## Safety

- `GNUCASH_WRITES_ENABLED=false` remained the runtime and default.
- GnuCash Desktop remains the authoritative editor.
- No production write mode was enabled.
- No real/private book or private financial data was used.
- No `.env`, token, key, cert, app DB, backup, screenshot, raw CSV export, copied runtime book, or private path was committed.
