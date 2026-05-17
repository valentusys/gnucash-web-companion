# Phase 27 — Discoverability and Community Announcement Readiness

## Status

Complete.

## Goal

Implement the discoverability issue from the pre-Phase-26 audit so the repository is clearer for GnuCash/self-hosted visitors before any wider announcement.

## Scope

- README/community documentation and GitHub metadata only.
- No production code changes.
- No release/tag publication.
- No marketing as production-ready.

## Changes

### README.md

- Added a short project pitch.
- Added “Who this is for / not for”.
- Added comparison with:
  - `gnucash-web`
  - GnuDash
  - Fava/Beancount
- Linked community/draft materials.

### docs/community/announcement-draft.md

- Added a conservative announcement draft.
- Includes pre-alpha, read-only-by-default, not-production-ready, not-security-audited, and test-copy-first warnings.
- Explicitly says controlled writes are experimental post-MVP and disabled by default.

### docs/community/social-preview.md

- Documented GitHub social preview as a manual repository setting.
- Added safety checklist to avoid real financial data, secrets, private URLs, and production/safety claims.

### GitHub topics

Configured repository topics:

- `gnucash`
- `personal-finance`
- `accounting`
- `self-hosted`
- `sveltekit`
- `fastapi`
- `open-source`
- `finance`
- `sqlite`

### PROJECT_STATUS.md

- Advanced baseline through Phase 27.
- Added summaries for Phase 26 and Phase 27.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the documented default.
- No code changes or write-path changes.
- No real financial data, screenshots, secrets, tokens, app DBs, backups, keys, or certs added.
- Social preview remains documented as manual setup with a synthetic-data-only checklist.
- No release/tag created.

## Verification

- Backend: `cd apps/api && pytest -q` — 262 passed, 27 warnings.
- Frontend: `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — 0 errors, auth route checks passed, production build succeeded.
- Docker config: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — valid.
- GitHub topics: configured and verified through GitHub API.

## Commit

Committed and pushed to origin/main. Final commit hash is recorded in the phase report.

## GitHub

- Related issue: #16 Improve project discoverability before wider announcement.
- Expected state after commit: issue #16 can be closed as completed.

## Blockers

None.
