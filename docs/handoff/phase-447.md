# Phase 447 — Backup manifest and restore readiness check

- goal: Make backup/restore readiness machine-verifiable before mutation.
- scope: Added build_manifest in owner_write_session_preflight.py with redacted target_ref/backup_ref, fingerprint prefix, backup_readiness_status, restore_check_status, redaction_status.
- non-goals: no production/stable/public-write safety claim; no original/private/only-copy mutation; no private evidence.
- acceptance criteria: Tests prove no raw target path in manifest.
- safety checks: No GnuCash books, app DBs, backups, exports, screenshots, .env, secrets, private paths/account names/memos/amounts, or raw private evidence committed. GNUCASH_WRITES_ENABLED remains default false; APP_ENV=test gate not weakened.
- verification: pytest -q tests/test_owner_write_session_preflight.py.
- expected artifacts: scripts/owner_write_session_preflight.py; apps/api/tests/test_owner_write_session_preflight.py; docs/handoff/phase-447.md
- final verdict: CONTINUE.
