# Phase 62 Audit — Deployment Safety

## Executive summary

Phase 62 audited whether the local/self-hosted deployment documentation is safe enough for the current pre-alpha/read-only posture.

Verdict: deployment docs are acceptable for cautious local/LAN/VPN-only testing, with no release-blocking safety contradiction found. The docs repeatedly warn against direct public-internet exposure, require a strong JWT secret, recommend HTTPS/VPN/LAN-only access, document Docker data locations, and distinguish the app metadata DB from copied GnuCash books.

One non-blocking hardening item was created: GitHub #26 tracks making the `CORS_ORIGINS=["*"]` development default harder to miss before shared LAN/VPN deployments. This is not a Phase 62 blocker because the existing deployment guide already warns operators to narrow CORS before shared deployment and not expose the app publicly.

## Verdict

No deployment-safety blocker found for local/private read-only testing; v0.1 publication remains blocked by earlier release-note and runtime dogfood evidence gates (#24, #25), not by Phase 62 deployment docs.

## Blockers

None found in the Phase 62 deployment-safety scope.

Carried forward from previous phases and still release-blocking before `v0.1.0-readonly` publication:

1. GitHub #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. GitHub #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

## Non-blockers

1. `.env.example` and `docker-compose.yml` use `CORS_ORIGINS=["*"]` as a development-friendly default. Existing docs warn to narrow it before shared LAN/VPN deployment. Tracked as GitHub #26 for release-note/checklist visibility.
2. `docker-compose.yml` publishes the proxy as `8080:80` by default. The deployment guide explicitly gives a localhost-only override and warns not to publish the port directly to the public internet.
3. `.env.example` leaves `APP_ADMIN_PASSWORD` blank and recommends `APP_ADMIN_PASSWORD_HASH` for non-local use. This is safer than a hardcoded default password, but operators must still set a real secret locally.

## Phase 62 audit checks

| Roadmap check | Evidence found | Result |
| --- | --- | --- |
| `.env.example` has safe defaults | `GNUCASH_WRITES_ENABLED=false`; JWT secret is a placeholder that docs say is intentionally rejected; admin password is blank; app DB path is separate from GnuCash book path. CORS wildcard is development-friendly and documented as something to narrow. | Pass with non-blocking CORS follow-up (#26) |
| JWT secret warnings are clear | `.env.example`, README quick start, deployment guide, and auth-cookie deployment doc all require replacing the placeholder with a long random value. | Pass |
| Default password warnings are clear | `.env.example` leaves `APP_ADMIN_PASSWORD` blank; deployment docs say prefer `APP_ADMIN_PASSWORD_HASH` for non-local use and treat `.env` as secret. | Pass |
| Public internet exposure warning exists | README, `docs/deployment/local-secure-deployment.md`, and `docs/security/auth-cookie-deployment.md` explicitly warn not to expose directly to the public internet. | Pass |
| HTTPS/VPN/LAN recommendation exists | Deployment guide recommends localhost first, LAN/VPN-only for private-network testing, HTTPS for non-local access, and VPN for remote access. | Pass |
| Docker volumes are documented | Deployment guide documents default `./data:/data` mount and host/container paths for `data/app`, `data/books`, `data/backups`, and `data/locks`. | Pass |
| Backup locations are documented | Deployment guide and backup/recovery runbook document app DB, copied books, controlled-write backups, and restore dry-runs. | Pass |
| App DB vs GnuCash book DB distinction is clear | `.env.example`, README architecture, deployment guide, backup runbook, and AGENTS.md distinguish `/data/app/app.db` from `/data/books/*.gnucash.sqlite`. | Pass |
| Docs imply public exposure is safe | No. Docs say the opposite. | Pass |
| Secrets are weak or hardcoded | No committed real secret found in inspected deployment docs. Placeholder JWT secret is documented as unsafe and rejected; no default admin password is set. | Pass |
| Writes appear easy to enable casually | Existing docs repeatedly say keep `GNUCASH_WRITES_ENABLED=false`; controlled writes are experimental/post-MVP only. | Pass |

## Product consistency

Checked files and state:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `.env.example`
- `docker-compose.yml`
- `apps/api/app/config.py`
- `docs/release/v0.1.0-readonly-plan.md`
- `docs/release/v0.1.0-readonly-checklist.md`
- `docs/deployment/local-secure-deployment.md`
- `docs/operations/backup-and-recovery.md`
- `docs/security/auth-cookie-deployment.md`
- `docs/handoff/phase-61.md`
- auditor roadmap Phase 62 entry
- open GitHub issues via `gh issue list`

Findings:

- Public docs still position the project as pre-alpha, self-hosted, read-only by default, and not production-ready/security-audited.
- No inspected doc reframes the project as SaaS, a GnuCash replacement, collaborative accounting, or safe write-mode software.
- Phase 62 does not unblock `v0.1.0-readonly` publication because #24 and #25 remain open.

## Safety boundary

Findings:

- `apps/api/app/config.py` keeps `gnucash_writes_enabled: bool = False`.
- `.env.example` and `docker-compose.yml` keep `GNUCASH_WRITES_ENABLED=false` as the default.
- Controlled writes remain documented as experimental/post-MVP only.
- GnuCash Desktop remains documented as the authoritative editor.
- No product code changed in this phase.
- No real GnuCash book, `.env`, app DB, backup, secret, key, cert, real screenshot, or real financial CSV export was added by this phase.

## Release/readme/docs consistency

README and PROJECT_STATUS should be updated to record Phase 62 as a deployment-safety audit. This must not imply the project is ready for public-internet exposure or that v0.1 can be published.

CHANGELOG may record the Phase 62 release-facing audit result because deployment-safety posture is relevant to future `v0.1.0-readonly` release notes.

## GitHub project hygiene

Open issues reviewed via `gh issue list`:

- #25 — copied/disposable-data runtime smoke/dogfood gate.
- #24 — conservative v0.1 release notes.
- #22, #17, #13, #12, #11 — non-blocking backlog previously triaged for v0.1.

Created:

- #26 — Document CORS origin narrowing for LAN/VPN deployments: https://github.com/valentusys/gnucash-web-companion/issues/26

No duplicate issue was created for the already-known release blockers #24 and #25.

## Security notes

This was not a professional security audit. It was a deployment-safety documentation audit.

The inspected docs correctly warn that:

- the app is pre-alpha and not production-ready/security-audited;
- direct public-internet exposure is not safe;
- HTTPS should be used for non-local access;
- LAN/VPN-only access is the intended private deployment posture;
- JWT secret and admin credentials must be treated as secrets;
- `.env`, app DBs, copied books, backups, screenshots, CSV exports, logs with sensitive values, keys, certs, and real financial data must not be committed or attached to public reports.

## Test/CI notes

Phase 62 is audit/status documentation work with no product-code changes. Because it reports a deployment/readiness verdict, the phase should run and record the standard checks:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

Final check results are recorded in `docs/handoff/phase-62.md`.

## Recommended next actions

1. Do not publish `v0.1.0-readonly` from Phase 62.
2. Keep #24 and #25 as release blockers before v0.1 publication.
3. Update README/PROJECT_STATUS/handoff to record the Phase 62 deployment-safety audit result.
4. Use #26 to make CORS origin narrowing visible in future v0.1 release notes/checklists or deployment hardening docs.
5. Keep direct public-internet exposure out of scope; prefer localhost, LAN, or VPN with HTTPS for non-local access.

## Suggested GitHub issues

Created:

1. #26 — Document CORS origin narrowing for LAN/VPN deployments: https://github.com/valentusys/gnucash-web-companion/issues/26

Suggested: none beyond #26. Existing #24 and #25 remain the release blockers.

## What not to do next

- Do not publish a `v0.1.0-readonly` tag or GitHub release from Phase 62.
- Do not claim public-internet deployment is safe.
- Do not weaken `JWT_SECRET`, admin credential, CORS, HTTPS, VPN/LAN, or backup warnings.
- Do not enable or expand controlled writes.
- Do not commit `.env`, copied books, app DBs, backups, screenshots, CSV exports, secrets, keys, tokens, or certs.
- Do not start Phase 63 without an explicit request.
