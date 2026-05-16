# Phase 5 Handoff — Read-only GnuCash Book Service Layer

## Status

Complete.

Phase 5 adds the first direct GnuCash SQL book integration through `piecash`, behind a strictly read-only service layer. No FastAPI routes or frontend UI were added; Phase 6 remains responsible for Books + Accounts API/UI.

## Scope delivered

### Dependencies

Added backend dependencies:

- `piecash>=1.2`
- `SQLAlchemy>=1.4,<1.5`

`piecash` currently depends on SQLAlchemy 1.4 APIs, so the backend dependency is pinned below 1.5.

### Controlled errors

Created `apps/api/app/services/gnucash_exceptions.py`:

- `BookNotFoundError`
- `BookNotConfiguredError`
- `EntityNotFoundError`
- `GnuCashReadError`

These are intended for Phase 6 routes to translate into stable HTTP responses.

### DTO schemas

Created `apps/api/app/schemas/gnucash.py`:

- `MoneyDTO`
- `AccountDTO`
- `AccountTreeNodeDTO`
- `TransactionSplitDTO`
- `TransactionListItemDTO`
- `TransactionDetailDTO`
- `BookSummaryDTO`
- `CashflowDTO`

Money is represented as string values externally. The service uses `Decimal` internally and rejects floats in the money formatter.

### Service layer

Created `apps/api/app/services/gnucash_book.py` with `GnuCashBookService(book_config)`.

Supported methods:

- `check_connection()`
- `list_accounts()`
- `get_account(account_id)`
- `get_account_tree()`
- `list_transactions(account_id=None, date_from=None, date_to=None, query=None, limit=50, offset=0)`
- `get_transaction(transaction_id)`
- `get_summary()`
- `get_cashflow(date_from, date_to)`

Supporting mappers/utilities:

- `format_money(value)`
- `account_full_name(account)`

## Read-only boundary

The service opens books only through:

```python
# filesystem path
piecash.open_book(uri_or_path, readonly=True)

# SQL connection URI
piecash.open_book(uri_conn=uri_or_path, readonly=True)
```

The service does not expose or call:

- `save`
- `commit`
- object creation APIs
- mutation APIs
- delete APIs

Each public operation opens the book, maps data to DTOs, and closes the book. Routes/UI should consume DTOs only and should not receive raw mutable piecash ORM objects.

## Book config contract

`GnuCashBookService` accepts either:

- app metadata `Book` model-like object with `uri_or_path` and optional `base_currency`
- dict-like config with `uri_or_path` and optional `base_currency`

Examples:

```python
service = GnuCashBookService(book)
service = GnuCashBookService({"uri_or_path": "/data/books/main.gnucash.sqlite", "base_currency": "SEK"})
```

## Mapping decisions

### Accounts

`AccountDTO.full_name` is built by walking parent accounts and joining names with `:`.

`AccountDTO.balance` prefers:

1. `account.get_balance()` if available
2. `account.balance` / `account.current_balance` if present
3. sum of account splits as fallback

### Transactions

`TransactionListItemDTO` selects the split relevant to the requested `account_id`. If no account is requested, it uses the first split as the list context.

Counter-account logic:

- two splits: the other split's account full name
- more than two splits: `Split transaction`
- one split: empty string

Pagination is applied after filtering and sorting. `limit` is clamped to `0..500`; `offset` is clamped to `>=0`.

### Cashflow

`get_cashflow()` currently provides a basic read-only aggregate over `INCOME` and `EXPENSE` account splits in the date range. Income account splits are treated as inflow; expense account splits are treated as outflow, with negative values treated as reversals/refunds. This is intentionally minimal and should be refined in later reporting phases.

## Tests

Added `apps/api/tests/test_gnucash_book.py`.

Coverage includes:

- money formatting without floats
- full account name mapping
- missing configured book path
- missing book file
- read-only `piecash.open_book(..., readonly=True)` call
- account DTO mapping
- account tree mapping
- transaction list mapping
- split transaction counter-account label
- filtering, pagination, query
- transaction detail mapping
- summary
- basic cashflow
- optional fixture-book connection test, skipped unless `tests/fixtures/sample.gnucash` exists

Verification result:

```text
58 passed, 1 skipped, 1 warning
```

The warning comes from `piecash` using SQLAlchemy 1.4 APIs and is expected with the current dependency stack.

## Explicit non-goals

Phase 5 does not implement:

- FastAPI routes
- frontend UI
- account/transaction pages
- writes to GnuCash
- GnuCash object creation/edit/delete
- multi-user editing
- collaborative accounting

## Next phase

Phase 6 should use:

- `BookRegistryService` to resolve the default book
- `GnuCashBookService` for read-only DTOs
- controlled errors from `gnucash_exceptions.py` for HTTP error mapping

Suggested Phase 6 endpoints/UI:

- books/default status
- accounts list/tree API
- basic dashboard account list UI
