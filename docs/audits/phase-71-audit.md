# Phase 71 Audit — Performance Risk Audit

Date: 2026-05-18

## Executive summary

Phase 71 reviewed obvious read-only performance risks before any wider v0.1/read-only confidence claims. The current implementation has important user-facing caps and pagination in place, but it does not yet have large-book benchmark evidence. The main risk is not an immediate safety failure; it is that small synthetic fixtures can hide slow full-book scans, large split counts, and dashboard aggregate costs.

## Verdict

Needs performance-risk tracking before broader confidence claims.

This is not a blocker for keeping the project in pre-alpha or for limited feedback-oriented sharing. It remains a blocker for any future claim that large GnuCash books are known to perform well. It does not approve `v0.1.0-readonly` publication; #24 and #25 remain the release blockers.

## Top blockers

No new Phase 71 blocker was found for the current pre-alpha/read-only posture.

Carried-forward blockers before `v0.1.0-readonly` publication remain:

1. #24 — conservative `v0.1.0-readonly` release notes are required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is required before publication.

## Important non-blockers

1. No large-book benchmark exists yet for the current piecash-backed read-only service layer.
2. No targeted benchmark exists for accounts with many splits.
3. CSV export has a documented 10,000-row cap, but timeout/slow-export behavior is not defined or tested.
4. Dashboard aggregate endpoints use service-layer iteration over accounts/transactions/splits and are correctness-tested on small fixtures, not benchmarked on large books.
5. Frontend transaction rendering is capped by backend pagination (`limit <= 200`) and dashboard cards/lists use small result sets, but there is no browser-side large-list benchmark evidence.

## Performance risk checks

### Transaction pagination

Evidence:

- `apps/api/app/routers/transactions.py` caps list endpoints with `limit: int = Query(50, ge=1, le=200)` for default-book and book-aware transaction list routes.
- `apps/api/app/services/gnucash_book.py` additionally clamps service-layer `list_transactions()` to `limit <= 500`.
- `apps/api/tests/test_transactions.py` covers basic limit/offset behavior.
- `apps/web/src/routes/transactions/+page.svelte` renders current-page items only and uses the shared `Pagination` component.

Risk:

- `list_transactions()` currently builds and sorts all matched transactions before slicing, and the route calls `count_transactions()` separately. On large books this can scan the same data twice per request.

Decision:

- Track as non-blocking performance work, not a Phase 71 product fix.

GitHub issue:

- #30 — Add large-book read-only benchmark.

### Account tree loading

Evidence:

- `apps/api/app/services/gnucash_book.py:get_account_tree()` loads all accounts into DTOs and then builds an in-memory tree.
- Account counts are usually much smaller than split/transaction counts, and the existing API is read-only.

Risk:

- Very large charts of accounts could still make account tree load heavy, and there is no benchmark fixture for that case.

Decision:

- Cover under #30 rather than create a separate noisy issue.

### CSV export cap

Evidence:

- `apps/api/app/routers/transactions.py` defines `CSV_EXPORT_LIMIT = 10_000`.
- CSV export uses the same read-only filters and caps rows at 10,000.
- `docs/transactions-filters.md` documents that CSV export intentionally excludes pagination and is capped at 10,000 rows.
- Frontend copy says export is capped at 10,000 rows.

Risk:

- Export currently counts matching transactions and then loads the capped result set. Timeout/slow-export behavior for large filtered sets is not defined or tested.

Decision:

- Track timeout/truncation/large-export behavior as non-blocking performance follow-up.

GitHub issue:

- #32 — Define CSV export timeout and truncation behavior.

### Dashboard aggregate queries

Evidence:

- `apps/api/app/routers/reports.py` exposes summary, cashflow, expenses-by-account, and recent-transactions endpoints.
- `apps/api/app/services/gnucash_book.py` computes summary/cashflow/expenses by iterating over accounts/transactions/splits in the read-only service layer.
- Recent transactions are capped (`limit <= 50`), but summary/cashflow/expense aggregates are full-range scans for their requested windows.

Risk:

- Dashboard may become slow on large books or large split counts even though correctness tests pass on small fixtures.

Decision:

- Track a dedicated aggregate performance benchmark issue.

GitHub issue:

- #33 — Track dashboard aggregate performance on large books.

### Large book behavior

Evidence:

- Current committed fixtures are synthetic/disposable and small.
- Compatibility and test coverage docs intentionally avoid broad performance or compatibility claims.

Risk:

- No current evidence supports broad large-book performance claims.

Decision:

- Create a large-book benchmark issue and keep release/docs wording conservative.

GitHub issue:

- #30 — Add large-book read-only benchmark.

### Large split count behavior

Evidence:

- Transaction detail returns all splits for a transaction.
- Account transaction filtering checks splits while matching transactions.
- Existing tests include split transaction correctness, but not high split-count performance.

Risk:

- Accounts with many splits and transactions with unusually many splits could expose slow matching/detail behavior.

Decision:

- Track a dedicated many-splits benchmark issue.

GitHub issue:

- #31 — Benchmark account with many splits.

### Frontend rendering of tables/cards

Evidence:

- Transaction page receives paginated backend results and renders `TransactionTable` plus mobile `TransactionCard` for the current page.
- Backend route cap keeps transaction pages to `limit <= 200`.
- Dashboard components render small card/list datasets.

Risk:

- Frontend risk is currently lower than backend scan risk. No separate issue is needed unless future product work raises client-side page sizes or virtualized views.

Decision:

- Covered by #30 large-book benchmark; do not create a noisy frontend-only issue now.

## Product consistency

The performance audit did not find documentation claiming broad large-book performance. README remains pre-alpha, read-only by default, not production-ready, not security-audited, not SaaS, not a GnuCash replacement, and not collaborative accounting.

## Safety boundary

Phase 71 did not change product code. The audited performance risks are read-only scalability risks, not write-safety changes.

Safety boundary remains intact:

- MVP v0.1 remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default/documented state.
- Controlled writes remain experimental/post-MVP only.
- GnuCash Desktop remains the authoritative editor.
- No real GnuCash books, `.env`, app DBs, backups, secrets, keys, certs, real screenshots, or real CSV exports were added.

## Release/readme/docs consistency

- README says Phase 0–70 were complete before this phase and links Phase 70 as the latest audit; Phase 71 should update this after the audit artifact is committed.
- CHANGELOG already carries release-facing audit entries through Phase 70; Phase 71 is release-facing enough to record because it creates public performance-risk tracking issues.
- v0.1 release plan remains conservative and does not claim large-book performance.
- v0.1 publication remains blocked by #24/#25, not by this new performance audit alone.

## GitHub project hygiene

Created meaningful Phase 71 performance follow-up issues:

1. #30 — Add large-book read-only benchmark.
2. #31 — Benchmark account with many splits.
3. #32 — Define CSV export timeout and truncation behavior.
4. #33 — Track dashboard aggregate performance on large books.

Created label:

- `performance` — Performance benchmarks and scalability risk tracking.

No fake/noisy issue was created for frontend rendering because the current backend pagination cap already bounds transaction-page item counts.

## Security notes

No auth, secret handling, write gate, CORS, cookie, or telemetry code changed in Phase 71. This audit does not constitute a security audit.

## Test/CI notes

Relevant code/test evidence inspected:

- transaction pagination and CSV cap in `apps/api/app/routers/transactions.py`;
- read-only service-layer transaction/account/report iteration in `apps/api/app/services/gnucash_book.py`;
- report routes in `apps/api/app/routers/reports.py`;
- account tree route in `apps/api/app/routers/accounts.py`;
- transaction pagination tests in `apps/api/tests/test_transactions.py`;
- recent-transaction report tests in `apps/api/tests/test_reports.py`;
- CSV cap documentation in `docs/transactions-filters.md`;
- frontend transaction/dashboard rendering paths in `apps/web/src/routes/transactions/+page.svelte` and `apps/web/src/routes/dashboard/+page.svelte`.

Full check results are recorded in `docs/handoff/phase-71.md`.

## Recommended next actions

1. Keep #30–#33 open as explicit performance-risk follow-ups.
2. Do not claim large-book performance until synthetic benchmark evidence exists.
3. Keep `v0.1.0-readonly` publication blocked by #24/#25 until release notes and copied/disposable-data runtime evidence are complete.
4. If a future phase implements performance tests, use generated/disposable data only and avoid committing real books or real exports.

## Suggested GitHub issues

Created:

- #30 — Add large-book read-only benchmark — labels: `audit`, `performance`, `read-only`.
- #31 — Benchmark account with many splits — labels: `audit`, `performance`, `read-only`, `gnucash`.
- #32 — Define CSV export timeout and truncation behavior — labels: `audit`, `performance`, `read-only`.
- #33 — Track dashboard aggregate performance on large books — labels: `audit`, `performance`, `read-only`.

## What not to do next

- Do not start Phase 72 without explicit user request.
- Do not optimize blindly without a disposable benchmark target.
- Do not add caching/indexing that risks stale financial views without clear invalidation semantics.
- Do not expand controlled-write scope while addressing read-only performance.
- Do not claim production readiness, security-audited status, broad compatibility, or known large-book scalability from this audit.
