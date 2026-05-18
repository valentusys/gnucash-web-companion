# Phase 66 Audit — Security Posture

Date: 2026-05-18

## Executive summary

Phase 66 reviewed the repository security posture without treating this as a professional security audit. The core conservative posture is intact: the project still says pre-alpha, not production-ready, not security-audited, read-only by default, and controlled writes remain experimental/post-MVP and disabled by default.

No evidence was found that auth tokens are stored in browser localStorage/sessionStorage, and the SvelteKit login flow sets the auth cookie with `httpOnly: true`. `JWT_SECRET` is not hardcoded as an active usable secret; the documented placeholder is rejected by the backend before login.

One meaningful security-hardening finding was identified: default-book seeding logs the full configured GnuCash book path/URI. That can expose local filesystem layout or connection URI details in logs and should be fixed before broader/shared deployments. This was filed as GitHub #27. The already-known CORS wildcard development default remains tracked as GitHub #26.

## Verdict

Ready to continue pre-alpha security hardening; not a professional security audit; not ready to claim audited security.

`v0.1.0-readonly` publication remains blocked by the carried-forward release gates #24 and #25. Phase 66 adds one security-hardening issue (#27) that should be resolved or explicitly accepted before any broader/shared deployment posture is presented as hardened.

## Top blockers

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.
3. #27 — default-book seed logging currently includes the full configured GnuCash book path/URI; logs should use a non-sensitive filename/redacted summary instead.

## Important non-blockers

1. #26 — `CORS_ORIGINS=["*"]` remains a development-friendly default with deployment docs warning operators to narrow origins before shared LAN/VPN deployments. This remains a non-blocking hardening/release-visibility item unless PM changes the release gate.
2. Theme preference uses `localStorage` in `apps/web/src/lib/theme.ts` and `apps/web/src/app.html`; the auth-route static check explicitly permits this only for theme preference and asserts those files do not reference `access_token`.
3. The smoke script stores a bearer token in process memory only for API calls and does not print the token/password. This is acceptable for a local copied/disposable-data smoke script.

## Product consistency

The audited docs keep the expected positioning:

- MVP is read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes are experimental/post-MVP only.
- GnuCash Desktop remains the authoritative editor.
- The project is not SaaS, not a GnuCash replacement, and not collaborative accounting.
- No production-ready or security-audited claim was found in README, SECURITY.md, release docs, or current handoff/status docs.

## Safety boundary

Security posture checks did not find a write-scope expansion:

- `apps/api/app/config.py` has `gnucash_writes_enabled: bool = False`.
- `.env.example` sets `GNUCASH_WRITES_ENABLED=false`.
- Release docs continue to say controlled writes are post-MVP and disabled by default.
- Phase 66 did not publish a release, enable writes, add write routes/UI, or add product feature work.

## Auth and token storage

Findings:

- `apps/web/src/routes/login/+page.server.ts` sets `access_token` using a SvelteKit cookie with `httpOnly: true`, `sameSite: 'lax'`, `path: '/'`, and `secure` depending on HTTPS protocol.
- `apps/web/scripts/test-auth-routes.mjs` checks that login stores the token in a cookie and does not use browser storage.
- Static search found `localStorage` only in theme-related files and auth-route tests; no auth-token localStorage/sessionStorage path was found.
- Backend auth error messages are generic for invalid credentials/token cases.
- JWT logout remains stateless and documented as such; this is a known limitation, not a hidden guarantee.

## JWT secret and admin password posture

Findings:

- `apps/api/app/config.py` defaults `jwt_secret` to an empty string.
- `.env.example` contains the placeholder `JWT_SECRET=change-me-use-a-long-random-secret` with replacement instructions.
- `apps/api/app/services/auth.py` rejects empty/change-me placeholder JWT secrets via `require_configured_jwt_secret()` before login/token validation.
- `.env.example` leaves `APP_ADMIN_PASSWORD=` blank and recommends `APP_ADMIN_PASSWORD_HASH` for non-local use.
- Seeding logs whether the hash or plaintext bootstrap source was used, but does not log the password or hash value.

## CORS posture

Findings:

- `apps/api/app/config.py`, `.env.example`, and `docker-compose.yml` still default CORS origins to `["*"]` for development convenience.
- `apps/api/app/main.py` applies `allow_credentials=True` together with configured CORS origins.
- `docs/deployment/local-secure-deployment.md` warns operators to narrow CORS origins before shared LAN/VPN deployment.
- GitHub #26 already tracks making this origin-narrowing requirement more visible; Phase 66 updated #26 rather than creating a duplicate issue.

Verdict on CORS: acceptable only for current pre-alpha/local development posture because warnings exist and #26 tracks hardening. Do not present this as production-ready or broadly hardened.

## Logs and error-message review

Findings:

- `apps/api/app/diagnostics.py` intentionally emits non-sensitive startup diagnostics: app env, degraded/ok state, app database backend/name, default-book filename only, and writes-enabled flag.
- `apps/api/app/services/auth.py` seed logs include username and credential-source type, but not token/password/hash values.
- `apps/api/app/services/seed.py` logs the full seeded default book path/URI with `book.uri_or_path`. This is a real hardening gap because file paths or DB URIs can expose sensitive deployment structure in logs.
- No obvious logs printing JWT tokens, admin passwords, or Authorization headers were found in the searched backend/frontend code paths.

## Dependency/security-scanning readiness

Dependency files exist for future security scanning:

- `apps/api/pyproject.toml`
- `apps/api/requirements.txt`
- `apps/web/package.json`
- `apps/web/package-lock.json`

Phase 66 did not run a full dependency vulnerability scan and does not claim dependency security has been audited.

## Release/readme/docs consistency

- README current status was at Phase 65 before this phase and still correctly described the project as pre-alpha and not production-ready.
- SECURITY.md says the project has not undergone a security audit and warns against public exposure/production deployment.
- Release planning docs explicitly prohibit production-readiness/audited-security claims.
- After Phase 66, README/PROJECT_STATUS/CHANGELOG/handoff should be synchronized to point at this audit.

## GitHub project hygiene

Reviewed open issues with `gh issue list`:

- #24 and #25 remain v0.1 publication blockers.
- #22 remains compatibility follow-up.
- #26 remains CORS origin narrowing visibility/hardening.
- #17/#13/#12/#11 remain existing non-blocking backlog items.

Created:

- #27 — Avoid logging full GnuCash book paths during default book seed.

Updated:

- #26 — commented with Phase 66 CORS audit result and kept open.

## Security notes

This audit is a focused repository posture review, not a professional penetration test, secure code review, threat model, or dependency vulnerability audit. The project must continue to say it has not been security-audited.

## Test/CI notes

The relevant Phase 66 checks should include:

- backend pytest suite;
- frontend `npm run check`, `npm run test:auth-routes`, and `npm run build`;
- Docker Compose config validation;
- `git diff --check`.

Results are recorded in `docs/handoff/phase-66.md`.

## Recommended next actions

1. Keep #24/#25 as v0.1 publication blockers.
2. Fix #27 by redacting/sanitizing default-book seed logs and adding/adjusting tests for path/secret-safe logging.
3. Keep #26 open until CORS origin narrowing is visible enough in release/deployment docs or defaults are changed.
4. Do not claim the project is security-audited after this phase.
5. Continue to require copied/disposable-data runtime smoke evidence before any `v0.1.0-readonly` release.

## Suggested / created GitHub issues

Created:

- #27 — Avoid logging full GnuCash book paths during default book seed (`security`, `audit`, `safety`).

Updated:

- #26 — Document CORS origin narrowing for LAN/VPN deployments.

No other new issue was created because CORS is already tracked and the remaining release blockers are already tracked by #24/#25.

## What not to do next

- Do not publish `v0.1.0-readonly` while #24/#25 are unresolved.
- Do not describe Phase 66 as a security audit certification.
- Do not expand controlled-write scope or enable writes by default.
- Do not hide #27 under general release wording; either fix it or explicitly accept it as a known security-hardening risk.
- Do not create noisy duplicate issues for already-tracked CORS/release-gate work.
