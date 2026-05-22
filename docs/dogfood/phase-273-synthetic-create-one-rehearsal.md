# Phase 273 — Synthetic CREATE-one rehearsal

Status: COMPLETE — synthetic/disposable CREATE-one rehearsal passed for routed CREATE, restore, and default-disabled reset; owner CREATE remains unauthorized.

## Scope

This rehearsal used only synthetic/disposable fixture copies. No owner/private/original/only-copy book was used.

Covered steps:

1. Seeded the local runtime from the committed synthetic fixture.
2. Started Docker/Caddy with explicit local `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.
3. Ran `scripts/write_alpha_copied_book_dogfood.py --create-one` against an outside-git synthetic copy.
4. Delegated routed CREATE to `scripts/smoke/write-alpha-create-smoke.py`.
5. Reset the runtime to `GNUCASH_WRITES_ENABLED=false`.
6. Ran restore verification from the pre-mutation wrapper backup with a read-only API probe.
7. Ran the compatibility harness on the restored synthetic copy.
8. Verified read-only API smoke after reset.

## Redacted evidence summary

| Step | Result | Evidence |
| --- | --- | --- |
| CREATE-one wrapper | PASS | preflight ready; pre-step backup created; mutation requested/performed for synthetic fixture only; delegated create command passed; default-disabled posture verified |
| Routed CREATE smoke | PASS | health/books/accounts passed; validation rejected unsafe probes; exactly one balanced two-split CREATE succeeded; transaction read-back passed; backup count increased; audit success count increased by one; lock evidence inactive/stale-safe |
| Restore verification | PASS | restored outside-git synthetic working copy from pre-mutation backup; checksum matched; piecash read-back passed; read-only API probe passed |
| Compatibility harness | BLOCKED/NON-BLOCKING | piecash read-back passed; host `gnucash-cli` was unavailable and recorded as blocked, not compatibility evidence |
| Reset default false | PASS | runtime restarted with `GNUCASH_WRITES_ENABLED=false`; read-only API smoke verified validate/create/PATCH/DELETE are disabled |
| Redaction | PASS for wrapper/restore evidence | wrapper and restore evidence passed the repository redaction validator; compatibility harness uses its own redacted schema and recorded no broad compatibility claim |

Safe allowlisted results:

```text
wrapper_result=pass
wrapper_mode=create-one
wrapper_preflight_status=ready
wrapper_backup_status=created-before-step
wrapper_mutation_requested=true
wrapper_mutation_performed=true
wrapper_create_command_status=passed
wrapper_disabled_reset_status=verified-default-disabled
restore_result=pass
restore_status=restored-from-pre-mutation-backup
restore_proof_status=verified
restore_read_back_status=pass
restore_api_read_status=pass
compat_result=blocked
compat_piecash_status=pass
compat_desktop_status=blocked
compat_broad_claimed=false
```

## Safety review

- The mutation was synthetic/disposable only.
- No owner copied-book CREATE/PATCH/DELETE was run.
- No private financial artifact, raw path, account name, memo, amount, balance, screenshot, CSV export, app DB, token, key, cert, or backup filename is committed.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- Explicit write-alpha execution remains `APP_ENV=test` gated.
- Host Desktop/CLI compatibility remains blocked when `gnucash-cli` is unavailable; no broad compatibility claim is made.
- Original/only-copy books remain forbidden.

## Verification commands

```text
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... docker compose up -d --build
APP_ENV=test GNUCASH_WRITES_ENABLED=true ... python3 scripts/write_alpha_copied_book_dogfood.py --create-one <redacted args>
python3 scripts/redact_dogfood_evidence.py <redacted-wrapper-evidence>
APP_ENV=test GNUCASH_WRITES_ENABLED=false ... docker compose up -d
python3 scripts/write_alpha_restore_verify.py <redacted args> --api-read-command python3 scripts/smoke/read-only-api-smoke.py
python3 scripts/redact_dogfood_evidence.py <redacted-restore-evidence>
python3 scripts/write_alpha_compatibility_check.py <redacted-synthetic-copy> --output <redacted-evidence>
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_PASSWORD=<dummy> python3 scripts/smoke/read-only-api-smoke.py
```

## Result

Phase 273 is sufficient to show that the planned CREATE-one path works on synthetic/disposable fixtures with backup, audit, lock, read-back, restore, redaction, and default-disabled reset evidence. It is not owner mutation authorization. The host Desktop/CLI compatibility probe remains blocked by unavailable `gnucash-cli`, so Phase 274 must treat compatibility evidence conservatively.
