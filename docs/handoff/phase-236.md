# Phase 236 handoff — Redacted dogfood evidence schema

Date: 2026-05-21
Status: COMPLETE — redacted dogfood evidence schema/helper added; no copied/private book opened, copied, backed up, or mutated.

## Summary

Phase 236 added `docs/write-alpha/dogfood-evidence-schema.md`, a conservative schema for future copied/disposable dogfood evidence. The schema records phase number, scenario type, synthetic/copied-disposable classification, commands run, pass/fail result, redacted artifact refs, backup count, audit row count, lock status, restore proof status, and disabled-reset status without allowing raw paths, amounts, memos, account names, payloads, screenshots, CSV exports, runtime DBs, books, backups, `.env`, tokens, keys, or certs.

The optional helper `scripts/redact_dogfood_evidence.py` was added with reject/redact modes for JSON evidence. It rejects or replaces path-like, amount-like, sensitive-key, and float values before evidence is committed. The helper is an extra guard only; it does not open books, parse GnuCash rows, acquire locks, create backups, call write routes, or mutate data.

## Files changed

- `docs/write-alpha/dogfood-evidence-schema.md` — schema, placeholder-only JSON example, helper usage, and pre-commit review checklist.
- `scripts/redact_dogfood_evidence.py` — local JSON helper with fail-closed reject mode and explicit redact mode.
- `apps/api/tests/test_redact_dogfood_evidence.py` — targeted tests for safe schema evidence, reject mode, redact mode, and CLI non-leak behavior.
- `README.md`, `README.ru.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md` — public status synchronized to Phase 236 without changing release or write-safety posture.
- `scripts/check_public_status.py` and `apps/api/tests/test_public_status_guard.py` — public-status guard expectations advanced to Phase 236.
- `docs/handoff/phase-236.md` — this handoff.

## Verification performed

- `cd apps/api && pytest tests/test_redact_dogfood_evidence.py -q` — passed.
- `cd apps/api && pytest tests/test_redact_dogfood_evidence.py tests/test_public_status_guard.py -q` — passed.
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
- No real/private/only-copy book was used, opened, copied, backed up, mutated, or committed.
- No copied-book dogfood run was performed in this phase.
- No `.env`, app DB, runtime book, backup, CSV, screenshot, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.
- No production readiness, stable release, security audit, public-internet safety, broad compatibility, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 236 blocker remains. The helper is conservative and may require manual placeholder adjustments in later dogfood reports; it is not a substitute for human review and does not prove copied-book write safety.

## Next

Do not continue to Phase 237 from this session.
