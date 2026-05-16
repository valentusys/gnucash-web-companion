# PROJECT_STATUS

Last updated: 2026-05-17

## Repository

- GitHub: `valentusys/gnucash-web-companion`
- Local path: `/home/val/gnucash-web-companion`
- Branch: `main`
- Status: pre-alpha / MVP in progress

## Current baseline

Completed through Phase 14:

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

## Phase 14 — MVP read-only scope lock

Status: complete in current working tree pending commit/push.

Goal:

- Reconcile post-MVP Phase 12 controlled write code with the absolute MVP v0.1 read-only constraint.
- Keep controlled write implementation available for future phases, but disabled by default.
- Hide write UI by default.
- Document single-agent phase workflow and absolute constraints in `AGENTS.md`.

Implementation:

- Backend config adds `GNUCASH_WRITES_ENABLED=false` default.
- Write routes return `403` unless writes are explicitly enabled.
- Frontend hides `/transactions/new` entry point unless writes are enabled.
- `/transactions/new` redirects back to `/transactions` unless writes are enabled.
- Docker and `.env.example` carry `GNUCASH_WRITES_ENABLED=false`.

GitHub tooling check:

- `git` is installed.
- `gh` is not installed on this machine, so GitHub issue automation via `gh` is blocked.
- Git push may still work through existing git credentials.

## Standing constraints

- MVP v0.1 is strictly read-only for GnuCash.
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
