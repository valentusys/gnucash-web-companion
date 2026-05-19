# Phase 137 — Local Secure Deployment Hardening Guide

Date: 2026-05-19
Status: DONE

## Goal

Update and expand the safe deployment guide for conservative localhost, LAN, and VPN self-hosting scenarios.

## Scope completed

- Updated `docs/deployment/local-secure-deployment.md`:
  - added explicit recommended `CORS_ORIGINS` values for localhost-only, trusted LAN HTTP, and VPN/private HTTPS deployments;
  - added JWT secret generation guidance, safe handling expectations, and conservative stop-change-start rotation procedure;
  - documented app metadata DB backup expectations for `data/app/app.db`, separate from GnuCash book backups;
  - expanded the pre-deployment checklist into concrete, verifiable self-hosting checks.
- Updated `.env.example` comments:
  - clarified that `JWT_SECRET` must be freshly generated and rotated after exposure or shared-environment changes;
  - gave exact CORS examples for localhost, LAN, and VPN/private HTTPS testing.
- Updated `PROJECT_STATUS.md` through Phase 137.

## Non-goals / safety boundaries

- No backend code changed.
- No frontend code changed.
- No endpoints, routes, services, schemas, or Docker runtime defaults were added or changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/read-only default.
- No release, tag, package, or publication was performed.
- No real/private GnuCash books, app DBs, backups, `.env`, tokens, keys, screenshots, exports, private paths, or private financial data were added or committed.
- Docs remain honest: pre-alpha/private testing, test copies first, no production guarantee, no security-audit claim.

## Verification

- `cd apps/api && pytest tests/test_health.py -q` — passed (`6 passed, 1 warning`).
- `cd apps/api && pytest -q` — passed (`377 passed, 32 warnings`).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Safety checks — passed: changed docs/config example contain no real secrets, `.env`, app DB, GnuCash book, backup, screenshot/export, token/key material, or production-readiness claims.

## Expected artifacts

- `docs/deployment/local-secure-deployment.md`
- `.env.example`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-137.md`

## GitHub / release state

- No release/publication gate was executed for this phase.
- No tag or GitHub release was created.
- Push `main` after all verification passes and the single Phase 137 commit is created.
