# Phase 18 — README Screenshots and Mobile Preview with Synthetic Data

## Status
Planned — 2026-05-17.

## Context

Phase 17 delivered a synthetic GnuCash SQLite fixture (`apps/api/tests/fixtures/test-book.gnucash.sqlite`) with 10 accounts and 5 transactions in SEK. The full stack is functional: login, dashboard, accounts, transactions, reports, dark mode, mobile shell. The `v0.0.1-prealpha` tag exists but the README has no screenshots yet.

The project is pre-alpha and must not expose real financial data. All screenshots must use only the synthetic fixture data (or the existing test book).

## Goal

Add visual proof of the current UI to the README so that visitors to the repository can see what the project looks like before cloning.

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
- Reference them from `README.md` using relative paths: `![Dashboard](docs/images/dashboard-desktop.png)`.
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
