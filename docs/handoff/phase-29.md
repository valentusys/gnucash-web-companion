# Phase 29 — Audit-Driven Release Documentation Sync

## Status

Complete.

## Goal

Run the required independent audit cycle before Phase 29 and, because the audit found release/status documentation blockers, fix those accepted blockers instead of expanding product features.

## PM decision

Prioritize documentation/release-state consistency over new feature work.

Reason: the audit found no read-only/default-write safety regression, but public docs were stale after Phases 26–28. That can mislead reviewers before the next pre-alpha candidate review.

## Scope

- Documentation and project-status updates only.
- No production code changes.
- No write-path changes.
- No tag or GitHub release publication.
- No real financial data, GnuCash books, app DBs, backups, secrets, tokens, keys, certs, or real screenshots.

## Audit summary

Audit report: `docs/audits/2026-05-17-audit.md`

Verdict before Phase 29 fixes: **Ready only after blockers are fixed**.

Top blockers accepted for immediate fix:

1. Public release/status docs lagged behind completed Phases 26–28.
2. `docs/handoff/phase-28.md` still had a pending commit placeholder.

GitHub issues: no new issue created; the documentation drift was fixed immediately as Phase 29.

## Changes

### docs/audits/2026-05-17-audit.md

- Refreshed the independent audit report for the current repo state.
- Recorded that `v0.0.1-prealpha` exists and `v0.0.2-prealpha` is not published.
- Identified stale README/CHANGELOG/roadmap/release-candidate notes as the release blocker.
- Confirmed `GNUCASH_WRITES_ENABLED=false` remained the default in `.env.example` and `docker-compose.yml`.

### README.md

- Advanced current status from Phase 0–25 to Phase 0–29.
- Added link to the latest audit report.

### CHANGELOG.md

- Added Unreleased entries for Phases 25–29.
- Added Phase 29 audit refresh under Security.
- Added the compatibility-matrix limitation to Known limitations.

### docs/release/v0.0.2-prealpha-notes.md

- Expanded the candidate overview from Phases 17–24 to Phases 17–29.
- Added documentation/audit/release-readiness items for Phases 25–29.
- Replaced the stale compatibility TBD language with the current synthetic-fixture compatibility baseline and explicit untested backend/version limitations.

### docs/ROADMAP.md

- Reworked the stale roadmap so `v0.0.1-prealpha` is no longer described as the next unpublished step.
- Added current release posture and grouped completed phases through Phase 29.
- Kept next work focused on read-only MVP/release-readiness items.

### PROJECT_STATUS.md

- Advanced the baseline through Phase 29.
- Added Phase 29 summary and artifacts.

### docs/handoff/phase-28.md

- Replaced the stale pending commit placeholder with commit `343e098`.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default setting.
- No production code changes.
- No write-path changes.
- No release/tag/package publication.
- No real financial data or secrets added.
- Release language remains conservative: pre-alpha, not production-ready, not security-audited, test/disposable copies first.

## Verification

- Backend: `cd apps/api && pytest -q` — 264 passed, 27 warnings.
- Frontend: `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — OK.
- Docker config: `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — OK.

## Commit

This handoff is included in the Phase 29 commit; see final report or `git log -1` for the pushed hash.

## GitHub

- No new issue created.
- Existing read-only/release backlog remains open: #11, #12, #13, #14, #17.
- No tag or release published.

## Blockers

None after the accepted audit documentation blockers are fixed.
