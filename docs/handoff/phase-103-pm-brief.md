# Phase 103 PM Brief — Read-only transaction date-range presets (#11)

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-102.md`
Current planning HEAD: `bb335f8`

## Decision

Plan Phase 103 as the next practical non-publishing roadmap phase: deliver a narrow read-only transaction/search UX polish slice from GitHub #11 by adding transaction date-range presets to the existing transaction filter UI.

Current `main` is complete through Phase 102, so roadmap Phases 95-102 are already done. Publication of `v0.1.1-readonly` remains unauthorized and must not be planned here. GitHub #38 remains blocked without an explicit safe copied/disposable book path, and GitHub #22 remains blocked for broader real GnuCash Desktop compatibility evidence in this environment. The next uncompleted practical roadmap item is Phase 103. Within Phase 103, date-range presets are the safest narrow user-facing improvement: they build on existing read-only `date_from`/`date_to` filters and avoid new GnuCash schema interpretation risk.

## Goal

Add a small, tested, user-facing read-only UX improvement to the transactions page: date-range preset controls for common ranges such as this month, last month, year to date, and clear/custom filter state.

The presets must populate the existing `date_from` and `date_to` query parameters so the transaction list and CSV export continue to use the same read-only backend filtering path.

## Non-goals

- Do not publish `v0.1.1-readonly`.
- Do not create or push any tag.
- Do not create or edit a GitHub release.
- Do not publish packages or external release artifacts.
- Do not run a copied personal-book dogfood pass unless Val separately provides an explicit safe copied/disposable GnuCash SQL book path outside git.
- Do not search private directories for GnuCash books.
- Do not implement scheduled/recurring transaction parsing in this phase.
- Do not implement saved presets/accounts, browser persistence, localStorage-backed financial filters, or user profile settings.
- Do not implement write-mode work, import, banking integrations, account editing, delete flows, or v0.2 controlled-write expansion.
- Do not add heavy UI libraries.
- Do not change money calculations, fake currency conversion, or use float for money.
- Do not claim production readiness, audited security, broad GnuCash compatibility, or personal-book dogfood success.

## Acceptance criteria

- Engineer starts from current `main`, verifies a clean working tree, and confirms Phase 102 is complete.
- Engineer reads `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-102.md`, `docs/audits/2026-05-18-analyst-10-phase-plan.md`, and GitHub #11 scope.
- Transactions UI exposes date-range presets for at least:
  - this month;
  - last month;
  - year to date;
  - clear/custom state.
- Presets set or preserve ordinary URL query parameters (`date_from`, `date_to`) rather than creating a new backend contract.
- CSV export link continues to preserve the active filters, including date presets once applied.
- Existing manual/custom date inputs still work and are not hidden behind JavaScript-only behavior.
- Active filter summary remains accurate after a preset is applied.
- The implementation is mobile-friendly and accessible: buttons/links have readable text, focusable controls, and no pointer-only behavior.
- Tests cover the preset URL behavior, active summary behavior, and CSV export query-string parity.
- `PROJECT_STATUS.md` is updated after implementation to mark Phase 103 complete and identify the next practical step.
- `docs/handoff/phase-103.md` is created with implementation summary, verification summary, safety statement, changed files, GitHub/backlog note, risks/follow-up, and commit/push evidence.
- GitHub #11 is updated with non-sensitive evidence if `gh` is authenticated. Close #11 only if all accepted issue scope is genuinely complete; otherwise leave it open for broader future enhancements.
- No real/private financial data, GnuCash book, app DB, backup, `.env`, screenshot, CSV export with private data, secret, token, cert, key, or private path is committed.

## Safety checks

- Keep MVP read-only by default and keep `GNUCASH_WRITES_ENABLED=false` as the default posture.
- Use only existing read-only transaction list/export routes.
- Do not modify write routes or controlled-write enablement.
- Do not add persistence for financial filters in localStorage/sessionStorage.
- Do not commit real/private data or generated exports.
- Preserve httpOnly-cookie auth posture; do not introduce auth token access from frontend JavaScript.
- Keep GnuCash Desktop as the authoritative editor.
- Keep claims conservative: pre-alpha, read-only by default, not production-ready, not security-audited.
- Do not run any publish command. Publication still requires separate explicit authorization from Val.

## Verification required from engineer

Run these checks from the repository root unless noted:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD
git tag --list 'v0.1.1-readonly'
gh auth status || true
gh release view v0.1.1-readonly || true
```

Frontend checks are mandatory for this phase:

```bash
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
```

Backend checks are required if API/service/tests change; otherwise run at least a targeted no-backend-change justification in the handoff:

```bash
cd apps/api && pytest -q
```

Docker/config validation is required before final handoff:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Always run before commit:

```bash
git diff --check
```

## Files/docs to update

Expected files:

- `apps/web/src/routes/transactions/+page.svelte` — add preset controls and keep custom filter/export parity.
- `apps/web/src/routes/transactions/+page.server.ts` — update only if needed for safer date/preset handling; prefer keeping existing query-param contract.
- Existing frontend route/static checks under `apps/web/` — add coverage for preset links/buttons, active summary, and CSV parity.
- `PROJECT_STATUS.md` — after implementation, mark Phase 103 outcome and next planned phase.
- `CHANGELOG.md` — add a concise Unreleased entry if the UX change lands.
- `docs/handoff/phase-103.md` — implementation handoff.

Do not modify historical handoff documents except for a narrowly necessary forward-reference correction.

## GitHub/backlog note

- GitHub #11 is the primary issue for this phase.
- Update #11 with Phase 103 evidence if `gh` is authenticated.
- Close #11 only if the whole accepted issue is genuinely complete. More likely, leave it open because broader search/filter enhancements such as state filters, saved presets, and broader search semantics may remain.
- GitHub #38 remains open/blocked until Val provides an explicit safe copied/disposable GnuCash SQL book path outside git.
- GitHub #22 remains open unless a separate safe real-version compatibility source is provided and tested.
- GitHub #39 remains closed unless concrete CSV export regression evidence is found.
- Do not create new GitHub issues unless a concrete new bug is discovered and cannot fit an existing issue.
- Do not publish `v0.1.1-readonly` without separate explicit authorization from Val.

## Exact engineer instructions

1. Start from current `main`; verify `git status --short` is clean.
2. Read `AGENTS.md`, `PROJECT_STATUS.md`, this PM brief, `docs/handoff/phase-102.md`, `docs/audits/2026-05-18-analyst-10-phase-plan.md`, and GitHub #11.
3. Confirm Phase 102 is complete and that publication remains unauthorized.
4. Run non-mutating release-boundary checks: branch/HEAD, tag absence, GitHub release absence, and `gh auth status || true`.
5. Inspect current transactions page filter behavior and route checks.
6. Implement date-range preset controls on the transactions page using existing `date_from` and `date_to` query parameters.
7. Prefer progressive-enhancement-safe links or form buttons that work with normal navigation; avoid adding browser storage for financial filters.
8. Ensure preset-applied filters are visible in the active summary and included in the CSV export URL exactly like custom dates.
9. Preserve custom date inputs and existing search/account/amount filters.
10. Add/update frontend route/static checks for preset behavior, active summary, and CSV export query-string parity.
11. Run required frontend checks, Docker config validation, and `git diff --check`; run backend tests if backend code changes.
12. Update `CHANGELOG.md` if the UX change lands.
13. Create `docs/handoff/phase-103.md` with implementation summary, verification summary, safety statement, GitHub/backlog note, changed files, risks/follow-up, and commit/push evidence.
14. Update `PROJECT_STATUS.md` to mark Phase 103 complete and identify the next practical step.
15. Update GitHub #11 with non-sensitive evidence if `gh` is authenticated; leave it open unless all accepted scope is truly complete.
16. Do not create tags, GitHub releases, packages, GnuCash books, app DBs, backups, screenshots, private CSV exports, `.env`, or secret artifacts.
17. Commit and push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 103 title and verdict: completed, partially completed, blocked, or failed.
- What date-range preset UX was added and how it preserves read-only list/CSV filter parity.
- Paths to changed frontend/tests/docs and `docs/handoff/phase-103.md`.
- Whether GitHub #11 was updated or closed; if left open, the exact remaining scope.
- Confirmation that no tag/release/package was published.
- Verification summary: branch/HEAD, tag/release absence, frontend checks, backend checks if run or why not needed, Docker config validation, and `git diff --check`.
- Safety statement: writes remain disabled by default; controlled writes remain post-MVP/experimental; no real/private data or private exports were committed.
- Commit hash and push status.
