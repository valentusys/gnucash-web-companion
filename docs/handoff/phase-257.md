# Phase 257 — Restore verification harness for copied-book dogfood

Date: 2026-05-21

Status: COMPLETE — local-only copied-book restore verification harness added, documented, and tested.

## Summary

Phase 257 added a restore verification flow for future copied/disposable write-alpha dogfood:

- `scripts/write_alpha_restore_verify.py` restores only an outside-git copied working book from an outside-git pre-mutation backup.
- The harness requires explicit confirmations that the target is copied/disposable, the original remains untouched, restore is over the copy only, and the backup is pre-mutation.
- It verifies backup/restored checksum equality and an optional expected full sha256, opens the restored copy read-only with piecash, optionally runs a read-only web/API probe command with output redacted, and records bounded JSON evidence.
- Evidence is validated before write with the Phase 236 redaction helper and contains only statuses, counts, short checksum prefixes, placeholder command labels, and redacted artifact refs.
- `docs/write-alpha/restore-verification-harness.md`, the maintainer copied-book dogfood packet, and the dogfood evidence schema now describe the restore evidence contract.

## Artifacts

- `scripts/write_alpha_restore_verify.py`
- `apps/api/tests/test_write_alpha_restore_verify.py`
- `docs/write-alpha/restore-verification-harness.md`
- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/write-alpha/dogfood-evidence-schema.md`
- `README.md`
- `README.ru.md`
- `docs/ROADMAP.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `scripts/check_public_status.py`
- `docs/handoff/phase-257.md`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The `APP_ENV=test` backend write-alpha gate was not changed or weakened.
- No write-alpha mutation, mutation expansion, release/tag, production disaster-recovery claim, production/security/public-internet claim, or broad compatibility claim was added.
- No real/private/original/only-copy book was used.
- No app DB, book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, API payload, or private financial data artifact was committed.

## Verification performed

```bash
cd apps/api && pytest tests/test_write_alpha_restore_verify.py -q
python3 scripts/check_public_status.py
cd apps/api && pytest tests/test_public_status_guard.py tests/test_write_alpha_restore_verify.py tests/test_redact_dogfood_evidence.py -q
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet
JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
python3 - <<'PY'
# sensitive tracked-file hygiene scan
PY
git diff --check
```

Results:

- Synthetic backup/restore test with fixture copy, expected checksum, piecash read-back, mocked read-only API command, and redacted evidence: PASS.
- Blocked-path test without API command: PASS; restore proof remains verified but complete web/API restore evidence is blocked.
- Unsafe inside-repo target rejection: PASS.
- Expected-checksum mismatch failure path: PASS.
- Required confirmation failure path: PASS.
- Public status guard: PASS.
- Docker Compose config: PASS; rendered `GNUCASH_WRITES_ENABLED: "false"` for app/API services.
- Sensitive tracked-file hygiene scan: PASS.
- Git whitespace check: PASS.

## GitHub issues

Updated existing issue #36 with Phase 257 restore verification harness evidence. No new GitHub issue was required.

## Next phase boundary

Phase 258 may run the full synthetic copied-book package rehearsal, including dry-run, create-one, read-back, compatibility harness, restore verification, default-disabled reset, and redacted evidence. Phase 257 did not run real/copied owner dogfood, execute a write-alpha mutation, publish a release, or claim real/private/only-copy write safety.
