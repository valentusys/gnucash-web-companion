# Phase 7 Handoff — Read-only Transaction Browsing

## Status

Complete.

Phase 7 adds authenticated, book-context-aware read-only transaction browsing APIs and SvelteKit transaction pages. It preserves the MVP read-only boundary and does not add transaction mutations.

## Backend

### Router

Added:

- `apps/api/app/routers/transactions.py`

Registered in:

- `apps/api/app/main.py`

### Endpoints

Book-aware endpoints:

- `GET /books/{book_id}/transactions`
- `GET /books/{book_id}/transactions/{transaction_id}`
- `GET /books/{book_id}/accounts/{account_id}/transactions`

MVP default-book aliases:

- `GET /transactions`
- `GET /transactions/{transaction_id}`
- `GET /accounts/{account_id}/transactions`

### Query parameters

List endpoints support:

- `limit` — default `50`, max `200`
- `offset` — default `0`
- `account_id` — optional account filter on book-level transaction lists
- `date_from` — optional `YYYY-MM-DD`
- `date_to` — optional `YYYY-MM-DD`
- `query` — optional description search
- `min_amount` — optional decimal string, compared against absolute displayed split amount
- `max_amount` — optional decimal string, compared against absolute displayed split amount

Response shape:

```json
{
  "items": [],
  "limit": 50,
  "offset": 0,
  "total": 1240
}
```

### Auth and access control

All transaction endpoints require auth through the existing `get_current_user` dependency.

Book-scoped endpoints use:

- `BookRegistryService` through the existing `resolve_viewable_book()` helper
- `BookAccessService.assert_can_view()` through the existing access helper
- `GnuCashBookService` through `transaction_service_for()`

Routes do not import or call `piecash` directly.

### Service-layer updates

Updated:

- `apps/api/app/services/gnucash_book.py`
- `apps/api/app/schemas/gnucash.py`

Added/extended:

- `count_transactions(...)`
- amount range filtering for `list_transactions(...)` and `count_transactions(...)`
- `PaginatedResponse` DTO for list wrappers

Money values remain exact decimal strings. Floats remain rejected by the service layer.

### Error behavior

- Missing/archived book: `404`
- Missing transaction: `404`
- Missing account/entity from GnuCash service: `404`
- Unauthorized book access: `403`
- Misconfigured/missing/unreadable GnuCash book: `503`

### Tests

Added/updated:

- `apps/api/tests/test_transactions.py`

Coverage includes:

- auth required for transaction routes
- default-book MVP aliases
- book-aware transaction routes
- account-scoped transaction routes
- pagination response shape and counts
- query filter
- date range filter
- account filter
- amount range filter
- transaction detail with all splits
- unknown transaction returns `404`
- unauthorized book access returns `403`

## Frontend

### Routes

Added:

- `/transactions`
- `/transactions/[id]`

Updated:

- `/accounts/[id]` now includes paginated account transactions.

Protected in:

- `src/hooks.server.ts`

### Components

Added:

- `src/lib/components/TransactionTable.svelte`
- `src/lib/components/TransactionCard.svelte`
- `src/lib/components/TransactionFilters.svelte`
- `src/lib/components/Pagination.svelte`
- `src/lib/components/TransactionSplits.svelte`

Reused:

- `src/lib/components/Money.svelte`

### UI behavior

`/transactions`:

- SSR-loads `/books`, `/accounts`, and paginated `/transactions`
- shows the active default book
- hides book selector for the single-book MVP but remains ready for multiple books later
- desktop transaction table
- mobile transaction cards
- filters for:
  - `query`
  - `date_from`
  - `date_to`
  - `account_id`
- filters are reflected in URL query parameters
- pagination is reflected in URL query parameters
- selecting a row/card opens transaction detail

`/transactions/[id]`:

- SSR-loads transaction detail
- shows all splits through `TransactionSplits.svelte`

`/accounts/[id]`:

- SSR-loads account metadata and `/accounts/{account_id}/transactions`
- shows paginated account transaction list
- preserves pagination in URL query parameters

## Explicit non-goals

Phase 7 does not implement:

- transaction create/edit/delete
- writes to GnuCash
- direct `piecash` usage in routers
- full dataset loading in the frontend
- complex reports
- book administration UI
- collaborative editing

## Verification

Backend:

```text
pytest -q
107 passed, 1 skipped, 1 warning
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

## Notes for Phase 8

Transaction browsing is now in place. Follow-up phases can add richer reports or transaction detail enhancements, but should keep the same safety boundary:

- service layer only for GnuCash reads
- no direct `piecash` in routers
- no GnuCash writes
- money as exact strings
- pagination for list views
