# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]

### Added

- Phase 116 — completed GitHub #38 copied personal-book dogfood with a local-only Docker/Caddy read-only run against Val's provided safe copied book archive, recording only redacted route/status evidence and no private book data, app DB, screenshots, CSV exports, `.env`, paths, names, descriptions, memos, amounts, secrets, tags, releases, or packages.
- Phase 115 — prepared conservative `v0.1.2-readonly` release notes, release-prep checklist, and final-gate artifact for a possible future maintenance pre-release without publishing a tag, GitHub release, package, or changing the default read-only/write-disabled posture.
- Phase 114 — added a durable headless Chromium/CDP browser dogfood helper and recorded a synthetic/disposable Docker/Caddy UI/API dogfood refresh covering login, dashboard, accounts, books, scheduled awareness, transaction filters, account/transaction detail, CSV export, and disabled-write probes with `GNUCASH_WRITES_ENABLED=false`.
- Phase 113 — added a Russian accounting/safety glossary and localized the transaction filter/CSV export UI slice through the existing message catalog, while keeping English canonical, translation partial, URL-only filters, and read-only/export warnings intact.
- Phase 112 — added safe CORS deployment posture diagnostics to `/health` and startup logs, warning when wildcard `CORS_ORIGINS` is used outside development-like environments while documenting exact localhost/LAN/VPN origin examples without production-readiness claims.
- Phase 111 — added a safe GnuCash Desktop/CLI tooling availability probe for compatibility evidence, documented that the local environment has no `gnucash`/`gnucash-cli`, and kept Desktop-generated compatibility claims explicitly blocked until a disposable Desktop environment exists.
- Phase 110 — hardened the read-only `/books` metadata UX with explicit access role/status/read-only metadata, safe book-context links to existing read-only views, stronger no-management-action copy, and regression coverage that archived/unauthorized books remain hidden or blocked.
- Phase 109 — added a conservative read-only scheduled/recurring transaction awareness API and `/scheduled` UI page that expose only safe summary metadata, avoid next-run predictions and template split details, and keep GnuCash Desktop as the authoritative editor.

### Fixed

- Phase 105 — synchronized local release/status documentation and the existing GitHub release body for the already published `v0.1.1-readonly` pre-release. This corrected stale release-prep-only wording, updated README/PROJECT_STATUS/release notes to name `v0.1.1-readonly` as the current public read-only pre-alpha release, and documented the guardrail that release/status docs must be updated in the same phase as factual release-state changes. No product code, tag, release, package, write-mode setting, private data, or real GnuCash book was changed.

## [0.1.1-readonly] - 2026-05-18

### Fixed

- Phase 81 — redacted default-book seed logs so startup logs no longer expose full configured book paths or connection URI details.
- Phase 82 — expanded read-only multi-book access-boundary regression coverage for archived and unauthorized books across route families.
- Phase 83 — hardened frontend money-display decisions to avoid using `Number()` for money-string display logic.
- Phase 84 — added CSV export response headers and frontend proxy forwarding for export limit, total, truncation, and timeout policy metadata.
- Phase 95 — fixed GitHub #39: read-only CSV export now fetches up to the documented 10,000-row export cap instead of inheriting the historical 500-row list-service clamp. Regression coverage and synthetic benchmark evidence confirmed correct row-count/header behavior.
- Phase 96 — confirmed the Phase 95 CSV export fix through the generated synthetic large-book benchmark path; a 1,000-transaction generated run returned 1,000 CSV data rows with matching expected-body metadata.

### Added

- Phase 86 — added a redacted copied-book preflight helper for future safe personal-book dogfood attempts.
- Phase 87 through Phase 89 — expanded generated/synthetic benchmark coverage for large books, many-splits transactions, and dashboard aggregate paths without broad production-performance claims.
- Phase 90 — added a readable transaction active-filter summary and copy stating that the same filters apply to the read-only list and CSV export.
- Phase 91 — added a read-only `/books` metadata page for accessible configured books without upload, deletion, registry editing, GnuCash data editing, collaborative, or family-wallet workflow.
- Phase 92 — added safe GnuCash compatibility metadata collection for copied/disposable SQLite books without exposing private paths or financial details.
- Phase 93 — added a narrow Russian localization slice while keeping English canonical and translation status honest.
- Phase 103 — added read-only transaction date-range preset links for `This month`, `Last month`, `Year to date`, and `Clear dates`; presets use the existing date query parameters, preserve other active filters, and keep CSV export parity.
- Phase 104 — broadened the existing read-only transaction `query` filter so transaction list/count, account transaction lists, and CSV export match split memo text as well as transaction descriptions, case-insensitively.

### Release notes

- `v0.1.1-readonly` was published as a GitHub pre-release on 2026-05-18 and the tag points to `a4d04150c043ad4da3dea577b30ed7ffd2032df0`, after Phase 104. Its published scope therefore includes the Phase 103/104 read-only transaction date-preset and split-memo search changes.
- This remains a conservative pre-alpha/read-only release. `GNUCASH_WRITES_ENABLED=false` remains the default; controlled-write code is experimental post-MVP work outside this release scope.

### Known limitations

- Not production-ready and not security-audited.
- Do not expose early deployments directly to the public internet.
- Test with disposable fixtures or copied GnuCash SQL books first, keep backups, and keep `.env`, app DBs, GnuCash books, backups, private exports/screenshots, secrets, tokens, keys, and certs out of git.
- GitHub #38 remains open/blocked until a safe copied personal GnuCash SQL book is available outside git for a local-only dogfood rerun.
- Compatibility evidence remains intentionally narrow; no broad PostgreSQL/MySQL/MariaDB/XML/all-version or arbitrary real-world-book compatibility is claimed.
- No hosted SaaS readiness, collaborative accounting, family-wallet positioning, real-time multi-user editing, CSV/OFX import, banking integration, or safe production write mode is claimed.

## [0.1.0-readonly] - 2026-05-18

### Added

- Phase 43 — local secure deployment guide for conservative localhost, LAN, and VPN-only self-host testing while keeping writes disabled by default.
- Phase 44 — backup and recovery runbook for app metadata DB, copied GnuCash books, Docker data paths, restore dry-runs, and experimental controlled-write pre-write backup expectations.
- Phase 45 — GnuCash real-version compatibility fixture plan covering target versions, fixture data model, safe generation/storage policy, and acceptance tests for issue #22.
- Phase 46 — generated disposable GnuCash SQLite compatibility fixture v1 path with read-only service tests for account tree, transaction list, split detail, reports, and checksum no-mutation behavior.
- Phase 48 through Phase 50 — read-only core UX polish, transaction search/filter hardening, and book switcher stabilization.
- Phase 52 and Phase 53 — Russian localization planning/i18n foundation plus conservative community announcement materials.
- Phase 54 — structured safe startup diagnostics, richer non-sensitive `/health` payload, and self-hosted troubleshooting guidance.
- Phase 77 and Phase 78 — copied/disposable-data Docker/API/browser dogfood evidence, including the `/login` redirect-loop fix and CSV export proxy behavior.
- Phase 79 — conservative `v0.1.0-readonly` release notes and final release-gate artifact.
- Phase 80 — published `v0.1.0-readonly` as an annotated git tag on commit `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` and created the GitHub pre-release using `docs/release/v0.1.0-readonly-notes.md`.

### Security

- Multiple audit phases re-verified read-only/default-write-disabled posture, httpOnly auth-cookie expectations, private-data hygiene, conservative deployment warnings, and limited compatibility claims.
- `GNUCASH_WRITES_ENABLED=false` remained the default; controlled writes remained experimental/post-MVP.

### Known limitations

- Pre-alpha only; no production-readiness or security-audit guarantee.
- Users should test with copied/disposable data first and avoid direct public-internet exposure.
- GitHub #38 remains open for copied personal-book dogfood when a safe copied SQL book is available.

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
