# PROJECT_STATUS

Last updated: 2026-05-17

## Repository

- GitHub: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Status: pre-alpha / MVP in progress

## Current baseline

Completed through Phase 35.

Completed phases:

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
- Phase 25 — documentation, release, and roadmap sync
- Phase 26 — audit-driven status sync
- Phase 27 — discoverability and community announcement readiness
- Phase 28 — GnuCash compatibility matrix
- Phase 29 — audit-driven release documentation sync
- Phase 30 — transaction amount range filters for CSV export
- Phase 31 — read-only safety status banner
- Phase 32 — backend write-gating regression coverage
- Phase 33 — controlled-writes documentation cleanup and status sync
- Phase 34 — README/public status baseline sync after Phase 33 audit finding
- Phase 35 — audit-driven Phase 34 public baseline and controlled-writes docs sync

Next planned phase:

- TBD by Project Lead after release/documentation triage.

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

## Phase 25 — Documentation, Release, and Roadmap Sync

Status: complete. Phase commits pushed: `bbd1c8b`, `fa328d6`.

Goal: sync public docs, changelog, controlled-write notes, release candidate notes, and backlog after Phases 17–24 without creating a tag or release.

Artifacts:

- `README.md` — updated current status and release-candidate links for `v0.0.2-prealpha`.
- `CHANGELOG.md` — added Unreleased entries for Phases 17–24.
- `docs/v0.2-controlled-writes.md` — updated completed and pending write-safety checklist items.
- `docs/release/v0.0.2-prealpha-notes.md` — created candidate notes only; no tag/release published.
- `docs/handoff/phase-25.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issues opened after Phase 25 / audit: GitHub #16, GitHub #17.

## Phase 26 — Audit-Driven Status Sync

Status: complete. Phase commit pushed.

Goal: fix audit-identified status/release documentation drift without changing product code or publishing tags/releases.

Artifacts:

- `docs/audits/2026-05-17-audit.md` — independent audit report.
- `README.md` — advanced current status to Phase 0–25 and clarified `v0.0.1-prealpha` vs `v0.0.2-prealpha` candidate state.
- `PROJECT_STATUS.md` — advanced status baseline through Phase 25.
- `docs/agents/project-lead.md` — removed stale GitHub auth blocker and marked old Phase 18 recommendation as historical.
- `docs/handoff/phase-26.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issues: GitHub #16, GitHub #17.

## Phase 27 — Discoverability and Community Announcement Readiness

Status: complete. Phase commit pushed.

Goal: complete the non-blocking discoverability work before wider announcement while preserving pre-alpha/read-only positioning.

Artifacts:

- `README.md` — added short pitch, “Who this is for / not for”, comparison with `gnucash-web`, GnuDash, and Fava/Beancount, and community draft links.
- `docs/community/announcement-draft.md` — conservative announcement draft with safety warnings.
- `docs/community/social-preview.md` — manual GitHub social preview setup and safety checklist.
- GitHub topics configured: `gnucash`, `personal-finance`, `accounting`, `self-hosted`, `sveltekit`, `fastapi`, `open-source`, `finance`, `sqlite`.
- `docs/handoff/phase-27.md` — handoff document.

Test results: 262 passed, frontend check/auth-routes/build OK, Docker config valid.

Related issue: GitHub #16.

## Phase 28 — GnuCash Compatibility Matrix

Status: complete. Phase commit pushed.

Goal: document and test the current GnuCash SQL fixture compatibility baseline without claiming broad version support.

Artifacts:

- `docs/gnucash-compatibility.md` — compatibility matrix for committed synthetic fixtures, untested backends, user guidance, and future compatibility work.
- `apps/api/tests/test_gnucash_compatibility.py` — tests verifying fixture `versions` table markers and doc coverage.
- `README.md` — link to compatibility/safety docs.
- `docs/handoff/phase-28.md` — handoff document.

Test results: 264 passed, frontend check/auth-routes/build OK, Docker config validation OK.

Related issue: GitHub #15.

## Phase 29 — Audit-Driven Release Documentation Sync

Status: complete. Phase commit pushed.

Goal: run the required independent audit before Phase 29 and fix accepted release/status documentation blockers instead of expanding feature scope.

Artifacts:

- `docs/audits/2026-05-17-audit.md` — refreshed independent audit report for Phase 29.
- `README.md` — current status advanced through Phase 29 and linked to the latest audit.
- `CHANGELOG.md` — Unreleased entries updated through Phase 29.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated for Phases 25–29 and current compatibility limits.
- `docs/ROADMAP.md` — roadmap refreshed so `v0.0.1-prealpha` is no longer described as the next unpublished step.
- `docs/handoff/phase-28.md` — replaced stale pending commit placeholder with `343e098`.
- `docs/handoff/phase-29.md` — handoff document.

Test results: backend 264 passed (27 warnings), frontend check/auth-routes/build OK, Docker config validation OK.

Related issues: none created; audit blocker was fixed immediately in Phase 29.

## Phase 30 — Transaction Amount Range Filters for CSV Export

Status: complete. Phase commit pushed.

Goal: expose read-only transaction amount range filters in the frontend and preserve them in CSV export URLs.

Artifacts:

- `apps/web/src/lib/components/TransactionFilters.svelte` — added `min_amount` and `max_amount` controls with client-side min/max validation.
- `apps/web/src/routes/transactions/+page.server.ts` — passes amount range filters to the backend list endpoint and page data.
- `apps/web/src/routes/transactions/+page.svelte` — preserves amount filters across pagination/export and shows active filter count on the CSV export button.
- `apps/api/app/routers/transactions.py` — rejects inverted amount ranges before querying GnuCash.
- `apps/api/tests/test_transaction_export.py` — added export amount range and inverted-range tests.
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/release/v0.0.2-prealpha-notes.md`, and `docs/handoff/phase-30.md` — status/release docs updated.

Test results: backend full suite, frontend check/auth-routes/build, and Docker config validation all passed.

Related issue: GitHub #14.

## Phase 31 — Read-Only Safety Status Banner

Status: complete. Phase commit pushed.

Goal: add a small global UI reminder that the MVP is read-only by default and that GnuCash Desktop remains the authoritative editor.

Artifacts:

- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte` — reusable authenticated-app banner with explicit read-only/default-write safety language.
- `apps/web/src/routes/+layout.svelte` — displays the banner in the authenticated app shell above page content.
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/release/v0.0.2-prealpha-notes.md`, and `docs/handoff/phase-31.md` — status/release docs updated.

Test results: backend full suite, frontend check/auth-routes/build, and Docker config validation all passed.

Related issues: none; this completed a small release-readiness/read-only MVP polish item from the roadmap.

## Phase 32 — Backend Write-Gating Regression Coverage

Status: complete. Phase commits pushed.

Goal: convert the Phase 1 background-mission ad-hoc write-gating audit into committed regression tests for validate/create/patch controlled-write endpoints with writes disabled.

Artifacts:

- `docs/handoff/phase-32.md` — PM brief for the next engineer phase.
- `apps/api/tests/test_transaction_writes.py` — disabled-write regression coverage for validate/create/patch routes, including a guard that fails if `_write_service_for` is constructed while writes are disabled.
- `CHANGELOG.md` — Unreleased safety/testing entry for Phase 32.
- `docs/v0.2-controlled-writes.md` — documented that disabled-write bypass regression coverage exists while writes remain experimental and disabled by default.

Result: `Settings.gnucash_writes_enabled` remains `False` by default, all three controlled-write routes return read-only 403 responses with writes disabled, and committed tests prove `_write_service_for` / `GnuCashWriteService` is not constructed for those requests.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend check/auth-routes/build passed; Docker config validation passed.

Related issue: GitHub #18 (write-gating verification follow-up; status managed by audit/release triage).

## Phase 33 — Controlled-Writes Documentation Cleanup and Status Sync

Status: complete. Phase commit pushed.

Goal: clean stale controlled-writes documentation and synchronize the public status baseline after disabled-write regression coverage without expanding controlled-write scope.

Artifacts:

- `docs/v0.2-controlled-writes.md` — replaced stale active legacy-lock wording with current `fcntl.flock()` file-locking status, documented Phase 23 restore smoke coverage and Phase 32 disabled-write bypass regression coverage, and moved completed limitations into a resolved historical section.
- `README.md` — then-current status baseline advanced without claiming a `v0.0.2-prealpha` tag/release exists.
- `CHANGELOG.md` — added Phase 33 documentation/status cleanup entry.
- `docs/release/v0.0.2-prealpha-notes.md` and `docs/ROADMAP.md` — synchronized Phase 32 safety coverage and retained pre-alpha/read-only positioning.
- `docs/handoff/phase-33.md` — implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental/post-MVP and disabled by default; no product code or frontend auth storage paths were changed; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #23 closed by Phase 33; GitHub #19 reopened by the phase 7 audit for follow-up public status synchronization; GitHub #18 intentionally unchanged by this documentation phase.

## Phase 34 — README/Public Status Baseline Sync After Phase 33 Audit Finding

Status: complete. Phase commit pushed.

Goal: synchronize public status/readiness documentation through the Phase 33 baseline after the phase 7 audit reopened GitHub issue #19 for stale README wording.

Artifacts:

- `README.md` — current status advanced to the then-current Phase 33 baseline while retaining pre-alpha, not production-ready, not security-audited, read-only-by-default, and unpublished `v0.0.2-prealpha` language.
- `CHANGELOG.md` — added Phase 34 documentation/status sync entry.
- `docs/release/v0.0.2-prealpha-notes.md` — updated candidate scope from Phases 17–32 to Phases 17–33 and added Phase 33 documentation cleanup note; no tag or release was published.
- `docs/ROADMAP.md` — release-governance grouping updated to include Phase 33/34 status baseline cleanup.
- `docs/handoff/phase-34.md` — engineer implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental/post-MVP and disabled by default; no product code or frontend auth storage paths were changed; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #19 closed by Phase 34; GitHub #18, #20, #21, and #22 intentionally remain open.

## Phase 35 — Audit-Driven Phase 34 Public Baseline and Controlled-Writes Docs Sync

Status: complete. Phase commit pushed.

Goal: resolve the accepted phase 10 audit documentation blockers by synchronizing public current-status wording through the Phase 34/35 baseline and removing the stale controlled-writes limitation that described frontend amount range filters as missing.

Artifacts:

- `README.md` — current status advanced so Phase 34 is no longer missing from the public baseline, while retaining pre-alpha, not production-ready, not security-audited, read-only-by-default, and unpublished `v0.0.2-prealpha` language.
- `docs/v0.2-controlled-writes.md` — updated known limitations to state that Phase 30 added frontend amount range filters for browsing and CSV export; moved that work into resolved historical limitations.
- `CHANGELOG.md` — added Phase 35 documentation/status sync and controlled-writes limitation cleanup entries.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated through Phase 35 without publishing a tag or GitHub release.
- `docs/ROADMAP.md` — release-governance grouping updated to include Phase 35 documentation cleanup.
- `docs/handoff/phase-35.md` — implementation handoff updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental/post-MVP and disabled by default; no code path or write-gating route order was changed; no frontend auth storage path was changed; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #19 closed by Phase 35; GitHub #18, #20, #21, and #22 intentionally remain open.

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
