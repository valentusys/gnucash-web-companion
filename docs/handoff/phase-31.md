# Phase 31 — Read-Only Safety Status Banner

## Status

Complete.

## Goal

Add a small, bounded release-readiness/read-only MVP polish item: a persistent authenticated-app reminder that the MVP is read-only by default and that GnuCash Desktop remains the authoritative editor.

## PM decision

Choose the roadmap item “clearer read-only indicators in the UI” as the final phase of the six-phase continuation mission.

Reason: after Phase 30 completed transaction amount range filters, the remaining release-readiness backlog favored small UI/documentation safety improvements over expanding feature scope. A global read-only status banner is bounded, visible, and reinforces the MVP safety boundary without touching write behavior.

## Scope

- Add a reusable read-only status banner component.
- Display it in the authenticated app shell above page content.
- Keep language conservative: read-only by default, GnuCash Desktop remains authoritative, writes require an explicit post-MVP feature flag.
- Update project status, changelog, roadmap, and release candidate notes.

## Non-goals

- No write-path expansion.
- No changes to `GNUCASH_WRITES_ENABLED` behavior.
- No privacy-mode implementation for hiding balances.
- No clean-machine Docker/E2E runtime validation.
- No tag, release, package publication, or real screenshots.
- No real financial data, GnuCash books, app DBs, backups, secrets, tokens, keys, or certs.

## Changes

### Frontend

- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte`
  - New accessible banner with `aria-label="Read-only safety status"`.
  - Shows a “Read-only by default” status line and concise safety text.
  - Uses existing theme variables and no new dependencies.

- `apps/web/src/routes/+layout.svelte`
  - Displays `ReadOnlyStatusBanner` for authenticated app pages.
  - Removed an unused `BookSwitcher` import from the layout.

### Docs

- `README.md` — current status advanced through Phase 31.
- `CHANGELOG.md` — Phase 31 entry added.
- `docs/ROADMAP.md` — read-only indicator item marked complete; remaining work narrowed to Docker/E2E, release checklist, deployment hardening, and privacy mode.
- `docs/release/v0.0.2-prealpha-notes.md` — candidate notes updated through Phase 31.
- `PROJECT_STATUS.md` — baseline advanced through Phase 31.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No backend write route, write service, lock, backup, or audit-write behavior changed.
- UI copy reinforces read-only-by-default and post-MVP write gating.
- No real financial data or secrets added.
- No tags/releases/packages published.

## Verification

- Backend full suite: see final Phase 31 report.
- Frontend: see final Phase 31 report.
- Docker config: see final Phase 31 report.

## Commit

Phase commit: see final Phase 31 report / `git log` for the pushed commit SHA.

## GitHub

- Open backlog inspected with `gh issue list`.
- Related issues: none closed; this was a small release-readiness/read-only UI polish item from the roadmap.

## Final mission summary

This completes the requested six-phase continuation after Phase 25:

- Phase 26 — audit-driven status sync.
- Phase 27 — discoverability and community announcement readiness.
- Phase 28 — GnuCash compatibility matrix.
- Phase 29 — required audit and release documentation sync.
- Phase 30 — transaction amount range filters for browsing and CSV export.
- Phase 31 — read-only safety status banner.

## Blockers

None.
