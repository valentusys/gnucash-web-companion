# Book switcher read-only model

Phase 50 stabilizes the existing multi-book UI foundation without turning the app into collaborative accounting or a book-management system.

## Scope

The book switcher is a read-only navigation aid for books that the signed-in user can already access through the app metadata database.

It does:

- show the current book clearly in the authenticated app shell;
- list only books returned by `GET /books`, which is already scoped by `UserBookAccess`;
- show read-only metadata/status for accessible books, including base currency, storage type, access role, access status, current/default markers, safe storage diagnostics, private-path-redaction copy, and explicit no-management-action copy;
- switch the active book by storing a non-secret `selected_book_id` cookie;
- preserve the current route and query string on switch so list/filter pages stay book-aware;
- provide `/books` safe links that first verify the target book against the authenticated accessible list, then set `selected_book_id` and redirect only to approved read-only views (`/dashboard`, `/accounts`, `/transactions`, `/scheduled`);
- fall back to the accessible default book, then the first accessible book, when the selected cookie is invalid or points to a book no longer visible to the user.

It does not:

- upload or import GnuCash books;
- create, edit, delete, or register books through the UI;
- grant access to unauthorized books;
- imply shared-wallet, family-wallet, or collaborative editing semantics;
- change `GNUCASH_WRITES_ENABLED=false` or expand controlled-write scope.

## Access boundary

The frontend never trusts `selected_book_id` as authorization. Each server-side page load resolves the selected book against the accessible list from `GET /books` before constructing book-aware API routes.

The backend remains authoritative:

- `GET /books` returns only books visible to the current user and includes only app metadata/status for those visible books (`access_role`, `read_only`, `access_status`, safe `status`/`storage_diagnostics`, and an empty `management_actions` list), without opening a GnuCash file or returning raw `uri_or_path` values;
- book-aware account, transaction, report, scheduled metadata, and export endpoints resolve the book and enforce `UserBookAccess`;
- `/books/{bookId}/select` verifies the requested book id against the authenticated `GET /books` result before setting the selected-book cookie;
- unauthorized or archived book ids return `403`/`404` or are excluded from the visible list.

## Fallback behavior

If the selected book cookie is missing, malformed, stale, or points to a book outside the user's accessible list, the app resolves the active book in this order:

1. selected accessible book;
2. accessible default book;
3. first accessible book;
4. no active book if the user has no book access.

When fallback occurs, the server refreshes or clears the `selected_book_id` cookie so subsequent page loads stay aligned with the visible read-only context.

## Storage diagnostics

The `/books` metadata response may report safe operator-facing storage diagnostics:

- `available` — a local SQLite path is configured and exists from this runtime; listing still does not open the GnuCash data.
- `missing_file` — a local SQLite path is configured but not found from this runtime; operators should check host/container mounts and app metadata outside the web UI.
- `not_configured` — no book location is configured in app metadata.
- `remote_or_unchecked` — non-local/URI storage is configured but not validated by the metadata listing.

The diagnostics intentionally return safe summaries and next actions only. They must not expose raw filesystem paths, private hostnames, credentials, account names, descriptions, memos, balances, screenshots, or exports.

## Archive and visibility semantics

Archived books are not visible in the read-only switcher because `GET /books` returns only non-archived books that the signed-in user can view. Direct requests for archived books are treated as not found by the backend route resolver before any GnuCash data is opened.

The current app has no book-management UI. Any future archive/unarchive or visibility-management work must keep these semantics explicit and add regression tests before it is presented as safe multi-book administration.

## Safety position

Multi-book support means multiple independent GnuCash books with scoped access. GnuCash Desktop remains the authoritative editor for each book. Phase 50 does not add book upload, book registration UI, write capability, import/sync, or collaborative editing.
