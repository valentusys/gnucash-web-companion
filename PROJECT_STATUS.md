# PROJECT_STATUS

Last updated: 2026-05-18

## Repository

- GitHub: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Status: pre-alpha / v0.1 read-only published

## Current baseline

Completed through Phase 99.

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
- Phase 36 — write-mode UI warning and explicit confirmation
- Phase 37 — independent audit and baseline sync
- Phase 38 — personal dogfood readiness
- Phase 39 — read-only smoke test automation
- Phase 40 — v0.0.2-prealpha release candidate cleanup
- Phase 41 — release gate audit for v0.0.2-prealpha
- Phase 42 — publish v0.0.2-prealpha
- Phase 43 — local deployment hardening guide
- Phase 44 — backup and recovery runbook
- Phase 45 — GnuCash compatibility fixture plan
- Phase 46 — Compatibility fixture implementation v1
- Phase 47 — auditor pass after compatibility work
- Phase 48 — UX polish for read-only core
- Phase 49 — transaction search/filter hardening
- Phase 50 — book switcher stabilization
- Phase 51 — auditor pass after UX/book/filter work
- Phase 52 — Russian localization planning and i18n foundation
- Phase 53 — community announcement draft
- Phase 54 — observability and diagnostics
- Phase 55 — v0.1 read-only scope freeze audit
- Phase 56 — v0.1 read-only release planning
- Phase 57 — v0.1.0-readonly release-gate audit
- Phase 58 — v0.1.0-readonly release publication audit
- Phase 59 — post-release regression risk audit
- Phase 60 — dogfood readiness audit
- Phase 61 — dogfood results audit
- Phase 62 — deployment safety audit
- Phase 63 — backup/recovery audit
- Phase 64 — compatibility audit
- Phase 65 — test coverage audit
- Phase 66 — security posture audit
- Phase 67 — open-source hygiene audit
- Phase 68 — documentation formatting audit
- Phase 69 — localization/i18n audit
- Phase 70 — community announcement audit
- Phase 71 — performance risk audit
- Phase 72 — data model and money correctness audit
- Phase 73 — multi-book access model audit
- Phase 74 — controlled writes boundary audit
- Phase 75 — v0.1.1 maintenance release audit
- Phase 76 — v0.2 planning audit
- Phase 77 — real read-only dogfood on copied/disposable GnuCash SQL book
- Phase 78 — Docker `/login` redirect-loop fix and browser/UI dogfood rerun
- Phase 79 — accept dogfood evidence, write v0.1 release notes, and final release gate
- Phase 80 — publish v0.1.0-readonly pre-release
- Phase 81 — redact default-book seed logs and close post-release security hardening issue #27
- Phase 82 — expand read-only multi-book access boundary regression coverage and close #35
- Phase 83 — replace frontend `Number()` money display decisions and close #34
- Phase 84 — define tested CSV export truncation/timeout behavior and close #32
- Phase 85 — post-v0.1 copied personal-book dogfood attempt with safe blocker tracking
- Phase 86 — Phase 85 dogfood blocker triage and safe copied-book preflight helper
- Phase 87 — large-book read-only benchmark v1
- Phase 88 — account with many splits performance test
- Phase 89 — dashboard aggregate performance and correctness pass
- Phase 90 — transaction active filter summary UX improvement
- Phase 91 — read-only book management metadata UI
- Phase 92 — compatibility fixture v2 / version matrix progress
- Phase 93 — Russian localization small slice
- Phase 94 — post-v0.1 maintenance release decision
- Phase 95 — CSV export row-count/header mismatch fix
- Phase 96 — synthetic large-export benchmark and UX confirmation
- Phase 97 — v0.1.1-readonly release-prep checklist and notes
- Phase 98 — v0.1.1-readonly release-gate verification
- Phase 99 — v0.1.1-readonly pre-publish dry-run and authorization guard

- Phase 87 completed the large-book read-only benchmark v1 on generated synthetic data only: a local CLI now creates a disposable synthetic GnuCash SQLite book and measures accounts tree, transactions first page, transaction filters, account detail transactions, dashboard summary, and CSV export through read-only authenticated API paths. Results are documented in `docs/performance/phase-87-large-book-benchmark.md`. The 1,000-transaction run found no endpoint failure, but account-detail transactions measured above one second locally and CSV export returned only 500 rows while reporting `csv_total=1000` and `truncated=false`; GitHub #39 tracks that follow-up. GitHub #30 was closed as the benchmark now exists. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 88 completed the account-with-many-splits performance test on generated synthetic data only: the benchmark fixture now includes 1,000 transactions, one 60-split transaction, account-detail pagination checks for offsets 0 and 50, and transaction-detail rendering for the many-splits transaction. Results are documented in `docs/performance/phase-88-many-splits-benchmark.md`. The many-splits detail path rendered 60 splits without endpoint failure in the local/TestClient run; account-detail pagination remains above one second locally and is documented as a limitation rather than a scalability claim. GitHub #31 was closed with evidence. GitHub #39 remains open for the CSV export row-count/header mismatch. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 89 completed the dashboard aggregate performance and correctness pass on generated synthetic data only: dashboard summary now exposes `reporting_basis=base_currency_only`, `includes_currency_conversion=false`, and no-conversion/mixed-currency limitations, the web dashboard displays those limitations, report date validation now returns clearer `422` client errors, and the large-book benchmark now covers dashboard summary, cashflow-by-month, expenses-by-account, and recent-transactions. Results are documented in `docs/performance/phase-89-dashboard-aggregate-benchmark.md`. All dashboard endpoints returned `200` in the 1,000-transaction local/TestClient benchmark; cashflow-by-month and recent-transactions remain service-layer scans and are documented as pre-alpha evidence rather than a production scalability claim. GitHub #33 was closed with evidence. GitHub #39 remains open for the CSV export row-count/header mismatch. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 90 completed a narrow transaction search/filter UX improvement from GitHub #11: the transaction filter form now shows a readable active filter summary for search, account, date range, and amount range, explicitly stating that the same filters apply to the read-only list and CSV export. Frontend route checks cover the summary and CSV parity copy. No backend write changes were made, CSV export query-string parity remains intact, no real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 91 completed the read-only book management metadata UI from the roadmap and GitHub #13 subset: the web app now exposes `/books` from desktop/mobile navigation, lists only accessible configured books, marks the current/default book, and shows book name, base currency, storage type, read-only status, and access status without upload, deletion, registry editing, GnuCash data editing, collaborative, or family-wallet framing. Existing backend access-boundary tests continue to prove unauthorized and archived books are hidden/blocked; frontend route checks cover the new page and nav links. GitHub #13 was updated with evidence and remains open for future admin-only registration/default/deletion-from-registry workflows. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 92 completed a narrow compatibility-fixture/version-matrix maintenance result: a tested metadata collector now records safe schema/version evidence from copied/disposable GnuCash SQLite books while redacting the input path and excluding account names, transaction descriptions, amounts, memos, split rows, screenshots, app DB data, and secrets. `docs/gnucash-compatibility.md` now includes a narrow Phase 92 matrix row for the local generated-fixture metadata procedure, and `docs/gnucash-version-fixture-plan.md` now documents the copied/test-book collection process. GnuCash Desktop was not installed in this environment, so no desktop-version compatibility pass is claimed. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 93 completed a narrow Russian localization slice: desktop/mobile navigation now localizes the `/books` label, the read-only `/books` metadata page uses English/Russian catalog strings for headings, helper copy, read-only badges, access/status labels, empty state, and the GnuCash Desktop authoritative-editor safety note, and `README.ru.md` plus `docs/localization.md` document that English remains canonical and translation is incomplete. Frontend route/static checks cover the new catalog strings and localized `/books` usage. No real/private data was committed, no new tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 94 completed the post-v0.1 maintenance-release decision from the roadmap without analyst/auditor involvement or audit-only artifacts: `docs/release/v0.1.1-readonly-decision.md` records the verdict `More fixes required before maintenance release`. The reviewed post-`v0.1.0-readonly` change set is meaningful, but GitHub #39 remains an open read-only CSV export correctness blocker because benchmark evidence repeatedly showed the CSV body capped at 500 rows while headers report a 10,000-row cap and `truncated=false`. No `v0.1.1-readonly` notes/checklist were created, no tag/release was published, no real/private data was committed, writes remain disabled by default, and no v0.2 work was started.

- Phase 95 fixed the read-only CSV export row-count/header mismatch tracked by GitHub #39: CSV export now asks the service layer for up to the documented export cap instead of inheriting the historical 500-row service clamp used by normal list-style callers. Regression coverage proves a 501-row synthetic export returns 501 data rows with `X-CSV-Export-Limit: 10000`, `X-CSV-Export-Total: 501`, and `X-CSV-Export-Truncated: false`; the benchmark helper also records the CSV limit header. A targeted 1,000-transaction synthetic benchmark returned 1,000 CSV data rows with `csv_limit=10000`, `csv_total=1000`, and `truncated=False`. No frontend proxy change was needed because it already forwards CSV metadata headers; frontend route checks still verify that behavior. No real/private data was committed, no tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 96 confirmed the Phase 95 / GitHub #39 fix through the generated synthetic large-book benchmark path and a narrow frontend UX copy check. The 1,000-transaction synthetic benchmark returned 1,000 CSV data rows with `csv_limit=10000`, `csv_total=1000`, `truncated=False`, `csv_expected_body_rows=1000`, and `csv_body_matches_expected=True`; results are documented in `docs/performance/phase-96-large-export-benchmark.md`. Benchmark JSON now records expected body-row consistency fields, and the transaction export helper copy now states that export is read-only, filtered, capped at 10,000 rows, synchronous, and may require narrower filters if a request times out or is truncated. GitHub #39 remains closed; GitHub #38 remains open and separate for copied personal-book dogfood. No real/private data was committed, no tag/release was published, writes remain disabled by default, and no v0.2 work was started.

- Phase 97 prepared conservative `v0.1.1-readonly` release-prep artifacts without publishing a tag/release: `docs/release/v0.1.1-readonly-notes.md` and `docs/release/v0.1.1-readonly-checklist.md`. The notes/checklist summarize post-`v0.1.0-readonly` maintenance value, especially the Phase 95 CSV export fix and Phase 96 synthetic benchmark confirmation, while keeping pre-alpha/read-only/default-write-disabled safety language and explicitly requiring a later Phase 98 release gate before publication. GitHub #39 remains closed; GitHub #38 remains open/blocked for copied personal-book dogfood. No real/private financial data, GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, or keys were committed; writes remain disabled by default; controlled writes remain post-MVP/experimental; no v0.2 work was started.

- Phase 98 completed the `v0.1.1-readonly` final release-gate verification without publishing a tag/release: `docs/release/v0.1.1-readonly-final-gate.md` records the verdict `Ready for later authorized publish phase`. Backend tests passed (`329 passed, 27 warnings`), frontend check/auth-routes/build passed, Docker Compose config validation passed, recent GitHub Actions `main` runs were successful, no local tag or GitHub release named `v0.1.1-readonly` exists, GitHub #39 remains closed, and GitHub #38 remains open/blocked for copied personal-book dogfood. No backend/frontend/config/write-mode code was changed; writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private financial data, GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, or keys were committed; no v0.2 work was started.

- Phase 99 completed a safe non-publishing `v0.1.1-readonly` pre-publish dry-run and authorization guard: `docs/release/v0.1.1-readonly-prepublish-dry-run.md` records the verdict `Ready for explicit authorized publish`, confirms release notes/checklist/final-gate artifact presence, confirms no local tag or GitHub release named `v0.1.1-readonly` exists, records recent GitHub Actions state, records would-run publish commands as `NOT EXECUTED`, and records that publication authorization is absent in this phase. GitHub #39 remains closed; GitHub #38 remains open/blocked for copied personal-book dogfood. No backend/frontend/config/write-mode code was changed; no tag, GitHub release, package, or release artifact was published; writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private financial data, GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, or keys were committed; no v0.2 work was started.

Next planned phase:

- Phase 100 is planned in `docs/handoff/phase-100-pm-brief.md` as a non-publishing synthetic/disposable install/upgrade smoke on current `main`, because Val has not provided the separate explicit authorization required for `v0.1.1-readonly` publication. Do not create a tag, GitHub release, package, or release artifact in Phase 100. If Val explicitly authorizes publication in a separate request instead, re-check branch, HEAD, clean working tree, tag/release absence, recent GitHub Actions state, and release notes before any publish command.

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

## Phase 36 — Write-Mode UI Warning and Explicit Confirmation

Status: complete. Phase commit pushed.

Goal: resolve GitHub #21 by adding explicit warning and acknowledgement coverage around the experimental controlled-write UI without expanding write capabilities or changing backend write-gating.

Artifacts:

- `apps/web/src/lib/components/WriteModeWarning.svelte` — prominent reusable warning that controlled writes are experimental post-MVP, disabled by default, for disposable/test copies with backups only, and subordinate to GnuCash Desktop.
- `apps/web/src/routes/transactions/+page.svelte` — enabled write entry point remains hidden unless frontend `GNUCASH_WRITES_ENABLED === 'true'` and now includes warning text/panel when shown.
- `apps/web/src/routes/transactions/new/+page.svelte` — warning panel before the form plus required acknowledgement checkbox before final create submission; validation action remains available with `formnovalidate`.
- `apps/web/src/routes/transactions/new/+page.server.ts` — final create action rejects missing acknowledgement before validate/create API calls.
- `apps/web/scripts/test-auth-routes.mjs` — static route checks now verify disabled-write redirect, enabled warning copy, and acknowledgement coverage.
- `CHANGELOG.md`, `docs/v0.2-controlled-writes.md`, `docs/release/v0.0.2-prealpha-notes.md`, and `docs/handoff/phase-36.md` — Phase 36 status/safety docs updated.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the default documented state; controlled writes remain experimental/post-MVP and disabled by default; backend disabled-write guards remain covered by `TestWritesDisabledByDefault`; no auth localStorage/sessionStorage path was introduced; no real financial/secrets artifacts were added.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #21 closed by Phase 36; GitHub #18, #20, and #22 intentionally remain open.

## Phase 37 — Independent Audit and Baseline Sync

Status: complete. Phase commit pushed.

Goal: run the required independent audit after Phase 36 and synchronize public baseline/status documentation without adding features, publishing a release, or expanding controlled writes.

Artifacts:

- `docs/audits/2026-05-18-phase-37-audit.md` — independent Phase 37 audit artifact.
- `README.md` — current status advanced to Phase 0–36 complete and latest audit link updated to the Phase 37 audit.
- `CHANGELOG.md` — added Phase 37 Unreleased entry.
- `docs/handoff/phase-37.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental/post-MVP and disabled by default; Phase 37 made documentation/status-only fixes after the audit and did not change write code, auth storage, or release artifacts.

Test results: disabled-write regression subset passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: GitHub #19 closed by Phase 37; GitHub #18, #20, and #22 intentionally remain open.

## Phase 38 — Personal Dogfood Readiness

Status: complete. Phase commit pushed.

Goal: prepare safe personal read-only dogfood instructions for testing against a copied GnuCash SQL book without adding features, expanding write scope, or publishing a release.

Artifacts:

- `docs/dogfood/personal-readonly-dogfood.md` — step-by-step local dogfood guide covering copied-book setup, `data/books/`, `GNUCASH_WRITES_ENABLED=false`, Docker startup, screen checks, CSV export handling, write-UI-hidden confirmation, shutdown, cleanup, and safe reporting rules.
- `scripts/smoke/read-only-smoke-check.md` — manual smoke checklist for read-only dogfood readiness; automation remains planned for Phase 39.
- `CHANGELOG.md` — added Phase 38 Unreleased entry.
- `docs/handoff/phase-38.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 38 added documentation/checklists only and did not change product code, backend write-gating, frontend write UI, auth storage, or release artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: no Phase 38-specific GitHub issue found in the current open issue list; GitHub #18, #20, and #22 intentionally remain open.

## Phase 39 — Read-Only Smoke Test Automation

Status: complete. Phase commit pushed.

Goal: add a minimal automated API smoke script for local read-only Docker deployments without requiring real financial data or expanding write scope.

Artifacts:

- `scripts/smoke/read-only-api-smoke.py` — stdlib-only Python smoke script for local API deployments; checks `/health`, login, `/auth/me`, default book discovery through `/books`, book metadata, accounts, transactions, reports summary, and disabled-write 403 responses for validate/create/patch controlled-write endpoints.
- `scripts/smoke/read-only-smoke-check.md` — updated manual checklist with the Phase 39 automated API smoke command and environment variables.
- `CHANGELOG.md` — added Phase 39 Unreleased entry.
- `docs/handoff/phase-39.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 39 adds smoke automation only and does not enable writes, add write capability, change auth storage, publish a release, or add real financial/secrets artifacts.

Test results: script help/compile check passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed.

Related issues: no Phase 39-specific GitHub issue found in the current open issue list; GitHub #18, #20, and #22 intentionally remain open.

## Phase 40 — v0.0.2-prealpha Release Candidate Cleanup

Status: complete. Phase commit pushed.

Goal: prepare honest release-candidate documentation for `v0.0.2-prealpha` without publishing a tag or GitHub release.

Artifacts:

- `docs/release/v0.0.2-prealpha-checklist.md` — new release-candidate checklist covering scope, exclusions, required gate, automated checks, optional local smoke, and release command placeholder reserved for the explicit publish phase.
- `docs/release/v0.0.2-prealpha-notes.md` — updated through Phase 40 with dogfood/smoke work and release-gate language.
- `README.md` — current status advanced through Phase 40 and linked to the `v0.0.2-prealpha` checklist.
- `CHANGELOG.md` — added Phase 40 Unreleased entry.
- `docs/handoff/phase-40.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 40 is documentation/release-candidate cleanup only and does not enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #20 updated with Phase 40 status; GitHub #18 and #22 intentionally remain open.

## Phase 41 — Release Gate Audit for v0.0.2-prealpha

Status: complete. Phase commit pushed.

Goal: run the external release-gate audit before any `v0.0.2-prealpha` tag or GitHub release is published, then fix only accepted audit blockers/mismatches.

Artifacts:

- `docs/audits/2026-05-18-v0.0.2-release-gate.md` — independent release-gate audit artifact with verdict `Ready after listed blockers`.
- `README.md` — current status advanced through Phase 41 and latest audit link updated to the release-gate audit.
- `docs/release/v0.0.2-prealpha-notes.md` — Phase 41 audit note added and stale related-doc links fixed before use as release notes.
- `CHANGELOG.md` — added Phase 41 Unreleased entry.
- `docs/handoff/phase-41.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 41 did not enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts. Disabled validate/create/patch write gating was re-verified.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed. Post-push GitHub CI should be checked before Phase 42 publication.

Related issues: GitHub #18 closed after release-gate re-verification; GitHub #20 updated with Phase 41 gate status; GitHub #22 remains open for compatibility fixtures.

## Phase 42 — Publish v0.0.2-prealpha

Status: complete. Phase commit pushed, annotated tag pushed, and GitHub pre-release published.

Goal: publish `v0.0.2-prealpha` only after confirming the Phase 41 release gate was complete and post-push GitHub CI for the gate commit was green.

Artifacts:

- Git tag: `v0.0.2-prealpha`.
- GitHub pre-release: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.0.2-prealpha
- `README.md` — current status and release readiness now point to the published `v0.0.2-prealpha` release.
- `CHANGELOG.md` — moved accumulated pre-alpha changes into the `0.0.2-prealpha` release section and added the Phase 42 publication entry.
- `docs/handoff/phase-42.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 42 did not enable writes, expand write scope, or add real financial/secrets artifacts.

Test results: post-Phase-41 GitHub CI was green before publication; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #20 updated and closed after successful `v0.0.2-prealpha` publication.

## Phase 43 — Local Deployment Hardening Guide

Status: complete. Phase commit pushed.

Goal: add practical, conservative instructions for safely running the pre-alpha app locally or on a trusted LAN/VPN without implying production readiness.

Artifacts:

- `docs/deployment/local-secure-deployment.md` — local-only and LAN/VPN-only deployment guide covering reverse proxy/HTTPS notes, `.env` secrets, data/backup/app DB locations, GnuCash copied-book handling, public-internet warning, read-only smoke verification, and keeping `GNUCASH_WRITES_ENABLED=false`.
- `README.md` — current status advanced through Phase 43 and linked to the local secure deployment guide from quick-start and security/deployment sections.
- `CHANGELOG.md` — added Phase 43 Unreleased entry.
- `docs/handoff/phase-43.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 43 is documentation-only and does not enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no Phase 43-specific GitHub issue found in the current open issue list; GitHub #22, #17, #13, #12, and #11 remain open for later roadmap work.

## Phase 44 — Backup and Recovery Runbook

Status: complete. Phase commit pushed.

Goal: document conservative backup and recovery procedures for read-only deployments and future experimental controlled-write testing without claiming production-grade disaster recovery.

Artifacts:

- `docs/operations/backup-and-recovery.md` — manual backup/recovery runbook covering app metadata DB backups, copied GnuCash book backups, Docker data paths, backup frequency, restore dry-runs, controlled-write pre-write backup expectations, restored-book verification, and explicit non-guarantees.
- `README.md` — current status advanced through Phase 44 and linked to the backup/recovery runbook from safety/deployment documentation.
- `docs/deployment/local-secure-deployment.md` — Phase 43 placeholder for a later runbook replaced with the actual Phase 44 runbook link.
- `CHANGELOG.md` — added Phase 44 Unreleased entry.
- `docs/handoff/phase-44.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 44 is documentation-only and does not enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no Phase 44-specific GitHub issue found in the current open issue list; GitHub #22, #17, #13, #12, and #11 remain open for later roadmap work.

## Phase 45 — GnuCash Compatibility Fixture Plan

Status: complete. Phase commit pushed.

Goal: advance GitHub issue #22 by defining a safe, conservative plan for real-version GnuCash compatibility fixtures without committing binary fixtures, real data, or expanding write scope.

Artifacts:

- `docs/gnucash-version-fixture-plan.md` — new planning document covering target GnuCash version families, OS/source metadata, synthetic fixture data model, safe generation/storage policy, and acceptance tests for future fixture implementation.
- `docs/gnucash-compatibility.md` — linked the Phase 45 fixture plan from future compatibility work.
- `README.md` — current status advanced through Phase 45 and linked the fixture plan under compatibility/safety docs.
- `CHANGELOG.md` — added Phase 45 Unreleased entry.
- `docs/handoff/phase-45.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 45 is documentation/planning-only and does not add fixture binaries, enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed (`269 passed`, 27 existing warnings); frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 45 plan and remains open for Phase 46 implementation.

## Phase 46 — Compatibility Fixture Implementation v1

Status: complete. Phase commit pushed.

Goal: add the first generated disposable compatibility fixture path beyond mocks without committing a new binary GnuCash file or expanding write scope.

Artifacts:

- `apps/api/scripts/create_compatibility_fixture_v1.py` — deterministic generator for a synthetic disposable GnuCash SQLite fixture and non-sensitive metadata/sha256 output.
- `apps/api/tests/test_compatibility_fixture_v1.py` — read-only compatibility tests for generation metadata, checksum no-mutation behavior, account tree, transaction list, split transaction detail, reports basic, and loading a copied generated fixture.
- `docs/gnucash-compatibility-fixture-v1.md` — documentation for the generator path, data model, validation coverage, and safety limits.
- `.gitignore` — ignores `apps/api/tests/generated-fixtures/` so locally generated SQLite fixtures are not committed.
- `docs/gnucash-compatibility.md`, `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-46.md` — status and compatibility docs synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 46 does not add write capability, enable writes, publish a release/tag, or add real financial/secrets artifacts. The generated fixture is synthetic and generated in temp/ignored paths; no new binary GnuCash fixture is committed.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 46 implementation status and remains open for future desktop-version fixture coverage unless maintainers decide this generator path is sufficient for the issue.

## Phase 47 — Auditor Pass After Compatibility Work

Status: complete. Phase commit pushed.

Goal: independently audit the Phase 46 compatibility fixture work for fixture safety, personal-data hygiene, unwanted binary commits, honest compatibility documentation, and README overclaim risk.

Artifacts:

- `docs/audits/2026-05-18-phase-47-audit.md` — independent Phase 47 audit artifact with verdict `Ready for pre-alpha release` and no blockers.
- `README.md` — current status advanced through Phase 47 and latest-audit link updated to the Phase 47 audit.
- `CHANGELOG.md` — added Phase 47 Unreleased entry.
- `docs/handoff/phase-47.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 47 did not enable writes, expand write scope, publish a release/tag, or add real financial/secrets artifacts. Only existing committed fixture binaries are the historical synthetic test fixtures; the Phase 46 generated fixture output path remains ignored and no generated binary was committed.

Test results: Phase 46 compatibility fixture tests passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #22 updated with the Phase 47 audit result and remains open for future desktop-version fixture coverage unless maintainers decide the generated fixture path is sufficient for the issue.

## Phase 48 — UX Polish for Read-Only Core

Status: complete. Phase commit pushed.

Goal: improve read-only daily usability with small frontend-only polish while avoiding any write-scope expansion.

Artifacts:

- `apps/web/src/lib/components/TransactionFilters.svelte` — adds explanatory read-only filter copy, filtered-view status, and a disabled/explicit reset-filters button when no filters are active.
- `apps/web/src/lib/components/TransactionCard.svelte` and `TransactionTable.svelte` — improve empty transaction states and mobile transaction card copy.
- `apps/web/src/routes/transactions/+page.svelte` — clarifies CSV export filter count/status and documents the 10,000-row cap next to the export action.
- `apps/web/src/routes/accounts/+page.svelte` — adds an account-tree empty state for missing/empty read-only book views.
- `apps/web/src/routes/accounts/[id]/+page.svelte` — replaces the plain back link with clearer account breadcrumbs.
- `CHANGELOG.md` and `docs/handoff/phase-48.md` — phase status and handoff synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 48 is frontend UX-only and does not add write capability, account editing, import/sync, release/tag publication, or real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: none identified in the roadmap for Phase 48.

## Phase 49 — Transaction Search/Filter Hardening

Status: complete. Phase commit pushed.

Goal: make read-only transaction search and filters more reliable and understandable while keeping API/frontend/CSV export behavior aligned.

Artifacts:

- `apps/api/app/routers/transactions.py` — adds shared transaction-filter validation so list, account-scoped list, book-scoped list, and CSV export reject invalid/inverted date ranges and inverted amount ranges before querying GnuCash.
- `apps/api/tests/test_transactions.py` — adds list-view regression coverage for inverted date and amount ranges.
- `apps/api/tests/test_transaction_export.py` — adds CSV export regression coverage for inverted date ranges and combined query/date/account/amount filter parity.
- `apps/web/src/lib/components/TransactionFilters.svelte` — adds client-side inverted date range validation with accessible inline error state alongside existing amount validation.
- `apps/web/scripts/test-auth-routes.mjs` — extends frontend route checks to assert transaction filter URL/CSV parity and frontend range validation coverage.
- `docs/transactions-filters.md` — documents supported filters, validation, URL/pagination behavior, and CSV export parity.
- `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-49.md` — phase status and documentation synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 49 does not add write capability, enable write mode, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #11 updated with the Phase 49 hardening summary and left open for broader future read-only search/filter enhancements.

## Phase 50 — Book Switcher Stabilization

Status: complete. Phase commit pushed.

Goal: stabilize the existing multi-book UI foundation at a safe read-only level without adding book upload, book registration UI, collaborative editing, or write-scope expansion.

Artifacts:

- `apps/web/src/lib/api/server.ts` — adds shared accessible-book context resolution that prefers the selected accessible book, then accessible default, then first accessible book; stale/unauthorized selected-book cookies are refreshed or cleared before book-aware API routes are built.
- `apps/web/src/routes/+layout.server.ts`, `dashboard/+page.server.ts`, `accounts/+page.server.ts`, `accounts/[id]/+page.server.ts`, `transactions/+page.server.ts`, and `transactions/[id]/+page.server.ts` — use shared active-book context so page data routes no longer trust raw `selected_book_id` directly.
- `apps/web/src/lib/components/BookSwitcher.svelte` — labels the current book clearly, preserves route/query string on switch, marks the default book, and frames multi-book as independent read-only books.
- `apps/web/scripts/test-auth-routes.mjs` — adds static frontend checks for book context fallback, route usage, route/query preservation, and no collaborative/upload framing.
- `docs/book-switcher-readonly-model.md` — documents read-only multi-book behavior, access boundary, fallback order, and non-goals.
- `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/handoff/phase-50.md` — phase status and documentation synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 50 does not add write capability, book upload, import/sync, account editing, collaborative editing, release/tag publication, or real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #13 updated with the Phase 50 stabilization summary and remains open for future admin-only book management UI.

## Phase 51 — Auditor Pass After UX/Book/Filter Work

Status: complete. Phase commit pushed.

Goal: independently audit the Phase 48–50 UX, transaction filter/export, and book-switcher work to confirm read-only scope, independent-books framing, filter/export safety, and documentation consistency.

Artifacts:

- `docs/audits/2026-05-18-phase-51-audit.md` — independent Phase 51 audit artifact with verdict `Ready for pre-alpha release` and no blockers.
- `README.md` — current status advanced through Phase 51 and latest-audit link updated to the Phase 51 audit.
- `CHANGELOG.md` — added Phase 51 Unreleased entry.
- `docs/handoff/phase-51.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 51 did not enable writes, expand write scope, add book upload/import/management UI, add collaborative editing, publish a release/tag, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: GitHub #11 and #13 updated with the Phase 51 audit result and remain open for broader future search/filter and admin-only book-management work.

## Phase 52 — Russian Localization Planning and i18n Foundation

Status: complete. Phase commit pushed.

Goal: start SvelteKit i18n carefully without translating the whole project or making Russian the default.

Artifacts:

- `apps/web/src/lib/i18n/messages.ts` and `apps/web/src/lib/i18n/index.ts` — typed English-default locale catalog with opt-in Russian strings.
- `apps/web/src/routes/locale/+server.ts` — safe locale cookie handler for switching UI language without browser localStorage/sessionStorage.
- `apps/web/src/lib/components/LocaleSwitcher.svelte` — small locale switcher used on login and authenticated navigation.
- Login, navigation, read-only safety banner, dashboard title, accounts title, and transactions title now use the i18n catalog while English remains the default.
- `README.ru.md` — initial Russian README stub with explicit canonical-English and safety caveats.
- `docs/localization.md` — localization approach, reviewed Russian safety text policy, and non-goals.
- `README.md`, `CHANGELOG.md`, and `docs/handoff/phase-52.md` — phase status and documentation synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default; Phase 52 does not enable writes, expand write scope, publish a release/tag, add real financial/secrets artifacts, or make Russian the default. English docs remain canonical and Russian safety text is manually reviewed.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #17 updated with the Phase 52 localization foundation summary and remains open for broader future translation work.

## Phase 53 — Community Announcement Draft

Status: complete. Phase commit pushed.

Goal: prepare a cautious community announcement package for interested GnuCash/self-hosted testers without production marketing or write-safety overclaims.

Artifacts:

- `docs/community/announcement-draft.md` — refreshed conservative announcement draft with short pitch, current working scope, not-ready scope, safety warning, target tester profile, feedback prompts, and suggested posts for r/GnuCash, r/selfhosted, later Show HN, and Mastodon/Linux/self-hosted communities.
- `docs/community/where-to-share.md` — channel guidance, posting gates, anti-channels, feedback prompts, and safety checklist for community sharing.
- `README.md` — current status advanced through Phase 53 and community docs linked.
- `CHANGELOG.md` — Unreleased entry added for Phase 53.
- `docs/handoff/phase-53.md` — PM/engineer handoff and verification report.

Safety result: Phase 53 is documentation/community-planning only. MVP remains read-only by default; `GNUCASH_WRITES_ENABLED=false` remains the safe/default state; controlled writes remain experimental post-MVP and disabled by default. No write scope, release/tag, product code, real financial data, `.env`, app DB, backup, secret, key, token, certificate, real screenshot, or real export was added.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: GitHub #16 received a Phase 53 follow-up comment and remains closed.

## Phase 54 — Observability and Diagnostics

Status: complete. Phase commit pushed.

Goal: make self-hosted deployment errors easier to diagnose with safe startup diagnostics, a richer non-sensitive health endpoint, default-book/app-DB checks, and troubleshooting documentation.

Artifacts:

- `apps/api/app/diagnostics.py` — safe diagnostics helpers for default book existence, app metadata DB reachability, health payload construction, and structured startup logging.
- `apps/api/app/main.py` — startup now logs a `startup_diagnostics` JSON event, and `/health` returns app DB/default-book/write-mode checks without exposing secrets or full paths.
- `apps/api/tests/test_health.py` — regression tests for richer health payloads, understandable missing-book diagnostics, and secret/path-safe startup logs.
- `docs/operations/troubleshooting.md` — self-hosted troubleshooting guide covering health payloads, missing default book checks, app DB reachability, startup diagnostics logs, and safe bug-report contents.
- `README.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`, and `docs/handoff/phase-54.md` — status and troubleshooting docs synchronized.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 54 does not add write capability, enable write mode, publish a release/tag, add telemetry, or add real financial/secrets artifacts. Health/startup diagnostics intentionally avoid full book paths, credentials, JWT secrets, admin passwords, database URLs, and real data.

Test results: health diagnostics tests passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issue: no Phase 54-specific GitHub issue was identified in the open issue list.

## Phase 55 — v0.1 Read-Only Scope Freeze Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to prepare a real `v0.1.0-readonly` milestone plan without publishing a release or expanding write scope.

Artifacts:

- `docs/audits/2026-05-18-phase-55-v0.1-readonly-scope-freeze.md` — independent scope-freeze audit artifact with verdict `Ready to prepare v0.1 read-only`.
- `docs/ROADMAP.md` — stale release-posture wording fixed so `v0.0.2-prealpha` is no longer described as unpublished.
- `README.md` — current status advanced through Phase 55 and latest-audit link updated to the Phase 55 audit.
- `CHANGELOG.md` — Unreleased entry added for Phase 55.
- `docs/handoff/phase-55.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 55 did not enable writes, expand write scope, publish a release/tag, add production/security-audited claims, or add real financial/secrets artifacts.

Test results: disabled-write regression subset passed; backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no new Phase 55 issue was required. GitHub #22, #17, #13, #12, and #11 remain open backlog items to consider during v0.1 planning.

## Phase 56 — v0.1 Read-Only Release Planning

Status: complete. Phase commit pushed.

Goal: create a conservative `v0.1.0-readonly` release plan and checklist after the Phase 55 audit verdict allowed v0.1 planning, without publishing a tag/release or expanding write scope.

Artifacts:

- `docs/release/v0.1.0-readonly-plan.md` — included/excluded scope, open backlog triage, minimum checks, dogfood requirements, compatibility scope, upgrade path, release blockers, rollback plan, and required next governance step.
- `docs/release/v0.1.0-readonly-checklist.md` — release-gate checklist for scope, docs, automated checks, runtime smoke/dogfood, compatibility, sensitive-data hygiene, GitHub/project hygiene, publication gate, and rollback readiness.
- `README.md` — current status advanced through Phase 56 and v0.1 planning docs linked.
- `CHANGELOG.md` — Unreleased entry added for Phase 56.
- `docs/ROADMAP.md` — next posture advanced from planning to a future v0.1 release-gate audit.
- `docs/handoff/phase-56.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 56 did not enable writes, expand write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real financial/secrets artifacts.

Test results: backend full suite passed; frontend check/auth-routes/build passed; Docker config validation passed; `git diff --check` passed.

Related issues: no Phase 56-specific GitHub issue was required. The plan explicitly triages open issues #22, #17, #13, #12, and #11 for v0.1 in/out scope.

## Phase 57 — v0.1.0-readonly Release-Gate Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to publish `v0.1.0-readonly` without publishing a tag/release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-57-audit.md` — independent Phase 57 release-gate audit artifact with verdict `Not ready for v0.1.0-readonly`.
- `README.md` — current status advanced through Phase 57 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for Phase 57.
- `docs/handoff/phase-57.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 57 did not enable writes, expand write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real financial/secrets artifacts.

Release-gate result: v0.1 publication is blocked by process/docs evidence gaps, not by a discovered read-only boundary break. Required blockers are conservative `v0.1.0-readonly` release notes and a recorded runtime smoke/dogfood pass on copied or disposable data.

Test results: disabled-write regression subset and backend full suite passed. Frontend check/auth-routes/build, Docker config validation, and `git diff --check` are recorded in the Phase 57 handoff.

Related issues: GitHub #24 and #25 created for the Phase 57 release-gate blockers.

## Phase 58 — v0.1.0-readonly Release Publication Audit

Status: complete. Phase commit pushed.

Goal: audit the expected `v0.1.0-readonly` publication state from the auditor roadmap without publishing a tag/release or expanding write scope.

Artifacts:

- `docs/audits/phase-58-audit.md` — independent Phase 58 publication audit artifact with verdict `Not ready / publication audit blocked`.
- `README.md` — current status advanced through Phase 58 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 58 publication audit result.
- `docs/handoff/phase-58.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 58 did not enable writes, expand write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real financial/secrets artifacts.

Release-publication result: no `v0.1.0-readonly` git tag or GitHub release exists, which is consistent with the unresolved Phase 57 blockers. Publication remains blocked by missing conservative v0.1 release notes and missing copied/disposable-data runtime smoke/dogfood evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 58 handoff.

Related issues: no new issue created; GitHub #24 and #25 were updated with Phase 58 audit comments and remain the meaningful release-publication blockers.

## Phase 59 — Post-Release Regression Risk Audit

Status: complete. Phase commit pushed.

Goal: audit whether commits after `v0.1.0-readonly` accidentally changed release assumptions, without publishing a tag/release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-59-audit.md` — independent Phase 59 post-release regression-risk audit artifact with verdict `Not applicable as a post-v0.1 regression audit; stay pre-release for v0.1`.
- `README.md` — current status advanced through Phase 59 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 59 regression-risk audit result.
- `docs/handoff/phase-59.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 59 did not enable writes, expand write scope, publish a v0.1 tag/release, add production/security-audited claims, or add real financial/secrets artifacts.

Post-release regression result: a true post-v0.1 regression audit is not applicable yet because no `v0.1.0-readonly` git tag or GitHub release exists. README and PROJECT_STATUS continue to distinguish latest public release (`v0.0.2-prealpha`) from current `main`; publication remains blocked by missing conservative v0.1 release notes and missing copied/disposable-data runtime smoke/dogfood evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 59 handoff.

Related issues: no new issue created; GitHub #24 and #25 were updated with Phase 59 audit comments and remain the meaningful v0.1 publication blockers.

## Phase 60 — Dogfood Readiness Audit

Status: complete. Phase commit pushed.

Goal: audit whether the maintainer can safely start read-only dogfood on a copied real GnuCash SQL book, without performing the dogfood run, publishing a release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-60-audit.md` — independent Phase 60 dogfood-readiness audit artifact with verdict `Ready for maintainer dogfood`.
- `README.md` — current status advanced through Phase 60 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 60 dogfood-readiness audit result.
- `docs/handoff/phase-60.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 60 did not enable writes, expand write scope, publish a v0.1 tag/release, add production/security-audited claims, run dogfood against a real book, or add real financial/secrets artifacts.

Dogfood-readiness result: maintainer dogfood instructions exist and cover copied-book setup, `GNUCASH_DEFAULT_BOOK_PATH`, disabled writes, Docker startup, dashboard/accounts/transactions checks, CSV export, shutdown, cleanup, and public-internet warnings. This confirms readiness to execute dogfood; it does not record a completed dogfood pass and does not close the release blocker tracked in GitHub #25.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 60 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 60 dogfood-readiness audit result and remains open until actual copied/disposable-data runtime evidence is recorded. GitHub #24 also remains open for conservative v0.1 release notes.

## Phase 61 — Dogfood Results Audit

Status: complete. Phase commit pushed.

Goal: audit reported results from real copied-book dogfooding, without running dogfood, publishing a release, expanding write scope, or weakening safety language.

Artifacts:

- `docs/audits/phase-61-audit.md` — independent Phase 61 dogfood-results audit artifact with verdict `Blocked: no completed copied-book dogfood results are available to audit`.
- `README.md` — current status advanced through Phase 61 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 61 dogfood-results audit result.
- `docs/handoff/phase-61.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 61 did not enable writes, expand write scope, publish a v0.1 tag/release, run dogfood against a real book, or add real financial/secrets artifacts.

Dogfood-results result: no actual copied-book dogfood results are recorded yet, so crashes, missing account types, wrong balances, split-transaction behavior, multi-currency surprises, slow pages, CSV export issues, auth/session problems, and misleading UI copy cannot be audited. GitHub #25 remains open as the meaningful tracker for copied/disposable-data runtime evidence; no duplicate issue was created.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 61 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 61 blocked dogfood-results audit result and remains open. GitHub #24 also remains open for conservative v0.1 release notes.

## Phase 62 — Deployment Safety Audit

Status: complete. Phase commit pushed.

Goal: audit whether local/self-hosted deployment docs are safe for the current pre-alpha/read-only posture without publishing a release, expanding write scope, or implying public-internet readiness.

Artifacts:

- `docs/audits/phase-62-audit.md` — independent Phase 62 deployment-safety audit artifact with verdict `No deployment-safety blocker found for local/private read-only testing`.
- `README.md` — current status advanced through Phase 62 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 62 deployment-safety audit result.
- `docs/handoff/phase-62.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 62 did not enable writes, expand write scope, publish a v0.1 tag/release, claim public-internet safety, or add real financial/secrets artifacts.

Deployment-safety result: docs are conservative for localhost, LAN, and VPN-only read-only testing. They warn against direct public-internet exposure, require a strong JWT secret, recommend HTTPS/VPN/LAN posture, document Docker volume/data paths, document backup locations, and distinguish the app metadata DB from copied GnuCash books. A non-blocking CORS visibility follow-up was created as GitHub #26.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 62 handoff.

Related issues: GitHub #26 created for CORS origin narrowing visibility. GitHub #24 and #25 remain release blockers for conservative v0.1 release notes and copied/disposable-data runtime smoke/dogfood evidence.

## Phase 63 — Backup/Recovery Audit

Status: complete. Phase commit pushed.

Goal: audit backup and recovery documentation from the auditor roadmap without publishing a release, expanding write scope, or implying production disaster-recovery guarantees.

Artifacts:

- `docs/audits/phase-63-audit.md` — independent Phase 63 backup/recovery audit artifact with verdict `Backup/recovery documentation is acceptable for cautious local/private read-only testing after the accepted grep-command docs fix`.
- `docs/operations/backup-and-recovery.md` — corrected the Compose V2 write-disabled verification example.
- `docs/deployment/local-secure-deployment.md` — corrected the matching write-disabled verification example used by deployment docs.
- `README.md` — current status advanced through Phase 63 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 63 backup/recovery audit result.
- `docs/handoff/phase-63.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 63 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production-grade disaster recovery, or add real financial/secrets artifacts.

Backup/recovery result: the runbook documents backing up copied GnuCash books, backing up `data/app/app.db`, preserving experimental controlled-write backups, dry-run restore, manual recovery, read-only smoke verification, and explicit limitations. No new GitHub issue was created because the only Phase 63 finding was fixed directly as a small docs correction; #24 and #25 remain the release blockers.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 63 handoff.

Related issues: no new issue created. GitHub #24 and #25 remain release blockers; GitHub #26 remains a non-blocking deployment-hardening visibility item.

## Phase 22 — Real Controlled Write Integration Tests

Status: complete. Phase commit pushed.

Goal: add integration tests that exercise the controlled write path against a real disposable GnuCash SQLite fixture using piecash, validating the full write flow end-to-end.

Artifacts:

- `apps/api/tests/test_write_integration.py` — 30 integration tests across 8 test classes covering create, patch, backup, audit, lock lifecycle, lock contention, rejection scenarios, read-back verification, and original fixture immutability against real piecash books.

Test results: 248 passed (218 existing + 30 new), 0 failed. Frontend: check 0 errors, build success, auth-routes passed. Docker config valid.

Deviations: ROOT account has `placeholder=0` (not 1 as spec assumed) but is rejected because it's not in `book.accounts` (it's `book.root_account`), achieving the same test goal. 30 tests implemented vs 15 minimum.

Production code changes: none. Zero production code changes required; write service works correctly against real piecash books.

Related issues: GitHub #8 (closed).

## Phase 64 — Compatibility Audit

Status: complete. Phase commit pushed.

Goal: audit GnuCash compatibility claims from the auditor roadmap without publishing a release, expanding write scope, or claiming broad all-book/all-version support.

Artifacts:

- `docs/audits/phase-64-audit.md` — independent Phase 64 compatibility-claims audit artifact with verdict `No compatibility-claims blocker found for the current pre-alpha/read-only posture`.
- `README.md` — current status advanced through Phase 64 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 64 compatibility audit result.
- `docs/handoff/phase-64.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 64 did not enable writes, expand write scope, publish a v0.1 tag/release, claim XML/PostgreSQL/MySQL/MariaDB/all-version compatibility, or add real financial/secrets artifacts.

Compatibility result: README, release planning docs, and compatibility docs avoid broad compatibility claims. Tested coverage remains limited to documented synthetic GnuCash SQL SQLite fixture paths. GitHub #22 remains open for real GnuCash Desktop version fixture coverage. v0.1 publication remains blocked by #24/#25.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 64 handoff.

Related issues: no new issue created; GitHub #22 was updated with the Phase 64 audit result and remains open. GitHub #24 and #25 remain release blockers; GitHub #26 remains a non-blocking deployment-hardening visibility item.

## Phase 65 — Test Coverage Audit

Status: complete. Phase commit pushed.

Goal: audit whether the current tests support the repository's maturity claims from the auditor roadmap without adding product features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-65-audit.md` — independent Phase 65 test-coverage audit artifact with a claim-to-test-coverage matrix and verdict: automated coverage supports the current pre-alpha/read-only posture, but does not unblock `v0.1.0-readonly` publication.
- `README.md` — current status advanced through Phase 65 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 65 test-coverage audit result.
- `docs/handoff/phase-65.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 65 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit/broad compatibility, or add real financial/secrets artifacts.

Coverage result: backend tests, frontend check/auth-route/build coverage, Docker Compose validation, and CI workflow coverage support the current conservative pre-alpha/read-only claims. The audit found no new test-coverage blocker, but kept #24/#25 as release blockers because automated tests do not replace conservative v0.1 release notes or copied/disposable-data runtime smoke/dogfood evidence.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 65 handoff.

Related issues: no new issue created; GitHub #25 was updated with the Phase 65 audit result and remains open. GitHub #24 and #25 remain release blockers; GitHub #22 and #26 remain open for compatibility/deployment-hardening follow-up.

## Phase 66 — Security Posture Audit

Status: complete. Phase commit pushed.

Goal: audit the current security posture from the auditor roadmap without pretending to perform a professional security audit, adding product features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-66-audit.md` — independent Phase 66 security-posture audit artifact with verdict: ready to continue pre-alpha security hardening, not security-audited, and not ready to claim audited security.
- `README.md` — current status advanced through Phase 66 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 66 security-posture audit result.
- `docs/handoff/phase-66.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 66 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real financial/secrets artifacts.

Security-posture result: auth tokens remain stored in httpOnly cookies rather than browser auth storage; placeholder JWT secrets are rejected; dependency files exist for future security scanning; CORS wildcard development defaults remain documented and tracked in #26; and #27 was created for the meaningful hardening finding that default-book seeding logs full configured GnuCash book paths/URIs.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 66 handoff.

Related issues: GitHub #27 created for seed-log path redaction; GitHub #26 updated and kept open for CORS origin narrowing visibility. GitHub #24 and #25 remain v0.1 release blockers; GitHub #22 remains open for compatibility follow-up.

## Phase 67 — Open-Source Hygiene Audit

Status: complete. Phase commit pushed.

Goal: audit public project health from the auditor roadmap without adding product features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-67-audit.md` — independent Phase 67 open-source hygiene audit artifact with verdict: good OSS hygiene, with minor cleanup completed.
- `README.md` — current status advanced through Phase 67 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 67 OSS hygiene audit result.
- `docs/handoff/phase-67.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 67 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real financial/secrets artifacts.

Open-source hygiene result: license, README, contributing guide, code of conduct, security policy, funding placeholder, issue/PR templates, GitHub topics, documented social-preview setup, and meaningful open issues are present. The missing `needs-triage` label referenced by issue templates was created. The GitHub repository description was updated to include read-only positioning: `Modern self-hosted read-only web companion for GnuCash books.`

Test results: `git diff --check` and GitHub hygiene verification are recorded in the Phase 67 handoff. No v0.1 readiness verdict was made and no product code changed, so the full backend/frontend/Docker suite was not rerun for this audit-only phase.

Related issues: no new issue created; label/repository-description hygiene was fixed directly. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26 and #22 remain open for deployment/compatibility follow-up.

## Phase 68 — Documentation Formatting Audit

Status: complete. Phase commit pushed.

Goal: audit human readability of markdown source from the auditor roadmap without adding product features, expanding write scope, or publishing a release.

Artifacts:

- `docs/audits/phase-68-audit.md` — independent Phase 68 documentation-formatting audit artifact with verdict: documentation formatting is acceptable with non-blocking cleanup needed before wider announcement.
- `README.md` — current status advanced through Phase 68 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 68 documentation-formatting audit result.
- `docs/handoff/phase-68.md` — PM/auditor/engineer handoff and verification report.
- `docs/DEVELOPMENT.md`, `docs/handoff/phase-17.md`, `docs/handoff/phase-18.md`, and `docs/handoff/phase-22.md` — small historical markdown readability/link clarifications accepted by PM.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 68 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real financial/secrets artifacts.

Documentation-formatting result: markdown source readability is acceptable for current pre-alpha docs, but many historical docs have very long raw-source lines. The phase fixed five unlabeled historical code fences and clarified one handoff-relative image path example. GitHub #28 now tracks broader gradual markdown source readability cleanup before wider announcement.

Test results: custom markdown static scan and `git diff --check` are recorded in the Phase 68 handoff. Full backend/frontend/Docker suite was not rerun because this phase is audit/docs-only, changed no product code, and made no v0.1 release-readiness verdict.

Related issues: GitHub #28 created for gradual markdown source readability cleanup. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26 and #22 remain open for deployment/compatibility follow-up.

## Phase 69 — Localization/i18n Audit

Status: complete. Phase commit pushed.

Goal: audit Russian localization planning and implementation from the auditor roadmap without adding product features, expanding write scope, making Russian the default locale, or publishing a release.

Artifacts:

- `docs/audits/phase-69-audit.md` — independent Phase 69 localization/i18n audit artifact with verdict: localization/i18n posture is acceptable for the current pre-alpha read-only scope, with non-blocking glossary follow-up required before localization grows.
- `README.md` — current status advanced through Phase 69 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 69 localization/i18n audit result.
- `docs/handoff/phase-69.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 69 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, make Russian the default locale, or add real financial/secrets artifacts.

Localization result: English remains canonical; `README.ru.md` is intentionally a short starter reference and does not contradict English safety/read-only positioning; Russian UI strings are opt-in and preserve the read-only/default-write/GnuCash Desktop authority boundary; complete translation remains non-blocking for v0.1 unless PM changes release criteria. GitHub #29 now tracks the non-blocking glossary gap for accounting/safety terminology.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 69 handoff.

Related issues: GitHub #29 created for a localization glossary. GitHub #17 remains open for broader Russian documentation/UI localization planning. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, and #28 remain open for deployment/compatibility/markdown follow-up.

## Phase 70 — Community Announcement Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to be shared with interested communities from the auditor roadmap without publishing a release, expanding write scope, or using production-style marketing.

Artifacts:

- `docs/audits/phase-70-audit.md` — independent Phase 70 community-announcement audit artifact with verdict: ready only in limited circles.
- `README.md` — current status advanced through Phase 70 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 70 community-announcement audit result.
- `docs/handoff/phase-70.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 70 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, or add real financial/secrets artifacts.

Community-announcement result: README explains who the project is and is not for; README screenshots are labeled as synthetic fixture data; `docs/community/announcement-draft.md` exists and uses feedback-wanted conservative copy; `docs/community/where-to-share.md` limits ready-now sharing to narrow technical/GnuCash circles; README related-project comparison is fair and does not overclaim. Broad launch-style promotion remains inappropriate while #24/#25 are open.

Test results: documentation/static announcement-readiness checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 70 handoff.

Related issues: no new issue created; existing #24, #25, #28, and #29 cover meaningful release/community follow-ups without adding noisy backlog theater. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, #28, and #29 remain open for deployment/compatibility/markdown/localization follow-up.

## Phase 71 — Performance Risk Audit

Status: complete. Phase commit pushed.

Goal: audit whether obvious read-only performance risks are tracked before any broader v0.1/large-book confidence claims.

Artifacts:

- `docs/audits/phase-71-audit.md` — independent Phase 71 performance-risk audit artifact with verdict: needs performance-risk tracking before broader confidence claims.
- `README.md` — current status advanced through Phase 71 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 71 performance-risk audit result.
- `docs/handoff/phase-71.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 71 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, claim known large-book scalability, or add real financial/secrets artifacts.

Performance-risk result: transaction list routes have pagination caps and CSV export has a documented 10,000-row cap, but the read-only service layer can still scan/sort matched transactions and dashboard aggregates iterate accounts/transactions/splits. No large-book benchmark evidence exists yet, so large-book scalability must not be claimed.

Test results: static performance-risk audit checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 71 handoff.

Related issues: GitHub #30, #31, #32, and #33 were created for large-book benchmark, many-splits benchmark, CSV timeout/truncation behavior, and dashboard aggregate performance tracking. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, #28, and #29 remain open for deployment/compatibility/markdown/localization follow-up.

## Phase 72 — Data Model and Money Correctness Audit

Status: complete. Phase commit pushed.

Goal: audit money handling from the auditor roadmap without adding product features, expanding write scope, publishing a release, or claiming v0.1 readiness.

Artifacts:

- `docs/audits/phase-72-audit.md` — independent Phase 72 data model and money-correctness audit artifact with verdict: no new blocker for the current pre-alpha/read-only posture.
- `docs/money-model.md` — canonical money representation, CSV export, sign-convention, split-amount, and multi-currency behavior notes.
- `README.md` — current status advanced through Phase 72 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 72 audit/docs result.
- `docs/handoff/phase-72.md` — PM/auditor/engineer handoff and verification report.
- `docs/ARCHITECTURE.md` — linked to the canonical money model.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 72 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, add fake currency conversion, or add real financial/secrets artifacts.

Money-correctness result: backend core read-only money paths use Decimal/string DTOs, reject floats in service-layer money conversion, serialize JSON money as strings, and write CSV export amounts from string DTOs. Multi-currency report totals remain conservative and exclude non-base-currency values instead of converting them. Canonical docs now clarify sign and split amount conventions.

Test results: static money-correctness audit searches, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 72 handoff.

Related issues: GitHub #34 was created for frontend display-only `Number()` money hygiene. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, #28, #29, and #30–#33 remain open for deployment/compatibility/markdown/localization/performance follow-up.

## Phase 73 — Multi-book Access Model Audit

Status: complete. Phase commit pushed.

Goal: audit the multi-book access model from the auditor roadmap without adding product feature scope, expanding writes, publishing a release, or implying collaborative accounting/family-wallet semantics.

Artifacts:

- `docs/audits/phase-73-audit.md` — independent Phase 73 multi-book access model audit artifact with verdict: no new blocker for the current pre-alpha/read-only posture.
- `docs/book-switcher-readonly-model.md` — clarified archived-book visibility and future archive/visibility-management documentation expectations.
- `README.md` — current status advanced through Phase 73 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 73 audit/docs result.
- `docs/handoff/phase-73.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 73 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, add collaborative accounting/family-wallet framing, or add real financial/secrets artifacts.

Multi-book access result: user-book access remains explicit through `UserBookAccess`; `GET /books` returns only non-archived books visible to the current user; book-aware account, transaction, CSV export, and report routes resolve a viewable book before opening GnuCash data; the frontend switcher shows only accessible books from the authenticated `GET /books` context and keeps independent read-only wording. Archive/visibility route semantics need stronger dedicated regression coverage and are tracked in #35.

Test results: static multi-book access/documentation audit checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 73 handoff.

Related issues: GitHub #35 was created for archived-book/full route-family multi-book access boundary test hardening. GitHub #24 and #25 remain v0.1 release blockers; GitHub #27 remains open for seed-log path redaction; GitHub #26, #22, #28, #29, #30–#34 remain open for deployment/compatibility/markdown/localization/performance/money follow-up.

## Phase 74 — Controlled Writes Boundary Audit

Status: complete. Phase commit pushed.

Goal: re-audit the controlled-writes boundary from the auditor roadmap without enabling writes, expanding write scope, publishing a release, or implying write-mode safety for real books.

Artifacts:

- `docs/audits/phase-74-audit.md` — independent Phase 74 controlled-writes boundary audit artifact with verdict: keep writes experimental.
- `README.md` — current status advanced through Phase 74 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 74 audit result.
- `docs/handoff/phase-74.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 74 did not enable writes, expand write scope, publish a v0.1 tag/release, claim production readiness/security audit, claim safe write mode, or add real financial/secrets artifacts.

Controlled-writes boundary result: backend validate/create/patch routes call the write feature gate before resolving books or constructing `GnuCashWriteService`; frontend write UI is hidden unless explicitly enabled and requires warning/acknowledgement; write integration tests and backup/restore tests use disposable copied fixtures; file-based locking and backup restore smoke coverage are documented. Remaining v0.2 write-readiness gaps are tracked in #36.

Test results: static controlled-writes boundary audit checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 74 handoff.

Related issues: GitHub #36 was created for remaining controlled-write v0.2 readiness gates. GitHub #24 and #25 remain v0.1 release blockers; GitHub #22 remains open for real GnuCash version fixture coverage; GitHub #27 remains open for seed-log path redaction; GitHub #26, #28, #29, #30–#35 remain open for deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 75 — v0.1.1 Maintenance Release Audit

Status: complete. Phase commit pushed.

Goal: audit whether a `v0.1.1-readonly` maintenance release is needed from the auditor roadmap without preparing or publishing any release, expanding write scope, or implying that `v0.1.0-readonly` already exists.

Artifacts:

- `docs/audits/phase-75-audit.md` — independent Phase 75 maintenance-release audit artifact with verdict: no release needed.
- `README.md` — current status advanced through Phase 75 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 75 audit result.
- `docs/handoff/phase-75.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 75 did not enable writes, expand write scope, publish a v0.1/v0.1.1 tag or release, prepare a maintenance release, claim production readiness/security audit, or add real financial/secrets artifacts.

Maintenance-release result: no `v0.1.1-readonly` maintenance release is needed/applicable because `v0.1.0-readonly` has not been published as a git tag or GitHub release. There is no post-v0.1 dogfood bugfix/docs/small read-only UX fix stream to package. Initial v0.1 publication remains blocked by #24/#25.

Test results: git/GitHub release/tag checks, static release/docs/write-boundary audit checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 75 handoff.

Related issues: no new issue was created because #24 and #25 already cover the meaningful initial v0.1 release blockers, and a v0.1.1 placeholder issue would be noisy before v0.1.0 exists. GitHub #36 remains open for controlled-write v0.2 readiness gates; GitHub #22 remains open for real GnuCash version fixture coverage; GitHub #27 remains open for seed-log path redaction; GitHub #26, #28, #29, #30–#35 remain open for deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 76 — v0.2 Planning Audit

Status: complete. Phase commit pushed.

Goal: audit whether the project is ready to create or promote v0.2 controlled-writes planning from the auditor roadmap without enabling writes, expanding write scope, creating a misleading write milestone, publishing a release, or implying write-mode safety for real books.

Artifacts:

- `docs/audits/phase-76-audit.md` — independent Phase 76 v0.2 planning audit artifact with verdict: not ready; keep write mode experimental.
- `README.md` — current status advanced through Phase 76 and latest-audit link updated.
- `CHANGELOG.md` — Unreleased entry added for the release-facing Phase 76 planning-audit result.
- `docs/handoff/phase-76.md` — PM/auditor/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/default state; controlled writes remain experimental post-MVP and disabled by default. Phase 76 did not enable writes, expand write scope, create a v0.2 milestone, publish a release, claim production readiness/security audit, claim safe write mode, or add real financial/secrets artifacts.

Planning result: not ready to create or promote a v0.2 controlled-writes planning milestone. `v0.1.0-readonly` is not published and remains blocked by #24/#25; actual copied-book dogfood evidence is still missing; #36 remains open for remaining write-readiness gates; #22 remains open for real GnuCash version fixture coverage. Existing write-boundary safeguards support only the current experimental/post-MVP posture.

Test results: git/GitHub release/tag checks, static release/docs/write-boundary audit checks, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 76 handoff.

Related issues: no new issue was created because #36 already tracks the meaningful v0.2 write-readiness gates. #36 was updated to record the Phase 76 planning-audit verdict and correct missing `GNUCASH_WRITES_ENABLED=false` wording. GitHub #24 and #25 remain initial v0.1 release blockers; GitHub #22 remains open for real GnuCash version fixture coverage; GitHub #27 remains open for seed-log path redaction; GitHub #26, #28, #29, #30–#35 remain open for deployment/markdown/localization/performance/money/multi-book follow-up.

## Phase 77 — Real Read-only Dogfood on Copied/Disposable GnuCash Book

Status: complete. Phase commit pushed.

Goal: run the application locally against a copied/disposable GnuCash SQL book, record actual usability evidence, verify runtime writes-disabled behavior, identify release blockers, and avoid creating another audit-only phase.

Artifacts:

- `docs/dogfood/phase-77-readonly-dogfood.md` — dogfood environment, copied/disposable book source class, writes-disabled proof, API/browser checks, safe log snippets, issues, and release verdict.
- `docs/audits/phase-77-audit.md` — independent evidence review and release verdict.
- `docs/handoff/phase-77.md` — PM/engineer/auditor handoff and verification report.
- `CHANGELOG.md` — Unreleased entry for the Phase 77 dogfood result.

Safety result: `GNUCASH_WRITES_ENABLED=false` was verified in Docker Compose-resolved runtime config and `/api/health`; validate/create/patch write endpoint probes returned read-only 403 responses. Phase 77 did not enable writes, expand write scope, add features, write to the GnuCash book, touch a real/original book, commit runtime data/secrets, or publish a release.

Dogfood result: Docker API-level dogfood passed against a copied/disposable SQL fixture: login, `/auth/me`, book discovery, accounts, account detail, transactions, transaction detail, reports summary, search/filter, CSV export, and disabled-write probes all worked. Browser/UI dogfood failed because `/login` redirects to itself and the web container is unhealthy.

Release result: not ready for `v0.1.0-readonly`. GitHub #37 is a new release blocker for browser dogfood. GitHub #25 remains open because Phase 77 is API-success/browser-fail evidence, not a full copied/disposable-data browser dogfood pass. GitHub #24 remains open for conservative release notes.

Test results: Docker config validation, Docker API runtime health, API smoke script, manual API dogfood, browser redirect-loop evidence, backend full suite, frontend check/auth-routes/build, Docker Compose config validation, and `git diff --check` are recorded in the Phase 77 handoff.

Related issues: GitHub #37 was created for the `/login` redirect loop. GitHub #25 remains open as the umbrella copied/disposable-data runtime dogfood gate; #24 remains the release-notes blocker; #22, #26–#36 remain open as applicable follow-up.

## Phase 78 — Fix Docker /login Redirect Loop and Rerun Browser Dogfood

Status: complete. Phase commit pushed.

Goal: fix release blocker #37, verify the Docker web UI can load `/login` through Caddy, and rerun browser/UI dogfood on copied/disposable data with writes disabled.

Artifacts:

- `apps/web/src/routes/+layout.server.ts` — root layout now returns public unauthenticated layout data before token/book-context lookup, preventing `/login` self-redirects while preserving protected-route auth behavior.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` — server-side CSV export proxy for the existing UI export link, using the httpOnly auth cookie server-side and streaming the API CSV response.
- `apps/web/scripts/test-auth-routes.mjs` — regression coverage for unauthenticated public layout behavior, protected-route redirect expectations, authenticated book-context loading, and CSV export proxy auth behavior.
- `docs/dogfood/phase-78-browser-dogfood.md` — reproduction evidence, root cause, fix, Docker/browser dogfood, write-disabled runtime probes, and checks.
- `docs/handoff/phase-78.md` — PM/engineer handoff and verification report.
- `CHANGELOG.md` — Unreleased entry for the Phase 78 fix and dogfood result.

Safety result: `GNUCASH_WRITES_ENABLED=false` was verified in Docker Compose-resolved runtime config and `/api/health`; validate/create/patch write endpoint probes returned read-only 403 responses with valid payloads. Browser UI showed the write entry point hidden (`new_button_visible=false`). Phase 78 did not enable writes, expand write scope, start v0.2 work, commit runtime data/secrets/real books, or publish a release.

Dogfood result: Docker/browser dogfood through Caddy passed on the copied/disposable fixture. `/login` returned 200; unauthenticated `/dashboard` redirected to `/login?next=%2Fdashboard`; Chromium login reached dashboard; dashboard, accounts, account detail, transactions, transaction detail, and CSV export route loaded; API smoke passed.

Release result: #37 fixed. #25 remains open pending PM/release-gate acceptance of Phase 78 browser dogfood evidence and any remaining copied-real-book limitation. #24 remains open because release notes were not completed in this phase. `v0.1.0-readonly` was not published.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, Docker browser dogfood through Caddy, API smoke, write-disabled probes, and `git diff --check` are recorded in the Phase 78 handoff.

Related issues: GitHub #37 was closed/updated as fixed by Phase 78. GitHub #25 remains the copied/disposable-data runtime dogfood gate. GitHub #24 remains the release-notes blocker; #22, #26–#36 remain open as applicable follow-up.

## Phase 79 — Accept Dogfood Evidence and Final v0.1.0-readonly Release Gate

Status: complete. Phase commit pushed.

Goal: accept Phase 78 copied/disposable-data dogfood evidence, create conservative `v0.1.0-readonly` release notes, run the final release gate, update release/status artifacts, and close satisfied release-blocker issues without publishing a tag or GitHub release.

Artifacts:

- `docs/release/v0.1.0-readonly-notes.md` — conservative release notes: pre-alpha, read-only by default, not production-ready, not security-audited, test copied/disposable books first, no SaaS/GnuCash replacement/collaborative-editing claim, no broad compatibility guarantee, writes disabled by default.
- `docs/release/v0.1.0-readonly-checklist.md` — final checklist status and Phase 79 evidence.
- `docs/release/v0.1.0-readonly-final-gate.md` — final gate verdict: ready for publication as a separate explicit next step.
- `docs/handoff/phase-79.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — release/status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default; controlled writes remain experimental/post-MVP and disabled by default. Phase 79 did not enable writes, add features, start v0.2 work, publish a tag/release, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Release result: Phase 78 dogfood evidence was accepted for #25 because it used copied/disposable data and passed Docker/Caddy browser dogfood, API smoke, CSV export, hidden write UI, and disabled write probes. `v0.1.0-readonly` is ready for a separate explicit publication step. No v0.1 tag or GitHub release exists yet.

Test results: backend full suite, frontend check/auth-routes/build, Docker Compose config validation, `git diff --check`, GitHub Actions CI, v0.1 tag lookup, and GitHub release lookup are recorded in the Phase 79 handoff/final gate.

Related issues: GitHub #24 was closed as satisfied by release notes. GitHub #25 was closed as satisfied by accepted Phase 78 copied/disposable-data runtime dogfood. GitHub #37 remains closed/fixed. GitHub #22 and #26–#36 remain open as non-blocking follow-up for broader hardening/future releases.

## Phase 80 — Publish v0.1.0-readonly Pre-release

Status: complete. Annotated tag and GitHub pre-release published; status docs committed and pushed.

Goal: perform the narrow publish-only `v0.1.0-readonly` phase after the Phase 79 release gate verdict was ready for publication.

PM decision: publish exactly the existing release artifact on the Phase 79 gate commit. Do not expand scope, add writes, start v0.2 work, create an audit-only phase, or change the conservative release language.

Publication evidence:

- Annotated git tag: `v0.1.0-readonly`.
- Tagged commit: `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` (`docs: record phase 79 ci result`).
- Remote tag: `refs/tags/v0.1.0-readonly` pushed to `origin`.
- GitHub pre-release: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly
- Release notes source: `docs/release/v0.1.0-readonly-notes.md`.
- Published at: `2026-05-18T06:04:26Z`.

Artifacts updated after publication:

- `README.md` — current release/status links now point to `v0.1.0-readonly`.
- `CHANGELOG.md` — Unreleased Phase 80 publication evidence entry.
- `PROJECT_STATUS.md` — baseline advanced through Phase 80 and next work guidance updated.
- `docs/handoff/phase-80.md` — PM/engineer handoff and verification report.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default; controlled writes remain experimental/post-MVP and disabled by default. Phase 80 did not enable writes, add application behavior beyond publishing the existing release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Test and release verification results are recorded in `docs/handoff/phase-80.md`. Local required checks passed before publication, Phase 79 main-branch CI was green before tagging, the v0.1 tag/release absence was verified before publication, and the tag/release presence was verified after publication.

Related issues: no issues were closed in Phase 80. Open follow-up issues #22 and #26–#36 remain non-blocking for this conservative pre-alpha read-only publication.

## Phase 81 — Default-book Seed Log Redaction

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open release-hardening backlog by fixing GitHub #27 without starting audit-only work, write-mode work, a new tag/release, or v0.2 planning.

PM decision: choose #27 because it is low-risk, concrete, testable, post-release security/logging hardening. The expected result is a tested behavior change: default-book seed logs must not expose full filesystem paths, connection URIs, hosts, usernames, passwords/tokens, or query parameters.

Artifacts:

- `apps/api/app/services/seed.py` — added `_safe_book_log_label()` and changed default-book seed logging/name derivation to use sanitized filename/label for log-visible data while preserving the configured path/URI in `Book.uri_or_path`.
- `apps/api/tests/test_seed.py` — added regression tests for redacting full filesystem paths and connection URI details from seed logs.
- `docs/handoff/phase-81.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 81 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: backend tests, frontend check/auth-routes/build, Docker Compose config validation, `git diff --check`, release state verification, pushed commit verification, and clean working tree verification are recorded in `docs/handoff/phase-81.md`.

Related issues: GitHub #27 closed as completed with evidence. Open follow-up issues #22, #26, #28–#36 remain non-blocking backlog for later narrow phases.

## Phase 82 — Read-only Multi-book Boundary Regression Coverage

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open read-only/release-hardening backlog by satisfying GitHub #35 with backend regression coverage, without starting audit-only work, write-mode work, a new tag/release, or v0.2 planning.

PM decision: choose #35 because it is low-risk, concrete, testable, and protects the read-only multi-book boundary after the v0.1.0-readonly publication. The expected result is a tested safety/behavior guard: archived books must be hidden/blocked, and unauthorized users must be denied across book-aware read-only route families before any GnuCash data is exposed.

Artifacts:

- `apps/api/tests/test_multi_book_access.py` — added an archived-book fixture with explicit user access, regression coverage that `GET /books` excludes archived books, `GET /books/{book_id}` returns `404` for archived books, and parametrized coverage for unauthorized `403` / archived `404` behavior across accounts, transactions, CSV export, account transactions, and all book-aware report route families.
- `docs/handoff/phase-82.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 82 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: targeted multi-book tests, backend tests, frontend check/auth-routes/build, Docker Compose config validation, `git diff --check`, release state verification, pushed commit verification, and clean working tree verification are recorded in `docs/handoff/phase-82.md`.

Related issues: GitHub #35 closed as completed with evidence. Open follow-up issues #22, #26, #28–#34, and #36 remain non-blocking backlog for later narrow phases.

## Phase 83 — Frontend Decimal-string Money Display Hardening

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open read-only/release-hardening backlog by satisfying GitHub #34 with frontend decimal-string money display helpers, without starting audit-only work, write-mode work, a new tag/release, or v0.2 planning.

PM decision: choose #34 because it is low-risk, concrete, testable, and aligns the frontend read-only UI with the project money rule. The expected result is a tested user-facing/display hardening change: frontend amount/balance/total/net decisions should not convert money strings through JS `Number()`.

Artifacts:

- `apps/web/src/lib/money.js` — added decimal-string parse/compare/sign/percentage helpers using `BigInt` rather than JS `Number()` for money strings.
- `apps/web/scripts/test-money-strings.mjs` and `apps/web/package.json` — added lightweight helper coverage via `npm run test:money-strings`.
- `apps/web/src/lib/components/SummaryGrid.svelte`, `RecentTransactions.svelte`, `CashflowSummary.svelte`, `ExpensesByAccount.svelte`, and `TransactionFilters.svelte` — replaced money-string `Number()` decisions with decimal-string helpers for sign colors/trends, expense bar widths, and client-side amount-range prevalidation.
- `docs/handoff/phase-83.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 83 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: helper tests, frontend check/auth-routes/build, backend tests, Docker Compose config validation, `git diff --check`, release state verification, pushed commit verification, and clean working tree verification are recorded in `docs/handoff/phase-83.md`.

Related issues: GitHub #34 closed as completed with evidence. Open follow-up issues #22, #26, #28–#33, and #36 remain non-blocking backlog for later narrow phases.

## Phase 84 — CSV Export Truncation and Timeout Behavior

Status: complete. Phase commit pushed.

Goal: complete one narrow post-release concrete hardening task from the open read-only/release-hardening backlog by satisfying GitHub #32 with tested CSV export cap/truncation/timeout behavior, without starting audit-only work, write-mode work, a new tag/release, or v0.2 planning.

PM decision: choose #32 because it is low-risk, concrete, testable, and improves a user/operator-facing read-only export boundary after the v0.1.0-readonly publication. The expected result is a tested maintenance/UX behavior: CSV export remains capped at 10,000 rows, reports whether the filtered set was truncated, documents/labels synchronous timeout behavior, and tells users to narrow filters if a large export times out.

Artifacts:

- `apps/api/app/routers/transactions.py` — successful CSV exports now include `X-CSV-Export-Limit`, `X-CSV-Export-Total`, `X-CSV-Export-Truncated`, and `X-CSV-Export-Timeout-Policy` response headers.
- `apps/api/tests/test_transaction_export.py` — added disposable fake-data regression coverage for truncated and non-truncated CSV export responses.
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` — forwards the CSV export metadata headers through the SvelteKit/browser download proxy.
- `apps/web/scripts/test-auth-routes.mjs` — verifies the proxy keeps forwarding the export metadata headers.
- `apps/web/src/routes/transactions/+page.svelte` — user-facing CSV export status now says large exports are synchronous and should be narrowed if they time out.
- `docs/transactions-filters.md` — documents the 10,000-row cap, truncation headers, and synchronous request-timeout policy.
- `docs/handoff/phase-84.md` — PM/engineer handoff and verification report.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 84 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: targeted CSV export tests, frontend auth-route/proxy checks, frontend check/build, backend tests, Docker Compose config validation, `git diff --check`, release state verification, pushed commit verification, and clean working tree verification are recorded in `docs/handoff/phase-84.md`.

Related issues: GitHub #32 closed as completed with evidence. Open follow-up issues #22, #26, #28–#31, #33, and #36 remain non-blocking backlog for later narrow phases.

## Phase 85 — Post-v0.1 Personal Copied-Book Dogfood

Status: complete with blocker recorded. Phase commit pushed.

Goal: attempt exactly the roadmap Phase 85 dogfood pass against a copied personal GnuCash SQL book outside git, using the published/read-only app posture, without analyst/auditor involvement, write enablement, private-data commits, a new release/tag, or v0.2 work.

PM decision: run only the safe copied personal-book dogfood scenario. The original book must remain untouched, writes must stay disabled, access must be local-only, and no screenshots/exports/private financial data may be committed. If no safe copied personal SQL book is available, record that as a blocker rather than pretending a real-book pass succeeded.

Artifacts:

- `docs/dogfood/phase-85-personal-copied-book-results.md` — redacted dogfood result artifact. It records that no safe copied personal SQL book was available to this environment outside git, so the real-book Docker/browser/API checklist is blocked rather than passed.
- `docs/handoff/phase-85.md` — PM/engineer handoff, safety scope, blocked runtime checklist, verification, issue, commit, and push evidence.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — post-release status sync.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 85 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts. No private account names, private amounts, private paths, screenshots, CSV exports, `.env`, app DB, backup, real GnuCash book, token, cert, or key were committed.

Verification result: required backend tests, frontend check/auth-routes/build, Docker Compose config validation, `git diff --check`, release state verification, pushed commit verification, and clean working tree verification are recorded in `docs/handoff/phase-85.md`. Docker/browser/API smoke against the copied personal book is explicitly blocked because no safe copied personal SQL book is available in this environment.

Related issues: GitHub #38 opened to track rerunning the copied personal-book dogfood checklist when a safe copied personal SQL book is available. No existing issue was closed without runtime evidence.

## Phase 86 — Fix Phase 85 Dogfood Blockers

Status: complete. Phase commit pushed.

Goal: triage Phase 85 findings and fix only the highest-priority concrete dogfood blocker, without analyst/auditor involvement, new features, write-mode work, broad refactor, v0.2 work, or a new release/tag.

PM decision: Phase 85 produced no reproducible application bug such as a dashboard crash, transaction-detail failure, filter crash, CSV export failure, wrong empty state, or account display bug. The only finding was a release-blocking dogfood input/environment blocker: no safe copied personal GnuCash SQL book was available outside git. Because there was no code bug to fix, Phase 86 used the allowed maintenance fallback and added a narrow tested preflight helper for #38 so future copied-book dogfood attempts can classify candidate availability safely before runtime work begins.

Artifacts:

- `apps/api/app/dogfood_preflight.py` — redacted helper that classifies a copied-book candidate as blocked/ready without opening the book or exposing full paths.
- `apps/api/scripts/check_dogfood_book_candidate.py` — operator CLI wrapper that prints only filename-level safe summaries and exits non-zero when the candidate is blocked.
- `apps/api/tests/test_dogfood_preflight.py` — regression tests for missing candidate, candidate inside git, and valid outside-repo candidate, including private-path redaction assertions.
- `docs/handoff/phase-86.md` — PM/engineer handoff with triage, safety, verification, issue, commit, and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — post-release status sync.

Safety result: writes remain disabled by default. The helper does not parse, copy, export, screenshot, or commit any GnuCash book data; it only checks path existence and whether the candidate is outside the git working tree. No real financial data, `.env`, app DB, backup, secret, token, private key, private screenshot, CSV export, or real GnuCash book was committed. No v0.2 work or release publication was done.

Verification result: the new regression test and required backend/frontend/docker/git checks are recorded in `docs/handoff/phase-86.md`. Docker/browser/API personal-book dogfood remains blocked until #38 has a safe copied book; Phase 86 does not claim a real-book pass.

Related issues: GitHub #38 updated with Phase 86 triage and preflight-helper evidence, but kept open because the real copied personal-book dogfood rerun still requires a safe copied book.

## Phase 87 — Large-book Read-only Benchmark v1

Status: complete. Phase commit pushed.

Goal: add a generated synthetic large-book benchmark for read-only API paths without using private books, enabling writes, publishing a release, or starting v0.2 work.

Artifacts:

- `apps/api/app/performance/large_book_benchmark.py` — synthetic benchmark fixture and authenticated read-only API measurement helper.
- `apps/api/scripts/run_large_book_benchmark.py` — local benchmark CLI.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for benchmark plan/scope.
- `docs/performance/phase-87-large-book-benchmark.md` — benchmark evidence and limitations.
- `docs/handoff/phase-87.md` — PM/engineer handoff.

Safety result: generated synthetic data only, no committed generated binary fixture, no write-mode work, no v0.2 work, no tag/release.

Related issues: GitHub #30 closed as completed. GitHub #39 opened for CSV export row-count/header mismatch.

## Phase 88 — Account with Many Splits Performance Test

Status: complete. Phase commit pushed.

Goal: extend the synthetic read-only benchmark to include many-splits transaction detail and account transaction pagination evidence.

Artifacts:

- `apps/api/app/performance/large_book_benchmark.py` — now creates one 60-split transaction and measures account-detail pagination plus many-splits transaction detail.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for many-splits scope.
- `docs/performance/phase-88-many-splits-benchmark.md` — benchmark evidence and limitations.
- `docs/handoff/phase-88.md` — PM/engineer handoff.

Safety result: generated synthetic data only, no committed generated binary fixture, no write-mode work, no v0.2 work, no tag/release.

Related issues: GitHub #31 closed as completed. GitHub #39 remains open for CSV export row-count/header mismatch.

## Phase 89 — Dashboard Aggregate Performance and Correctness Pass

Status: complete. Phase commit pushed.

Goal: make dashboard aggregates less likely to be slow or misleading on larger books by hardening conservative reporting claims and expanding synthetic benchmark coverage.

PM decision: implement exactly the roadmap Phase 89 dashboard aggregate pass. Dashboard claims must remain conservative: no fake currency conversion, base-currency-only reporting, visible limitations/empty/error behavior, and measured read-only aggregate endpoints rather than broad performance claims.

Artifacts:

- `apps/api/app/routers/reports.py` — centralized dashboard report date parsing/range validation and clear `422` client errors.
- `apps/api/app/services/gnucash_book.py` — summary DTO now includes `reporting_basis="base_currency_only"`, `includes_currency_conversion=false`, and explicit no-conversion/mixed-currency limitation text.
- `apps/api/app/schemas/gnucash.py` — summary schema includes the conservative reporting metadata.
- `apps/api/tests/test_reports.py` — regression coverage for empty summary, mixed-currency exclusion, date error quality, cashflow, expenses, recent transactions, and book-aware report endpoints.
- `apps/api/app/performance/large_book_benchmark.py` — benchmark now covers dashboard summary, cashflow-by-month, expenses-by-account, and recent-transactions.
- `apps/api/tests/test_large_book_benchmark.py` — regression coverage for the expanded dashboard benchmark plan.
- `apps/web/src/lib/api/types.ts` — frontend summary type includes conservative reporting metadata.
- `apps/web/src/routes/dashboard/+page.svelte` — dashboard renders the summary limitation visibly above summary cards.
- `docs/performance/phase-89-dashboard-aggregate-benchmark.md` — benchmark command, local results, findings, and limitations.
- `docs/handoff/phase-89.md` — PM/engineer handoff.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — status sync.

Benchmark result: the 1,000-transaction synthetic TestClient benchmark returned `200` for dashboard summary, cashflow-by-month, expenses-by-account, and recent-transactions. Summary and expenses-by-account were below one second locally; cashflow-by-month and recent-transactions were also below one second locally but remain service-layer scans and are not a production scalability guarantee.

Safety result: generated synthetic data only. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 89 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim collaborative editing/SaaS/GnuCash replacement status, or add real financial/secrets/runtime artifacts.

Verification result: targeted report/benchmark tests and required backend/frontend/docker/git checks are recorded in `docs/handoff/phase-89.md`.

Related issues: GitHub #33 closed as completed with Phase 89 evidence. GitHub #39 remains open for the existing CSV export row-count/header mismatch.

## Phase 94 — Post-v0.1 Maintenance Release Decision

Status: complete. Phase commit pushed.

Goal: decide whether enough post-`v0.1.0-readonly` changes exist to prepare `v0.1.1-readonly`, without analyst/auditor involvement, audit-only artifacts, tag/release publication, write-mode enablement, v0.2 work, or private data artifacts.

PM decision: more fixes are required before maintenance release. Do not prepare or publish `v0.1.1-readonly` yet.

Artifacts:

- `docs/release/v0.1.1-readonly-decision.md` — durable maintenance-release decision artifact reviewing Phases 81–93, release/tag state, open blockers, and minimum requirements before a future release-prep phase.
- `docs/handoff/phase-94.md` — PM/engineer handoff with decision, safety scope, verification, GitHub state, commit, and push evidence.
- `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` — status sync through Phase 94.

Release decision result: the post-release change set is meaningful, including seed-log redaction, multi-book boundary hardening, money-display hardening, CSV export header/truncation signaling, benchmark evidence, transaction-filter UX, read-only book metadata UI, compatibility metadata collection, and a narrow Russian localization slice. However, GitHub #39 remains an open read-only CSV export correctness blocker because benchmark evidence repeatedly showed the CSV body capped at 500 rows while export headers report a 10,000-row cap and `truncated=false`. Fix #39 with regression coverage before creating `v0.1.1-readonly` notes/checklist.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 94 did not enable writes, add write scope, publish a new tag/release, start v0.2 work, claim production readiness/security audit, claim broad compatibility, or add real financial/secrets/runtime artifacts.

Verification result: required backend/frontend/docker/git checks plus release/tag/open-issue verification are recorded in `docs/handoff/phase-94.md`.

Related issues: GitHub #39 updated with Phase 94 release-decision evidence and kept open as the maintenance-release prep blocker. GitHub #38 remains open for the separate copied personal-book dogfood rerun when a safe copied SQL book is available.

## Phase 97 — v0.1.1-readonly Release-Prep Checklist and Notes

Status: complete. Phase commit pushed.

Goal: prepare conservative `v0.1.1-readonly` release notes and a release-prep checklist after the Phase 95 GitHub #39 CSV export fix and Phase 96 synthetic benchmark confirmation, without publishing a tag/release.

PM decision: release-prep only. Do not publish `v0.1.1-readonly`, do not run the final release gate in this phase, do not claim production readiness/security audit/broad compatibility/personal-book dogfood success, and keep #38 separate unless a safe copied personal SQL book becomes available outside git.

Artifacts:

- `docs/release/v0.1.1-readonly-notes.md` — conservative draft release notes for a future GitHub pre-release.
- `docs/release/v0.1.1-readonly-checklist.md` — release-prep checklist separating completed Phase 95/96 evidence, required Phase 98 gate checks, intentionally unauthorized publication steps, known limitations, and open issues.
- `docs/handoff/phase-97.md` — PM/engineer handoff with implementation summary, safety statement, verification, release/GitHub state, commit, and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status sync through Phase 97.

Release-prep result: the candidate notes/checklist summarize post-`v0.1.0-readonly` maintenance value, especially the Phase 95 CSV export fix and Phase 96 synthetic benchmark confirmation, while explicitly stating that `v0.1.1-readonly` is not published yet and still requires Phase 98 release-gate verification before any authorized publication.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 97 did not enable writes, add write scope, publish a tag/release, start v0.2 work, claim production readiness/security audit/broad compatibility/personal-book dogfood success, or add real financial/secrets/runtime artifacts.

Verification result: `git diff --check` passed. Backend/frontend/Docker checks were not run because Phase 97 changed only docs/release/status/handoff artifacts and did not touch backend, frontend, or config code; those checks are required for Phase 98 release-gate verification.

Related issues: GitHub #39 remains closed based on Phase 95/96 synthetic evidence. GitHub #38 remains open/blocked pending a safe copied personal GnuCash SQL book outside git.

## Phase 98 — v0.1.1-readonly Release-Gate Verification

Status: complete. Phase commit pushed.

Goal: run the final `v0.1.1-readonly` release-gate verification before any publication and record an honest ready/blocked verdict artifact.

PM decision: release-gate only. Do not publish `v0.1.1-readonly`, do not create a tag/release, do not enable writes, do not broaden release claims, and keep #38 separate unless a safe copied personal SQL book becomes available outside git.

Artifacts:

- `docs/release/v0.1.1-readonly-final-gate.md` — final release-gate artifact with branch/HEAD evidence, command summary, GitHub Actions/release-state evidence, read-only/write-disabled confirmation, sensitive-data hygiene summary, and verdict.
- `docs/handoff/phase-98.md` — PM/engineer handoff with implementation summary, safety statement, verification, release/GitHub state, commit, and push evidence.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — status sync through Phase 98.

Release-gate result: the verdict is `Ready for later authorized publish phase`. Backend, frontend, Docker config, GitHub Actions recent `main` runs, tag/release absence, issue-state, disabled-write/read-only safety, and hygiene checks passed. `v0.1.1-readonly` is still not published; publication requires a later explicit Phase 99/publish authorization.

Safety result: `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. Phase 98 did not enable writes, add write scope, publish a tag/release, start v0.2 work, claim production readiness/security audit/broad compatibility/personal-book dogfood success, or add real financial/secrets/runtime artifacts.

Verification result: backend full suite passed (`329 passed, 27 warnings`); frontend check/auth-routes/build passed; Docker Compose config validation passed; `git diff --check` passed before commit; GitHub Actions recent `main` runs were successful; no `v0.1.1-readonly` local tag or GitHub release exists.

Related issues: GitHub #39 remains closed based on Phase 95/96 synthetic evidence and Phase 98 release-gate checks. GitHub #38 remains open/blocked pending a safe copied personal GnuCash SQL book outside git.

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
