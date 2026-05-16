# Phase 0 Handoff: gnucash-web-companion

Reviewed on: 2026-05-16

## Status

Phase 0 competitive/product positioning research is complete.

Artifacts:

- `docs/COMPETITIVE_REVIEW.md`
- `docs/PRODUCT_POSITIONING.md`
- `docs/handoff/phase-0.md`

No application code was written in this phase.

## What was researched

Reviewed projects:

1. `joshuabach/gnucash-web`
2. `QuirkyTurtle94/GnuDash`
3. `loftx/gnucash-rest`
4. `lorimark/gnucashew-dev` / GnuCashew
5. `jam-py-v5/gnucash-2-web`
6. `phjardas/gnucash-browser`

Research sources included repository READMEs, project structure, package/dependency files, GitHub metadata, and visible open issues.

## Core decision

Build `gnucash-web-companion` as a **modern self-hosted read-first companion for existing GnuCash books**.

It should not be a GnuCash replacement, a SaaS, or a collaborative multi-user accounting editor.

## Decisions made

### 1. MVP is read-only

Reason: write-capable GnuCash apps immediately inherit accounting correctness, locking, backup, auth, precision, and recovery risks.

MVP should prove the app can safely and accurately:

- open/read a configured book
- show account hierarchy
- show balances
- list transactions/splits
- search/filter
- produce dashboard/report calculations

### 2. Default is single-book

Reason: one configured default book matches the first user need and keeps deployment/configuration safe.

### 3. Multi-book-ready later, not multi-book-first

Reason: avoid hard-coded singleton internals where cheap, but do not build book management UI in MVP.

Recommended internal boundary: `BookContext` or equivalent book identifier abstraction.

### 4. App metadata DB is separate

Reason: UI preferences, saved filters, cache/index status, user settings, and future metadata should not modify the GnuCash book.

### 5. SvelteKit + FastAPI + piecash remains the target stack

Reason: this differentiates the project from Flask template apps, browser-WASM dashboards, native-binding REST wrappers, C++ Wt, and low-code direct DB apps.

### 6. API is product-first and read-only

Reason: avoid prematurely creating a general mutable GnuCash API.

Suggested first endpoints:

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

### 7. Collaborative multi-user editing is an anti-goal

Reason: it implies permissions, conflict resolution, concurrent writes, audit trails, and a much bigger product than a safe web companion.

## Lessons to carry forward

### From `gnucash-web`

- Companion framing is correct.
- Mobile-friendly account/transaction browsing matters.
- Single-book simplicity is valuable.
- Self-host deployment needs clear Docker and config docs.
- Write support requires strong warnings and safety design.

### From `GnuDash`

UI patterns to borrow:

- Dashboard-first navigation.
- Account tree with balances/type indicators.
- Drill-down reports.
- Sankey-style flow diagrams.
- Net-worth/cash-flow/income-expense/investment report separation.
- GnuCash-style register view, but read-only in MVP.
- Privacy mode.
- Demo/sample mode.

Risks to remember:

- Rich UI can quickly become a full accounting engine.
- Numeric precision must be exact, not “good enough.”
- Editing/export/sync are large features, not MVP details.

### From `gnucash-rest`

API ideas to borrow:

- Resource-oriented endpoints.
- GUIDs in paths.
- Account -> splits -> transaction relationships.
- Date/state query filters.
- JSON contracts for UI and integrations.

Avoid:

- broad write API
- custom HTTP verbs like `PAY`
- weakly documented auth/deployment boundaries

### From `gnucash-browser`

- Read-only web browsing is a valid and safe product mode.
- But static generation is too limited for this product.

### From `gnucash-2-web`

- Schema mapping discipline matters.
- Avoid anything that can alter GnuCash schema or mutate the book outside controlled write design.

### From GnuCashew

- GnuCash compatibility is complex.
- Do not drift into building a full replacement accounting system.

## Anti-goals to preserve

- No application code in phase 0.
- No writes in MVP.
- No collaborative multi-user editing as a core feature.
- No direct GnuCash schema mutation.
- No app metadata inside the GnuCash book.
- No SaaS-first architecture.
- No broad mutable API.
- No full GnuCash replacement ambition.
- No “family shared editing of one book” baseline.

## Open questions for phase 1

1. Which GnuCash file/database formats will MVP officially support first?
   - Recommended: start with SQLite through piecash if feasible.

2. How will read-only opening be enforced?
   - Need piecash/opening mode validation.
   - Need tests proving no file mutation.

3. How should exact numeric values be represented in API responses?
   - Recommended: structured rational/decimal representation with commodity metadata.

4. What sample/test books should be used?
   - Need at least a small personal book, multi-currency book, investment book, and edge-case transaction book over time.

5. What app metadata DB should be used?
   - Likely SQLite for MVP, but keep it clearly separate from the GnuCash book.

6. What auth model is appropriate for a private self-hosted MVP?
   - Could start with reverse-proxy auth support plus optional simple app auth, but this needs design before implementation.

7. Should indexing/cache exist in MVP?
   - Read-through may be enough initially; cache/index only if needed for performance.

## Recommended phase 1 plan

Phase 1 should still be conservative and test-driven.

Recommended tasks:

1. Create project skeleton.
   - SvelteKit frontend.
   - FastAPI backend.
   - Docker/dev compose.
   - No business logic yet.

2. Add sample GnuCash fixture(s).
   - Use non-sensitive fixture data only.
   - Document fixture source and expected balances.

3. Validate piecash read-only access.
   - Prove app can open a book without modifying it.
   - Add checksum/mtime tests around open/read operations.

4. Define exact amount representation.
   - No lossy floats for money.
   - Include commodity/currency metadata.

5. Draft API contract.
   - OpenAPI schemas for book, account, split, transaction, amount.
   - Read-only endpoints only.

6. Implement minimal backend read endpoints.
   - `/api/health`
   - `/api/book`
   - `/api/accounts`
   - `/api/accounts/{guid}`

7. Implement minimal UI shell.
   - Dashboard placeholder.
   - Account tree.
   - Read-only status indicator.

8. Add safety documentation.
   - Backups.
   - Read-only guarantee.
   - Supported formats.
   - “Use GnuCash desktop for editing.”

## Definition of done for phase 1

- Local dev environment starts reliably.
- Backend can open a sample book read-only.
- Tests prove opening/listing accounts does not mutate the book.
- API returns exact structured amount values.
- UI can display account hierarchy from API.
- Docs still reflect read-only MVP and anti-goals.
