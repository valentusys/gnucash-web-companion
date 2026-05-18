# Phase 109 PM brief — scheduled/recurring transaction awareness

Date: 2026-05-19
Status: planned
Related GitHub issue: #12
Roadmap source: analyst Phase 4 of 10

## Decision

Implement Phase 109 as a conservative read-only awareness slice for GnuCash scheduled/recurring transactions: expose only safe summary metadata if piecash can read it, render an honest UI page, and explicitly keep all creation/editing/scheduling work in GnuCash Desktop.

## Why

GitHub #12 asks for scheduled/recurring transaction visibility. piecash exposes `ScheduledTransaction` and `Recurrence` metadata, but this phase must avoid fake upcoming-run calculations and must not build a scheduling editor. A narrow metadata-only endpoint/page gives practical visibility while preserving the read-only MVP boundary.

## Phase brief

- Goal: Add read-only scheduled/recurring transaction awareness for the active accessible book.
- Non-goals: No scheduled transaction creation/editing/deletion, no automatic next-run prediction unless verified, no template split/account detail exposure, no raw SQL dumps, no write-mode changes, no tag/release publication.
- Acceptance criteria:
  - Backend provides book-aware and default-book read-only scheduled transaction endpoints.
  - The response contains safe summary fields only: id, name, enabled state, configured date/count flags, auto-create/notify flags, advance-day values, template-account presence, and recurrence summaries.
  - If a book has no scheduled transactions or the metadata is unavailable through the safe adapter path, the UI shows a clear empty/limitation state rather than fake predictions.
  - Frontend exposes a protected `/scheduled` page for the active accessible book and states that editing remains in GnuCash Desktop.
  - No next occurrence/frequency calculations are invented beyond raw recurrence metadata.
- Safety checks:
  - Keep `GNUCASH_WRITES_ENABLED=false` default untouched.
  - Do not modify scheduled transaction tables or write services.
  - Do not expose private raw SQL, template split contents, account names from template accounts, memos, descriptions, amounts, paths, or private data.
  - Preserve authenticated book access boundary; archived/unauthorized books must stay hidden/blocked by existing API context.
- Verification:
  - `cd apps/api && pytest -q tests/test_scheduled_transactions.py tests/test_transaction_writes.py`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

## Risks

- piecash scheduled transaction coverage may vary by book/schema; the UI must be honest when the safe metadata path returns an empty or unavailable result.
- Recurrence fields are metadata, not guaranteed upcoming-run schedules; avoid promising exact future occurrences.
- Navigation must remain protected and book-aware without adding browser storage or direct frontend file access.

## Files/docs to update

- `apps/api/app/services/gnucash_book.py`
- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/routers/books.py`
- New backend router/tests for scheduled transactions if needed
- `apps/web/src/routes/scheduled/+page.server.ts`
- `apps/web/src/routes/scheduled/+page.svelte`
- Navigation/i18n/static route checks
- `docs/scheduled-transactions.md`
- `docs/handoff/phase-109.md`
- `PROJECT_STATUS.md`

## GitHub/backlog

- Update GitHub #12 with Phase 109 evidence if `gh` is authenticated.
- Leave #12 open unless the implemented awareness slice fully satisfies the issue without editor/upcoming-calculation scope.
