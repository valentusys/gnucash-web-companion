# Phase 226 handoff — Read-only regression after write-alpha remediation

Date: 2026-05-21
Status: COMPLETE — default-read-only Docker/Caddy API and browser regression passed after write-alpha backup/evidence remediation.

## Summary

Phase 226 stayed within the Cycle 3 Phase 5 contract. It ran the full default-read-only product path with Docker/Caddy, the committed synthetic fixture copied into ignored runtime storage, and `GNUCASH_WRITES_ENABLED=false` rendered for both API and web services.

API smoke passed health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, scheduled metadata, write-alpha audit summary, and disabled validate/create/PATCH/DELETE probes returning 403. Browser dogfood passed at both `320x720` and `1280x900` with write UI hidden, auth cookie not readable from `document.cookie`, CSV fetch success without saved raw artifact, no horizontal overflow, and no screenshot/download/export artifacts.

No write-enabled run was performed.

## Files changed

- `docs/dogfood/phase-226-default-readonly-regression.md` — redacted default-read-only regression evidence.
- `docs/handoff/phase-226.md` — this handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — phase status synchronized.

No product code or smoke helper code was changed in this phase.

## Verification performed

Dogfood / smoke evidence:

- Stopped-runtime cleanup before setup — passed with zero starting runtime artifacts.
- Copied committed synthetic fixture to ignored `data/books/phase-226-synthetic.gnucash.sqlite`.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 GNUCASH_DEFAULT_BOOK_PATH=/data/books/phase-226-synthetic.gnucash.sqlite GNUCASH_WRITES_ENABLED=false docker compose config --quiet` — passed.
- Rendered Compose grep for `GNUCASH_WRITES_ENABLED: "false"` — passed for API and web services.
- Docker/Caddy default-read-only runtime — built and started healthy.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py` — passed.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 320 --viewport-height 720 --fixture-path data/books/phase-226-synthetic.gnucash.sqlite` — passed.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-browser-dogfood.py --base-url http://localhost:8080 --viewport-width 1280 --viewport-height 900 --fixture-path data/books/phase-226-synthetic.gnucash.sqlite` — passed.
- `docker compose down --volumes --remove-orphans` with the same dummy env/default book placeholders — passed.
- Stopped-runtime cleanup — removed ignored runtime book and generated app DB; final dry-run reported `books=0`, `app=0`, `backups=0`, `locks=0`.

Standard checks:

- `cd apps/api && pytest -q` — passed, 523 tests.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and rendered for API/web.
- No write-enabled run was performed.
- `APP_ENV=test` was not weakened.
- Runtime used only a committed synthetic fixture copied into ignored `data/books/`.
- No release/tag/package/image/deployment was published.
- No real/private/only-copy book was used.
- No runtime book, backup, app DB, lock artifact, `.env`, screenshot, export, token, cookie, cert, key, raw private path, account name, memo, amount, backup filename, or private financial data was staged or committed.

## Risks / blockers

Phase 226 confirms the default read-only product path did not regress after the write-alpha backup/evidence remediation. It does not claim production readiness, security audit coverage, broad GnuCash compatibility, or real/private/only-copy book safety. Later roadmap phases still need operator-facing blocker-closure UX, fresh-clone/upgrade smokes, final release-candidate dogfood, and final release gate before any publication decision.

## Next

Do not start the next roadmap phase from this session. The next safe phase is Cycle 3 Phase 6/227 only if explicitly launched in a fresh Hermes session.
