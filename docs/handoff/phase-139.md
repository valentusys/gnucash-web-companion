# Phase 139 — Synthetic dogfood refresh

Date: 2026-05-19
Status: DONE

## Goal

Run a full synthetic local Docker/Caddy dogfood pass after the Phase 133–138 read-only UX, docs, compatibility, and deployment-hardening changes.

## Scope completed

- Started local Docker Compose/Caddy against the existing synthetic/disposable runtime fixture with `GNUCASH_WRITES_ENABLED=false`.
- Validated Docker Compose configuration with dummy secrets.
- Ran `scripts/smoke/read-only-api-smoke.py` against `http://127.0.0.1:8080/api`.
- Ran `scripts/smoke/read-only-browser-dogfood.py` against `http://127.0.0.1:8080`.
- Covered core UI paths:
  - login;
  - protected redirect to login;
  - dashboard;
  - accounts;
  - books;
  - scheduled transactions;
  - transactions list with filters;
  - account detail;
  - transaction detail;
  - CSV export through the authenticated browser/proxy route.
- Verified write UI stayed hidden on checked pages and write probes stayed disabled with `GNUCASH_WRITES_ENABLED=false`.
- Documented redacted evidence in `docs/dogfood/phase-139-synthetic-dogfood.md`.
- Updated `PROJECT_STATUS.md` for Phase 139.

## Non-goals / safety boundaries

- No real/private GnuCash book was used.
- No backend code changed.
- No frontend code changed.
- No tests were changed because this was a dogfood-only phase with no behavior/code change.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remained the runtime and documented default.
- No release, tag, package, or publication was performed.
- No screenshots, raw CSV exports, app DBs, GnuCash books, backups, `.env`, tokens, keys, certs, private paths, or real/private financial data were added or committed.
- Docs remain honest: pre-alpha/private testing, test copies first, no production guarantee, no security-audit claim, no real/private-book write-safety claim.

## Verification

- Initial git state checked first:
  - branch: `main`;
  - starting HEAD: `6e1a7ec9270a3c1615557f33ddd38dc428e570c5`;
  - pre-existing untracked `.hermes/` local agent logs were not touched or committed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false API_INTERNAL_URL=http://api:8000 ORIGIN=http://127.0.0.1:8080 docker compose up -d --build` — passed.
- `curl -fsS http://127.0.0.1:8080/api/health` — passed; `writes_enabled=false`, default synthetic book exists/readable.
- `APP_ADMIN_PASSWORD=dummy SMOKE_ADMIN_PASSWORD=dummy SMOKE_API_BASE_URL=http://127.0.0.1:8080/api scripts/smoke/read-only-api-smoke.py` — passed.
- `SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-browser-dogfood.py --base-url http://127.0.0.1:8080 --fixture-path data/books/main.gnucash.sqlite` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose down` — passed after supplying required compose interpolation env.

## Operational notes

- The pre-existing ignored local `data/app/app.db` had an admin credential that did not match the requested dummy password; it was backed up outside git, the disposable dogfood app DB was regenerated for the smoke run, and the previous ignored app DB was restored after Docker shutdown.
- A browser retry was needed after aligning `ORIGIN` with the actual dogfood host (`http://127.0.0.1:8080`) to satisfy SvelteKit's cross-site form protection. This was an environment mismatch, not a product code issue.

## Expected artifacts

- `docs/dogfood/phase-139-synthetic-dogfood.md`
- `docs/handoff/phase-139.md`
- `PROJECT_STATUS.md`

## GitHub / release state

- No release/publication gate was executed for this phase.
- No tag or GitHub release was created.
- Phase 139 should be committed as a single documentation/evidence commit and pushed to `origin/main`.
