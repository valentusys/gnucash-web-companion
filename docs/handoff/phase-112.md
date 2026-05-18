# Phase 112 — LAN/VPN deployment safety behavior

Date: 2026-05-19
Status: complete
Related GitHub issue: #26
PM brief: `docs/handoff/phase-112-pm-brief.md`

## Summary

Phase 112 implemented the analyst roadmap Phase 7 slice for practical LAN/VPN deployment safety behavior. The app now surfaces a non-secret CORS deployment posture check through `/health` and startup diagnostics, while preserving local development/test defaults and keeping all guidance conservative for pre-alpha read-only deployments.

## PM decision

Address GitHub #26 with operator-visible diagnostics and exact origin examples, not with a production-readiness claim or a default-breaking configuration change. Keep `CORS_ORIGINS=["*"]` usable for development, but warn when it appears outside development-like `APP_ENV` values.

## Implementation

Updated backend diagnostics:

- `apps/api/app/diagnostics.py`
  - adds `cors_deployment_posture(settings)`;
  - classifies `dev`, `development`, `local`, `test`, and `testing` as development-like;
  - reports safe fields: `wildcard_enabled`, `app_env`, `development_like_env`, `risk_level`, and `message`;
  - adds the CORS posture check and warning list to `/health` payloads;
  - logs a structured `cors_deployment_warning` only when wildcard CORS is used outside development-like environments.

Updated tests:

- `apps/api/tests/test_health.py`
  - verifies local/test wildcard defaults remain non-warning;
  - verifies production/wildcard posture returns a warning in health diagnostics;
  - verifies narrowed production origins are accepted;
  - verifies startup warning logs do not expose secrets, admin passwords, or private temp paths.

Updated docs/config examples:

- `.env.example`
  - keeps `CORS_ORIGINS=["*"]` as the development default;
  - adds exact localhost/LAN/VPN origin examples.
- `docs/deployment/local-secure-deployment.md`
  - adds a practical CORS origin narrowing section with localhost, LAN, and VPN examples;
  - states CORS is not a public-internet security boundary;
  - keeps direct public-internet exposure out of scope.
- `docs/DEVELOPMENT.md`
  - documents the new health/startup CORS posture warning.
- `CHANGELOG.md` and `PROJECT_STATUS.md` updated for Phase 112.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No write endpoints/services were changed.
- Health/startup diagnostics do not expose JWT secrets, admin passwords, database URLs, full GnuCash book paths, account names, transaction descriptions, memos, amounts, CSV data, tokens, keys, or certs.
- No public-internet, production-ready, or security-audited claim was added.
- No tag, release, or package was published.
- No real/private GnuCash books, app DBs, backups, `.env`, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, or personal financial data were committed.
- Money logic was not changed; no float money logic was added.

## Verification

Passed:

```bash
cd apps/api && pytest -q tests/test_health.py tests/test_transaction_writes.py
# 41 passed, 7 warnings

cd apps/api && pytest -q
# 349 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `.env.example`
- `apps/api/app/diagnostics.py`
- `apps/api/tests/test_health.py`
- `docs/DEVELOPMENT.md`
- `docs/deployment/local-secure-deployment.md`
- `docs/handoff/phase-112-pm-brief.md`
- `docs/handoff/phase-112.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## GitHub

- Updated and closed #26 with Phase 112 evidence if GitHub authentication remains available.

## Commit/push

- Commit: this commit (`Add CORS deployment posture diagnostics`); final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
