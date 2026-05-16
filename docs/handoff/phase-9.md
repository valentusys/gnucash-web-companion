# Phase 9 Handoff — Frontend Foundation

## Scope

Phase 9 improves the SvelteKit frontend foundation without changing backend API behavior. It adds a CSS-variable theme system, authenticated app shell navigation, reusable state components, mobile polish, and a PWA manifest foundation.

This phase does not add write operations, budgets, chart libraries, heavy animation libraries, or private financial data caching.

## Theme system

Implemented in:

- `apps/web/src/app.css`
- `apps/web/src/app.html`
- `apps/web/src/lib/theme.ts`
- `apps/web/src/lib/components/ThemeSwitcher.svelte`

Required CSS variables exist for both light and dark themes:

- `--app-bg`
- `--app-panel`
- `--app-text`
- `--app-muted`
- `--app-accent`
- `--app-danger`
- `--app-success`
- `--app-border`

Additional supporting variables exist for hover, input, nav, ring, and elevated panel colors.

Theme mode is applied via `document.documentElement[data-theme]`.

Theme persistence uses `localStorage` key `theme` only. Auth tokens remain in the existing httpOnly cookie and are not stored or mixed with theme storage.

`app.html` includes a small inline script that applies the stored/system theme before first paint to reduce light/dark flash.

## Navigation and app shell

Implemented in:

- `apps/web/src/routes/+layout.server.ts`
- `apps/web/src/routes/+layout.svelte`
- `apps/web/src/lib/components/DesktopNav.svelte`
- `apps/web/src/lib/components/MobileNav.svelte`

Authenticated routes now render inside the app shell:

- Sticky desktop/top navigation.
- Mobile bottom navigation.
- Links: Dashboard, Accounts, Transactions.
- Theme switcher and logout are available from the top navigation.

The login page is intentionally excluded from the app shell, including when an auth cookie is already present.

Mobile bottom navigation uses safe-area padding and the layout adds bottom padding so content is not covered.

## Reusable states

Added reusable state components:

- `apps/web/src/lib/components/EmptyState.svelte`
- `apps/web/src/lib/components/ErrorState.svelte`
- `apps/web/src/lib/components/LoadingState.svelte`

Existing dashboard/report/list components were updated toward variable-driven colors and reusable empty/error/loading patterns.

## Mobile polish

Changes include:

- Global `box-sizing: border-box`.
- `overflow-x: hidden` guard on `html, body`.
- `viewport-fit=cover` for mobile safe areas.
- Bottom-nav safe-area support via `.safe-bottom`.
- Authenticated content gets bottom padding on mobile so fixed nav does not cover content.
- Tables keep desktop table behavior while existing mobile card/fallback views remain in use.

Target viewport sizes considered:

- 360px
- 390px
- 768px
- desktop

## PWA foundation

Added:

- `apps/web/static/manifest.webmanifest`
- `apps/web/static/icon.svg`
- manifest link and icon link in `apps/web/src/app.html`

Manifest fields:

```json
{
  "name": "GnuCash Web Companion",
  "short_name": "GnuCash",
  "display": "standalone",
  "start_url": "/dashboard",
  "theme_color": "#2563eb",
  "background_color": "#f9fafb"
}
```

No service worker or aggressive API caching was added. This avoids caching private financial API data.

## Accessibility pass

Added or preserved:

- Visible focus styles via `:focus-visible`.
- Semantic `<nav>` regions with labels.
- Theme switcher has accessible labels and titles.
- Decorative icons use `aria-hidden`.
- Empty/error/loading states use `role="status"`, `role="alert"`, or `aria-busy` where appropriate.
- Login page remains a focused standalone flow without shell navigation.

## Verification

Frontend checks:

```bash
cd apps/web
npm run check
npm run test:auth-routes
npm run build
```

Result:

```text
svelte-check found 0 errors and 0 warnings
auth route checks passed
vite build OK
```

Additional smoke check:

- `/login` with a fake `access_token` cookie does not render the authenticated app shell.

Backend tests were not rerun because Phase 9 does not change backend API/code.

## Notes and future work

- Theme preference currently uses localStorage. If server-side theme rendering is later needed, a theme-only cookie can be added without touching auth storage.
- No service worker is present yet. If added later, it must not cache authenticated financial API responses.
- Active-route highlighting in navigation can be improved in a later UI polish phase.
