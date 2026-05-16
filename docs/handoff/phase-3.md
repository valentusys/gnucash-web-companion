# Phase 3 Handoff — App Metadata DB and Book Registry Foundation

## Status

Complete.

Phase 3 adds the separate application metadata database foundation and book registry/access services. It does not add UI book selection, piecash integration, GnuCash writes, or collaborative editing.

## Scope delivered

- Configured the app metadata database through `APP_DATABASE_URL`.
- Added SQLAlchemy as the backend ORM dependency.
- Created app metadata models:
  - `User`
  - `Book`
  - `UserBookAccess`
  - `AuditLog`
- Created `BookRegistryService`.
- Created `BookAccessService`.
- Added idempotent default-book seeding from `GNUCASH_DEFAULT_BOOK_PATH`.
- Added controlled warning behavior when the default book path is missing/empty.
- Updated API startup to initialize `app.db` schema and seed the default book.
- Updated architecture documentation.
- Added tests for models, services, role access, and default-book seeding.

## Files changed

Backend:

- `apps/api/app/database.py`
  - SQLAlchemy declarative base.
  - Engine/session factory helpers.
  - SQLite parent directory creation for file-backed app metadata DBs.

- `apps/api/app/models/__init__.py`
  - `User`
  - `Book`
  - `UserBookAccess`
  - `AuditLog`
  - Role constraint for `owner`, `editor`, `viewer`.

- `apps/api/app/services/book_registry.py`
  - `get_default_book()`
  - `list_books_for_user(user)`
  - `get_book(book_id)`

- `apps/api/app/services/book_access.py`
  - `get_role(user, book)`
  - `assert_can_view(user, book)`
  - `assert_can_edit(user, book)`
  - `AccessDenied`

- `apps/api/app/services/seed.py`
  - `seed_default_book(session, path)`
  - Controlled warning when `GNUCASH_DEFAULT_BOOK_PATH` is empty/missing.

- `apps/api/app/main.py`
  - Lifespan startup initializes app metadata schema.
  - Startup seeds the default book from config.

Tests:

- `apps/api/tests/test_models.py`
- `apps/api/tests/test_services.py`
- `apps/api/tests/test_seed.py`

Dependencies:

- `apps/api/requirements.txt`
- `apps/api/pyproject.toml`

Docs:

- `docs/ARCHITECTURE.md`
- `docs/handoff/phase-3.md`

## Data model notes

### `User`

Supports future auth/admin work:

- `id`
- `username`
- `display_name`
- `password_hash`
- `is_admin`
- `created_at`

No default admin user is seeded in Phase 3. That remains an Auth phase concern.

### `Book`

Represents app-known GnuCash books without storing app metadata in the GnuCash book itself:

- `id`
- `name`
- `storage_type`
- `uri_or_path`
- `base_currency`
- `is_default`
- `is_archived`
- `created_at`

Phase 3 seeds one default book from `GNUCASH_DEFAULT_BOOK_PATH`.

### `UserBookAccess`

Stores app-level user/book access in `app.db`, not in GnuCash:

- `user_id`
- `book_id`
- `role`

Allowed roles:

- `owner`
- `editor`
- `viewer`

### `AuditLog`

Placeholder for later audit events:

- `id`
- `user_id`
- `book_id`
- `action`
- `payload_json`
- `created_at`

## Runtime behavior

On FastAPI startup:

1. Create the `app.db` parent directory if needed.
2. Create app metadata tables if needed.
3. Seed one default `Book` from `GNUCASH_DEFAULT_BOOK_PATH`.
4. If the configured path is empty/missing, log a warning and continue without crashing.

Default Docker paths:

- App metadata DB: `/data/app/app.db`
- Default GnuCash book path: `/data/books/main.gnucash.sqlite`

These are intentionally separate.

## Services

### BookRegistryService

Used to resolve book records before feature code touches GnuCash data.

- `get_default_book()` returns the non-archived default book or `None`.
- `list_books_for_user(user)` returns non-archived books with explicit access rows.
- `get_book(book_id)` returns a book by id or `None`.

### BookAccessService

Centralizes role checks.

- `viewer`, `editor`, and `owner` can view.
- `editor` and `owner` can edit app-level book metadata in future phases.
- `viewer` cannot edit.

Important: roles do not enable GnuCash writes in MVP. The MVP remains read-only regardless of role.

## Verification

Command run from `apps/api`:

```bash
pytest -q
```

Result:

```text
34 passed
```

## Intentionally not done

- No frontend UI for book selection.
- No multi-user UI.
- No shared/collaborative editing.
- No piecash connection.
- No GnuCash writes.
- No admin user seeding.
- No auth/session implementation.
- No `/books` API yet; the services are ready for future book-context APIs.

## Next phase recommendation

Phase 4 should connect read-only GnuCash data access behind the book registry boundary:

1. Resolve the default `Book` via `BookRegistryService`.
2. Open the configured book read-only through piecash.
3. Add read-only book/account/transaction endpoints.
4. Keep all GnuCash writes disabled.
5. Add integration tests using a small fixture book.
