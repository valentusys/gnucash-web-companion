# Phase 93 — Russian localization small slice

## Status

Complete. Phase 93 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-93-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Implement Phase 93 as a narrow, user-facing Russian localization slice for the existing `/books` read-only metadata surface and navigation, plus the required Russian/localization docs refresh.

### Why

The project already had Phase 52 i18n foundations for login, navigation, safety banner, dashboard/accounts/transactions headings. The highest-value small continuation is to make the newer `/books` page and its navigation label participate in that same English/Russian catalog without expanding translation scope or touching write-mode behavior.

### Phase brief

- Goal: make Russian support real but limited by localizing the `/books` nav label and read-only metadata page while refreshing `README.ru.md` and `docs/localization.md`.
- Non-goals: no full app translation, no backend/API localization, no release publication, no v0.2 work, no write-mode enablement, no audit-only artifact.
- Acceptance criteria:
  - English remains canonical and default.
  - Russian safety/read-only wording preserves the same meaning as English.
  - Desktop/mobile navigation and `/books` page do not break when locale is switched.
  - `README.ru.md` and `docs/localization.md` state that translation is incomplete.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - `/books` remains read-only metadata only.
  - No upload, deletion, registry editing, GnuCash data editing, collaborative, or family-wallet workflow is added.
  - `GNUCASH_WRITES_ENABLED=false` remains the safe default.
  - No real/private financial artifacts are committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - GitHub issue/release/tag verification.

### GitHub/backlog

- GitHub #17 remains the broad Russian localization tracking issue and should be updated with Phase 93 evidence.
- No new localization issue is required for this narrow slice.
- No tag/release publication.

## Engineer report

### Concrete result

Implemented the selected localization slice:

- `apps/web/src/lib/i18n/messages.ts`:
  - added `nav.books` for English/Russian navigation;
  - added English/Russian `/books` page strings for heading, helper copy, configured-books heading, hidden/blocked policy, no-mutation badge, current/default markers, read-only/access badges, metadata labels, read-only safety note, empty state, and fallback values.
- `apps/web/src/lib/components/DesktopNav.svelte` and `apps/web/src/lib/components/MobileNav.svelte`:
  - `/books` label now uses `t(locale, 'nav.books')` instead of hard-coded English.
- `apps/web/src/routes/books/+page.svelte`:
  - page title/headings/status/safety copy now use the i18n catalog;
  - page remains read-only metadata only and exposes no mutation controls.
- `apps/web/scripts/test-auth-routes.mjs`:
  - regression/static checks cover `nav.books`, Russian `/books` strings, localized `/books` page keys, and localized desktop/mobile `/books` navigation.
- `README.ru.md`:
  - refreshed from the old Phase 52 stub into an honest limited-Russian-support page.
- `docs/localization.md`:
  - documents the Phase 93 localized surface, English-canonical policy, incomplete translation status, and testing expectation.
- `README.md`, `PROJECT_STATUS.md`, and `CHANGELOG.md`:
  - status synced through Phase 93.

### Required checks

```text
cd apps/api && pytest -q
PASS — 326 passed, 27 warnings

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

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/components/DesktopNav.svelte`
- `apps/web/src/lib/components/MobileNav.svelte`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `README.ru.md`
- `docs/localization.md`
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-93.md`

### GitHub/release

- Open issues were inspected before implementation.
- GitHub #17 is the relevant broad Russian localization tracking issue and was/will be updated with Phase 93 evidence.
- Existing tags/releases were verified as `v0.1.0-readonly`, `v0.0.2-prealpha`, and `v0.0.1-prealpha` only.
- No new tag or GitHub release was created.

### Commit/push

Phase implementation commit and push evidence are recorded in the final controller report after push.
