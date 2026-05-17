# Phase 25 — Documentation, Release, and Roadmap Sync

## Status

Complete.

## Goal

Documentation-only phase. Sync README, CHANGELOG, controlled writes docs, and release notes to reflect Phases 0–24. Create release candidate notes for v0.0.2-prealpha. Open backlog GitHub issues.

## Scope

- No code changes.
- No git tag or GitHub release.
- Documentation and backlog only.

## Changes

### README.md

- Updated "Current status" from "Phase 0–14" to "Phase 0–24".
- Added v0.0.2-prealpha release candidate section with link to release notes.

### CHANGELOG.md

- Added `[Unreleased]` section with Phase 17–24 changes under `Added`, `Security`, and `Known limitations`.

### docs/v0.2-controlled-writes.md

- Updated "Known limitations": struck through resolved items (Phase 21 write lock, Phase 22 integration tests, Phase 23 backup restore). Added CSV export and multi-book UI notes.
- Updated "Required before enabling writes for real users": marked completed items (fixture, integration tests, file lock, backup restore). Annotated pending items.

### docs/release/v0.0.2-prealpha-notes.md

- Created release candidate notes for v0.0.2-prealpha.
- Covers Phases 17–24, safety status, known limitations, compatibility, verification commands, and related docs.

### docs/handoff/phase-25.md

- This document.

## GitHub issues opened

See verification section below.

## Verification

All checks passed:

- Backend: `cd apps/api && pytest -q` — 262 passed, 0 failed.
- Frontend: `cd apps/web && npm run check` — 0 errors.
- Frontend: `cd apps/web && npm run test:auth-routes` — passed.
- Frontend: `cd apps/web && npm run build` — success.
- Docker config: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — valid.

## Commit

Committed and pushed to origin/main.

## Blockers

None.
