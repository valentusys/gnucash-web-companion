# AGENTS.md

Project context for Hermes and other coding agents working in this repository.

## Operating mode

- One autonomous Hermes coding agent executes phases sequentially.
- Do not use parallel subagents or `delegate_task` unless the user explicitly overrides this.
- If work is interrupted, resume from `PROJECT_STATUS.md` and `docs/handoff/phase-*.md`.
- Do not ask for confirmation between phases unless blocked by secrets, GitHub auth, or irreversible/destructive action.

## Project

`gnucash-web-companion` is a modern self-hosted web companion for existing GnuCash SQL books.

Base product model:

- MVP: one installation, one local admin user, one default GnuCash book, read-only access.
- Future: one installation, multiple users, multiple independent books, users access only assigned books.
- Advanced future: shared editing of one book only as serialized/locked mode; no real-time collaborative editing.

Important positioning:

- Do not build a "family wallet" as the baseline model.
- Do not build collaborative accounting on top of GnuCash.
- Treat each GnuCash book as a monopolistic accounting ledger.
- Multi-user expansion is through multiple independent books, not collaborative editing of one book.

## Stack

- Frontend: SvelteKit, TypeScript, Tailwind CSS, SSR-first, mobile-first, CSS variables for theming, minimal client-side state.
- Backend: FastAPI, Python, Pydantic, `piecash` behind service layers, thin routers.
- App metadata DB: `/data/app/app.db` SQLite for users, books, access, sessions/audit placeholders.
- GnuCash books: `/data/books/*.gnucash.sqlite`.
- Backups: `/data/backups/<book_id>/`.
- Deployment: Docker Compose with Caddy reverse proxy.
- License: AGPL-3.0.

## Architecture decisions

- GnuCash desktop remains the authoritative accounting application.
- The MVP v0.1 is strictly read-only for GnuCash.
- Frontend never reads a GnuCash file/database directly.
- `piecash` is used only inside backend service layers.
- App users, auth, book registry, access metadata, and audit logs live in the app metadata DB, not in the GnuCash DB.
- Single-book by default, multi-book-ready later.
- Money must use `Decimal`/string representation. Never use floats for monetary values.
- Auth tokens are stored in httpOnly cookies. Never use localStorage/sessionStorage for auth.
- Do not fake currency conversion. If conversion is not implemented, document limitations.

## Absolute restrictions

- MVP v0.1 must not create, edit, or delete GnuCash entities.
- Do not add banking integrations.
- Do not add CSV/OFX import in the MVP.
- Do not add heavy UI libraries without strong reason.
- Do not add multi-user shared editing.
- Do not promise production security or hosted financial SaaS readiness.
- Do not publish packages or releases unless explicitly requested.

## Post-MVP controlled writes

Controlled write code may exist only as a post-MVP/future feature and must be disabled by default.

If explicitly enabled in a later phase, write features must be narrow, tested, and documented:

- Backup before every GnuCash write.
- Acquire a per-book write lock before writing.
- Audit every routed write attempt, including failures after the request enters the write route.
- Validate before write: split count, zero-sum by currency, valid decimal strings, valid accounts, placeholder rejection, role checks.
- Do not implement direct SQL writes to GnuCash.
- Do not implement delete/import/recurring/account-edit write features unless explicitly requested.

## Security and data rules

Never commit:

- `.env`
- secrets, tokens, credentials, certs, private keys
- real GnuCash files
- real SQLite books
- `app.db`
- backups
- real financial exports or screenshots

Keep `.gitignore` protections for `data/books/*`, `data/backups/*`, `data/app/*`, `.env`, `secrets/`, and credential files. Use test copies of GnuCash books for development and QA.

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

GitHub/CI preflight:

```bash
git --version
gh --version
gh auth status
```

If `gh` is authenticated, use `gh` for GitHub issues/runs. If `gh` is not authenticated but a safe token is explicitly available, configure auth. If GitHub auth is impossible, continue locally and record the blocker.

## Phase workflow

After each phase:

- update `PROJECT_STATUS.md`
- create/update `docs/handoff/phase-N.md`
- run relevant checks
- commit changes
- push to GitHub if auth is available
- create/update a GitHub issue if `gh` is available

## Coding rules

- Keep changes scoped to the current phase.
- Add or update tests for behavior changes and bug fixes.
- Prefer service-layer logic over route-level business logic.
- Keep DTOs explicit and typed.
- Use controlled exceptions and user-safe error messages.
- Maintain mobile-friendly frontend UX and accessible labels.
- Do not introduce telemetry.
- Keep docs honest: pre-alpha, test copies first, no production guarantee.
