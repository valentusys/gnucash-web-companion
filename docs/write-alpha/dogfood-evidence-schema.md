# Redacted dogfood evidence schema

Phase 236 standardizes how future copied/disposable write-alpha dogfood runs record evidence without exposing private financial data.

This document is a schema and redaction contract only. It does not authorize mutation, does not run copied-book dogfood, and does not claim safety for real/private or only-copy books.

## Scope and safety boundary

Evidence may describe only these targets:

- `synthetic`: committed or generated test fixtures with no private data.
- `copied_disposable`: a restorable copy used outside git, never the original book and never the only copy.

Evidence must never include:

- raw filesystem paths, host names, usernames, or mounted runtime paths;
- account names, account descriptions, transaction descriptions, split memos, payees, counterparties, or notes;
- raw amounts, balances, prices, quantities, currencies tied to private rows, or CSV rows;
- request/response payloads that contain financial content;
- screenshots, CSV exports, app DBs, books, backups, `.env` files, tokens, keys, or certs.

Use bounded placeholders such as `<redacted-path>`, `<redacted-artifact-ref:phase-N-kind>`, `<redacted-book-ref>`, `<redacted-command-output>`, and `<redacted-sensitive-field>` instead of private values.

`GNUCASH_WRITES_ENABLED=false` remains the default. Any future write-alpha dogfood that explicitly enables writes must still use `APP_ENV=test`, local-only execution, copied/disposable targets, backups, locks, audit evidence, restore proof where applicable, and a reset back to disabled writes.

## Required schema

Dogfood evidence reports should include the following fields.

| Field | Type | Required | Allowed content |
| --- | --- | --- | --- |
| `phase_number` | integer | yes | Phase number that produced the evidence. |
| `scenario_type` | string | yes | Short controlled label such as `preflight-only`, `readiness-dry-run`, `create-one-synthetic`, or `route-family-synthetic`. |
| `classification` | string | yes | `synthetic` or `copied_disposable`. Do not use `private`, `original`, or `only-copy`. |
| `commands_run` | array of strings | yes | Redacted command summaries. Arguments containing private paths or values must be replaced with placeholders. |
| `result` | string | yes | `pass`, `fail`, or `blocked`. |
| `artifact_refs` | array of strings | yes | Redacted references only, for example `<redacted-artifact-ref:phase-239-api-smoke>`. |
| `backup_count` | integer | yes | Count only. Do not include backup paths or filenames. Use `0` for no-mutation dry-runs. |
| `audit_row_count` | integer | yes | Count only. Do not include raw audit payloads or transaction identifiers unless already redacted to a safe bounded prefix. |
| `lock_status` | string | yes | Controlled status such as `not-acquired-no-mutation`, `acquired-and-released`, `rejected-before-lock`, or `blocked`. |
| `restore_proof_status` | string | yes | Controlled status such as `not-applicable-no-mutation`, `verified`, `blocked`, or `failed`. |
| `disabled_reset_status` | string | yes | Controlled status such as `verified-default-false`, `not-applicable-default-unchanged`, or `failed`. |
| `ownership_summary` | object | required for PATCH/DELETE scenarios | Redacted ownership evidence such as `created_transaction_owned=true`, `non_owned_patch_rejected=true`, and `non_owned_delete_rejected=true`. Do not include raw transaction IDs beyond existing safe prefixes. |
| `notes` | string | optional | Redacted operator note only. Do not include private row details, amounts, names, paths, or payloads. |

## JSON example

This example uses placeholders only and does not describe a real book.

```json
{
  "phase_number": 236,
  "scenario_type": "schema-only",
  "classification": "synthetic",
  "commands_run": [
    "python3 scripts/redact_dogfood_evidence.py --mode reject <redacted-evidence-json>"
  ],
  "result": "pass",
  "artifact_refs": [
    "<redacted-artifact-ref:phase-236-schema-doc>"
  ],
  "backup_count": 0,
  "audit_row_count": 0,
  "lock_status": "not-acquired-no-mutation",
  "restore_proof_status": "not-applicable-no-mutation",
  "disabled_reset_status": "not-applicable-default-unchanged",
  "notes": "Schema-only phase; no book opened, copied, backed up, or mutated."
}
```

## Helper

`scripts/redact_dogfood_evidence.py` can be used by later dogfood phases to preflight evidence JSON before committing it.

Reject mode fails closed:

```bash
python3 scripts/redact_dogfood_evidence.py <redacted-evidence-json>
```

Redact mode replaces detected unsafe values with placeholders:

```bash
python3 scripts/redact_dogfood_evidence.py --mode redact <redacted-evidence-json>
```

The helper is conservative and detects:

- absolute, home-relative, Windows, runtime-data, and GnuCash/SQLite/backup/CSV path-like strings;
- decimal or currency-like amount strings;
- sensitive-key values such as `path`, `uri`, `filename`, `account_name`, `memo`, `description`, `amount`, `split`, and `payload`.

Use the helper as an additional guard, not as permission to commit private evidence. Human review must still confirm that examples and reports contain placeholders only.

## Review checklist before committing evidence

- `classification` is `synthetic` or `copied_disposable` only.
- Original and only-copy books are not mentioned as dogfood targets.
- `commands_run` contains placeholders instead of raw private arguments.
- Counts are numeric counts only; no raw backup/audit paths or filenames are present.
- Lock, restore, and disabled-reset statuses use bounded labels.
- No account names, memos, descriptions, amounts, CSV rows, screenshots, app DBs, books, backups, `.env`, tokens, keys, or certs are committed.
- For PATCH/DELETE scenarios, `ownership_summary` confirms that the transaction created by
  write-alpha was the only allowed mutation target and that non-owned historical/manual targets were
  rejected.
- For any future write-enabled run, evidence includes reset proof that default-disabled posture was restored.
