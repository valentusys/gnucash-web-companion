# Phase 235 handoff — Copied/disposable target preflight CLI

Date: 2026-05-21
Status: COMPLETE — local-only redacted preflight CLI added; no copied/private book opened, copied, or mutated.

## Summary

Phase 235 added `scripts/write_alpha_preflight.py`, a metadata/path/environment preflight for future copied/disposable write-alpha dogfood targets. The CLI requires an explicit target path, rejects missing/unreadable files and targets inside the git working tree, validates that the backup destination is outside git or ignored by git, blocks unsafe write-alpha environment values unless `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`, and emits redacted normal output.

The CLI performs no mutation: it does not upload a book, open it with piecash, copy it, create a backup, or automatically enable writes. A production/original-looking target name produces only a redacted warning.

## Files changed

- `scripts/write_alpha_preflight.py` — new local-only redacted target preflight CLI.
- `apps/api/tests/test_write_alpha_preflight_cli.py` — targeted tests for missing target, inside-git target, unsafe environment, unsafe backup destination, ready redacted output/warning, and CLI nonzero/redaction behavior.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, `docs/ROADMAP.md` — public status synchronized to Phase 235 without changing release or write-safety posture.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations advanced to Phase 235.
- `docs/handoff/phase-235.md` — this handoff.

## Verification performed

- `cd apps/api && pytest tests/test_write_alpha_preflight_cli.py -q` — passed.
- `cd apps/api && pytest tests/test_dogfood_preflight.py tests/test_write_alpha_preflight_cli.py tests/test_public_status_guard.py -q` — passed.
- `python3 scripts/check_public_status.py` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `grep -R "GNUCASH_WRITES_ENABLED" -n .env.example docker-compose.yml apps` — inspected; default remains false.
- `grep -R "gnucash_writes_enabled" -n apps/api` — inspected; existing backend write gate remains present.
- `grep -R "APP_ENV=test" -n README.md docs apps` — inspected; write-alpha test gate remains documented.
- `grep -R "localStorage\|sessionStorage" -n apps/web/src` — inspected; no new browser storage added by this phase.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- The backend `APP_ENV=test` write-alpha gate was not weakened.
- The new CLI blocks unless the operator explicitly runs with `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`; this is only a preflight expectation, not automatic enablement.
- No real/private/only-copy book was used, opened, copied, mutated, or committed.
- No `.env`, app DB, runtime book, backup, CSV, screenshot, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.
- No production readiness, stable release, security audit, public-internet safety, broad compatibility, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 235 blocker remains. The CLI is only a preflight; it does not prove copied-book write safety and must be followed by separate dry-run/dogfood evidence in later phases.

## Next

Do not continue to Phase 236 from this session.
