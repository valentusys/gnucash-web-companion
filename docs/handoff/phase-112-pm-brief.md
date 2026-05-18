# Phase 112 PM brief — LAN/VPN deployment safety behavior

Date: 2026-05-19
Status: planned
Related GitHub issue: #26
Roadmap source: analyst Phase 7 of 10

## Decision

Implement Phase 112 as a narrow operator-facing deployment safety slice: keep local development defaults usable, but make risky wildcard CORS posture visible through safe health/startup diagnostics and deployment docs with exact LAN/VPN origin examples.

## Why

GitHub #26 has been tracked as a non-blocking deployment-hardening item because `CORS_ORIGINS=["*"]` remains a development-friendly default. Existing docs warn operators to narrow origins, but the running app does not currently surface a practical warning when the same wildcard posture is used outside a development-like environment.

## Phase brief

- Goal: Add non-secret backend diagnostics/warnings for wildcard CORS outside development-like environments and document exact LAN/VPN origin narrowing examples.
- Non-goals: No production-readiness claim, no release/tag publication, no auth redesign, no public-internet deployment support, no write-mode changes, no frontend GnuCash file access, no storage of private deployment origins beyond normal env config.
- Acceptance criteria:
  - `/health` includes a safe CORS deployment posture check without exposing secrets, JWTs, passwords, database URLs, full GnuCash paths, or private tokens.
  - Startup diagnostics log a clear warning when `CORS_ORIGINS` contains `*` while `APP_ENV` is not development-like.
  - Development/test/local defaults remain usable and do not emit the risky-posture warning as an error.
  - `.env.example` remains usable for local development but points operators to exact LAN/VPN origin examples.
  - Deployment docs explain how to narrow CORS to exact browser origins such as localhost, LAN HTTP/HTTPS hostnames, and VPN hostnames; docs continue to warn against direct public-internet exposure.
- Safety checks:
  - Preserve `GNUCASH_WRITES_ENABLED=false` default and do not touch write endpoints/services.
  - Do not log secrets, JWTs, admin passwords, app DB URLs, full private book paths, account names, transaction descriptions, amounts, memos, or CSV data.
  - Do not imply that CORS narrowing alone makes the app production-ready or safe for public internet exposure.
  - Do not commit `.env`, app DBs, GnuCash books, backups, screenshots, exports, certs, tokens, keys, or real/private financial data.
- Verification:
  - `cd apps/api && pytest -q tests/test_health.py tests/test_transaction_writes.py`
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

## Risks

- A warning that is too aggressive could break local development expectations; keep the risky warning tied to wildcard CORS plus non-development-like `APP_ENV`.
- Health/startup diagnostics must remain redacted and operationally useful without leaking private origins beyond the configured origin strings themselves.
- Docs must avoid suggesting that CORS is a security boundary for public internet exposure.

## Files/docs to update

- `apps/api/app/diagnostics.py`
- `apps/api/tests/test_health.py`
- `.env.example`
- `docs/deployment/local-secure-deployment.md`
- `docs/DEVELOPMENT.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-112.md`

## GitHub/backlog

- Update GitHub #26 with Phase 112 evidence if `gh` is authenticated.
- Close #26 only if diagnostics, docs, and tests provide practical operator visibility for origin narrowing while preserving local defaults.
