# Architecture

> **Status: pre-alpha / MVP in progress.** The current codebase has a SvelteKit frontend, FastAPI backend, app metadata database, authentication foundation, read-only piecash service layer, and read-only accounts/transactions/reports UI. It is still not production-ready.

## Product boundary

`gnucash-web-companion` is a self-hosted, read-only-first companion for existing GnuCash books. GnuCash desktop remains the authoritative editor.

Safety boundaries:

- The MVP does not write to GnuCash books.
- GnuCash files/databases are not used to store web-app users, roles, sessions, UI state, audit logs, or feature flags.
- Application metadata lives in a physically separate SQLite database (`app.db`).
- The default user experience is one configured book.
- Multi-book support is represented in the data model and service boundaries, but a multi-book management UI is not the MVP baseline.
- Collaborative multi-user editing is not a core feature.

## Stack

- **Frontend:** SvelteKit in `apps/web/`
- **Backend:** FastAPI in `apps/api/`
- **GnuCash access:** `piecash`, opened read-only behind `GnuCashBookService`
- **App metadata DB:** SQLite via SQLAlchemy, default `sqlite:////data/app/app.db`
- **Authentication:** JWT issued by the API; frontend stores it in an httpOnly cookie named `access_token`
- **Deployment:** Docker Compose with Caddy reverse proxy

## Runtime components

### Web app (`apps/web`)

Responsibilities:

- Login/logout flow.
- Server-side route protection through SvelteKit hooks.
- Dashboard, account browsing, account detail, transaction list, transaction detail.
- Theme system (light/dark) using CSS custom properties.
- Mobile navigation and PWA manifest foundation.

Important constraints:

- Auth token is not stored in `localStorage` or `sessionStorage`.
- `localStorage` is used only for the UI theme preference (`theme`).
- No service worker is installed; private financial API data is not aggressively cached.
- UI exposes read-only browsing/reporting only.

### API app (`apps/api`)

Responsibilities:

- Owns HTTP API and application services.
- Owns the app metadata DB connection and schema.
- Seeds a default book record from `GNUCASH_DEFAULT_BOOK_PATH`.
- Seeds an admin user during bootstrap when configured through environment variables.
- Enforces authentication and book access checks on read-only book routes.
- Opens GnuCash books read-only through the service layer.
- Returns DTOs/schemas rather than mutable piecash ORM objects.

Implemented router areas:

- `GET /health`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /books`
- `GET /books/{book_id}`
- `GET /books/{book_id}/accounts`
- `GET /books/{book_id}/accounts/tree`
- `GET /books/{book_id}/accounts/{account_id}`
- `GET /books/{book_id}/transactions`
- `GET /books/{book_id}/transactions/{transaction_id}`
- `GET /books/{book_id}/accounts/{account_id}/transactions`
- `GET /books/{book_id}/reports/summary`
- `GET /books/{book_id}/reports/cashflow`
- `GET /books/{book_id}/reports/expenses-by-account`
- `GET /books/{book_id}/reports/recent-transactions`

MVP alias routes exist for the default book where appropriate, but feature code should prefer explicit book-aware services.

### GnuCash book

Responsibilities:

- Source of truth for accounting data.
- Opened read-only by `piecash` in MVP.
- Never stores app metadata.
- Never stores web users, access roles, sessions, audit logs, saved UI state, or feature flags.

### App metadata DB (`app.db`)

Responsibilities:

- Stores web-app metadata separate from the GnuCash book.
- Provides the foundation for default-book routing, auth, and future multi-book support.
- Default Docker location: `/data/app/app.db`.
- Default GnuCash book path: `/data/books/main.gnucash.sqlite`.

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

## Service layer

### `BookRegistryService`

The registry is the app-level source of truth for book records. Feature code should resolve books through this service rather than reading `GNUCASH_DEFAULT_BOOK_PATH` directly.

Key methods:

- `get_default_book()`
- `list_books_for_user(user)`
- `get_book(book_id)`

### `BookAccessService`

Centralizes role checks.

Key methods:

- `get_role(user, book)`
- `assert_can_view(user, book)`
- `assert_can_edit(user, book)`

Role behavior:

- `owner`: can view; reserved for future app metadata administration.
- `editor`: can view; reserved for future app metadata editing.
- `viewer`: can view.

Important MVP note: GnuCash writes remain disabled regardless of role.

### `GnuCashBookService`

The only service that should directly call `piecash`.

Key methods:

- `check_connection()`
- `list_accounts()`
- `get_account(account_id)`
- `get_account_tree()`
- `list_transactions(...)`
- `count_transactions(...)`
- `get_transaction(transaction_id)`
- `get_summary()`
- `get_cashflow()`
- `get_report_summary()`
- `get_expenses_by_account()`
- `get_cashflow_by_month()`

Safety constraints:

- Opens books with `readonly=True`.
- Does not expose save/commit/mutation methods.
- Closes books after reads.
- Converts values into DTOs.
- Represents money as strings externally; no floats for money.

Controlled errors:

- `BookNotFoundError`
- `BookNotConfiguredError`
- `EntityNotFoundError`
- `GnuCashReadError`

## Startup and seeding

On API startup:

1. The API creates the app metadata DB schema if needed.
2. The API seeds one default `Book` from `GNUCASH_DEFAULT_BOOK_PATH` when configured.
3. The API may seed an admin user from `APP_ADMIN_USERNAME` plus `APP_ADMIN_PASSWORD_HASH` or `APP_ADMIN_PASSWORD`.

Bootstrap notes:

- `APP_ADMIN_PASSWORD_HASH` is preferred.
- `APP_ADMIN_PASSWORD` is a development/bootstrap fallback only.
- If book path config is absent, the API should fail controlled book-dependent requests rather than crashing during process startup.

## Data and money handling

- Use `Decimal` internally for money.
- Return money amounts as strings in API DTOs.
- Do not use floats for currency values.
- Transaction lists are paginated.
- Multi-split transaction list items use `counter_account_name = "Split transaction"`.

See `docs/money-model.md` for the current canonical money representation,
CSV export, sign-convention, split-amount, and multi-currency behavior notes.

## Multi-currency limitation

Current basic reports aggregate only values whose commodity matches the book's configured `base_currency`. Non-base-currency splits are excluded rather than converted. Future multi-currency reporting must define an exchange-rate source, date policy, and UI disclosure before combining currencies.

## Architectural decisions

- **Read-only MVP:** safest way to support existing books without corruption or lock contention.
- **Separate app metadata DB:** web-app state must not be mixed into GnuCash data.
- **Service-level book resolution:** avoids hardcoding one global book in feature code.
- **Book-aware APIs:** default single-book UX now, explicit book context for later multi-book support.
- **httpOnly cookie auth:** avoids storing auth tokens in browser storage.
- **No service worker:** avoids accidental offline caching of sensitive financial API responses.
- **No chart library in MVP:** dashboard uses lightweight CSS bars.
- **No collaborative editing core:** the product is a companion for GnuCash desktop, not a replacement accounting system.

## Non-goals

- No write operations to GnuCash in MVP.
- No collaborative multi-user editing as a core feature.
- No app metadata inside the GnuCash book.
- No SaaS-first architecture.
- No production guarantee in pre-alpha.
- No telemetry.
- No npm/PyPI package publishing unless explicitly requested.
