# Phase 135 — Read-only UX mobile navigation polish

Date: 2026-05-19
Status: DONE

## Goal

Improve mobile navigation and small-screen UX for the read-only app shell at 320px–768px widths.

## Scope completed

- Updated `DesktopNav.svelte` so the desktop header is hidden below the `md` breakpoint, avoiding duplicated mobile controls.
- Reworked `MobileNav.svelte` into the only small-screen app navigation shell:
  - fixed bottom navigation remains available for primary read-only routes;
  - a touch-friendly menu button opens/closes an inline mobile menu;
  - the mobile menu contains book switching, locale switching, theme toggle, and logout controls;
  - primary links and menu controls declare at least 44px touch targets;
  - fixed navigation uses bounded width/overflow classes and avoids horizontal scroll containers.
- Updated shared switchers for touch use:
  - `BookSwitcher.svelte` now supports compact mobile rendering, 44px select height, truncation, and max-width guards;
  - `LocaleSwitcher.svelte` select now has a 44px touch target;
  - `ThemeSwitcher.svelte` button now has a 44px touch target.
- Updated the root app shell to hide horizontal overflow and reserve enough bottom padding for the fixed mobile navigation.
- Updated `TransactionSplits.svelte` so transaction detail splits render as mobile cards on small screens and use a bounded desktop-only table without `overflow-x-auto`/`min-w-full`.
- Added/updated frontend static route checks for mobile/desktop breakpoint ownership, mobile menu open/close controls, menu contents, touch-target classes, app-shell overflow guard, and split mobile cards.
- Updated `PROJECT_STATUS.md` for Phase 135 completion.

## Non-goals / safety boundaries

- No new pages or routes were added.
- No backend API, schema, route, service, GnuCash adapter, or endpoint changed.
- No write endpoint, write service, write lock, audit, backup, or write-mode gate changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No release/tag/package/publication was performed.
- No real/private GnuCash books, app DBs, backups, `.env`, tokens, keys, screenshots, exports, or private financial data were added or committed.
- Docs remain honest: pre-alpha/test copies/no production guarantee.

## Verification

- RED: `cd apps/web && npm run test:auth-routes` — failed before implementation on missing desktop/mobile breakpoint split and later on missing mobile split-card rendering.
- GREEN: `cd apps/web && npm run test:auth-routes` — passed (`auth route checks passed`).
- `cd apps/web && npm run check` — passed (`0 errors, 0 warnings`).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file scan — passed; no committed `.env`, app DB, GnuCash book, backup, screenshot/export, key, token, or secret artifact detected in the phase diff.

## Expected artifacts

- `apps/web/src/lib/components/MobileNav.svelte`
- `apps/web/src/lib/components/DesktopNav.svelte`
- `apps/web/src/lib/components/BookSwitcher.svelte`
- `apps/web/src/lib/components/LocaleSwitcher.svelte`
- `apps/web/src/lib/components/ThemeSwitcher.svelte`
- `apps/web/src/lib/components/TransactionSplits.svelte`
- `apps/web/src/routes/+layout.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-135.md`

## GitHub / release state

- No release/publication gate was executed for this phase.
- No tag or GitHub release was created.
- Push `main` after all verification passes and the single Phase 135 commit is created.
