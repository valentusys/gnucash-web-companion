# Phase 20 — Multi-Book UI Foundation

## Status
Complete — 2026-05-17.

## Goal
Add a minimal book switcher to the frontend so the UI can display and switch between multiple GnuCash books, using the existing book-aware backend routes and the `Book` / `UserBookAccess` data model already in place.

## What was done

### Frontend changes
1. **`apps/web/src/lib/components/BookSwitcher.svelte`** — New component. Renders a `<select>` dropdown when multiple books exist, plain text for single-book installs. On change, sets `selected_book_id` cookie and reloads.
2. **`apps/web/src/lib/api/server.ts`** — Added `getActiveBookId(cookies)` helper that reads `selected_book_id` cookie, validates it's a positive integer, returns `null` if absent/invalid.
3. **`apps/web/src/routes/+layout.server.ts`** — Now fetches `GET /books`, resolves active book (cookie → default → first), returns `books`, `activeBook`, `showBookSelector`.
4. **`apps/web/src/routes/+layout.svelte`** — Passes `books`/`activeBook` to `DesktopNav`, `MobileNav`, and `BookSwitcher`.
5. **`apps/web/src/lib/components/DesktopNav.svelte`** — Added `BookSwitcher` in the right side of the nav bar (before ThemeSwitcher).
6. **`apps/web/src/lib/components/MobileNav.svelte`** — Added `BookSwitcher` row above the nav links in the mobile bottom bar.
7. **`apps/web/src/routes/dashboard/+page.server.ts`** — Uses book-aware routes (`/books/{book_id}/reports/*`) when `activeBookId` cookie is set, falls back to alias routes otherwise.
8. **`apps/web/src/routes/accounts/+page.server.ts`** — Uses book-aware route for account tree.
9. **`apps/web/src/routes/accounts/[id]/+page.server.ts`** — Uses book-aware routes for account detail + transactions.
10. **`apps/web/src/routes/transactions/+page.server.ts`** — Uses book-aware routes for transaction list + accounts.
11. **`apps/web/src/routes/transactions/[id]/+page.server.ts`** — Uses book-aware route for transaction detail.

### Backend changes
12. **`apps/api/tests/test_multi_book_access.py`** — New test file with 8 tests covering:
    - User A sees only their book, User B sees only theirs
    - Cross-user access denied (403) on `GET /books/{id}`
    - Users with no access see empty list
    - Shared access (viewer role) allows both users to see the same book

### No changes
- Backend routers, models, services — untouched (already multi-book-ready since Phase 6).
- `GNUCASH_WRITES_ENABLED` — untouched.
- `.gitignore` — untouched.

## Test results
- Backend: 207 passed (199 original + 8 new), 1 pre-existing failure (test_gnucash_book.py relative path issue when run from wrong directory).
- Frontend: `npm run check` — 0 errors, 0 warnings.
- Frontend: `npm run test:auth-routes` — passed.
- Frontend: `npm run build` — built successfully in 4.88s.
- Docker: `docker compose config --quiet` — passed.

## Deviations from spec
- Page-level `+page.server.ts` files no longer return `books`/`activeBook`/`showBookSelector` — these come from the layout instead, which is more efficient (single fetch, not per-page).
- The `selected_book_id` cookie is validated as a positive integer in `getActiveBookId()` — extra safety beyond the spec.

## Safety checks
- `GNUCASH_WRITES_ENABLED=false` untouched.
- No new write endpoints or write logic.
- `selected_book_id` cookie contains only a validated integer book ID.
- No real GnuCash books or financial data in new test fixtures.
- `.gitignore` protections remain intact.
- Book access filtering tested: users cannot see books they lack access to.

## Related issues
GitHub issue #5 — "Add book switcher UI for future multi-book support" (milestone: post-MVP multi-book).
`gh` auth is currently invalid — issue not closed automatically.
