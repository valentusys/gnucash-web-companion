# MVP v0.1

> **Status: MVP in progress / pre-alpha.** The project has working foundations for authentication, read-only GnuCash access, accounts, transactions, reports, and frontend navigation. It still needs integration testing and hardening before any production use.

## Goal

Ship a trustworthy read-only web companion for one existing GnuCash SQL book.

## Product baseline

- **Single-book by default:** one configured book is the normal MVP path.
- **Multi-book-ready later:** data models and APIs carry explicit book context, but multi-book management UI is not the baseline.
- **Read-only first:** GnuCash desktop remains the editor and source of truth.
- **Self-hosted:** users run the app on their own infrastructure.

## In scope

- Configure one GnuCash SQL book path/URI.
- Open/read the book safely through `piecash` with `readonly=True`.
- Show book metadata and health/status.
- Account hierarchy with balances.
- Account detail with related transactions.
- Transaction list with search, filters, and pagination.
- Transaction detail view with splits.
- Dashboard/report views:
  - net worth
  - assets/liabilities
  - income vs expenses
  - cash flow
  - top expense categories
  - recent transactions
- Basic authentication for private self-hosting.
- Token storage in an httpOnly cookie, not localStorage/sessionStorage.
- Separate app metadata DB for users, book registry, and access metadata.
- Docker Compose self-hosting scaffolding.
- Tests around read-only service behavior and API response shapes.

## Out of scope

- Transaction creation/editing/deletion.
- Account creation/editing/deletion.
- Invoice/bill/customer/vendor editing.
- Direct GnuCash schema modification.
- Multi-user collaborative editing.
- Multi-book management UI as a core MVP workflow.
- Import/export of modified books.
- Hosted SaaS offering.
- Telemetry.
- Production-readiness claims.

## Safety requirements

- No writes to the GnuCash book.
- No app metadata inside the GnuCash book.
- Exact amount representation; avoid lossy floats for money.
- Clear UI/documentation indicators that the app is read-only-first.
- Documentation warning users to test against a copy of their book first.
- Sensitive local files ignored by git (`.env`, book files, backups, secrets).
- No service worker or aggressive browser caching of private financial API data.

## Known MVP limitations

- Basic reports aggregate only the configured base currency; non-base-currency splits are excluded rather than converted.
- Docker Compose exists but should still be tested in the target deployment environment.
- Pre-alpha builds are for trusted private networks only.
- The auth foundation is not a substitute for a full production security audit.
