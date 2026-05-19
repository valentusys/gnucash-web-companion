# Phase 167 — Auth/session hardening for local/LAN pre-alpha

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 6/10 only)

## Goal

Harden auth/session defaults and operator feedback for local/LAN pre-alpha use without claiming production security audit.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-166.md`;
  - roadmap phase 6 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 167 only; no neighboring roadmap phases were started.
- Reviewed auth/session behavior for:
  - httpOnly login cookie flags;
  - logout cookie deletion;
  - session expiry behavior;
  - state-changing app routes;
  - placeholder JWT and CORS warning documentation.
- Implemented narrow hardening where gaps were found:
  - SvelteKit now rejects unsafe state-changing app-route requests when a browser `Origin` header is present and does not match the current app origin;
  - safe methods (`GET`, `HEAD`, `OPTIONS`) and originless local probes remain allowed;
  - the web login cookie max-age now follows `JWT_TOKEN_EXPIRE_MINUTES` with a 30-minute fallback instead of a hard-coded value;
  - Docker Compose passes `JWT_TOKEN_EXPIRE_MINUTES` to the web service as well as the API.
- Added/pinned tests:
  - backend auth test for expired JWT rejection;
  - frontend static auth-route checks for httpOnly cookie handling, no auth browser storage, same-origin unsafe-route guard, and configured auth cookie lifetime.
- Updated `docs/security/auth-cookie-deployment.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Production writes were not enabled.
- No OAuth/SSO or multi-user role expansion was added.
- No production-readiness or security-audited claim was added.
- Auth token remains stored only in the httpOnly `access_token` cookie.
- No auth token/local session state was added to `localStorage` or `sessionStorage`.
- Placeholder JWT secret rejection remains in place.
- CORS wildcard warnings for non-development LAN/VPN posture remain documented.
- No `.env`, token, key, cert, real/private GnuCash book, app DB, backup, screenshot/export, private path, account name, transaction description, memo, amount, or private financial data was committed.

## Verification

```bash
cd apps/api && pytest tests/test_auth.py -q
cd apps/web && npm run test:auth-routes
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted backend auth tests passed.
- Frontend auth/static route checks passed.
- Backend full suite passed.
- Frontend `npm run check` passed.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `apps/api/tests/test_auth.py`
- `apps/web/src/hooks.server.ts`
- `apps/web/src/routes/login/+page.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docker-compose.yml`
- `docs/security/auth-cookie-deployment.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-167.md`
