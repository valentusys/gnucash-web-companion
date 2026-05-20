# Phase 198 — Multi-book read-only diagnostics dogfood

Date: 2026-05-20
Status: COMPLETE — synthetic TestClient evidence, no GnuCash writes

## Scope

This dogfood used the backend synthetic multi-book registry fixture only. It exercised app-metadata listing and read-only route access boundaries for multiple independent books without opening private books while listing and without writing any GnuCash data.

## Synthetic setup

The test fixture creates:

- one accessible default book with an existing temporary synthetic path;
- one second accessible independent book with an existing temporary synthetic path;
- one accessible missing-file book;
- one accessible not-configured book;
- one archived book with access metadata;
- one unauthorized book.

All filesystem paths are temporary synthetic test paths and are asserted absent from API/UI-facing metadata.

## Evidence

Command:

```bash
cd apps/api && pytest tests/test_multibook_readonly_access.py tests/test_multi_book_access.py -q
```

Result:

```text
76 passed, 1 existing piecash/SQLAlchemy warning
```

Covered behavior:

- `/books` returns only accessible, non-archived books;
- archived and unauthorized books remain hidden/blocked;
- `uri_or_path` is absent from listed/detail API responses;
- accessible independent books expose safe labels, access-role copy, status severity, storage diagnostics, and read-only action availability;
- missing/not-configured books expose action-required diagnostics and `can_open_read_only_views=false`;
- accounts, account tree/detail, transactions, transaction export/detail/account-scope, scheduled transactions, and reports route families route only to the requested accessible book;
- unauthorized/archived route-family requests are blocked before constructing a GnuCash service;
- missing/not-configured service errors return path-safe `503` messages.

## Browser/UI boundary

Frontend static route checks verify:

- `/books` renders role copy, status severity, storage diagnostics, and no raw `uri_or_path`;
- unavailable/not-configured books do not show read-only data-view links;
- the server-validated book select route refuses unavailable books and redirects to a safe `/books` notice;
- selected-book cookies remain non-secret, server-validated, and never written from client JavaScript;
- no `localStorage`/`sessionStorage` sensitive state is used;
- route links are touch-friendly and bounded for mobile wrapping.

Command:

```bash
cd apps/web && npm run test:auth-routes
```

Result:

```text
auth route checks passed
```

## Safety

- `GNUCASH_WRITES_ENABLED=false` remains default.
- No GnuCash write route was enabled or called.
- No real/private book, app DB, backup, `.env`, token, key, screenshot, CSV/export artifact, or raw filesystem path was committed.
- Listing diagnostics remain app-metadata-only and do not open GnuCash books.
