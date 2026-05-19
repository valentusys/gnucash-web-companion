# Book switcher read-only model

Last updated: 2026-05-20 (Phase 164)

## Purpose

The web UI can show multiple configured GnuCash books, but each book remains an independent read-only accounting ledger. The book switcher and `/books` page only choose which already-configured accessible book to view in this browser session.

This is not a collaborative editor, family wallet, file browser, upload workflow, or registry-management UI.

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

## Safety boundaries

- `/books` lists app metadata for accessible books only.
- The metadata listing does not open GnuCash data.
- Raw `uri_or_path` values and private filesystem paths are not returned by the book metadata API and are not rendered by the web UI.
- Missing configured local book paths are reported only as safe operator diagnostics (`missing_file`) with redacted paths.
- No upload, delete, default-book change, registry edit, direct file browser, collaborative workflow, or GnuCash write is exposed.
- `GNUCASH_WRITES_ENABLED=false` remains the default.

## Tests

Phase 164 pins this behavior through:

- backend multi-book access tests for unauthorized/archived/missing/not-configured book metadata and private path redaction;
- frontend static route checks for selected-book recovery classification, `/books` review redirect, safe notices, and absence of browser storage for book-sensitive state.
