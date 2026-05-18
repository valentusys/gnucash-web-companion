# Phase 82 — Read-only Multi-book Boundary Regression Coverage

## Status

Complete. Phase 82 was a PM→Engineer post-release hardening phase with one concrete tested safety/behavior result. No auditor role was used. No audit-only phase or `docs/audits/phase-82-audit.md` was created.

No new tag/release was published. No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Pick GitHub #35 for Phase 82: a narrow, low-risk, post-release read-only boundary hardening task with concrete backend regression coverage.

### Why

Phase 80 already published `v0.1.0-readonly`, and Phase 81 completed a separate post-release hardening fix. Phase 82 therefore should not publish another tag/release, start v0.2 work, or perform audit-only documentation. #35 was open, concrete, testable, and directly protects the read-only multi-book surface: archived books and unauthorized independent books must not leak through book-aware route families.

### Phase brief

- Goal: expand backend regression coverage so archived books are hidden/blocked and unauthorized book access is denied across book-aware read-only route families.
- Non-goals: no auditor role, no audit-only docs, no write-mode changes, no `GNUCASH_WRITES_ENABLED` enablement, no v0.2 planning, no new release/tag, no product-scope expansion, no book-management UI.
- Acceptance criteria:
  - `GET /books` excludes archived books even when the user has a metadata access row.
  - `GET /books/{book_id}` returns `404` for archived books even when the user has access.
  - Unauthorized access returns `403` across representative book-aware read-only route families: accounts, account tree/detail, transactions, transaction detail, account transactions, CSV export, and reports.
  - Archived books return `404` across the same route families.
  - Tests stay read-only and use fixture/disposable metadata only.
  - `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff record Phase 82 evidence.
  - GitHub #35 is updated/closed only after evidence exists.
- Safety checks:
  - Keep MVP read-only by default.
  - Do not commit real financial data, real GnuCash books, `.env`, app DB, backups, secrets, keys, screenshots/exports with real data.
  - Preserve positioning: GnuCash Desktop remains authoritative; project is not SaaS, not a GnuCash replacement, not collaborative accounting.
- Verification:
  - `cd apps/api && pytest tests/test_multi_book_access.py -q`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - verify existing `v0.1.0-readonly` tag/release state with git/gh.

### GitHub/backlog

- Close #35 with implementation/check evidence.
- Leave #22, #26, #28–#34, and #36 open for later narrow phases; do not close issues without evidence.

## Engineer report

### Concrete result

Implemented post-release read-only boundary hardening as backend regression coverage:

- Added an archived-book fixture to `apps/api/tests/test_multi_book_access.py` with explicit `UserBookAccess`, proving archive state wins over metadata access.
- Strengthened `GET /books` coverage so Alice sees only her active book, not Bob’s inaccessible book and not her archived book.
- Added `GET /books/{book_id}` regression coverage for archived books returning `404`.
- Added parametrized coverage for every representative book-aware read-only route family:
  - `/books/{book_id}/accounts`
  - `/books/{book_id}/accounts/tree`
  - `/books/{book_id}/accounts/{account_id}`
  - `/books/{book_id}/accounts/{account_id}/transactions`
  - `/books/{book_id}/transactions`
  - `/books/{book_id}/transactions/export`
  - `/books/{book_id}/transactions/{transaction_id}`
  - `/books/{book_id}/reports/summary`
  - `/books/{book_id}/reports/cashflow`
  - `/books/{book_id}/reports/expenses-by-account`
  - `/books/{book_id}/reports/recent-transactions`
- Unauthorized access now has explicit regression assertions for `403 Book access denied` across those route families.
- Archived-book access now has explicit regression assertions for `404 Book not found` across those route families.

Production application code was not changed because the current shared resolver behavior already satisfied the new boundary tests. The concrete deliverable is committed regression coverage that locks the read-only safety boundary and prevents later regressions.

### Test-hardening evidence

Targeted check:

```text
cd apps/api && pytest tests/test_multi_book_access.py -q
31 passed, 1 warning
```

### Required checks

```text
cd apps/api && pytest -q
307 passed, 27 warnings

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

git diff --check
passed
```

Release-state verification:

```text
git tag --list 'v0.1.0-readonly'
v0.1.0-readonly

gh release view v0.1.0-readonly --json tagName,isPrerelease,url,targetCommitish,publishedAt
{"isPrerelease":true,"publishedAt":"2026-05-18T06:04:26Z","tagName":"v0.1.0-readonly","targetCommitish":"main","url":"https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly"}
```

### Files changed

- `apps/api/tests/test_multi_book_access.py`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-82.md`

### GitHub/release

- GitHub #35 closed after implementation and passing checks.
- No new release/tag was created.
- Existing `v0.1.0-readonly` GitHub pre-release remains published at https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly

### Commit/push

Phase changes were committed and pushed to `origin/main` after the required checks. The pushed HEAD was verified after push, and the working tree was clean.
