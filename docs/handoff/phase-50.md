# Phase 50 — Book Switcher Stabilization

## Status

Complete. Book switcher/read-only multi-book routing was stabilized without adding write scope, upload/import, book-registration UI, or collaborative-editing semantics. Required checks passed and no blockers remain.

## PM report

### Decision

Execute exactly Phase 50 from the roadmap: stabilize the existing book switcher and multi-book UI foundation at a safe read-only level.

### Why

Phase 49 finished transaction filter/export hardening. The next roadmap item is multi-book stabilization: users should clearly see the current book, switch only among accessible books, keep book-aware routes stable, and retain the independent-books model. This is read-only release-value work and does not require book management UI or controlled-write expansion.

### Phase brief

- Goal: make the existing book switcher safer and clearer for read-only multiple independent books.
- Non-goals: no book upload, no book registration/admin UI, no account editing, no import/sync, no collaborative/family-wallet framing, no release/tag publication, no new write behavior.
- Acceptance criteria:
  - Current book is shown clearly in the app shell.
  - Switching preserves the current route/query context.
  - Server-side page loads resolve active book only from the accessible `/books` list.
  - Invalid/stale/inaccessible selected-book cookies fall back to accessible default/first book instead of building unauthorized book routes.
  - Backend remains authoritative for unauthorized book access.
  - Multi-book is documented as independent read-only books with scoped access.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
  - Working tree clean after commit/push.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe/default state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No real GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, real screenshots, or real exports are committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Book switching could imply collaborative/family-wallet semantics. Mitigation: UI/doc copy explicitly says independent read-only books.
- Raw selected-book cookies could point at unauthorized or stale book ids. Mitigation: all relevant server page loads now resolve against `/books` first and refresh/clear invalid cookies.
- Full issue #13 could expand into admin book management UI. Mitigation: Phase 50 intentionally stabilizes the switcher only; issue remains open for future admin-only management work.

### Files/docs to update

- `apps/web/src/lib/api/server.ts`
- `apps/web/src/lib/components/BookSwitcher.svelte`
- Book-aware frontend server loads under `apps/web/src/routes/`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/book-switcher-readonly-model.md`
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-50.md`

### GitHub/backlog

- Phase 50 is related to GitHub #13 (`Book management UI`) only as a stabilization subset.
- GitHub #13 should be updated with the Phase 50 result and left open for future admin-only book registration/management UI.
- Next planned phase after completion: Phase 51 — auditor pass after UX/book/filter work.

## Engineer report

Implemented only Phase 50 work:

- Added shared active-book context resolution in `apps/web/src/lib/api/server.ts`.
- Updated layout/dashboard/accounts/account-detail/transactions/transaction-detail server loads to build book-aware API routes from the accessible active-book context rather than trusting raw `selected_book_id` directly.
- Invalid or stale selected-book cookies now fall back to the accessible default book, then first accessible book; the cookie is refreshed or cleared on fallback.
- Improved `BookSwitcher.svelte` copy: clear `Current book:` label, default marker, independent read-only books wording, and route/query-preserving switch navigation.
- Added static frontend checks in `npm run test:auth-routes` for active-book fallback, route usage, route/query preservation, and no upload/collaboration/family-wallet framing.
- Added `docs/book-switcher-readonly-model.md` documenting behavior, access boundary, fallback order, and non-goals.
- Updated `README.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff.

No write routes were changed. No book upload, registration UI, account editing, import/sync, collaborative editing, release, or tag was added.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed (`280 passed`, 27 existing warnings).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No book upload, book registration UI, account editing, import, sync, banking integration, or collaborative editing was added.
- No auth token localStorage/sessionStorage path was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Commit message: `fix: stabilize book switcher`.
- Push: pushed to `origin/main`.

## GitHub issue status

- GitHub #13 was updated with the Phase 50 stabilization summary.
- GitHub #13 remains open for future admin-only book management UI outside this phase.

## Blockers

None.
