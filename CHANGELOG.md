# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]

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

### Security

- Auth cookie deployment documentation (httpOnly, sameSite, secure flags, no production guarantee).
- Multi-currency reporting limitations documented and tested.
- Independent audit report refreshed for Phase 29 with read-only/default-write checks.
- Authenticated app shell now displays a persistent read-only-by-default reminder.
- Disabled-write API regression tests now prove validate/create/patch return read-only 403 responses without constructing the write service.
- Controlled-writes documentation now reflects file-based locking, backup restore smoke coverage, and disabled-write bypass regression coverage as completed safety work while write mode remains experimental and disabled by default.

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
