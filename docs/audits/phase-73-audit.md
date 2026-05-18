# Phase 73 Audit — Multi-book Access Model

## Executive summary
Phase 73 audited the multi-book access model. The current implementation keeps the read-only multi-book foundation scoped to explicit `UserBookAccess` records and frames books as independent GnuCash books, not a family wallet or collaborative accounting surface.

No new release blocker was found for the current pre-alpha/read-only posture. This is not a `v0.1.0-readonly` release approval: publication remains blocked by #24 and #25.

## Verdict
No new Phase 73 blocker for the current pre-alpha/read-only posture.

## Blockers
No new Phase 73 blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

## Important non-blockers
1. Regression coverage for archived-book visibility is not explicit enough. `BookRegistryService.list_books_for_user()` filters archived books and `resolve_viewable_book()` rejects archived books, but dedicated tests should lock this down before the multi-book/admin surface grows.
2. Report-route unauthorized-access tests cover the summary endpoint, while future hardening should cover every report endpoint family to prevent route-by-route drift.
3. The frontend book switcher is currently safe because it uses the already-scoped `GET /books` list and resolves invalid cookies to an accessible fallback, but future UX/docs should keep saying “independent read-only books” and avoid shared-wallet/collaboration wording.

## Audit scope and evidence
Inspected:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/handoff/phase-72.md`
- auditor roadmap file: `/home/val/.hermes/cache/documents/doc_524e3283b5e8_auditor-roadmap-56-75.txt`
- `docs/book-switcher-readonly-model.md`
- backend book/access/account/transaction/report routers and services
- backend multi-book/account/transaction/export/report tests
- frontend active-book context and `BookSwitcher.svelte`
- frontend static auth/route safety checks
- open GitHub issues

## Phase 73 audit checks

### User-book access is explicit
Pass.

- `apps/api/app/services/book_access.py` grants view access only for explicit `UserBookAccess` roles: `owner`, `editor`, or `viewer`.
- `BookAccessService.get_role()` looks up `UserBookAccess` by user id and book id.
- `BookRegistryService.list_books_for_user()` joins through `UserBookAccess` rather than returning all books.
- Backend tests in `apps/api/tests/test_multi_book_access.py` verify users see only books they have explicit access to and users with no access see an empty list.

### Unauthorized book access is blocked
Pass with a test-hardening follow-up.

- `apps/api/app/routers/books.py::resolve_viewable_book()` rejects missing/archived books and calls `require_book_view_access()` before opening any GnuCash data.
- Account routes, transaction routes, CSV export, and report routes resolve a viewable book before service access.
- Existing tests cover unauthorized access for book detail, accounts, account tree, account detail, transaction list/detail/account transactions, CSV export, and report summary.
- Gap: archived-book visibility and every report endpoint family are not covered with explicit route-level regression tests. This is a meaningful hardening gap, not a current release blocker for the pre-alpha read-only posture.

### Book switcher only shows accessible books
Pass.

- `apps/web/src/lib/api/server.ts::getActiveBookContext()` fetches `GET /books` with the authenticated token, then resolves the active book from that already-scoped accessible list.
- Invalid or stale `selected_book_id` cookies are replaced with an accessible fallback or cleared when no accessible book exists.
- `apps/web/src/lib/components/BookSwitcher.svelte` renders only `books` passed from the accessible layout context.
- `apps/web/scripts/test-auth-routes.mjs` statically checks active-book fallback behavior and book-aware route use.

### Multi-book docs say “independent books”
Pass.

- README says the app is single-book by default with a read-only book switcher foundation for later multiple independent books with scoped access.
- `docs/book-switcher-readonly-model.md` says the switcher is a read-only navigation aid for books the signed-in user can already access and explicitly says multi-book support means multiple independent GnuCash books with scoped access.
- `docs/release/v0.1.0-readonly-plan.md` includes only a read-only switcher foundation for already-accessible independent books.

### No “family wallet” framing
Pass.

- README explicitly says the project is not for “family shared-wallet baseline” use.
- AGENTS.md says not to build a family wallet as the baseline model.
- The inspected current-status/release/book-switcher docs do not frame the project as a family wallet.

### No collaborative editing implication
Pass.

- README says the project is not true collaborative multi-user accounting.
- AGENTS.md says no real-time collaborative editing and frames advanced write work only as serialized/locked mode.
- Book-switcher docs state the switcher does not imply collaborative editing semantics.
- Frontend static checks reject collaborative/shared-wallet/family-wallet wording in the book switcher.

### Default book alias remains safe
Pass.

- Default aliases resolve through `resolve_default_viewable_book()` and require the current user to have view access to the default book.
- The smoke script discovers the default book through `GET /books` and verifies `/books/{book_id}` rather than trusting an unauthenticated alias.
- The release plan keeps the v0.1 baseline to one default configured GnuCash book and requires copied/disposable dogfood evidence before publication.

## Safety boundary
Pass.

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental/post-MVP only.
- No Phase 73 audit finding requires expanding write scope.
- GnuCash Desktop remains the authoritative editor.
- The project remains not SaaS, not a GnuCash replacement, and not collaborative accounting.

## Release/readme/docs consistency
Consistent for Phase 73.

- README was at Phase 72 before this phase and correctly stated pre-alpha/MVP-in-progress, read-only by default, not production-ready, not security-audited, and latest audit as Phase 72.
- PROJECT_STATUS was at Phase 72 before this phase and correctly said Phase 73 should only run when explicitly requested.
- CHANGELOG had a release-facing Phase 72 entry and did not claim v0.1 readiness.
- `v0.1.0-readonly` docs still block publication until release notes and runtime smoke/dogfood evidence are completed.

## GitHub project hygiene
Meaningful follow-up issue created:

- #35 — Expand multi-book access boundary tests for archived books and all read-only routes.

No noisy issue was created for book-switcher wording because the existing code/docs already use the correct independent read-only framing.

## Security notes
- Authenticated users can currently see `uri_or_path` in serialized book metadata. That is a known design tradeoff for local/admin-oriented pre-alpha use and should not be exposed publicly. Existing deployment/security docs already warn against direct public-internet exposure.
- #27 separately tracks redacting full default-book paths from seed logs.
- This Phase 73 audit is not a professional security audit.

## Test/CI notes
Checks run for Phase 73 are recorded in `docs/handoff/phase-73.md`.

## Recommended next actions
1. Keep v0.1 publication blocked by #24 and #25 until those gates are complete.
2. Address #35 in a later explicit hardening phase by adding archived-book and complete route-family access-boundary regression tests.
3. Keep `docs/book-switcher-readonly-model.md` as the canonical multi-book wording reference and maintain independent-books/no-collaboration wording as the UI grows.
4. Do not add book-management UI, archive controls, shared editing, or write expansion as part of Phase 73.

## Suggested / created GitHub issues
Created:

- #35 — Expand multi-book access boundary tests for archived books and all read-only routes (`audit`, `multi-book`, `read-only`, `safety`).

Suggested but not created separately:

- Book switcher UX clarification — covered by existing UI/doc copy and static checks; no separate issue needed now.
- Book archive/visibility docs — folded into #35 plus the Phase 73 accepted docs update.

## What not to do next
- Do not publish `v0.1.0-readonly` until #24/#25 are resolved and an explicit release phase approves publication.
- Do not expand controlled writes or enable `GNUCASH_WRITES_ENABLED` by default.
- Do not add collaborative editing, family-wallet framing, book upload/import, banking integration, or direct GnuCash SQL writes.
- Do not claim production readiness, security audit, safe write mode, broad compatibility, or known large-book scalability.
