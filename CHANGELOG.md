# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]

### Fixed

- Phase 96 — confirmed the Phase 95 / GitHub #39 CSV export row-count fix through the synthetic large-book benchmark path and tightened user-visible export copy. A 1,000-transaction generated synthetic benchmark returned 1,000 CSV data rows with `csv_limit=10000`, `csv_total=1000`, `truncated=False`, `csv_expected_body_rows=1000`, and `csv_body_matches_expected=True`. Benchmark JSON now records the expected body-row consistency fields, and frontend route checks cover copy that export is read-only, filtered, capped, and synchronous. No real/private data was committed, writes remain disabled by default, and no tag/release was published.
- Phase 95 — fixed GitHub #39, the read-only CSV export row-count/header mismatch above the historical 500-row service clamp. CSV export now fetches up to the documented 10,000-row export cap while normal list-style callers keep their existing pagination limits. Regression coverage proves a 501-row synthetic export returns 501 data rows with `X-CSV-Export-Limit: 10000`, `X-CSV-Export-Total: 501`, and `X-CSV-Export-Truncated: false`; a targeted 1,000-transaction synthetic benchmark returned 1,000 CSV data rows with `csv_limit=10000`, `csv_total=1000`, and `truncated=False`. No write-mode scope was added or enabled, no real/private data was committed, and no tag/release was published.

### Added

- Phase 94 — made the post-v0.1 maintenance-release decision without launching an analyst/auditor or creating an audit-only artifact: `docs/release/v0.1.1-readonly-decision.md` records the verdict `More fixes required before maintenance release`. The post-`v0.1.0-readonly` change set is meaningful, but GitHub #39 remains an open read-only CSV export row-count/header consistency blocker, so no `v0.1.1-readonly` notes/checklist were created and no tag/release was published. Writes remain disabled by default, no v0.2 work was started, and no real/private data was committed.

- Phase 93 — extended the real-but-limited Russian localization slice without claiming complete translation: desktop/mobile navigation now localizes the `/books` label, the read-only `/books` metadata page uses English/Russian catalog strings for headings, helper copy, read-only badges, access/status labels, empty state, and the GnuCash Desktop authoritative-editor safety note, and `README.ru.md`/`docs/localization.md` were refreshed to state that English remains canonical. Frontend route/static checks cover the new strings and localized `/books` usage. No write scope was added or enabled, no v0.2 work was started, no real/private data was committed, and no new release/tag was published.

- Phase 92 — improved GnuCash compatibility evidence collection without broadening compatibility claims: added a tested safe metadata collector for copied/disposable SQLite books, documented the copied-book metadata procedure, and added a narrow compatibility matrix row for the Phase 92 local generated-fixture metadata run. The collector redacts the input path and records only declared GnuCash Desktop version, SQLite backend, `versions` markers, and selected table counts; tests prove private path, account names, and transaction descriptions are not serialized. GnuCash Desktop was not installed in the Phase 92 environment, so this is procedure evidence rather than a desktop-version compatibility claim. No real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.
- Phase 91 — added a safe read-only `/books` metadata page for the narrow roadmap/#13 subset. The page is linked from desktop/mobile navigation, lists only already accessible configured books, marks the current/default book, and shows book name, base currency, storage type, read-only status, and access status. It deliberately exposes no book upload, deletion, registry editing, GnuCash data editing, collaborative, or family-wallet workflow. Frontend route checks cover the page/nav, existing backend tests cover unauthorized/archived book hiding/blocking, GitHub #13 was updated with evidence and kept open for future admin-only registration/default/deletion-from-registry work, no real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.
- Phase 90 — improved transaction search/filter usability for GitHub #11 by adding a readable active filter summary to the transaction filter panel. The summary shows search text, selected account, date range, and amount range, and explicitly states that the same active filters apply to the read-only transaction list and CSV export. Frontend route checks cover the summary and CSV parity copy. No backend write changes were made, CSV export query-string parity remains intact, no real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.
- Phase 87 — added a local large-book read-only benchmark v1 using generated synthetic GnuCash SQLite data only. The benchmark CLI creates a disposable book and measures authenticated read-only API paths for accounts tree load, transactions first page, transaction filters, account detail transactions, dashboard summary, and CSV export up to the current cap. Results are documented in `docs/performance/phase-87-large-book-benchmark.md`; the initial 1,000-transaction run found no endpoint failures, filed GitHub #39 for CSV export row-count/header inconsistency, and closed GitHub #30 as implemented. No real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.
- Phase 88 — extended the synthetic read-only benchmark for the account-with-many-splits risk: the fixture now includes one 60-split transaction, account-detail pagination checks for offsets 0 and 50, and transaction-detail rendering for the many-splits transaction. Results are documented in `docs/performance/phase-88-many-splits-benchmark.md`; the local/TestClient run rendered the 60-split detail without endpoint failure, documented account-detail pagination above one second as a limitation, closed GitHub #31 with evidence, and left GitHub #39 open for the existing CSV export row-count/header mismatch. No real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.
- Phase 89 — hardened dashboard aggregate correctness and benchmark coverage: report date parsing now returns clear `422` client errors, summary responses expose `reporting_basis=base_currency_only`, `includes_currency_conversion=false`, and visible limitations for no-conversion/mixed-currency behavior, the web dashboard displays those limitations, and the synthetic benchmark now covers dashboard summary, cashflow-by-month, expenses-by-account, and recent-transactions paths. Results are documented in `docs/performance/phase-89-dashboard-aggregate-benchmark.md`; GitHub #33 was closed with evidence, and #39 remains open for the existing CSV export row-count/header mismatch. No real/private data was committed, no writes were enabled, no v0.2 work was started, and no new release/tag was published.

- Phase 86 — triaged the Phase 85 copied personal-book dogfood findings and found no concrete application bug to fix; the only finding remains the release-blocking absence of a safe copied personal GnuCash SQL book, tracked by GitHub #38. Added a tested redacted dogfood preflight helper plus CLI (`apps/api/app/dogfood_preflight.py`, `apps/api/scripts/check_dogfood_book_candidate.py`) so future dogfood attempts can classify a candidate copied-book path as blocked/ready without opening the book, leaking full private paths, or committing real data. GitHub #38 was updated with evidence and kept open; no new tag/release was published, writes remain disabled by default, no private data was committed, and no v0.2 work was started.

- Phase 85 — attempted the post-v0.1 copied personal-book dogfood pass with a strict safe scenario: copied book only, original untouched, writes disabled, local-only access, and no private output committed. No safe copied personal GnuCash SQL book was available to this environment outside git, so the real-book run is recorded as blocked rather than passed; `docs/dogfood/phase-85-personal-copied-book-results.md` documents the redacted result, and GitHub #38 tracks rerunning the dogfood pass when a safe copied book is available. No new tag/release was published, writes remain disabled by default, no private data was committed, and no v0.2 work was started.
- Phase 84 — completed post-release CSV export truncation/timeout hardening for #32 by adding successful-export response headers for the active row cap (`X-CSV-Export-Limit`), matching pre-cap total (`X-CSV-Export-Total`), truncation status (`X-CSV-Export-Truncated`), and synchronous timeout policy (`X-CSV-Export-Timeout-Policy`); forwarding those headers through the SvelteKit CSV export proxy; documenting that CSV exports are synchronous, capped at 10,000 rows, and should be narrowed if a request times out; and adding backend/proxy regression coverage with disposable fake data. No new tag/release was published, writes remain disabled by default, and no v0.2 work was started.
- Phase 83 — completed post-release frontend money-display hardening for #34 by adding decimal-string helper coverage and replacing `Number()` money decisions in dashboard net-worth trend, recent transaction amount color, cashflow net color, expenses bar widths, and transaction amount-range prevalidation. Remaining frontend `Number()` usage is limited to non-money IDs/pagination route values. No new tag/release was published, writes remain disabled by default, and no v0.2 work was started.
- Phase 82 — completed post-release read-only multi-book boundary hardening for #35 by adding backend regression tests that prove archived books are excluded from `GET /books`, `GET /books/{book_id}` returns `404` for archived books even when the user has metadata access, and unauthorized/archived access is blocked before data exposure across book-aware accounts, transaction browsing/detail/account transaction, CSV export, and all report route families. No new tag/release was published, writes remain disabled by default, and no v0.2 work was started.
- Phase 81 — completed post-release hardening for #27 by redacting default-book seed logs: startup seed logs now include only a sanitized book filename/label while preserving the configured path/URI in app metadata, and backend regression tests prove full filesystem paths, connection URI strings, hosts, usernames, passwords/tokens, and query parameters are not logged. No new tag/release was published, writes remain disabled by default, and no v0.2 work was started.
- Phase 80 — published `v0.1.0-readonly` as an annotated git tag on commit `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` and created the GitHub pre-release at <https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly> using `docs/release/v0.1.0-readonly-notes.md`; verified the v0.1 tag/release did not exist before publication, re-checked the green Phase 79 main-branch CI, kept `GNUCASH_WRITES_ENABLED=false`, made no scope expansion, and started no v0.2 work.
- Phase 79 — accepted Phase 78 copied/disposable-data browser dogfood evidence for the `v0.1.0-readonly` runtime gate, created conservative `docs/release/v0.1.0-readonly-notes.md`, completed `docs/release/v0.1.0-readonly-final-gate.md` with verdict ready for publication as a separate explicit next step, updated the v0.1 checklist/status docs, closed #24 and #25, verified #37 remains closed, kept `GNUCASH_WRITES_ENABLED=false`, and did not publish a tag or GitHub release.
- Phase 78 — fixed Docker web UI `/login` redirect loop (#37) by allowing the root SvelteKit layout to return public unauthenticated layout data before token/book-context lookup; added auth-route regression checks, added a server-side CSV export proxy for the existing UI export link, reran Docker browser/UI dogfood through Caddy on a copied/disposable SQL fixture, verified dashboard/accounts/account detail/transactions/transaction detail/CSV export load after login, confirmed write UI stays hidden and validate/create/patch write probes return 403 with `GNUCASH_WRITES_ENABLED=false`, and left #24/#25 open for release-note/release-gate completion without publishing a release.
- Phase 77 — real Docker read-only dogfood on a copied/disposable GnuCash SQL book: API health/login, accounts, account detail, transactions, transaction detail, search/filter, CSV export, and disabled validate/create/patch write-endpoint probes passed with `GNUCASH_WRITES_ENABLED=false`; browser/UI dogfood is blocked by #37 because `/login` redirects to itself, so #25 remains open and `v0.1.0-readonly` is not ready.
- Phase 76 — v0.2 planning audit, confirming the project is not ready to create or promote a controlled-writes planning milestone because `v0.1.0-readonly` remains unpublished and blocked by #24/#25, completed copied/disposable-data dogfood evidence is still missing, #36 remains open for write-readiness gates, and controlled writes must remain experimental/post-MVP and disabled by default.
- Phase 75 — v0.1.1 maintenance-release audit, confirming no maintenance release is needed/applicable because `v0.1.0-readonly` has not been published as a git tag or GitHub release; #24/#25 remain the initial v0.1 publication blockers, no new noisy GitHub issue was created, and v0.1.1 should not be considered until after a real v0.1.0 release plus post-release maintenance change set exist.
- Phase 74 — controlled-writes boundary audit, confirming `GNUCASH_WRITES_ENABLED=false` remains the backend/default environment setting, backend validate/create/patch routes are feature-gated before write service construction, frontend write UI is hidden unless explicitly enabled and requires warning/acknowledgement, disposable-fixture write tests plus file-lock/backup-restore coverage exist, and #36 tracks remaining v0.2 write-readiness gates while keeping controlled writes experimental/post-MVP and leaving `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 73 — multi-book access model audit, confirming explicit `UserBookAccess`-scoped visibility, blocked unauthorized book-aware access, accessible-list-only book switcher behavior, independent-books/no-family-wallet/no-collaborative-editing framing, and safe default-book alias behavior; clarified archive/visibility semantics in `docs/book-switcher-readonly-model.md` and created #35 for archived-book/full route-family boundary-test hardening while leaving `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 72 — data model and money-correctness audit, confirming backend core money paths use Decimal/string DTOs, JSON and CSV expose decimal strings, multi-currency report totals remain conservative with no fake conversion, and no newly introduced backend float-based money calculation was found; added canonical money/sign/split guidance in `docs/money-model.md` and created #34 to track frontend display-only `Number()` money hygiene while leaving `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 71 — performance-risk audit, confirming transaction pagination and CSV row-cap safeguards exist while identifying missing large-book, many-splits, CSV timeout/truncation, and dashboard aggregate benchmark evidence; created #30–#33 to track those read-only performance risks without changing product code or expanding write scope.
- Phase 70 — community-announcement audit, confirming README audience boundaries, synthetic-screenshot labeling, conservative feedback-wanted announcement drafts, fair related-project comparison, and limited-circles-only sharing posture while keeping broad launch-style promotion and `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 69 — localization/i18n audit, confirming English remains canonical, Russian README/UI localization is conservative and opt-in, localized safety wording preserves the read-only/default-write boundary, complete translation is not a v0.1 blocker unless PM changes release criteria, and #29 tracks a non-blocking localization glossary for accounting/safety terms while `v0.1.0-readonly` publication remains blocked by #24/#25.
- Phase 68 — documentation-formatting audit, confirming markdown source readability is acceptable with non-blocking cleanup needed before wider announcement; Phase 68 fixed small historical code-fence/link clarifications, created #28 for gradual raw-markdown readability cleanup, and left `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 67 — open-source hygiene audit, confirming license, README, contributing guide, code of conduct, security policy, funding placeholder, issue/PR templates, GitHub topics, documented social-preview setup, and meaningful open issues are in place; Phase 67 also created the missing `needs-triage` label used by issue templates and updated the GitHub repository description to include read-only positioning, while leaving `v0.1.0-readonly` publication blocked by #24/#25.
- Phase 66 — security posture audit, confirming no security-audited/production-ready claim, auth tokens remain in httpOnly cookies rather than browser auth storage, placeholder JWT secrets are rejected, dependency files exist for future scanning, CORS origin narrowing remains tracked in #26, and a new hardening issue #27 tracks redacting full GnuCash book paths from seed logs before broader/shared deployment posture is treated as hardened.
- Phase 65 — test coverage audit, mapping current maturity/read-only/release claims to backend tests, frontend check/auth-route/build coverage, Docker Compose validation, and CI workflow coverage; automated tests support the current pre-alpha/read-only posture, but live copied/disposable-data runtime smoke/dogfood evidence remains required before `v0.1.0-readonly` publication (#25), alongside conservative release notes (#24).
- Phase 64 — compatibility audit, confirming README/release/compatibility docs do not claim broad GnuCash compatibility without evidence: tested scope remains documented synthetic GnuCash SQL SQLite fixture paths, PostgreSQL/MySQL/MariaDB/XML/all-version support is not claimed, #22 remains open for real-version fixture coverage, and `v0.1.0-readonly` publication remains blocked by #24/#25.
- Phase 63 — backup/recovery audit, confirming the manual backup and restore runbook covers copied GnuCash books, app metadata, controlled-write pre-write backups, restore dry-runs, read-only verification, and production-DR limitations while correcting stale Compose write-disabled verification examples.
- Phase 62 — deployment-safety audit, confirming local/self-hosted docs are conservative for localhost/LAN/VPN-only read-only testing while keeping direct public-internet exposure unsafe, leaving `v0.1.0-readonly` publication blocked by #24/#25, and tracking CORS origin narrowing visibility in #26.
- Phase 61 — dogfood-results audit, confirming that no completed copied-book dogfood results are recorded yet; `v0.1.0-readonly` publication remains blocked until copied/disposable-data runtime evidence is completed and audited.
- Phase 60 — dogfood-readiness audit, confirming the maintainer can safely start read-only dogfood on a copied real GnuCash SQL book while keeping `v0.1.0-readonly` publication blocked until actual copied/disposable-data runtime evidence is recorded.
- Phase 59 — post-release regression-risk audit, confirming that a true post-v0.1 regression audit is not applicable yet because no `v0.1.0-readonly` tag/GitHub release exists; publication remains blocked by the Phase 57/58 release-notes and copied/disposable-data smoke/dogfood evidence issues.
- Phase 58 — `v0.1.0-readonly` release publication audit, confirming no v0.1 tag/GitHub release exists yet and publication remains blocked by the Phase 57 release-notes and copied/disposable-data smoke/dogfood evidence issues.
- Phase 57 — `v0.1.0-readonly` release-gate audit, confirming the read-only/default-write safety boundary is intact while blocking release publication until conservative v0.1 release notes and copied/disposable-data runtime smoke/dogfood evidence are completed.
- Phase 56 — `v0.1.0-readonly` release planning: conservative release plan and checklist defining included/excluded read-only scope, minimum checks, dogfood/runtime smoke gates, compatibility limits, upgrade path, blockers, rollback plan, and a required future release-gate audit before any tag/release.
- Phase 55 — v0.1 read-only scope-freeze audit, confirming the project is ready to prepare a `v0.1.0-readonly` plan while fixing stale roadmap release-posture wording and preserving the read-only/default-write safety boundary.
- Phase 54 — observability and diagnostics: structured safe startup diagnostics, richer non-sensitive `/health` payload with app DB/default-book/write-mode checks, and self-hosted troubleshooting guidance.
- Phase 53 — community announcement draft and where-to-share guidance for cautious feedback collection, with explicit pre-alpha, read-only-by-default, no production/security guarantee, and experimental-write warnings.
- Phase 52 — Russian localization planning and i18n foundation: English-default SvelteKit locale structure, opt-in Russian UI strings for login/navigation/safety banner/core page titles, `README.ru.md`, and localization guidance documenting English docs as canonical.
- Phase 51 — independent auditor pass after UX/book/filter work, confirming read-only scope, independent-books framing, filter/export safety, and documentation consistency with no blockers.
- Phase 50 — book switcher stabilization: clearer current-book UI, route/query-preserving switching, accessible-book fallback handling, independent-books documentation, and frontend route checks for book-aware access boundaries.
- Phase 49 — transaction search/filter hardening: shared API validation for inverted/invalid date ranges and inverted amount ranges, frontend date-range validation, documented URL/pagination behavior, and CSV export filter parity regression coverage.
- Phase 48 — read-only core UX polish: clearer transaction empty states, filter reset/status copy, CSV export cap/status copy, mobile card copy, account-tree empty state, and account breadcrumbs without write-scope expansion.
- Phase 47 — independent auditor pass after compatibility fixture work, confirming fixture safety/no personal data/no unwanted generated binary commits and keeping compatibility claims conservative.
- Phase 46 — generated disposable GnuCash SQLite compatibility fixture v1 path with read-only service tests for account tree, transaction list, split detail, reports, and checksum no-mutation behavior.
- Phase 45 — GnuCash real-version compatibility fixture plan covering target versions, fixture data model, safe generation/storage policy, and acceptance tests for issue #22.
- Phase 44 — backup and recovery runbook for app metadata DB, copied GnuCash books, Docker data paths, restore dry-runs, and experimental controlled-write pre-write backup expectations.
- Phase 43 — local secure deployment guide for conservative localhost, LAN, and VPN-only self-host testing while keeping writes disabled by default.

## [0.0.2-prealpha] - 2026-05-18

### Added

- Phase 17 — synthetic GnuCash fixture and read-only integration validation.
- Phase 18 — README screenshots and mobile preview with synthetic data.
- Phase 19 — multi-currency limitation tests and auth cookie security documentation.
- Phase 20 — multi-book UI foundation (book switcher, book-aware routes).
- Phase 21 — file-based write lock replacement (`fcntl.flock()` for multi-worker safety).
- Phase 22 — real controlled write integration tests against disposable piecash books.
- Phase 23 — backup restore smoke test (automated restore verification).
- Phase 24 — CSV export for transactions (read-only, filter-preserving, 10,000 row cap).
- Phase 25 — documentation, release, and roadmap sync for the next pre-alpha candidate.
- Phase 26 — audit-driven status sync after independent review.
- Phase 27 — discoverability and community announcement readiness docs.
- Phase 28 — GnuCash compatibility matrix for committed synthetic fixtures.
- Phase 29 — audit-driven release documentation sync for Phases 26–28.
- Phase 30 — frontend amount range filters for read-only transaction browsing and CSV export.
- Phase 31 — global read-only safety status banner in the authenticated web shell.
- Phase 32 — backend write-gating regression coverage for disabled validate/create/patch routes.
- Phase 33 — controlled-writes documentation cleanup and public status sync after disabled-write regression coverage.
- Phase 34 — public README/status baseline sync through the Phase 33 baseline.
- Phase 35 — audit-driven public status sync through Phase 34 and controlled-writes limitation cleanup.
- Phase 36 — write-mode UI warning and explicit confirmation for experimental controlled writes.
- Phase 37 — independent audit and baseline sync after Phase 36.
- Phase 38 — personal read-only dogfood guide and manual smoke checklist for copied GnuCash books.
- Phase 39 — automated read-only API smoke script for local Docker deployments.
- Phase 40 — `v0.0.2-prealpha` release-candidate checklist and notes cleanup without publishing a tag/release.
- Phase 41 — `v0.0.2-prealpha` release-gate audit and release-documentation hygiene cleanup without publishing a tag/release.
- Phase 42 — published `v0.0.2-prealpha` after the Phase 41 gate and green local/GitHub checks.

### Security

- Auth cookie deployment documentation (httpOnly, sameSite, secure flags, no production guarantee).
- Multi-currency reporting limitations documented and tested.
- Independent audit report refreshed for Phase 29 with read-only/default-write checks.
- Authenticated app shell now displays a persistent read-only-by-default reminder.
- Disabled-write API regression tests now prove validate/create/patch return read-only 403 responses without constructing the write service.
- Controlled-writes documentation now reflects file-based locking, backup restore smoke coverage, and disabled-write bypass regression coverage as completed safety work while write mode remains experimental and disabled by default.
- Controlled-writes limitations now correctly state that frontend amount range filters exist for read-only browsing and CSV export.
- Experimental write mode now shows a prominent UI warning and requires explicit acknowledgement before final create submission while remaining disabled by default.
- Release-gate audit re-verified disabled-write gating and tracked-file sensitive-data hygiene before `v0.0.2-prealpha` publication.

### Known limitations

- Pre-alpha only; no production-readiness guarantee.
- piecash write compatibility not guaranteed for all GnuCash versions.
- Transaction amount range filters are available for browsing and CSV export; advanced export customization is still limited.
- Multi-book UI is structural; full multi-user access control is post-MVP.
- Compatibility matrix currently covers committed synthetic SQLite fixtures only; PostgreSQL/MySQL/MariaDB, XML books, and multiple desktop-generated versions are not yet validated.

## [0.0.1] - 2026-05-16

### Added

- Initial public skeleton / MVP foundation.
- AGPL-3.0 license.
- README with project overview, honest pre-alpha status, safety warnings, and release/tag instructions.
- SECURITY.md with private vulnerability reporting guidance and pre-alpha safety warnings.
- CONTRIBUTING.md with current backend/frontend setup and sensitive data policy.
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1).
- `.env.example` with documented bootstrap and GnuCash book configuration.
- `.gitignore` rules for environment files, GnuCash book files, backups, and secrets.
- GitHub issue templates, pull request template, and funding metadata placeholder.
- GitHub Actions CI for required-file checks, sensitive tracked-file checks, frontend checks, backend tests, and Docker Compose validation.
- Documentation for architecture, MVP scope, roadmap, security model, GnuCash safety, development, competitive review, and product positioning.
- SvelteKit frontend skeleton with login flow, dashboard, accounts, transactions, theme system, mobile navigation, and PWA manifest foundation.
- FastAPI backend skeleton with health endpoint, authentication, app metadata database, book registry/access services, and read-only book APIs.
- `piecash` integration through a read-only service layer for GnuCash SQL books.
- Read-only account, transaction, and report DTOs/API endpoints.
- Docker Compose deployment scaffold with API, web, and Caddy proxy services.
- Backend pytest suite and frontend route/type/build checks.

### Security

- MVP GnuCash access is documented and implemented as read-only-first.
- App metadata is stored separately from the GnuCash book.
- Auth token is stored in an httpOnly cookie by the frontend, not browser local/session storage.
- No telemetry added.

### Known limitations

- Pre-alpha only; no production-readiness guarantee.
- Users should test with a copy or fixture book before real data.
- Basic reports aggregate only configured base-currency values; no automatic currency conversion.
- Docker Compose config is validated in CI, but deployments still need environment-specific testing.
