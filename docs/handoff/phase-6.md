# Phase 6 Handoff — Book-aware Accounts API and UI

## Status

Complete.

Phase 6 adds authenticated, book-context-aware read-only accounts endpoints and a mobile-friendly SvelteKit accounts UI. It does not add account mutations, transaction lists, or book administration.

## Backend

### Routers

Added:

- `apps/api/app/routers/books.py`
- `apps/api/app/routers/accounts.py`

Registered in:

- `apps/api/app/main.py`

### Endpoints

Book-aware endpoints:

- `GET /books`
- `GET /books/{book_id}`
- `GET /books/{book_id}/accounts`
- `GET /books/{book_id}/accounts/tree`
- `GET /books/{book_id}/accounts/{account_id}`

MVP default-book aliases:

- `GET /accounts`
- `GET /accounts/tree`
- `GET /accounts/{account_id}`

### Auth and access control

All endpoints require auth through the existing `get_current_user` dependency.

Book-scoped endpoints use:

- `BookRegistryService` to resolve books
- `BookAccessService.assert_can_view()` to enforce view access
- `GnuCashBookService` for read-only account data

Routes do not call `piecash` directly.

### Error behavior

- Missing/archived book: `404`
- Missing account: `404`
- Missing default book: `404`
- Unauthorized book access: `403`
- Misconfigured/missing/unreadable GnuCash book: `503`

The GnuCash service errors remain translated at router boundaries:

- `BookNotFoundError` -> `404`
- `EntityNotFoundError` -> `404`
- `BookNotConfiguredError` -> `503`
- `GnuCashReadError` -> `503`

### Tests

Added:

- `apps/api/tests/test_accounts.py`

Coverage includes:

- `/books` requires auth
- book listing only returns books with access
- book details require access
- accounts require auth
- unauthorized book access returns `403`
- account tree shape is correct
- unknown account returns `404`
- MVP aliases use default book
- fake GnuCash book adapter path, without real fixture dependency

## Frontend

### Routes

Added:

- `/accounts`
- `/accounts/[id]`

Protected via `hooks.server.ts` alongside dashboard routes.

### Components

Added:

- `src/lib/components/AccountTree.svelte`
- `src/lib/components/AccountTreeNode.svelte`
- `src/lib/components/AccountBalance.svelte`
- `src/lib/components/Money.svelte`

Added shared types/API helpers:

- `src/lib/api/types.ts`
- `src/lib/api/server.ts`

### UI behavior

`/accounts`:

- loads `/books` and `/accounts/tree`
- hides book selector when only one/default book exists
- keeps selector area adaptable for multiple books later
- displays account tree
- desktop table/tree columns:
  - name
  - type
  - balance
  - currency
- mobile-friendly card/list layout via responsive grid
- placeholder/hidden accounts are visually muted and tagged
- account rows link to account detail

`/accounts/[id]`:

- loads `/books` and `/accounts/{id}`
- shows account metadata:
  - full name
  - type
  - balance
  - currency
  - placeholder
  - hidden
- includes Phase 7 placeholder for transactions

The dashboard now links to `/accounts`.

## Explicit non-goals

Phase 6 does not implement:

- account create/edit/delete
- writes to GnuCash
- direct `piecash` usage in routes
- transaction list/detail UI
- complex book admin UI
- multi-book selector actions beyond future-ready display structure

## Verification

Backend:

```text
pytest -q
82 passed, 1 skipped, 1 warning
```

Frontend:

```text
npm run check
svelte-check found 0 errors and 0 warnings
```

```text
npm run test:auth-routes
auth route checks passed
```

```text
npm run build
vite build OK
```

The warning is the known `piecash` / SQLAlchemy 1.4 deprecation warning from Phase 5.

## Notes for Phase 7

Phase 7 can build transaction routes/UI using the same pattern:

- resolve book via `BookRegistryService`
- enforce `BookAccessService.assert_can_view()`
- use `GnuCashBookService` only, no direct `piecash` in routers
- translate controlled GnuCash errors at the router boundary
