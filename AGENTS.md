# AGENTS.md

Project context for Hermes and other coding agents working in this repository.

## Project

`gnucash-web-companion` is a modern self-hosted web companion for existing GnuCash SQL books.

- Frontend: SvelteKit in `apps/web/`
- Backend: FastAPI in `apps/api/`
- GnuCash access: `piecash` behind service layers
- App metadata: separate SQLite app DB (`app.db`), never stored inside the GnuCash book
- Deployment: Docker Compose with Caddy reverse proxy
- License: AGPL-3.0

## Architecture decisions

- GnuCash desktop remains the authoritative accounting application.
- The app is single-book by default, with service boundaries that keep later multi-book support possible.
- App users, auth, book registry, access metadata, and audit logs live in the app metadata DB, not in the GnuCash DB.
- Read-only browsing was the v0.1 baseline. Controlled writes are narrow and safety-gated.
- Money must use `Decimal`/string representation. Do not use floats for monetary values.
- Auth tokens are stored in httpOnly cookies. Never use localStorage/sessionStorage for auth.
- Dashboard/report aggregations must not fake currency conversion. If conversion is not implemented, document limitations.

## Controlled write rules

- Write features must be explicit, narrow, tested, and documented.
- Backup before every GnuCash write.
- Acquire a per-book write lock before writing.
- Audit every routed write attempt, including failures after the request enters the write route.
- Validate before write: split count, zero-sum by currency, valid decimal strings, valid accounts, placeholder rejection, role checks.
- Do not implement direct SQL writes to GnuCash.
- Do not implement collaborative multi-user editing as a core feature.
- Do not add delete/import/recurring/account-edit write features unless a later phase explicitly requests them.

## Security and data rules

- Never commit real financial data, GnuCash books, backups, `.env`, credentials, tokens, certificates, or private keys.
- Keep `.gitignore` protections for `data/books/*`, `data/backups/*`, `data/app/*`, `.env`, `secrets/`, and credential files.
- Use test copies of GnuCash books for development and QA.
- Do not expose pre-alpha builds directly to the public internet.
- If a secret or real book appears in git status/diff, stop and remove it before committing.
- Do not publish packages or releases unless explicitly requested.

## Commands

Backend:

```bash
cd apps/api
pytest -q
```

Frontend:

```bash
cd apps/web
npm run check
npm run test:auth-routes
npm run build
```

Docker/config validation:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Runtime smoke test, when Docker is available:

```bash
JWT_SECRET=<real-dev-secret> APP_ADMIN_PASSWORD=<dev-password> docker compose up --build
```

GitHub/CI:

```bash
git --version
gh --version
gh auth status
gh run list --limit 5
```

If `gh` is unavailable or unauthenticated, continue locally and record the blocker in `PROJECT_STATUS.md` or the phase handoff.

## Development workflow

- One agent executes phases sequentially. Do not rely on delegate subagents for this project workflow unless the user explicitly asks.
- Before GitHub operations: check `git --version`, `gh --version`, and `gh auth status`.
- If `gh` is authenticated, use `gh` for GitHub issues/runs.
- If `gh` is not authenticated but a safe token is explicitly available, configure auth.
- If GitHub auth is impossible, continue locally and document the blocker.
- After each phase:
  - update `PROJECT_STATUS.md`
  - create/update `docs/handoff/phase-N.md`
  - run relevant checks
  - commit changes
  - push if auth is available
  - create/update a GitHub issue if `gh` is available
- Do not ask for confirmation between phases unless blocked by secrets, GitHub auth, or an irreversible/destructive action.

## Coding rules

- Keep changes scoped to the current phase.
- Add or update tests for behavior changes and bug fixes.
- Prefer service-layer logic over route-level business logic.
- Keep DTOs explicit and typed.
- Use controlled exceptions and user-safe error messages.
- Maintain mobile-friendly frontend UX and accessible labels.
- Do not introduce telemetry.
- Do not add heavy chart/animation libraries without explicit need.
- Keep docs honest: pre-alpha, test copies first, no production guarantee.
