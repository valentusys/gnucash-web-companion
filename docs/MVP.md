# MVP v0.1

> Status: planned. This document defines the read-only MVP boundary.

## Goal

Ship a trustworthy read-only web companion for one existing GnuCash book.

## In scope

- Configure one GnuCash book.
- Open/read the book safely.
- Show book metadata and health/status.
- Account hierarchy with balances.
- Account detail with splits/transactions.
- Transaction detail view.
- Search and filter transactions.
- Dashboard/report views:
  - net worth
  - income vs expenses
  - cash flow
  - top expense categories
- Privacy mode for amount blurring.
- Separate app metadata DB.
- Docker-based self-hosting docs.
- Tests that prove read operations do not mutate fixture books.

## Out of scope

- Transaction creation/editing/deletion.
- Account creation/editing/deletion.
- Invoice/bill/customer/vendor editing.
- Multi-user collaborative editing.
- Multi-book management UI.
- Import/export of modified books.
- Hosted SaaS offering.

## Safety requirements

- No writes to the GnuCash book.
- No app metadata inside the GnuCash book.
- Exact amount representation; avoid lossy floats for money.
- Clear UI indicator that the book is read-only.
- Documentation warning users not to expose early builds publicly.
