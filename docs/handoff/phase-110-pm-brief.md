# Phase 110 PM brief — books metadata UX hardening

Date: 2026-05-19
Status: planned
Related GitHub issue: #13
Roadmap source: analyst Phase 5 of 10

## Decision

Implement Phase 110 as a narrow read-only `/books` hardening slice for operator confidence: improve the metadata contract and UI status/actions for already accessible independent books, without adding upload, deletion, registry editing, default-changing, or multi-user admin workflows.

## Why

The current `/books` page is already read-only and access-scoped, but GitHub #13 still has a safe subset that can improve the MVP before any admin book-management scope: clearer status/read-only metadata, explicit access role/status, stronger empty/inaccessible copy, and safe links into book-specific read-only views.

## Phase brief

- Goal: Make `/books` a more useful read-only metadata/status page for single-book and multi-book setups.
- Non-goals: No book upload/import, deletion, registry editing, default-book mutation, access-control editor, write-mode changes, family-wallet/collaborative framing, tag/release publication, or direct frontend GnuCash file reads.
- Acceptance criteria:
  - `GET /books` continues to return only non-archived books viewable by the current user.
  - Book metadata includes explicit read-only/status/access-role fields for frontend badges without opening GnuCash data.
  - `/books` clearly marks current/default books, storage/base currency, read-only status, accessible status, and empty/inaccessible states.
  - `/books` offers safe links to book-specific read-only views such as accounts, transactions, dashboard, and scheduled metadata while preserving the selected active book context.
  - No management controls are exposed.
- Safety checks:
  - Preserve `GNUCASH_WRITES_ENABLED=false` default and do not touch write endpoints/services.
  - Existing user/book access model remains authoritative; archived/unauthorized books stay hidden in lists and blocked on direct routes.
  - Frontend uses authenticated API context only and never reads GnuCash files directly.
  - Do not commit real books, exports, screenshots, app DBs, `.env`, secrets, tokens, certs, backups, or private paths.
- Verification:
  - `cd apps/api && pytest -q tests/test_accounts.py tests/test_transaction_writes.py`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

## Risks

- Safe links must not imply book management or mutate the registry; selecting a book can only set the existing non-secret selected-book cookie after API access verification.
- The API currently exposes app metadata only; do not expand this phase into live GnuCash health checking if that would require opening private books or producing unreliable status claims.
- Static frontend tests may need updating so new read-only links and badges remain pinned without brittle implementation coupling.

## Files/docs to update

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_accounts.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/api/server.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/routes/books/[bookId]/select/+server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/book-switcher-readonly-model.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-110.md`

## GitHub/backlog

- Update GitHub #13 with Phase 110 evidence if `gh` is authenticated.
- Keep #13 open unless future admin-only registration/default/deletion-from-registry workflows are explicitly completed; this phase intentionally does not implement those workflows.
