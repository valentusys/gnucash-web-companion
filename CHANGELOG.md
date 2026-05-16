# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]

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
