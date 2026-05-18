# Phase 18 — README Screenshots and Mobile Preview with Synthetic Data

## Status
Complete — 2026-05-17.

## Context

Phase 17 delivered a synthetic GnuCash SQLite fixture (`apps/api/tests/fixtures/test-book.gnucash.sqlite`) with 10 accounts and 5 transactions in SEK. The full stack is functional: login, dashboard, accounts, transactions, reports, dark mode, mobile shell. The `v0.0.1-prealpha` tag exists but the README had no screenshots yet.

The project is pre-alpha and must not expose real financial data. All screenshots use only the synthetic fixture data.

## Goal

Add visual proof of the current UI to the README so that visitors to the repository can see what the project looks like before cloning.

## Results

### Screenshots captured

All 7 screenshots captured successfully using Chromium headless via CDP (Chrome DevTools Protocol). Total size: ~453 KB.

| File | Size | Content |
|------|------|---------|
| `docs/images/login.png` | 20.0 KB | Login page, light mode, empty form |
| `docs/images/dashboard-desktop.png` | 84.8 KB | Desktop dashboard with summary cards, recent transactions, expense chart |
| `docs/images/dashboard-mobile.png` | 35.0 KB | Mobile viewport (375×812) responsive dashboard |
| `docs/images/accounts-tree.png` | 90.9 KB | Account hierarchy with balances (SEK) |
| `docs/images/transactions-list.png` | 95.9 KB | Transaction table with search/filter controls |
| `docs/images/transaction-detail.png` | 41.7 KB | Single transaction view with splits |
| `docs/images/dark-mode.png` | 84.7 KB | Dashboard in dark theme |

### Data safety verified

All screenshots contain only synthetic fixture data:
- Generic account names: Assets, Bank, Checking, Expenses, Food, Transport, Income, Salary, Liabilities, Credit Card
- Synthetic transactions: "Credit card payment", "Monthly expenses", "Bus pass", "Grocery store", "January salary"
- Currency: SEK
- No real financial data exposed

### README updated

`README.md` — replaced placeholder "Screenshots are not included yet" section with `## Screenshots` section containing all 7 images with relative paths (`docs/images/*.png`).

### Production code changes

None. Only `README.md` and `docs/images/` were modified.

### Deviations from spec

1. **Transaction detail URL**: The spec assumed `/transactions/1` but the synthetic fixture uses GUIDs as transaction IDs. Used the actual first transaction GUID (`89bdbe5a90af4c2fb4fc76b781d4a23b`) for the screenshot. The route pattern `/transactions/[id]` works correctly with GUIDs.

2. **Screenshot tooling**: The `browser_vision` tool timed out (no display available). Used Chromium headless with CDP via Python `websocket-client` instead. This approach works without a display server.

3. **Authentication method**: Could not inject httpOnly cookies directly via CDP `Network.set_cookie` because SvelteKit's server-side auth hook reads cookies from the request, and CDP cookie injection doesn't persist across navigations in headless mode. Used form-based login via CDP `Runtime.evaluate` to fill and submit the login form, which properly sets the httpOnly cookie through the SvelteKit action.

## Verification

- All 7 screenshot files exist under `docs/images/`, each < 300 KB ✓
- No screenshot contains real financial data ✓
- README has `## Screenshots` section with all 7 images ✓
- Relative paths used (`docs/images/*.png`) ✓
- No production code modified ✓
- `.gitignore` still blocks sensitive data ✓

## GitHub

Related issue: #3 (Add screenshots and mobile preview to README).

## Non-goals

- No new features or UI changes beyond what already exists.
- No real financial data in screenshots.
- No changes to production code paths (only README, docs, and screenshot image files).
- No Docker or deployment changes.
- No GitHub release or tag bump.
- No multi-book UI, no write features, no auth changes.

## Screenshots required

Capture using the synthetic fixture (test-book.gnucash.sqlite) or the existing demo book:

1. **Login page** — light mode, empty form.
2. **Dashboard — desktop** — full-width desktop view showing summary cards, cashflow chart, recent transactions.
3. **Dashboard — mobile** — narrow viewport (375px) showing responsive layout.
4. **Accounts tree** — expanded account hierarchy with balances.
5. **Transactions list** — table/card view with date, description, amount columns.
6. **Transaction detail** — single transaction view with splits.
7. **Dark mode** — any one page (dashboard preferred) in dark theme.

## Placement

- Store screenshot files under `docs/images/` (create directory if needed).
- Reference them from `README.md` using relative paths such as `docs/images/dashboard-desktop.png`.
  From this handoff file, the equivalent relative path is `../images/dashboard-desktop.png`.
- Keep image files compressed (PNG or WebP, < 200 KB each if possible).
- Add a `## Screenshots` section to README after the description/features section and before the "Getting Started" / "Quick Start" section.

## Files likely touched

### New files
- `docs/images/login.png`
- `docs/images/dashboard-desktop.png`
- `docs/images/dashboard-mobile.png`
- `docs/images/accounts-tree.png`
- `docs/images/transactions-list.png`
- `docs/images/transaction-detail.png`
- `docs/images/dark-mode.png`

### Modified files
- `README.md` — add Screenshots section with embedded images.
- `docs/handoff/phase-18.md` — this file.
- `PROJECT_STATUS.md` — mark Phase 18 complete.

## Acceptance criteria

1. `docs/images/` contains 7 screenshot files (PNG or WebP), each < 300 KB.
2. No screenshot contains real financial data (only synthetic fixture data: "Grocery store", "Bus pass", "January salary", SEK currency, generic account names).
3. `README.md` has a `## Screenshots` section with all 7 images rendered via Markdown image syntax.
4. Images render correctly in GitHub-flavored Markdown (relative paths work on the `main` branch).
5. No production code modified (no changes to `apps/api/`, `apps/web/src/`, Docker, or config).
6. `.gitignore` still blocks `data/`, `.env`, secrets, real books, backups.
7. All existing checks still pass:
   - `cd apps/api && pytest -q` — no regressions.
   - `cd apps/web && npm run check` — 0 errors, 0 warnings.
   - `cd apps/web && npm run build` — builds successfully.
   - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passes.
8. Phase handoff doc (`docs/handoff/phase-18.md`) updated with results.
9. `PROJECT_STATUS.md` updated: Phase 18 marked complete.

## Safety checks

- [ ] No production code modified (only README + docs/images).
- [ ] No real financial data in any screenshot.
- [ ] No `.env`, secrets, credentials created or modified.
- [ ] `GNUCASH_WRITES_ENABLED` remains `false` (not touched).
- [ ] `.gitignore` still blocks `data/books/*`, `data/app/*`, `data/backups/*`, `.env`, secrets.
- [ ] No Docker/deployment changes.
- [ ] All existing tests pass (187+ passed, no new failures).
- [ ] Image files are compressed and reasonable size.

## Verification commands

```bash
# Verify no production code changed
git diff --stat -- apps/api/ apps/web/src/ docker* .env.example
# (should show no changes)

# Verify screenshots exist and are reasonable size
ls -lh docs/images/
# (7 files, each < 300 KB)

# Verify README renders images correctly (spot-check paths)
grep -n 'docs/images/' README.md

# Verify no real data in screenshots (manual visual check required)

# Backend tests still pass
cd apps/api && pytest -q

# Frontend checks still pass
cd apps/web && npm run check
cd apps/web && npm run build

# Docker config still valid
cd ..
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

## Handoff requirements

After Phase 18 completion:
1. Update `PROJECT_STATUS.md` — add Phase 18 entry, mark complete.
2. Update `docs/handoff/phase-18.md` — record actual results, screenshot count, any deviations.
3. Commit all changes.
4. Push to GitHub if auth is available.
5. Create/update GitHub issue if `gh` is available.

## GitHub/backlog

Related existing issue:
- `docs/github/issues/03-readme-screenshots-mobile-preview.md`

After Phase 18, this issue should be closable.

Next backlog items after this phase:
- `docs/github/issues/04-prepare-v0.0.1-prealpha-release.md` — blocked on `gh` auth.
- `docs/github/issues/06-document-multicurrency-reporting-limitations.md`
- `docs/github/issues/10-auth-cookie-security-review.md`
- `docs/github/issues/05-book-switcher-ui-future-multibook.md`

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Screenshots contain real data accidentally | Privacy leak | Use only synthetic fixture; review each image before commit |
| Image files too large | Bloated repo | Compress to WebP or optimized PNG; target < 200 KB each |
| Relative image paths break on GitHub | Broken README rendering | Test by viewing README on GitHub after push; use paths relative to repo root |
| Screenshots become outdated quickly | Misleading docs | Label screenshots with version; re-capture in later phases if UI changes significantly |
| Dark mode screenshot hard to capture | Inconsistent quality | Use browser devTools to force dark theme via CSS variable override or toggle |
