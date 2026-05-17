# Phase 43 — Local Deployment Hardening Guide

## Status

Complete. Local secure deployment documentation was added, status/docs were synchronized, required checks passed, and the phase commit was pushed.

## PM report

### Decision

Execute exactly Phase 43 from the roadmap: add a practical local deployment hardening guide for safe localhost, LAN, and VPN-only testing.

### Why

`v0.0.2-prealpha` is now published, but the project still needs clearer operational guidance before broader dogfood/self-host use. The safest next step is documentation-only deployment hardening: explain secrets, volumes, HTTPS/reverse proxy boundaries, and write-disabled operation without adding features or expanding controlled writes.

### Phase brief

- Goal: create `docs/deployment/local-secure-deployment.md` explaining how to safely run the pre-alpha app locally or on a trusted LAN/VPN.
- Non-goals: no product code changes, no release/tag publication, no write-mode enablement, no write-scope expansion, no public-internet production guidance, no real data/screenshots/exports/secrets committed.
- Acceptance criteria:
  - Guide covers local-only deployment.
  - Guide covers LAN/VPN-only deployment.
  - Guide includes reverse proxy and HTTPS recommendations.
  - Guide explains `.env` secrets.
  - Guide explains backup volumes, app DB location, and GnuCash book location.
  - Guide explains why not to expose the app directly to the public internet.
  - Guide explains how to keep writes disabled.
  - No production guarantee is made.
  - Practical self-host instructions exist.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No real GnuCash files, `.env`, app DBs, backups, secrets, keys, tokens, screenshots, or exports are committed.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Deployment docs could overclaim production safety. Mitigation: explicit pre-alpha/no-production-guarantee language throughout.
- LAN guidance could imply public exposure is acceptable. Mitigation: guide recommends localhost first and LAN/VPN-only with HTTPS/access restrictions.
- Write mode could be normalized. Mitigation: guide keeps `GNUCASH_WRITES_ENABLED=false` as the expected setting and labels writes experimental post-MVP.

### Files/docs to update

- `docs/deployment/local-secure-deployment.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-43.md`

### GitHub/backlog

- No Phase 43-specific open GitHub issue was found.
- Existing open issues #22, #17, #13, #12, and #11 remain for later roadmap phases.

## Engineer report

Implemented Phase 43 documentation-only scope:

- Created `docs/deployment/local-secure-deployment.md`.
- Covered local-only deployment, LAN/VPN-only deployment, reverse proxy/HTTPS notes, `.env` secrets, backup/data volumes, app metadata DB location, GnuCash book location, public-internet warning, and keeping writes disabled.
- Added practical setup/start/verify/smoke-test/checklist commands.
- Updated `README.md` current status to Phase 0–43 complete and linked the deployment guide from quick-start and security/deployment sections.
- Updated `CHANGELOG.md` with a Phase 43 Unreleased entry.
- Updated `PROJECT_STATUS.md` through Phase 43 and set Phase 44 as next planned phase.
- Created this handoff file.

No product code changed. No release/tag was published. No write behavior changed.

## Verification

Passed:

- `cd apps/api && pytest -q` — passed (`269 passed`, 27 existing warnings).
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No auth localStorage/sessionStorage path was introduced.
- No real financial data, GnuCash books, `.env`, app DBs, backups, secrets, keys, tokens, certs, real screenshots, or real CSV exports were added.

## Commit / push

- Commit message: `docs: add local secure deployment guide`.
- Final commit SHA: see `git log -1 --oneline` for this phase commit.
- Push: pushed to `origin/main`.

## GitHub issue status

- No Phase 43-specific open GitHub issue found or updated.
- GitHub #22, #17, #13, #12, and #11 remain open for later roadmap work.

## Blockers

None.
