# Phase 239 — Write-alpha synthetic copied-book dry-run

Date: 2026-05-21
Status: PASS — synthetic/disposable no-mutation dry-run completed through Docker/Caddy.

## Scope

This run exercised the copied-book preflight/readiness flow with synthetic/disposable data only. It did not run create, PATCH, DELETE, import, restore, or any write-alpha mutation.

## Phase 236 schema evidence

```json
{
  "phase_number": 239,
  "scenario_type": "copied-book-dry-run",
  "classification": "synthetic-disposable",
  "commands_run": [
    "preflight-cli-redacted",
    "readiness-cli-enabled-test-redacted",
    "readiness-cli-default-disabled-redacted",
    "docker-caddy-readiness-redacted",
    "docker-caddy-api-smoke",
    "docker-caddy-browser-smoke",
    "public-status-guard",
    "docker-compose-default-config"
  ],
  "result": "pass",
  "redacted_artifact_refs": [
    "<redacted-artifact-ref:phase-239-dogfood-report>",
    "<redacted-artifact-ref:phase-239-handoff>"
  ],
  "backup_count": 0,
  "audit_row_count": 0,
  "lock_status": "no-lock-files",
  "restore_proof_status": "not-applicable-no-mutation",
  "disabled_reset_status": "verified-default-false",
  "mutation_performed": false,
  "raw_private_data_present": false
}
```

## Evidence summary

- Preflight passed against a synthetic copied target with `GNUCASH_WRITES_ENABLED=true` and `APP_ENV=test`; output was redacted and reported `mutation=none`.
- Readiness passed in explicit local test mode and returned `mutation_performed=false`.
- Readiness in default-disabled mode returned blocked readiness while still reporting `mutation_performed=false`.
- Docker/Caddy readiness ran inside the API container with writes disabled and reported blocked writes, `APP_ENV=test` gate OK, readable default synthetic book, and no mutation.
- Docker/Caddy API smoke passed through the Caddy endpoint with `GNUCASH_WRITES_ENABLED=false`.
- Disabled write probes for validate, create, PATCH, and DELETE returned 403 while writes were disabled.
- Docker/Caddy browser dogfood passed at a mobile viewport with hidden write UI and no saved browser artifacts.
- Runtime book checksum matched before and after the API/browser dry-run.
- Backup file count: 0.
- Lock file count: 0.
- App audit row count: 0.
- Rendered Docker Compose config kept `GNUCASH_WRITES_ENABLED=false` for API and web when not explicitly enabled.
- `scripts/check_public_status.py` passed.

## Safety boundaries

- No real/private/only-copy book was used.
- No create/PATCH/DELETE mutation was executed.
- No raw filesystem paths, account names, memos, amounts, request payloads, screenshots, CSV exports, app DBs, runtime books, backups, tokens, keys, or certs are committed in this evidence.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Backend `APP_ENV=test` write-alpha gating was not changed or weakened.
- No release/tag/package was published.

## Verdict

Phase 239 acceptance criteria are satisfied: dry-run evidence is recorded, no mutation occurred, disabled write probes still return 403, and the default-false reset/config posture was verified.
