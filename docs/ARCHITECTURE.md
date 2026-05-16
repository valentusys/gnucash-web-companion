# Architecture

> Status: Phase 3 foundation. The repository now has a runnable SvelteKit/FastAPI skeleton plus a separate app metadata database and book registry services. GnuCash data access via piecash starts in a later phase.

## Product boundary

`gnucash-web-companion` is a self-hosted, read-first companion for existing GnuCash books. GnuCash desktop remains the authoritative editor.

The app is designed to be safe around accounting data:

- The MVP is read-only against GnuCash books.
- GnuCash files/databases are not used to store web-app users, roles, UI state, audit logs, or access metadata.
- Application metadata lives in a physically separate `app.db` SQLite database.
- Multi-book support is prepared at the service/data-model layer, but the default MVP experience is still one configured book.

## Stack

- **Frontend:** SvelteKit in `apps/web/`
- **Backend:** FastAPI in `apps/api/`
- **GnuCash access:** piecash, planned for Phase 4+
- **App metadata DB:** SQLite via SQLAlchemy, default `sqlite:////data/app/app.db`
- **Deployment:** Docker / docker-compose under `docker/`
- **Reverse proxy:** Caddy

## High-level components

### 1. Web app (`apps/web`)

Responsibilities:

- Dashboard, account tree, transaction search, and read-only reports in later phases.
- Hide book selection when only one book exists.
- No transaction/account editing in MVP v0.1.
- No multi-user or book-selection UI in Phase 3.

### 2. API app (`apps/api`)

Responsibilities:

- Owns the HTTP API and application services.
- Owns the app metadata DB connection and schema.
- Resolves the current/default book through `BookRegistryService` instead of hardcoding a global book path in feature code.
- Enforces app-level book access through `BookAccessService` once auth is added.
- Will open GnuCash books read-only through piecash in a later phase.

### 3. GnuCash book

Responsibilities:

- Source of truth for accounting data.
- Opened read-only for MVP.
- Never stores app metadata.
- Never stores web users, access roles, sessions, audit logs, saved UI state, or feature flags.

### 4. App metadata DB (`app.db`)

Responsibilities:

- Stores web-app metadata separate from the GnuCash book.
- Provides the foundation for future multi-book routing and user-book access.
- Default location in Docker: `/data/app/app.db`.
- Default GnuCash book path in Docker: `/data/books/main.gnucash.sqlite`.

Current models:

- `User`
  - `id`
  - `username`
  - `display_name`
  - `password_hash`
  - `is_admin`
  - `created_at`

- `Book`
  - `id`
  - `name`
  - `storage_type`
  - `uri_or_path`
  - `base_currency`
  - `is_default`
  - `is_archived`
  - `created_at`

- `UserBookAccess`
  - `user_id`
  - `book_id`
  - `role`: `owner`, `editor`, or `viewer`

- `AuditLog`
  - `id`
  - `user_id`
  - `book_id`
  - `action`
  - `payload_json`
  - `created_at`

## Book registry and access services

### `BookRegistryService`

The registry is the app-level source of truth for book records. Feature code should use this service rather than reading `GNUCASH_DEFAULT_BOOK_PATH` directly.

Methods:

- `get_default_book()`
- `list_books_for_user(user)`
- `get_book(book_id)`

### `BookAccessService`

The access service centralizes role checks and avoids scattering role comparisons across API handlers.

Methods:

- `get_role(user, book)`
- `assert_can_view(user, book)`
- `assert_can_edit(user, book)`

Current role behavior:

- `owner`: can view and edit app-level book metadata in the future.
- `editor`: can view and edit app-level book metadata in the future.
- `viewer`: can view, cannot edit.

Important MVP note: GnuCash writes remain disabled regardless of role. `editor` and `owner` are stored now only so future app metadata permissions do not require a schema rewrite.

## Startup and seeding

On API startup:

1. The API creates the app metadata DB schema if needed.
2. The API seeds one default `Book` from `GNUCASH_DEFAULT_BOOK_PATH`.
3. If `GNUCASH_DEFAULT_BOOK_PATH` is empty or missing, startup logs a controlled warning and skips default-book seeding.

The seed operation is idempotent: an existing default book is reused rather than duplicated.

Auth is deferred to a later phase. The schema supports an admin user, but Phase 3 does not seed one by default.

## Initial API direction

Current implemented endpoint:

- `GET /api/health` through the proxy, backed by API `GET /health`

Planned read-only endpoints:

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

Future book-context APIs should resolve a `Book` through `BookRegistryService` first, then pass an explicit book context into GnuCash read services.

## Multi-book readiness

The baseline is **single-book by default + multi-book-ready later**, not family/collaborative access as the core product thesis.

Phase 3 prepares for multi-book by introducing:

- `Book` records in `app.db`
- `UserBookAccess` records in `app.db`
- `BookRegistryService`
- `BookAccessService`
- default-book seeding from config

What Phase 3 intentionally does not add:

- Book picker UI
- Multi-user UI
- Shared editing
- GnuCash write paths
- piecash integration

## Architectural decisions

- **Separate app metadata DB:** web-app state must not be mixed into GnuCash data.
- **Read-only MVP:** safest way to support existing books without corruption or lock contention.
- **Service-level book resolution:** avoids baking a global singleton book into future APIs.
- **Roles stored early:** enables future auth/access work without changing the core schema.
- **No collaborative editing core:** the product is a companion for GnuCash desktop, not a replacement multi-user accounting system.

## Non-goals

- No write operations to GnuCash in MVP.
- No collaborative multi-user editing as a core feature.
- No app metadata inside the GnuCash book.
- No SaaS-first architecture.
- No book-selection UI until there is real multi-book behavior to support it.
- No piecash integration before the app metadata foundation is stable.
