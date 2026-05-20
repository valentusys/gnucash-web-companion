# Phase 237 handoff — Write-alpha environment template and operator guard documentation

Date: 2026-05-21
Status: COMPLETE — local-only write-alpha environment reference and operator guard documentation added; default read-only config unchanged.

## Summary

Phase 237 added `.env.writealpha.example` as a clearly dangerous operator reference for explicit local write-alpha testing, not a default `.env` template. It also added `docs/write-alpha/environment.md` with conservative guidance for operators: do not copy the template blindly to `.env`, write-alpha requires both `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`, only synthetic/disposable/copied-test books are allowed, public exposure is forbidden, and the original/only-copy book must never be used.

No write mode was enabled. `.env.example` and Docker Compose defaults remain read-only.

## Files changed

- `.env.writealpha.example` — local-only write-alpha reference with strong unsafe-for-real-books warnings, explicit gates, local-only origins, and placeholder-only credentials.
- `docs/write-alpha/environment.md` — operator guidance for default read-only posture, write-alpha gates, allowed books, exposure boundary, checklist, and verification commands.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md` — public/status docs synchronized to Phase 237 without changing release or write-safety posture.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations advanced to Phase 237.
- `docs/handoff/phase-237.md` — this handoff.

## Verification performed

- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest tests/test_public_status_guard.py -q` — passed, 14 tests.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED: "false"'` — passed; rendered default false for api and web.
- `grep -n '^GNUCASH_WRITES_ENABLED=false$' .env.example` — passed.
- `grep -n 'GNUCASH_WRITES_ENABLED=true' .env.writealpha.example docs/write-alpha/environment.md` — inspected explicit write-alpha gate docs/reference.
- `grep -n 'APP_ENV=test' .env.writealpha.example docs/write-alpha/environment.md` — inspected explicit test-gate docs/reference.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan with `.env.writealpha.example` allowlisted as an intended operator reference — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the normal default in `.env.example` and rendered Docker Compose config.
- Docker Compose defaults were not changed.
- The backend `APP_ENV=test` write-alpha gate was not weakened.
- `.env.writealpha.example` is not used by default and is marked as dangerous for real/private/original/only-copy books.
- No real/private/only-copy book was used, opened, copied, backed up, mutated, or committed.
- No copied-book dogfood run was performed in this phase.
- No `.env`, app DB, runtime book, backup, CSV, screenshot, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.
- No production readiness, stable release, security audit, public-internet safety, broad compatibility, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 237 blocker remains. The template is intentionally explicit, but it still requires operator discipline: it must not be copied blindly into `.env` or used outside local synthetic/disposable/copied-test contexts.

## Next

Do not continue to Phase 238 from this session.
