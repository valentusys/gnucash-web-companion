# Phase 114 PM brief — Synthetic browser dogfood refresh

Date: 2026-05-19
Roadmap source: analyst Phase 9
Related GitHub issues: #11, #12, #13, #38

## Decision

Run a current Docker/Caddy browser and API dogfood pass against generated/disposable data only. This is a practical release-value evidence phase, not an audit-only pass and not personal-book dogfood.

## Goal

Verify the current read-only UI after recent filters/books/scheduled/localization changes through local Docker/Caddy using synthetic GnuCash data, covering login, dashboard, accounts, books, scheduled awareness, transactions filters, account detail, CSV export, and disabled write probes.

## Non-goals

- Do not use or search for personal/private GnuCash books.
- Do not commit runtime generated books, app DBs, screenshots, raw CSV exports, `.env`, secrets, tokens, backups, certs, keys, or private paths.
- Do not enable `GNUCASH_WRITES_ENABLED=true`.
- Do not add write-mode scope, publish a tag/release/package, or claim production readiness/security audit/personal-book dogfood success.
- Do not broaden v0.2 controlled-write planning.

## Acceptance criteria

- Docker Compose config validates with `GNUCASH_WRITES_ENABLED=false`.
- Local Docker/Caddy starts against a synthetic/disposable GnuCash SQLite book outside committed evidence.
- Browser route dogfood proves login and core read-only pages load after authentication: dashboard, accounts, books, scheduled, transaction filters, account detail, and transaction detail where fixture data is available.
- CSV export/filter parity is checked through the authenticated UI/proxy route and API smoke path without committing export files.
- Disabled write probes for validate/create/patch return 403.
- Any dogfood failure becomes either a narrow bugfix/test in this phase or an explicit blocker in the handoff.

## Safety checks

- Keep `GNUCASH_WRITES_ENABLED=false` in runtime and docs.
- Use only generated/disposable fixture data.
- Evidence must be redacted: no screenshots, no CSV files, no tokens/cookies, no full runtime private paths in committed docs.
- Money logic remains Decimal/string; no fake currency conversion.
- Frontend still never reads GnuCash directly.

## Verification

- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- Generate/copy synthetic fixture into `/tmp` or ignored runtime data only.
- Start Docker/Caddy locally with safe env and run scripted browser/API smoke.
- `cd apps/api && pytest -q`
- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run check`
- `cd apps/web && npm run build`
- `git diff --check`

## Files/docs to update

- `scripts/smoke/read-only-browser-dogfood.py` if durable browser dogfood tooling needs to be refreshed.
- `docs/dogfood/phase-114-synthetic-browser-dogfood.md`
- `docs/handoff/phase-114.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md` if this phase produces durable tooling/evidence worth user-facing status.

## GitHub/backlog

Add concise evidence to #11/#12/#13 if authenticated because this dogfood covers the recently changed read-only filter/scheduled/books surfaces. Keep #38 open because no personal copied-book dogfood was run.
