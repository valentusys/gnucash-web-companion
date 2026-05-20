# Phase 220 handoff — cycle-2 release-candidate dogfood

Date: 2026-05-21
Status: COMPLETE WITH NO-RELEASE BLOCKER — default-read-only API/browser dogfood passed; bounded write-alpha drill exposed a DELETE backup-count anomaly.

## Summary

Phase 220 collected the cycle-2 release-candidate dogfood evidence after Phases 212–219. Default Docker/Caddy read-only mode passed full API and browser dogfood with `GNUCASH_WRITES_ENABLED=false`. A separate explicit local write-alpha drill used only `APP_ENV=test`, `GNUCASH_WRITES_ENABLED=true`, dummy local-only credentials, and synthetic/disposable ignored runtime copies.

The write-alpha create and PATCH route-family smokes passed. The DELETE route-family smoke reached a successful DELETE and confirmed API/runtime absence plus bounded backup/audit evidence, but then failed because backup file count did not increase by exactly one after DELETE. Redacted inspection showed three successful backup-bearing route-family audit entries but only two backup files. This is a no-release blocker until investigated and re-smoked.

## Files changed

- `docs/dogfood/phase-220-cycle-2-release-candidate-dogfood.md`
- `docs/handoff/phase-220.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`

No product code or write endpoint behavior changed in this phase.

## Verification performed

Dogfood and smoke checks:

- Rendered Compose false before dogfood — passed; API and web had `GNUCASH_WRITES_ENABLED: "false"`.
- `python3 -m py_compile` for read-only/write-alpha smoke helpers — passed.
- Default-read-only API smoke — passed for health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, scheduled transaction metadata, write-alpha audit summary, and validate/create/PATCH/DELETE 403 probes.
- Browser dogfood `320x720` — passed with hidden write UI, httpOnly auth-cookie no-readability, CSV fetch, no-overflow checks, and no artifacts.
- Browser dogfood `1280x900` — passed with the same route/safety checks.
- Write-alpha preflight dry-run — passed with redacted external-disposable/ignored-runtime/ignored-backup classes.
- Write-alpha create smoke — passed.
- Write-alpha PATCH smoke — passed.
- Write-alpha DELETE+restore smoke — blocked after successful DELETE because backup file count did not increase by exactly one.
- Redacted post-failure inspection — backup file count was 2; successful backup-bearing audits existed for create=1, patch=1, delete=1; failed-safe PATCH audit without backup existed; lock was stale-released/not active.
- Rendered Compose false after write-alpha reset — passed.
- Default-read-only API smoke after reset — passed with validate/create/PATCH/DELETE returning 403.
- Stopped-runtime cleanup — removed smoke runtime book/backups/locks/generated smoke app DB; pre-existing ignored local app DB was restored and remains untracked local state.

Standard checks after docs/status updates:

- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest tests/test_public_status_guard.py -q` — passed (`6 passed`).
- `cd apps/api && pytest -q` — passed (`521 passed`, existing warnings only).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed; rendered config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` — passed.
- sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-alpha execution was explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` only.
- No `APP_ENV=test` gate was weakened.
- No real/private/only-copy book was used.
- No release/tag/package/image was published.
- No screenshot, raw CSV/export, runtime book, backup, generated app DB, `.env`, token, cookie, cert, key, raw private path, account name, memo, amount, or private financial data was staged or committed.

## Risks / blockers

Release blocker for Phase 221: investigate the DELETE backup-count anomaly before publishing any write-alpha release. The default-read-only dogfood is green, but the cycle requires bounded write-alpha route-family evidence and the DELETE helper found a backup count mismatch after a successful DELETE.

## Next

Do not start Phase 221 or publish a release from this session. The next phase should either investigate/remediate the backup-count anomaly and rerun bounded write-alpha evidence, or record an explicit no-release verdict.
