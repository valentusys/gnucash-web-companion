# Phase 110 — books metadata UX hardening

Date: 2026-05-19
Status: complete
Related GitHub issue: #13
PM brief: `docs/handoff/phase-110-pm-brief.md`

## Summary

Phase 110 implemented the analyst roadmap Phase 5 slice: `/books` is now a clearer read-only metadata/status page for accessible independent books, with stronger operator-confidence copy and safe links into existing book-specific read-only views.

## PM decision

Address GitHub #13 only as a safe read-only metadata UX hardening phase. Book upload, deletion, registry editing, default-book mutation, access-control administration, multi-user admin UI, write-mode behavior, family-wallet framing, and collaborative accounting remain out of scope.

## Implementation

Backend:

- Extended `GET /books` and `GET /books/{book_id}` app metadata responses with fields that do not open or inspect the GnuCash book:
  - `access_role`
  - `read_only=true`
  - `status=accessible`
  - `management_actions=[]`
- Kept `GET /books` scoped to non-archived books with `UserBookAccess` for the current user.
- Kept direct archived-book resolution as not found before any GnuCash data is opened.

Frontend:

- Extended the `Book` TypeScript contract with the new metadata/status fields.
- Updated `/books` to render:
  - current/default markers;
  - base currency;
  - storage type;
  - access role;
  - metadata status;
  - read-only status;
  - no-management-action copy.
- Added safe book-context links from each visible book card to existing read-only views:
  - `/dashboard`
  - `/accounts`
  - `/transactions`
  - `/scheduled`
- Added `GET /books/{bookId}/select`, which verifies the requested book id against the authenticated accessible book list before setting the existing non-secret `selected_book_id` cookie and redirecting only to the approved read-only paths.

Docs/status:

- Created the PM brief at `docs/handoff/phase-110-pm-brief.md`.
- Updated `docs/book-switcher-readonly-model.md` with the hardened metadata/safe-link behavior.
- Updated `PROJECT_STATUS.md` through Phase 110 and set Phase 111 as the next roadmap phase.
- Updated `CHANGELOG.md` Unreleased notes.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write endpoints/services were changed.
- No upload, deletion, registry-edit, default-changing, access-control administration, import, or book-management mutation UI was added.
- `/books/{bookId}/select` does not authorize by cookie alone; it verifies the requested book against authenticated `GET /books` context first.
- Archived and unauthorized books remain hidden or blocked by the backend access model.
- Frontend still never reads GnuCash files/databases directly.
- No localStorage/sessionStorage was added for book context or auth.
- No tag, release, or package was published.
- No real/private GnuCash books, `.env`, app DBs, backups, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.

## Verification

Passed:

```bash
cd apps/api && pytest -q tests/test_accounts.py::TestListBooks::test_returns_books_for_user tests/test_accounts.py::TestListBooks::test_excludes_archived_books_even_with_access tests/test_accounts.py::TestGetBook::test_returns_book
# 3 passed, 1 warning

cd apps/api && pytest -q tests/test_accounts.py tests/test_transaction_writes.py
# 60 passed, 7 warnings

cd apps/api && pytest -q
# 344 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_accounts.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/routes/books/[bookId]/select/+server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/book-switcher-readonly-model.md`
- `docs/handoff/phase-110-pm-brief.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-110.md`

## GitHub

- Update #13 with Phase 110 evidence if `gh` is authenticated.
- Keep #13 open because the original admin-only registration/default/deletion-from-registry workflows remain intentionally out of scope.

## Commit/push

- Commit: this commit (`Harden read-only books metadata UX`); final SHA is recorded in the phase controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
