# Phase 256 — Compatibility check harness after copied-book mutation

Date: 2026-05-21

Status: COMPLETE — local-only best-effort compatibility harness added, documented, and tested.

## Summary

Phase 256 added a post-mutation compatibility check harness for future copied/disposable write-alpha dogfood:

- `scripts/write_alpha_compatibility_check.py` opens a target GnuCash SQLite book read-only with piecash.
- If `gnucash-cli` is already available on `PATH`, the harness runs a bounded non-mutating `Balance Sheet` report probe.
- If `gnucash-cli` is unavailable, the harness reports `blocked` and records Desktop/CLI compatibility as still blocked.
- The JSON evidence records `pass`/`blocked`/`fail` clearly and explicitly sets `broad_compatibility_claimed=false`.
- Output and committed docs are redacted: no raw paths, account names, transaction descriptions, split memos, amounts, Desktop stdout/stderr, screenshots, CSV rows, or payloads.

The maintainer copied-book dogfood packet now places this compatibility check after mutation evidence and before restore verification.

## Artifacts

- `scripts/write_alpha_compatibility_check.py`
- `apps/api/tests/test_write_alpha_compatibility_check.py`
- `docs/write-alpha/compatibility-check-harness.md`
- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-256.md`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The `APP_ENV=test` backend write-alpha gate was not changed or weakened.
- No write-alpha mutation, GnuCash Desktop installation, release/tag, broad Desktop/version compatibility claim, or production/security/public-internet claim was added.
- No real/private/original/only-copy book was used.
- No app DB, book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, or private financial data artifact was committed.
- Missing Desktop/CLI tooling is a blocker, not compatibility evidence.

## Verification performed

```bash
cd apps/api && pytest tests/test_write_alpha_compatibility_check.py -q
```

Results:

- Synthetic fixture piecash check and blocked Desktop/CLI path: PASS.
- Synthetic fixture with mocked available `gnucash-cli` report success path: PASS.
- Missing target redaction failure path: PASS.
- Public status guard: PASS.
- Targeted public-status plus compatibility/wrapper regression tests: PASS (`31 passed`, warnings only from existing piecash/SQLAlchemy deprecations).
- Docker Compose config: PASS; rendered `GNUCASH_WRITES_ENABLED: "false"` for app/API services.
- Sensitive tracked-file hygiene scan: PASS.
- Git whitespace check: PASS.

Additional verification run after docs/status updates:

```bash
python3 scripts/check_public_status.py
cd apps/api && pytest tests/test_public_status_guard.py tests/test_write_alpha_compatibility_check.py tests/test_write_alpha_copied_book_dogfood.py -q
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
python3 - <<'PY'
# sensitive tracked-file hygiene scan
PY
git diff --check
```

## GitHub issues

Updated existing issue #22 with Phase 256 compatibility-harness evidence and the remaining broad Desktop/version compatibility boundary. Updated existing issue #36 with the copied-book dogfood package harness evidence. No new GitHub issue was required.

## Next phase boundary

Phase 257 may add a restore verification harness for copied-book dogfood. Phase 256 did not add restore verification, execute real/copied owner dogfood, install GnuCash Desktop tooling, publish a release, or claim real/private/only-copy write safety.
