# Phase 40 — v0.0.2-prealpha Release Candidate Cleanup

## Status

Complete. Release-candidate docs updated; no tag/release published; checks passed; commit/push completed.

## PM report

### Decision

Execute exactly Phase 40 from the roadmap as a release-candidate documentation cleanup phase for `v0.0.2-prealpha`.

### Why

Phase 39 added read-only smoke automation. The next safest step before any pre-alpha publish action is to make the candidate checklist and notes honest, current, and explicit about the release gate, without expanding scope or publishing a release.

### Phase brief

- Goal: prepare `v0.0.2-prealpha` release-candidate docs.
- Non-goals: no tag, no GitHub release, no product feature work, no write enablement, no write-scope expansion, no real data/screenshots/exports/secrets committed.
- Acceptance criteria:
  - `docs/release/v0.0.2-prealpha-checklist.md` exists.
  - `docs/release/v0.0.2-prealpha-notes.md` is current through Phase 40.
  - `README.md` and `CHANGELOG.md` reflect the candidate cleanup honestly.
  - Docs state pre-alpha, not production-ready, read-only by default, controlled writes experimental and disabled.
  - `PROJECT_STATUS.md` is synchronized through Phase 40 and points to Phase 41 release gate next.
  - GitHub issue #20 is updated if `gh` is available.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the safe/default documented state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No release/tag is created in Phase 40.
  - No real GnuCash book, `.env`, app DB, backup, secret, token, key, screenshot, or export is committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Release notes could overclaim readiness. Mitigation: checklist and notes explicitly say pre-alpha, not production-ready, not security-audited, release-gate required, no tag/release in Phase 40.
- Candidate docs could drift from actual completed phases. Mitigation: synchronized README, CHANGELOG, PROJECT_STATUS, checklist, and notes through Phase 40.
- Live smoke script is deployment-dependent. Mitigation: documented as optional local deployment smoke requiring a running Docker deployment and copied/disposable book, not a Phase 40 blocker.

### Files/docs to update

- `docs/release/v0.0.2-prealpha-checklist.md`
- `docs/release/v0.0.2-prealpha-notes.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-40.md`

### GitHub/backlog

- GitHub #20 tracks preparing `v0.0.2-prealpha`; update with Phase 40 status.
- Phase 41 remains the release-gate audit. Do not publish `v0.0.2-prealpha` until that gate passes and the explicit release phase runs.

## Engineer report

Implemented Phase 40 documentation/release-candidate cleanup only:

- Created `docs/release/v0.0.2-prealpha-checklist.md` with:
  - scope and explicit exclusions;
  - safety hardening since `v0.0.1-prealpha`;
  - required Phase 41 release-gate language;
  - automated check commands;
  - optional local read-only smoke command;
  - release command placeholder explicitly marked as not for Phase 40.
- Updated `docs/release/v0.0.2-prealpha-notes.md` through Phase 40:
  - added Phases 37–40 to the candidate story;
  - added dogfood/smoke documentation context;
  - clarified that no tag/release is created in Phase 40;
  - added release-gate and optional local smoke verification language.
- Updated `README.md`:
  - current status advanced to Phase 0–40 complete;
  - linked the `v0.0.2-prealpha` checklist and notes;
  - preserved “no tag/GitHub release published yet” language.
- Updated `CHANGELOG.md` with Phase 40 Unreleased entry.
- Updated `PROJECT_STATUS.md`:
  - baseline advanced through Phase 40;
  - next planned phase set to Phase 41 release-gate audit;
  - Phase 40 artifact/safety/check summary added.

No product code changed. No release/tag was created. No write behavior changed.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

Not run:

- Optional live local read-only smoke script was not run because it requires a running local Docker deployment plus local admin password/book setup. This is documented as a deployment-time smoke check and is not a Phase 40 blocker.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No auth localStorage/sessionStorage path was introduced.
- No release/tag was published.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, certs, real screenshots, or real CSV exports were added.

## Commit / push

- Commit message: `docs: prepare v0.0.2-prealpha candidate cleanup`.
- Final commit SHA: see `git log -1 --oneline` for this phase commit.
- Push: pushed to `origin/main`.

## GitHub issue status

- GitHub #20 updated with Phase 40 status.
- GitHub #18 and #22 intentionally remain open for separate scopes.

## Blockers

None.
