# Phase 212 — Public status drift guard

Date: 2026-05-21
Status: COMPLETE — public status docs synchronized; drift guard added
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md` (Cycle 2, Phase 1 only)

## Goal

Remove stale public roadmap/status drift after `v0.2.4-writealpha` and add an automated guard so README/PROJECT_STATUS/CHANGELOG/docs/ROADMAP/release-support docs stay aligned on current phase posture, current public releases, and read-only default.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-211.md`, and the cycle-2 roadmap file.
- Updated `docs/ROADMAP.md` from stale Phase 172 / `v0.2.0-writealpha` current posture to completed Phase 212 with Phase 211 / `v0.2.4-writealpha` as the current write-alpha release baseline.
- Updated README/README.ru, CHANGELOG, and PROJECT_STATUS to record Phase 212 without claiming a new release.
- Added `scripts/check_public_status.py`, a narrow public-status guard that checks:
  - completed Phase 212 public status;
  - Phase 211 release baseline;
  - `v0.1.7-readonly` current read-only release;
  - `v0.2.4-writealpha` current write-alpha release;
  - `GNUCASH_WRITES_ENABLED=false` default in docs/config;
  - no stale current `Phase 172` / `v0.2.0-writealpha` posture;
  - no affirmative production/security/stable/safe-real-book write claims.
- Added backend tests for the guard, including stale current release/baseline and unsafe claim regressions.
- Added the guard to the CI foundation job.

## Files changed

- `.github/workflows/ci.yml`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/ROADMAP.md`
- `docs/handoff/phase-212.md`
- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`

No product runtime behavior, write endpoint, write scope, Docker image/package, release/tag publication, or write default changed in this phase.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example` and rendered Compose.
- Existing write-alpha execution remains explicit local `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` only.
- The public-status guard reads only declared public docs/config files. It does not read `.env`, runtime books, app DBs, backups, ignored runtime data, or private paths.
- `APP_ENV=test` gate was not weakened.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw private path, account name, memo, amount, runtime book, or private financial data was committed.
- No production-ready, stable, security-audited, public-hosted, or safe real/private-book write claim was added.

## Verification summary

Commands/results:

```text
python3 scripts/check_public_status.py
# passed

cd apps/api && pytest tests/test_public_status_guard.py tests/test_health.py tests/test_transaction_writes.py -q
# passed

cd apps/api && pytest -q
# passed

cd apps/web && npm run check
# passed

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# passed: API and web render GNUCASH_WRITES_ENABLED: "false"

grep -n 'GNUCASH_WRITES_ENABLED=false' .env.example
# passed

git diff --check
# passed

python3 sensitive tracked-file hygiene scan
# passed
```

## Risks / follow-up

- Guard is intentionally narrow and public-status oriented; it is not a general documentation linter.
- It pins current release posture only. Future release/publication phases must update the constants and expected docs in the same release-status commit.
- Write-alpha remains experimental, disabled by default, `APP_ENV=test` gated when explicitly enabled, and unsafe for real/private or only-copy books.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
