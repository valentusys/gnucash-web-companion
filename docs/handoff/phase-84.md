# Phase 84 — CSV Export Truncation and Timeout Behavior

## Status

Complete. Phase 84 was a PM→Engineer post-release hardening phase with one concrete tested release-maintenance/user-facing result. No auditor role was used. No audit-only phase or `docs/audits/phase-84-audit.md` was created.

No new tag/release was published. No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Pick GitHub #32 for Phase 84: a narrow, low-risk, post-release read-only CSV export hardening task that defines and tests cap/truncation/timeout behavior.

### Why

Phase 80 already published `v0.1.0-readonly`, Phase 81 fixed post-release seed-log redaction, Phase 82 hardened multi-book access boundaries, and Phase 83 removed frontend `Number()` decisions from money display paths. Phase 84 therefore should not publish another tag/release, start v0.2 work, or perform audit-only documentation. #32 was open, concrete, testable, and aligned with release-hardening backlog: CSV export already had a 10,000-row cap, but successful responses did not expose truncation/timeout policy evidence to users/operators.

### Phase brief

- Goal: make CSV export cap/truncation/timeout behavior explicit and tested for the existing read-only CSV export path.
- Non-goals: no auditor role, no audit-only docs, no write-mode changes, no `GNUCASH_WRITES_ENABLED` enablement, no v0.2 planning, no new release/tag, no product-scope expansion, no background export jobs, no unbounded/real financial exports.
- Acceptance criteria:
  - Keep the existing 10,000-row CSV export cap.
  - Add successful-export metadata indicating the configured cap, matching pre-cap total, whether the result was truncated, and the timeout policy.
  - Forward that metadata through the SvelteKit CSV export proxy.
  - Add regression tests for truncated and non-truncated exports using disposable fake data.
  - Add user/operator-facing copy/docs explaining that large exports run synchronously and should be narrowed if they time out.
  - Update `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff with Phase 84 evidence.
  - Close GitHub #32 only after implementation and checks pass.
- Safety checks:
  - Keep MVP read-only by default.
  - Do not commit real financial data, real GnuCash books, `.env`, app DB, backups, secrets, keys, screenshots/exports with real data.
  - Preserve positioning: GnuCash Desktop remains authoritative; project is not SaaS, not a GnuCash replacement, not collaborative accounting.
- Verification:
  - `cd apps/api && pytest tests/test_transaction_export.py -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - verify existing `v0.1.0-readonly` tag/release state with git/gh.

### GitHub/backlog

- Close #32 with implementation/check evidence.
- Leave #22, #26, #28–#31, #33, and #36 open for later narrow phases; do not close issues without evidence.

## Engineer report

### Concrete result

Implemented CSV export truncation/timeout hardening for #32:

- `apps/api/app/routers/transactions.py` now includes CSV export metadata headers on successful responses:
  - `X-CSV-Export-Limit`
  - `X-CSV-Export-Total`
  - `X-CSV-Export-Truncated`
  - `X-CSV-Export-Timeout-Policy: synchronous-request-timeout`
- `apps/api/tests/test_transaction_export.py` covers both truncated and non-truncated export responses using disposable fake GnuCash-like data only.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` forwards those metadata headers through the SvelteKit browser-download proxy.
- `apps/web/scripts/test-auth-routes.mjs` verifies the proxy keeps forwarding the CSV metadata headers.
- `apps/web/src/routes/transactions/+page.svelte` now tells users that large CSV exports run synchronously and should be narrowed if the request times out.
- `docs/transactions-filters.md` documents the synchronous export model, the 10,000-row cap, the truncation headers, and timeout guidance.

This is read-only release maintenance/UX hardening only. It does not add writes, background jobs, currency conversion, or production-readiness claims.

### TDD evidence

RED:

```text
cd apps/api && pytest tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_cap_and_truncation_headers tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_not_truncated_when_under_cap -q
FAILED tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_cap_and_truncation_headers - KeyError: 'X-CSV-Export-Limit'
FAILED tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_not_truncated_when_under_cap - KeyError: 'X-CSV-Export-Limit'
```

GREEN:

```text
cd apps/api && pytest tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_cap_and_truncation_headers tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_reports_not_truncated_when_under_cap -q
2 passed, 1 warning

cd apps/web && npm run test:auth-routes
auth route checks passed
```

### Required checks

```text
cd apps/api && pytest tests/test_transaction_export.py -q
14 passed, 1 warning

cd apps/api && pytest -q
309 passed, 27 warnings

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

- `apps/api/app/routers/transactions.py`
- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `apps/web/src/routes/transactions/+page.svelte`
- `docs/transactions-filters.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-84.md`

### GitHub/release

- GitHub #32 to be closed after implementation and passing checks.
- No new release/tag was created.
- Existing `v0.1.0-readonly` GitHub pre-release remains published at https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly

### Commit/push

Pending final required checks, commit, push, pushed HEAD verification, and clean working tree verification.
