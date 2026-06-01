# Book switcher read-only model

Last updated: 2026-06-01 (autonomous long run #13)

## Purpose

The web UI can show multiple configured GnuCash books, but each book remains an independent read-only accounting ledger. The book switcher and `/books` page choose which accessible book to view in this browser session and let admins manage app metadata for already-mounted copied/test SQLite books.

This is not a collaborative editor, family wallet, file browser, upload workflow, or GnuCash accounting editor. Registry actions change only the app metadata registry; they do not upload, copy, open for accounting reads, edit, or delete GnuCash book files.

## Selected-book state

- The selected book is stored only as the non-secret `selected_book_id` cookie.
- The cookie is scoped to the web app path and uses `SameSite=Lax`.
- The selected-book state is not stored in `localStorage`, `sessionStorage`, app profiles, or the GnuCash book.
- Invalid, stale, archived, or no-longer-accessible selected-book cookies are treated as recoverable browser context drift, not as permission to expose hidden books.

## Recovery behavior

When the authenticated user has an invalid or stale selected-book cookie:

1. the server asks the backend only for the authenticated `/books` list;
2. unauthorized and archived books remain hidden or blocked by the backend;
3. the UI selects the first safe fallback in this order:
   - selected accessible book, if still valid;
   - accessible default book;
   - first accessible configured book;
4. the cookie is replaced with that accessible fallback, or cleared when no accessible books exist;
5. protected read-only views redirect to `/books?book_context=...` so the user can review the current/default labels before opening dashboard/accounts/transactions/scheduled views.

The `/books` page shows a safe recovery notice for:

- invalid selected-book cookie;
- stale/no-longer-accessible selected-book cookie;
- no accessible books.

## Admin metadata registration

Admins can register an already-mounted local SQLite copied/test GnuCash book from `/books`.

Registration rules:

- The form records display name, optional base currency, mounted local path, and optional default flag in the app metadata database.
- The API accepts only local `sqlite` targets. URI sources and upload flows are rejected.
- The mounted path must exist, be a file, be readable as SQLite, and contain core GnuCash SQLite schema marker tables.
- The schema check is read-only and inspects table names only; it does not read account names, transactions, memos, amounts, or other private accounting values.
- Validation errors are generic and never echo the submitted private path.
- The registering admin receives owner metadata access to the registered book.

## Safe storage diagnostics

The `/books` metadata listing performs bounded diagnostics for configured local SQLite paths:

- missing files are reported as `missing_file` with operator-only next actions and no raw path;
- readable local SQLite files that do not contain core GnuCash schema markers are reported as `invalid_gnucash_schema`;
- invalid-schema books are blocked from read-only data routes before the backend attempts to open them through the GnuCash service layer;
- valid local SQLite GnuCash-looking books are reported as `available`.

These diagnostics inspect only SQLite table names and never read account names, transactions, memos, amounts, or other private accounting values.

## Admin registry management

Admins can use `/books` to perform two metadata-only actions for registered books:

- Set as default: changes the app metadata fallback book for the installation. It does not write to the GnuCash file.
- Remove from registry: archives/removes the app metadata entry from normal listings. It never deletes the underlying GnuCash file.

Non-admin users do not receive these management actions and backend routes reject them with `403`.

## Safety boundaries

- `/books` lists app metadata for accessible books only.
- The metadata listing does not open GnuCash accounting data.
- Raw `uri_or_path` values and private filesystem paths are not returned by the book metadata API and are not rendered by the web UI.
- Missing configured local book paths are reported only as safe operator diagnostics (`missing_file`) with redacted paths.
- No upload, direct file browser, collaborative workflow, accounting-data edit, or GnuCash file deletion is exposed.
- Registry management is admin-only and metadata-only.
- `GNUCASH_WRITES_ENABLED=false` remains the default.

## Tests

This behavior is pinned through:

- backend multi-book access tests for unauthorized/archived/missing/not-configured book metadata and private path redaction;
- backend registration tests for admin-only local SQLite GnuCash schema validation and path-safe rejection of missing, non-SQLite, and non-GnuCash-looking targets;
- backend management tests for admin-only set-default and remove-from-registry behavior, including proof that registry removal does not delete the underlying file;
- frontend static route checks for selected-book recovery classification, `/books` review redirect, safe notices, and absence of browser storage for book-sensitive state;
- Svelte type/catalog checks for the `/books` management UI and EN/RU strings.
