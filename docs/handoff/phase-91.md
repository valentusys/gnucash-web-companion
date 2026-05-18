# Phase 91 — Book management UI: read-only metadata only

## Status

Complete. Phase 91 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-91-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement exactly the Phase 91 safe subset: a user-facing `/books` page for read-only book metadata visibility, not book upload/registration/deletion or GnuCash data editing.

### Why

GitHub #13 asks for broader admin book management, including registration, default changes, and deletion-from-registry. The Phase 91 roadmap explicitly narrows this to “read-only view/manage metadata only.” The safest concrete result is to make configured accessible books understandable while leaving all mutation/admin workflows out of scope.

### Phase brief

- Goal: make configured book metadata clearer in the web UI so users understand which book is current/default and what status it has.
- Non-goals: no book upload, no book registration form, no deletion from registry, no default-changing UI, no direct GnuCash data editing, no collaborative/family-wallet framing, no write-mode work, no v0.2 work, no release/tag publication, no real/private data artifacts.
- Acceptance criteria:
  - `/books` exists and is reachable from desktop/mobile authenticated navigation.
  - The page shows only accessible configured books returned by the authenticated `/books` API path.
  - The page shows book name, base currency, current/default marker, storage type, read-only status, and access status.
  - Archived and unauthorized books remain hidden or blocked by the backend access boundary.
  - No upload/delete/edit/write controls are present.
  - No collaborative/family-wallet framing is introduced.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - UI metadata-only change using existing book context and `/books` API.
  - Existing backend route-family tests prove unauthorized and archived book access remains blocked.
  - No backend write routes, write config, or GnuCash service write behavior changed.
  - No tag/release publication.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #13 is the broader book management UI issue.
- Phase 91 updates #13 with evidence and keeps it open because admin-only registration/default/deletion-from-registry workflows remain intentionally out of scope.
- No new release/tag publication.

## Engineer report

### Concrete result

Implemented the read-only book metadata UI:

- `apps/web/src/routes/books/+page.server.ts` loads the authenticated accessible book context with `getActiveBookContext()`.
- `apps/web/src/routes/books/+page.svelte` renders the `/books` page with:
  - configured accessible books;
  - current book marker;
  - active/default book marker;
  - book name;
  - base currency;
  - storage type;
  - read-only status;
  - access status;
  - explicit copy that archived/unauthorized books are hidden or blocked by the API;
  - explicit copy that there is no upload, deletion, or GnuCash data editing workflow.
- `apps/web/src/lib/components/DesktopNav.svelte` and `apps/web/src/lib/components/MobileNav.svelte` link to `/books`.
- `apps/web/scripts/test-auth-routes.mjs` now checks the `/books` page, nav links, safe metadata-only copy, and absence of mutation/collaboration framing.

### Required checks

```text
cd apps/api && pytest -q
PASS — 323 passed, 27 warnings

cd apps/web && npm run check
PASS — svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
PASS — auth route checks passed

cd apps/web && npm run build
PASS — production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

### Files changed

- `apps/web/src/routes/books/+page.server.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/lib/components/DesktopNav.svelte`
- `apps/web/src/lib/components/MobileNav.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/handoff/phase-91.md`

### GitHub/release

- GitHub #13 to be updated with Phase 91 evidence and kept open for the broader future admin-only book-management scope.
- Existing tags/releases should remain `v0.1.0-readonly`, `v0.0.2-prealpha`, and `v0.0.1-prealpha` only.
- No new tag or GitHub release should be created.
