# Product Positioning: gnucash-web-companion

Reviewed on: 2026-05-16

## Product thesis

`gnucash-web-companion` is a **modern self-hosted web companion for existing GnuCash books**.

It is not a replacement for GnuCash desktop. It is not a hosted personal-finance SaaS. It is not a collaborative accounting system.

The product should make it safe and pleasant to open a browser on a private self-hosted instance and answer questions like:

- What is my current financial position?
- What happened in this account?
- Where did money flow this month?
- Which transactions match this search/filter?
- What changed recently?
- Which reports do I need to review before opening GnuCash desktop?

The first release should build trust through **read-only visibility** before attempting any writes.

## Positioning statement

For GnuCash users who want a modern private web interface over their existing books, `gnucash-web-companion` is a self-hosted read-first companion that provides dashboards, account browsing, transaction search, and reports without taking ownership of the accounting book.

Unlike existing web/mobile attempts, it combines a modern SvelteKit UI, a FastAPI API, server-side piecash integration, a separate app metadata DB, and an explicit safety model that treats the GnuCash book as the source of truth.

## Target users

Primary users:

- Individual GnuCash users who self-host services.
- Power users who want browser/mobile visibility but still trust GnuCash desktop for authoritative editing.
- Households or small personal finance setups where one person maintains the book and wants better read access from other devices.
- Users who want modern dashboards over existing GnuCash data without uploading the file to a SaaS.

Secondary future users:

- Users with several separate books who want one companion UI to switch between them.
- Users who want limited, carefully designed write helpers after read-only behavior is proven.

## Non-users

This product is not primarily for:

- People who want a cloud-hosted personal finance SaaS.
- Teams needing simultaneous collaborative accounting edits.
- Businesses that need full AR/AP workflows in the web app.
- Users who want to abandon GnuCash desktop entirely.
- Users who expect mobile-first transaction entry as the first/core feature.

## Differentiation

### Compared with `joshuabach/gnucash-web`

`gnucash-web` is a simple Flask/piecash mobile write companion. `gnucash-web-companion` should be a modern read-first server app with stronger product separation between browsing/reporting and future writes.

Key difference: `gnucash-web-companion` does not start with add/edit/delete transaction flows.

### Compared with `GnuDash`

`GnuDash` is a rich browser-local dashboard/editor using Next.js, SQLite WASM, OPFS, and optional Postgres server mode. `gnucash-web-companion` should be a self-hosted server-side app using FastAPI and piecash.

Key difference: the GnuCash book stays on the server; app metadata stays separate; the MVP is read-only.

### Compared with `gnucash-rest`

`gnucash-rest` is an integration API around native GnuCash Python bindings with broad write operations. `gnucash-web-companion` should expose a product API designed for its own UI first, with read-only resources and later versioned expansion.

Key difference: no broad mutable accounting API in MVP.

### Compared with `GnuCashew`

`GnuCashew` aims toward a web accounting system compatible with GnuCash data files. `gnucash-web-companion` should remain a companion, not a replacement accounting engine.

### Compared with `gnucash-2-web`

`gnucash-2-web` uses Jam.py/low-code direct database access. `gnucash-web-companion` should avoid direct low-code mutation of GnuCash tables and avoid any app behavior that might alter the GnuCash schema.

### Compared with `gnucash-browser`

`gnucash-browser` validates read-only web access, but as a static generated site. `gnucash-web-companion` should provide an interactive, live, self-hosted app.

## MVP scope

The MVP should be **read-only**.

Recommended MVP features:

- Connect to one configured GnuCash book.
- Open book in read-only mode wherever supported.
- Display book metadata and last-open/last-index status.
- Account hierarchy with balances.
- Account detail page with splits/transactions.
- Transaction detail page.
- Search/filter transactions by date, account, description, memo, amount, commodity/currency.
- Dashboard summary:
  - net worth
  - income vs expenses
  - cash flow over time
  - top expense categories
- Basic reporting endpoints backing the UI.
- Privacy mode for UI number blurring.
- App metadata DB for user preferences, saved filters, UI state, and cached/index metadata only.
- Docker/self-host deployment.
- Clear warnings that GnuCash desktop remains the authoritative editor.

## Explicit anti-goals

- No collaborative multi-user editing as a core feature.
- No write operations in MVP.
- No transaction creation/edit/delete in MVP.
- No invoice/bill/customer/vendor mutation in MVP.
- No direct modification of GnuCash schema.
- No app metadata stored inside the GnuCash book.
- No attempt to replace GnuCash desktop.
- No SaaS-first architecture.
- No forced browser-upload model as the primary architecture.
- No broad public integration API before the product API is stable.
- No “family shared editing of one book” baseline.
- No multi-book UX in MVP unless it falls out naturally from internal boundaries.

## Why MVP must be read-only

Read-only is not a lack of ambition; it is the safety foundation.

Reasons:

1. **Accounting data is high-trust data.** A small bug can corrupt balances, reports, reconciliations, lots, invoices, or hidden invariants.
2. **GnuCash writes are subtle.** Two-split transaction entry is only the simplest case. Real books contain scheduled transactions, lots, commodities, prices, reconciliations, business objects, multi-currency, and precision constraints.
3. **Concurrency and locking matter.** Desktop GnuCash and web access can collide. A web app must understand read/write locks before writing.
4. **Numeric precision matters.** GnuCash stores rational values. UI/reporting must not casually convert money to floating-point approximations.
5. **Deployment mistakes become dangerous with writes.** Bad auth, reverse proxy mistakes, exposed DB ports, or CSRF bugs are much worse when writes exist.
6. **Backups and recovery need design.** Before writes, the app needs backup hooks, restore guidance, dry-run behavior, audit logs, and possibly write transaction logs.
7. **Trust must be earned.** Users will only allow a web app to write their books after they trust it to read, calculate, and present data accurately.

Therefore, the MVP should prove:

- correct opening/parsing
- correct balances
- correct split/transaction rendering
- correct date/range filters
- correct report calculations
- safe deployment
- clear boundaries between GnuCash data and app metadata

Only after that should write capabilities be considered.

## Why single-book by default + multi-book later

The baseline should be **single-book by default, multi-book-ready later**.

This is different from “family access to one shared book.”

Reasons:

1. **Single-book matches the first real use case.** Most self-hosted GnuCash users have one primary personal/household book.
2. **It reduces configuration and safety surface.** One configured book means fewer permission, path, locking, cache, and metadata mapping problems.
3. **It keeps MVP understandable.** The user installs the app, points it at a book, and gets dashboards.
4. **It avoids implying collaborative editing.** “Family access to one shared book” quickly leads to roles, permissions, concurrent writes, audit trails, conflict resolution, and blame/accountability questions.
5. **Multi-book is an architectural boundary, not an MVP UI requirement.** The backend should avoid hard-coding global singleton assumptions, but the UI does not need book management yet.
6. **Future multi-book support is cleaner if designed as separate book registrations.** Each book can have its own path/connection, read-only capability status, cache/index state, metadata namespace, and permissions later.

Recommended wording:

> MVP supports one configured default book. Internally, code should use a `BookContext`/book identifier boundary where cheap, so future multi-book support does not require a rewrite. The product should not market shared family editing or multi-user collaboration as a core capability.

## Architectural decisions for phase 0 / MVP

1. **Frontend:** SvelteKit.
   - Reason: modern app UX, fast dashboards, component-based UI, good self-host story.

2. **Backend:** FastAPI.
   - Reason: clear typed API, Python ecosystem, async-friendly server, OpenAPI docs.

3. **GnuCash access:** piecash.
   - Reason: purpose-built Python access to GnuCash SQL books and familiar to existing GnuCash web projects.

4. **MVP data mode:** read-only.
   - Reason: safety, trust, correctness, and reduced deployment risk.

5. **App metadata DB:** separate from GnuCash book.
   - Reason: never pollute or migrate the user’s accounting file for UI state/preferences.

6. **Default book model:** one configured book.
   - Reason: simplest safe deployment; matches first use case.

7. **Multi-book readiness:** internal abstraction only at first.
   - Reason: avoid rewrite later without expanding MVP scope.

8. **API shape:** resource-oriented read endpoints using GnuCash GUIDs.
   - Reason: aligns with GnuCash identity model and lessons from `gnucash-rest`.

9. **Writes:** explicitly out of scope until a later safety phase.
   - Reason: requires backups, audit log, lock handling, permissions, validation, and recovery design.

10. **Deployment:** private self-host first.
    - Reason: user owns sensitive financial data; no SaaS dependency.

## API positioning for MVP

The API should be product-first and read-only. It should not initially be marketed as a general-purpose GnuCash API.

Suggested first API shape:

- `GET /api/health`
- `GET /api/book`
- `GET /api/book/summary`
- `GET /api/accounts`
- `GET /api/accounts/{account_guid}`
- `GET /api/accounts/{account_guid}/splits`
- `GET /api/transactions/{transaction_guid}`
- `GET /api/search?q=...`
- `GET /api/reports/net-worth`
- `GET /api/reports/income-expense`
- `GET /api/reports/cash-flow`

Guidelines:

- Use GnuCash GUIDs where available.
- Return exact numeric values as structured values, not lossy floats.
- Include commodity/currency metadata with amounts.
- Keep report endpoints deterministic and reproducible.
- Add pagination and date filters early.
- Do not add `POST`, `PUT`, `PATCH`, or `DELETE` until write safety is designed.

## UI positioning

Borrow from GnuDash, but keep MVP focused.

Recommended UI patterns:

- Dashboard landing page with cards and charts.
- Left navigation for Overview, Accounts, Transactions/Search, Reports, Settings.
- Account tree with balances and account types.
- Drill-down from report charts into transaction lists.
- Transaction list with filters, saved views later.
- Transaction detail drawer/page.
- Privacy mode toggle to blur amounts.
- Clear book/read-only status indicator.
- “Open in GnuCash desktop” documentation/handoff rather than web editing.

Avoid in MVP:

- Inline transaction editing.
- Account creation/editing forms.
- Export modified book flows.
- Server sync between multiple active writers.
- Complex budget/investment editing.

## Safety model

The product should communicate safety directly:

- The configured GnuCash book is the source of truth.
- The app opens and reads the book; it does not mutate it in MVP.
- App metadata is stored separately.
- Users should keep normal GnuCash backups.
- The UI should show whether the current book is read-only, stale, inaccessible, or indexed.
- If a future write mode is added, it must be opt-in and guarded by backups, locks, audit logs, validation, and recovery docs.

## Success criteria for phase 1

Phase 1 is ready to begin when we can turn this positioning into an implementation plan that preserves the phase-0 decisions:

- Read-only book opening via piecash is validated against a sample book.
- Exact numeric representation approach is chosen.
- SvelteKit/FastAPI project skeleton is planned.
- Book configuration model is designed.
- App metadata DB boundaries are defined.
- Initial API contract is written before UI implementation.
- Test fixtures/sample books are selected.
