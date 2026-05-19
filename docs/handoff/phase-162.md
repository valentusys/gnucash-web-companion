# Phase 162 — Post-release baseline sync + v0.1.6 tagged smoke

Date: 2026-05-20
Status: DONE
Starting HEAD: `6b202c9`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 1/10 only)

## Goal

Synchronize the actual post-`v0.1.6-readonly` baseline where public docs drifted, and verify that the already-published `v0.1.6-readonly` tag starts through the documented read-only Docker path.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-161.md`;
  - roadmap phase 1 and common safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 162 only; no neighboring roadmap phases were started.
- Confirmed `docs/ROADMAP.md` was stale and still claimed Phase 137/138 and `v0.1.3-readonly` as the current read-only release.
- Updated `docs/ROADMAP.md` to the actual Phase 162 / `v0.1.6-readonly` baseline and current conservative release posture.
- Ran a fresh checkout smoke against published tag `v0.1.6-readonly` with synthetic/disposable fixture data and dummy local-only `.env` values.
- Added DELETE disabled-write coverage to smoke tooling:
  - `scripts/smoke/read-only-api-smoke.py` now checks validate/create/patch/delete write-disabled probes;
  - `scripts/smoke/fresh-clone-docker-smoke.sh` includes a wrapper-level DELETE probe so old published tags whose bundled API smoke predates DELETE coverage can still be verified.
- Recorded redacted tagged-smoke evidence in `docs/dogfood/phase-162-v0.1.6-tagged-smoke.md`.
- Synchronized `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff with the actual Phase 162 state.

## Tagged smoke evidence

Command:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh \
  --repo /home/val/gnucash-web-companion \
  --ref v0.1.6-readonly \
  --port 18086
```

Result: PASS.

Key evidence:

- Fresh checkout ref: `v0.1.6-readonly`.
- Checked-out tag commit: `6ea3cfb`.
- Full tag target: `6ea3cfb23bf3ff8c573a72303a53fe93be6b4f1a`.
- Runtime base URL: `http://127.0.0.1:18086`.
- Synthetic fixture filename: `main.gnucash.sqlite`.
- Synthetic fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Log: `/home/val/.hermes/logs/gnucash-web-companion/phase-162/v0.1.6-tagged-smoke.log`.

Covered runtime checks:

- Docker Compose config validation.
- `/api/health` returned `status=ok` and `writes_enabled=false`.
- API smoke passed: health, login, `/auth/me`, `/books`, `/books/1`, accounts, transactions, transaction detail, CSV export, reports summary, disabled validate/create/patch probes.
- Additional DELETE disabled-write probe passed with HTTP 403 and read-only/write-disabled explanation.
- Browser dogfood passed at 320x720: login page, protected redirect, authenticated login, auth cookie not readable from `document.cookie`, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, hidden write UI, no horizontal overflow, no screenshot/download/CSV artifacts.
- Temporary clone no-artifact check passed for raw screenshots/exports/backups.

## Verification

```bash
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
python3 -m py_compile scripts/smoke/read-only-api-smoke.py
bash -n scripts/smoke/fresh-clone-docker-smoke.sh
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Backend tests passed: `386 passed, 32 warnings`.
- Frontend `npm run check` passed with `0 errors and 0 warnings`.
- Frontend `npm run test:auth-routes` passed.
- Frontend `npm run build` passed.
- Smoke script compile/shell syntax checks passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default and was verified in rendered Compose config and tagged runtime health.
- No product behavior or write capability changed.
- No tag, GitHub release, package, Docker image, binary artifact, or production deployment was published in this phase.
- No real/private GnuCash book, committed `.env`, app DB, backup, screenshot/export, token, key, cert, private path, account name, transaction description, memo, amount, or private financial data was committed.
- Tagged smoke used only the committed synthetic fixture copied into ignored temporary runtime data.
- The evidence is local pre-alpha synthetic/disposable smoke only; it is not a production-readiness, security-audit, public-internet, broad real-book compatibility, or safe production write-mode claim.

## Files changed

- `scripts/smoke/read-only-api-smoke.py`
- `scripts/smoke/fresh-clone-docker-smoke.sh`
- `scripts/smoke/read-only-smoke-check.md`
- `docs/dogfood/phase-162-v0.1.6-tagged-smoke.md`
- `docs/ROADMAP.md`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-162.md`
