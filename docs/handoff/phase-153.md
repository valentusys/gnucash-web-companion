# Phase 153 — Fresh-clone Docker install smoke

Date: 2026-05-19
Status: DONE
Starting HEAD: `d52d31b`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 2/10 only)

## Goal

Prove a clean operator can run the read-only app from a fresh checkout with synthetic/disposable data and documented dummy secrets.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-152.md`;
  - roadmap phase 2 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 153 only; no neighboring roadmap phases were started.
- Added `scripts/smoke/fresh-clone-docker-smoke.sh`, a reproducible fresh-clone smoke helper that:
  - clones the repository into a temporary directory;
  - checks out a requested ref, default `HEAD`;
  - uses only the committed synthetic fixture copied into ignored runtime data;
  - creates a temporary clone-local `.env` with dummy local-only secrets and `GNUCASH_WRITES_ENABLED=false`;
  - creates an ignored Docker Compose override for port `18080` to avoid clashing with an existing local `8080` stack;
  - validates Docker Compose config and rendered write-disabled posture;
  - starts Docker Compose;
  - runs existing API smoke and browser dogfood helpers;
  - checks that no new raw screenshots/CSV exports/backups were created;
  - tears down Docker and removes the temporary clone by default.
- Ran the helper successfully from `/home/val/gnucash-web-companion`.
- Documented exact command path and safe redacted evidence in `docs/dogfood/phase-153-fresh-clone-docker-smoke.md`.
- Synchronized `PROJECT_STATUS.md` and `CHANGELOG.md`.

## Verification

Fresh-clone Docker smoke:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh
```

Result: passed.

Covered evidence:

- Temporary clone checked out helper commit `4edda3b`.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED=false`.
- Docker Compose startup passed at `http://127.0.0.1:18080`.
- `/api/health` returned `status=ok` and `writes_enabled=false`.
- API smoke passed for health, login, `/auth/me`, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled validate/create/patch write probes.
- Browser dogfood passed for login page, protected redirect, authenticated login with httpOnly cookie not readable from `document.cookie`, dashboard, accounts, books, scheduled, account detail, transaction filters, transaction detail, CSV export, hidden write UI, and no browser artifact creation.
- No-new-artifact check passed for raw screenshot/export/backup files in the temporary clone.

Standard/local checks run after doc sync:

- `bash -n scripts/smoke/fresh-clone-docker-smoke.sh` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- The smoke uses only synthetic/disposable data from the committed test fixture.
- The helper creates `.env`, app DB, copied runtime fixture, and Docker override only inside the temporary clone; those are untracked and removed by default.
- No production deployment hardening, public-internet exposure, production-readiness, or security-audit claim was added.
- No package, Docker image, binary, tag, or GitHub release was published.
- No real/private GnuCash book, `.env`, app DB, backup, screenshot, raw CSV export, token, key, cert, private path, or private financial data was committed.

## Files changed

- `scripts/smoke/fresh-clone-docker-smoke.sh`
- `docs/dogfood/phase-153-fresh-clone-docker-smoke.md`
- `docs/handoff/phase-153.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
