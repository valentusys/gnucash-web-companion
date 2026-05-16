# Contributing to gnucash-web-companion

Thank you for your interest in contributing! This document explains how to get involved.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Development setup

> 🚧 Placeholder — detailed development setup instructions will be provided in Phase 2 once the project skeleton (SvelteKit + FastAPI + Docker) exists.

Expected setup (subject to change):

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
# Edit .env with your local configuration
docker compose up --build
```

## How to contribute

### Reporting bugs

Use the [bug report issue template](https://github.com/valentusys/gnucash-web-companion/issues/new?template=bug_report.yml) to report bugs. Include:

- Steps to reproduce.
- Expected vs. actual behavior.
- Environment details (OS, browser, Docker version if relevant).

### Suggesting features

Use the [feature request issue template](https://github.com/valentusys/gnucash-web-companion/issues/new?template=feature_request.yml) to suggest features. Please check the [ROADMAP.md](docs/ROADMAP.md) and [MVP.md](docs/MVP.md) first to understand current scope boundaries.

### Pull requests

1. **Fork** the repository and create a feature branch from `main`.
2. **Keep changes focused.** One logical change per PR.
3. **Write clear commit messages.** See [Commit style](#commit-style) below.
4. **Add or update tests** where relevant (see below).
5. **Update documentation** if your change affects behavior, configuration, or architecture.
6. **Open a pull request** against `main` using the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).

### Branch naming

Use short, descriptive branch names:

- `feature/<short-description>` — new features or enhancements.
- `fix/<short-description>` — bug fixes.
- `docs/<short-description>` — documentation-only changes.
- `chore/<short-description>` — maintenance, tooling, CI, etc.

### Commit style

We don't enforce a strict commit convention, but we recommend clear, imperative-style messages:

```
Add account detail endpoint
Fix pagination offset in transaction search
Update README quick start section
```

For multi-step changes, consider breaking them into logical commits rather than one large commit.

### Tests

- **Backend (FastAPI):** add or update tests in the `apps/api/` test suite. New endpoints should have at least basic response-shape tests.
- **Frontend (SvelteKit):** add or update component or integration tests where relevant.
- **Safety-critical code** (anything that touches GnuCash data access) should have tests proving read-only behavior (e.g., checksum/mtime assertions around open/read operations).

If you're unsure whether tests are needed for your change, mention it in the PR description.

## Respect the read-only MVP boundary

The current milestone (v0.1) is **read-only**. When contributing:

- **Do not** add write endpoints, transaction creation, or book mutation logic.
- **Do not** add collaborative/multi-user editing features.
- **Do not** store app metadata inside the GnuCash book.
- **Do** keep internal abstractions (e.g., `BookContext`) clean for future multi-book support.
- **Do** flag any safety concerns in your PR description if your change touches data access.

If you're unsure whether a change fits within the current scope, open an issue for discussion before investing significant effort.

## License

By contributing to this project, you agree that your contributions will be licensed under the [AGPL-3.0](LICENSE).
