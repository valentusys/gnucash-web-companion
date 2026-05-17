# Phase 54 — Observability and Diagnostics

## Status

Complete. Phase 54 added safe startup diagnostics, a richer non-sensitive health endpoint, default-book/app-DB checks, troubleshooting documentation, synchronized status docs, passed required checks, and pushed the phase commit. No blockers remain.

## PM report

### Decision

Execute exactly Phase 54 from the roadmap: improve observability and diagnostics for self-hosted users without adding telemetry, exposing secrets, publishing a release, or expanding write scope.

### Why

After the read-only MVP, deployment, backup, compatibility, UX, i18n, and community-draft work, the next practical release-readiness gap is diagnosing local deployment problems. Self-hosted users need understandable signals for missing copied books and app metadata DB issues, but financial software diagnostics must avoid leaking paths, credentials, secrets, or real financial data.

### Phase brief

- Goal: add structured startup diagnostics, make `/health` richer but non-sensitive, check whether the configured default book exists, check app metadata DB reachability, keep logs safe, and add troubleshooting documentation.
- Non-goals: no telemetry, no external monitoring integration, no write-scope expansion, no release/tag publication, no real data/screenshots/exports, no production-readiness/security-audit claims.
- Acceptance criteria:
  - Startup emits structured diagnostics that help identify missing default book/app DB problems.
  - `/health` includes non-sensitive checks for app DB reachability, default book status, and write-mode flag.
  - Missing default book diagnostics are understandable.
  - Health/log diagnostics do not expose full filesystem paths, credentials, JWT secrets, admin passwords, DB URLs, or real data.
  - `docs/operations/troubleshooting.md` exists and explains safe diagnosis/reporting.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains the default documented state.
  - Controlled writes remain experimental post-MVP and disabled by default.
  - No write route/UI/settings behavior is expanded.
  - No real GnuCash book, `.env`, app DB, backup, secret, key, token, certificate, real screenshot, or real export is added.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Health endpoint could leak private deployment details. Mitigation: expose only backend/database filename, default-book filename, booleans, and user-safe messages; tests assert secrets/full temp paths are absent.
- Missing-book state could break container healthchecks. Mitigation: endpoint remains HTTP 200 and reports `status: degraded` in the payload while Docker healthchecks only require a successful HTTP response.
- Diagnostics could be mistaken for production monitoring. Mitigation: troubleshooting doc explicitly frames them as pre-alpha operational smoke diagnostics, not monitoring/security/backup guarantees.

### Files/docs to update

- `apps/api/app/diagnostics.py`
- `apps/api/app/main.py`
- `apps/api/tests/test_health.py`
- `docs/operations/troubleshooting.md`
- `README.md`
- `docs/DEVELOPMENT.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-54.md`

### GitHub/backlog

- No Phase 54-specific GitHub issue was identified in the open issue list. No issue update was required.
- Next planned phase after completion: Phase 55 — v0.1 read-only scope freeze audit.

## Engineer report

Implemented Phase 54 only:

- Added `apps/api/app/diagnostics.py` with safe helpers for:
  - default book configured/existence/readability diagnostics;
  - app metadata DB backend/name/reachability checks;
  - richer `/health` payload construction;
  - structured `startup_diagnostics` logging.
- Updated `apps/api/app/main.py` so startup logs a safe structured diagnostics event and `/health` returns non-sensitive `checks` for app DB, default book, and write-mode state.
- Reworked `apps/api/tests/test_health.py` to cover:
  - richer health payload with reachable app DB and present copied book;
  - understandable missing default book message without full path exposure;
  - startup diagnostics logs that avoid JWT/admin secrets and full paths.
- Added `docs/operations/troubleshooting.md` with safe self-hosted diagnostic steps, missing book/app DB guidance, startup log usage, and bug-report do/don't lists.
- Updated `README.md`, `docs/DEVELOPMENT.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` for Phase 54.

No telemetry was added. No write code, write UI, write flag default, auth storage, release/tag, real data, fixture binary, secret, or backup was changed or added.

## Verification

Passed:

- `cd apps/api && pytest -q tests/test_health.py` — passed (`3 passed`, 1 existing piecash/SQLAlchemy warning).
- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed (`282 passed`, 27 existing warnings).
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- Health/startup diagnostics intentionally avoid full filesystem paths, credentials, JWT secrets, admin passwords, DB URLs, and real financial data.
- No write scope was expanded.
- No production/security-audited claims were introduced.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Commit message: `feat: add phase 54 safe diagnostics`.
- Commit: this Phase 54 handoff is included in the phase commit pushed to `origin/main`.

## GitHub issue status

- No Phase 54-specific GitHub issue was identified in the open issue list, so no issue was updated.

## Blockers

None.
