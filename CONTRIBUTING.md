# Contributing to gnucash-web-companion

Thank you for your interest in contributing. This project handles sensitive financial data, so contributions should prioritize correctness, safety, and clear scope boundaries.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold it.

## Development setup

### Docker quick start

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
# Edit .env before running. Use a test copy of a GnuCash SQL book.
docker compose up --build
```

### Backend checks

```bash
cd apps/api
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q
```

### Frontend checks

```bash
cd apps/web
npm install
npm run check
npm run test:auth-routes
npm run build
```

If an optional app directory is missing in an early branch, CI should skip that part rather than require secrets or unavailable services.

## How to contribute

### Reporting bugs

Use the bug report issue template. Include:

- Steps to reproduce.
- Expected vs. actual behavior.
- Environment details (OS, browser, Docker version if relevant).
- Whether you used a fixture book or a copy of a real book.

Do **not** attach real GnuCash books, exports, screenshots, or logs containing personal financial data.

### Suggesting features

Use the feature request issue template. Please check [ROADMAP.md](docs/ROADMAP.md) and [MVP.md](docs/MVP.md) first to understand current scope boundaries.

### Pull requests

1. Fork the repository and create a branch from `main`.
2. Keep changes focused. One logical change per PR.
3. Add or update tests where relevant.
4. Update documentation if behavior, configuration, safety, or architecture changes.
5. Confirm the safety checklist in the pull request template.
6. Open a PR against `main`.

### Branch naming

- `feature/<short-description>` — new read-only features or enhancements.
- `fix/<short-description>` — bug fixes.
- `docs/<short-description>` — documentation-only changes.
- `chore/<short-description>` — maintenance, tooling, CI, release preparation.

### Commit style

Use clear, imperative messages. Conventional Commit prefixes are welcome but not strictly required.

Examples:

```text
Update README publication warnings
Fix transaction pagination offset
Add account detail response test
```

## Tests

- Backend: add/update tests in `apps/api/tests/`.
- Frontend: run SvelteKit type checks and add targeted tests where practical.
- Safety-critical code touching GnuCash data access should prove it does not mutate books, using fixture/copy-based strategies where possible.

## Respect the read-only MVP boundary

The current milestone is read-only-first. Do not add these without explicit project decision and design documentation:

- GnuCash write endpoints.
- Transaction/account creation, editing, or deletion.
- Direct GnuCash schema changes.
- Collaborative multi-user accounting workflows.
- App metadata stored in the GnuCash book.
- Telemetry.

## Sensitive data policy

Never commit:

- `.env` files.
- JWT secrets, API keys, passwords, or private keys.
- Real `.gnucash`, `.sqlite`, `.sqlite3`, backup, export, or report files.
- Screenshots/logs containing personal financial data.

Use synthetic fixtures for tests and examples.

## License

By contributing to this project, you agree that your contributions will be licensed under the [AGPL-3.0](LICENSE).
