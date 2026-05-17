# PROJECT_STATUS

Last updated: 2026-05-17

## Repository

- GitHub: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Status: pre-alpha / MVP in progress

## Current baseline

Completed through Phase 24:

- Phase 0 — competitive review and product positioning
- Phase 1 — open-source foundation
- Phase 2 — SvelteKit + FastAPI + Docker skeleton
- Phase 3 — app metadata DB and book registry foundation
- Phase 4 — authentication foundation
- Phase 5 — read-only piecash service layer
- Phase 6 — books/accounts API and UI
- Phase 7 — transaction browsing API and UI
- Phase 8 — dashboard reports API and UI
- Phase 9 — frontend theme, mobile shell, PWA manifest
- Phase 10 — public repo hygiene and release readiness
- Phase 11 — integration QA and MVP hardening
- Phase 12 — controlled transaction writes implemented as post-MVP capability
- Phase 13 — agent project context
- Phase 14 — MVP read-only scope lock and write gating
- Phase 15 — public pre-alpha release readiness
- Phase 16 — project lead subagent profile
- Phase 17 — synthetic GnuCash fixture and read-only integration validation
- Phase 18 — README screenshots and mobile preview with synthetic data
- Phase 19 — multi-currency limitation tests and auth cookie security documentation
- Phase 20 — multi-book UI foundation
- Phase 21 — file-based write lock replacement
- Phase 22 — real controlled write integration tests
- Phase 23 — backup restore smoke test
- Phase 24 — CSV export for transactions

## MVP product model

MVP v0.1:

- one installation
- one local admin user
- one default GnuCash book
- read-only access to GnuCash data

Future:

- one installation
- multiple users
- multiple independent books
- users can access only assigned books

Advanced future:

- shared editing of one book only as serialized/locked mode
- no real-time collaborative editing

Important positioning:

- Not a family-wallet baseline.
- Not collaborative accounting on top of GnuCash.
- A GnuCash book is treated as a monopolistic accounting ledger.
- Multi-user expansion is primarily through multiple independent books.

## Phase 15 — Public pre-alpha release readiness

Status: complete. Phase commit pushed and `v0.0.1-prealpha` tag pushed.

Release candidate: `v0.0.1-prealpha`.

GitHub issues:

- `gh` is installed in `~/.local/bin/gh` and authenticated for `valentusys`.
- GitHub labels and milestones were created from `docs/github/`.
- GitHub issues #1–#10 were created from `docs/github/issues/`.
- Issues #1, #2, and #4 were closed as completed by Phase 17 / release automation.

Release:

- `v0.0.1-prealpha` tag was pushed with git.
- GitHub pre-release was created with `gh`.
- Release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.0.1-prealpha
- Automation notes are in `docs/github/manual-release-instructions.md`.

Artifacts:

- `docs/v0.2-controlled-writes.md`
- `docs/release/v0.0.1-prealpha-checklist.md`
- `docs/release/v0.0.1-prealpha-notes.md`
- `docs/github/labels-to-create.md`
- `docs/github/milestones-to-create.md`
- `docs/github/issues/*.md`
- `docs/github/manual-release-instructions.md`
- `docs/handoff/phase-15.md`

## Phase 16 — Project Lead subagent profile

Status: complete. Phase commit pushed.

Created:

- `docs/agents/project-lead.md` — durable Project Lead / Руководитель проекта profile for future Hermes subagent use.
- Hermes skill `gnucash-web-companion-project-lead` — reusable project lead context for future sessions.

Purpose:

- plan phases
- review scope and safety boundaries
- manage release/backlog guidance
- prevent product drift away from read-only MVP positioning
- keep controlled writes post-MVP and disabled by default

The Project Lead is not a coding implementer and should not spawn further subagents.

## Phase 17 — Synthetic GnuCash Fixture and Read-Only Integration Validation

Status: complete. Phase commit pushed.

Goal: create a disposable synthetic GnuCash SQLite fixture using piecash and validate the read-only service layer against it with real integration tests.

Artifacts:

- `apps/api/scripts/create_test_fixture.py` — standalone script that generates the synthetic fixture.
- `apps/api/tests/fixtures/test-book.gnucash.sqlite` — 208 KB synthetic GnuCash book (9 user accounts + 1 ROOT, 5 transactions, SEK).
- `apps/api/tests/test_integration_fixture.py` — 19 integration tests validating the full read-only path.
- `apps/api/tests/test_gnucash_book.py` — replaced placeholder skipped test with fixture existence check.

Test results: 187 passed (167 existing + 19 new integration + 1 updated), 0 failed.

Deviation from spec: the spec assumed 9 accounts (1 ROOT + 8 children) but piecash `book.accounts` returns 10 non-ROOT accounts (ROOT is only in `book.root_account`). The service layer returns 10 accounts. Tests assert `account_count == 10`. The account tree has 4 top-level nodes (ROOT is not in `_accounts()` so its children become roots).

## Phase 18 — README Screenshots and Mobile Preview with Synthetic Data

Status: complete. Phase commit pushed.

Goal: add visual proof of the current UI to the README using only synthetic fixture data.

Artifacts:

- `docs/images/` — 7 screenshot files (login, dashboard desktop/mobile, accounts tree, transactions list, transaction detail, dark mode). Total ~453 KB.
- `README.md` — updated with `## Screenshots` section containing all 7 images via relative paths.

Screenshots: login (20 KB), dashboard-desktop (85 KB), dashboard-mobile (35 KB), accounts-tree (91 KB), transactions-list (96 KB), transaction-detail (42 KB), dark-mode (85 KB).

Deviations: transaction detail used GUID-based URL (`/transactions/89bdbe5a...`) instead of `/transactions/1` since the synthetic fixture uses GUIDs. Used Chromium headless with CDP via Python instead of `browser_vision` tool (display not available). Used form-based login via CDP instead of cookie injection.

Verification: all 7 screenshots < 300 KB, no real financial data, no production code changes, README renders images with relative paths.

Related issue: GitHub #3.

## Phase 19 — Multi-Currency Limitation Tests and Auth Cookie Security Documentation

Status: complete. Phase commit pushed.

Goal: add mixed-currency integration tests and document auth cookie security for self-hosted deployment.

Artifacts:

- `apps/api/scripts/create_multicurrency_fixture.py` — script to generate the multi-currency fixture.
- `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite` — 208 KB synthetic book (13 accounts: 10 SEK + 3 EUR; 6 transactions: 5 SEK + 1 EUR).
- `apps/api/tests/test_multicurrency_reports.py` — 11 integration tests validating multi-currency exclusion.
- `docs/security/auth-cookie-deployment.md` — cookie attributes, deployment warnings, no production guarantee.
- `README.md` — new `## Security and Deployment` section with link to the doc.

Test results: 198 passed (187 existing + 11 new), 0 failed.

Related issues: GitHub #6, GitHub #10.

## Phase 20 — Multi-Book UI Foundation

Status: complete. Phase commit pushed locally (gh auth invalid, push skipped).

Goal: add a minimal book switcher to the frontend and wire it to existing GET /books API, migrating page-level data loads from default-book alias routes to explicit book-aware routes.

Artifacts:

- `apps/web/src/lib/components/BookSwitcher.svelte` — new component, dropdown for multi-book, plain text for single-book.
- `apps/web/src/lib/api/server.ts` — added `getActiveBookId(cookies)` helper.
- `apps/web/src/routes/+layout.server.ts` — fetches books, resolves active book from cookie/default/first.
- `apps/web/src/routes/+layout.svelte` — passes book context to nav components.
- `apps/web/src/lib/components/DesktopNav.svelte` — integrated BookSwitcher.
- `apps/web/src/lib/components/MobileNav.svelte` — integrated BookSwitcher.
- `apps/web/src/routes/dashboard/+page.server.ts` — book-aware report routes.
- `apps/web/src/routes/accounts/+page.server.ts` — book-aware account tree route.
- `apps/web/src/routes/accounts/[id]/+page.server.ts` — book-aware account detail + transactions routes.
- `apps/web/src/routes/transactions/+page.server.ts` — book-aware transaction list + accounts routes.
- `apps/web/src/routes/transactions/[id]/+page.server.ts` — book-aware transaction detail route.
- `apps/api/tests/test_multi_book_access.py` — 8 new tests for multi-book access filtering.

Test results: 207 passed (199 + 8 new), 1 pre-existing failure (test_gnucash_book.py relative path). Frontend: check 0 errors, build success, auth-routes passed.

Deviations: page-level loads no longer return books/activeBook/showBookSelector (layout provides them instead). `getActiveBookId()` validates cookie value as positive integer.

Related issues: GitHub #5.

## Phase 21 — File-Based Write Lock Replacement

Status: complete. Phase commit pushed.

Goal: replace in-process `threading.Lock`-based write lock with `fcntl.flock()`-based file locking for multi-worker safety.

Artifacts:

- `apps/api/app/services/write_lock.py` — rewritten to use `fcntl.flock()` on per-book lock files under `/data/locks/`. Book IDs are sanitized (path separators → underscores) to produce flat filenames.
- `apps/api/tests/test_write_lock.py` — 10 new tests covering acquire/release, non-blocking behavior, context manager (normal + exception), independent books, lock file creation, idempotent release, blocking acquire, and auto-creation of nested lock directories.
- `apps/api/tests/test_transaction_writes.py` — updated old `TestWriteLockService` tests to use `tmp_path`-based lock directories; patched singleton in `test_create_endpoint_exists` to use a tmp-based file lock service.

Test results: 218 passed (208 existing + 10 new), 0 failed. Frontend: check 0 errors, build success, auth-routes passed. Docker config valid.

Deviation from spec: added book_id sanitization in `_lock_path()` to handle absolute paths and URIs (which contain `/` and `:` characters) by replacing them with underscores. This prevents path traversal when `book_key` is a filesystem path like `/data/books/test.gnucash.sqlite`.

Related issues: GitHub #7 (closed).

## Phase 23 — Backup Restore Smoke Test

Status: complete. Phase commit pushed.

Goal: add automated tests verifying backups created before write operations can be restored, confirming original GnuCash book state is fully recoverable.

Artifacts:

- `apps/api/tests/test_backup_restore.py` — 6 integration tests across 2 test classes covering backup file validity, backup pre-write state, restore undoes write (transaction count), restore preserves account count, restore preserves original transaction data, and original fixture immutability.

Test results: 254 passed (248 existing + 6 new), 0 failed. Frontend: check 0 errors, build success, auth-routes passed. Docker config valid.

Deviations: 6 tests implemented vs 4 minimum. Added `test_restore_preserves_original_transaction_data` and `test_original_fixture_never_modified` for stronger safety coverage.

Production code changes: none. Zero production code changes; restore is `shutil.copy2` overwrite matching the production backup model.

Related issues: GitHub #9 (closed).

## Phase 24 — CSV Export for Transactions

Status: complete. Phase commit pushed.

Goal: add read-only CSV export endpoint to backend and export button to frontend transactions page.

Artifacts:

- `apps/api/app/routers/transactions.py` — added `GET /books/{book_id}/transactions/export` endpoint (read-only, book-aware, respects all list filters, 10,000 row cap).
- `apps/api/tests/test_transaction_export.py` — 8 backend tests covering auth requirement, CSV headers, transaction data, date filter, account filter, query filter, access denial, and Content-Disposition filename.
- `apps/web/src/routes/transactions/+page.svelte` — added «Экспорт CSV» button that preserves current filters (query, date_from, date_to, account_id) in the export URL.
- `docs/handoff/phase-24.md` — handoff document.

Test results: 262 passed (254 existing + 8 new), 0 failed. Frontend: check 0 errors, build success, auth-routes passed. Docker config valid.

Deviations: 8 tests implemented vs 7 minimum. Export endpoint placed before `{transaction_id}` route to avoid path collision (`/export` would match as `transaction_id="export"`). No new dependencies required (uses stdlib `csv` + `io`).

Production code changes: read-only only. Zero write-path changes. No new dependencies.

Related issues: none.

## Phase 22 — Real Controlled Write Integration Tests

Status: complete. Phase commit pushed.

Goal: add integration tests that exercise the controlled write path against a real disposable GnuCash SQLite fixture using piecash, validating the full write flow end-to-end.

Artifacts:

- `apps/api/tests/test_write_integration.py` — 30 integration tests across 8 test classes covering create, patch, backup, audit, lock lifecycle, lock contention, rejection scenarios, read-back verification, and original fixture immutability against real piecash books.

Test results: 248 passed (218 existing + 30 new), 0 failed. Frontend: check 0 errors, build success, auth-routes passed. Docker config valid.

Deviations: ROOT account has `placeholder=0` (not 1 as spec assumed) but is rejected because it's not in `book.accounts` (it's `book.root_account`), achieving the same test goal. 30 tests implemented vs 15 minimum.

Production code changes: none. Zero production code changes required; write service works correctly against real piecash books.

Related issues: GitHub #8 (closed).

## Standing constraints

- MVP v0.1 is strictly read-only for GnuCash.
- `GNUCASH_WRITES_ENABLED=false` by default.
- Do not commit real financial data, GnuCash books, backups, `.env`, credentials, tokens, certificates, or private keys.
- Money values must use string/Decimal representation, not floats.
- Auth tokens must stay in httpOnly cookies, not localStorage/sessionStorage.
- Frontend never reads GnuCash files/databases directly.
- `piecash` stays inside backend service layers.
- App metadata stays separate from GnuCash books.
- Do not add banking integrations, CSV/OFX import, heavy UI libraries, or collaborative editing in MVP.
- Do not fake currency conversion.
- Keep docs honest: pre-alpha, test copies first, no production guarantee.

## Standard checks

Backend:

```bash
cd apps/api && pytest -q
```

Frontend:

```bash
cd apps/web && npm run check && npm run test:auth-routes && npm run build
```

Docker config:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```
