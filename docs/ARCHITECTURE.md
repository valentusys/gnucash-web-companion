# Architecture

> Status: placeholder / phase-1 foundation. Architecture will be validated during Phase 2 before application code is implemented.

## Product boundary

`gnucash-web-companion` is a self-hosted read-first companion for existing GnuCash books. GnuCash desktop remains the authoritative editor.

## Planned stack

- **Frontend:** SvelteKit in `apps/web/`
- **Backend:** FastAPI in `apps/api/`
- **GnuCash access:** piecash
- **App metadata DB:** separate SQLite database, not the GnuCash book
- **Deployment:** Docker / docker-compose under `docker/`

## High-level components

1. **Web app (`apps/web`)**
   - Dashboard, account tree, transaction search, and read-only reports.
   - No transaction/account editing in MVP v0.1.

2. **API app (`apps/api`)**
   - Read-only HTTP API over one configured GnuCash book.
   - Uses exact amount representation; no lossy floats for money.

3. **GnuCash book**
   - Source of truth.
   - Opened read-only for MVP.
   - Never stores app metadata.

4. **App metadata DB**
   - Stores UI preferences, saved filters, cache/index metadata, and future non-accounting state.
   - Must be physically and logically separate from the GnuCash book.

## Initial API direction

Read-only endpoints only:

- `GET /api/health`
- `GET /api/book`
- `GET /api/book/summary`
- `GET /api/accounts`
- `GET /api/accounts/{account_guid}`
- `GET /api/accounts/{account_guid}/splits`
- `GET /api/transactions/{transaction_guid}`
- `GET /api/search`
- `GET /api/reports/net-worth`
- `GET /api/reports/income-expense`
- `GET /api/reports/cash-flow`

## Multi-book readiness

MVP exposes one configured default book. Internally, code should avoid unnecessary global singleton assumptions so a future `BookContext`/book registry can be added without a rewrite.

## Non-goals

- No write operations in MVP.
- No collaborative multi-user editing as a core feature.
- No app metadata in the GnuCash book.
- No SaaS-first architecture.
