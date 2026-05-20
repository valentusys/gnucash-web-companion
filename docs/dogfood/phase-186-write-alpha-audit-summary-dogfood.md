# Phase 186 — write-alpha audit summary synthetic app-DB dogfood

Date: 2026-05-20
Status: PASS — redacted app-metadata audit summary checked with synthetic app DB only

## Scope

This dogfood checked the new read-only `GET /books/{book_id}/write-alpha-audit-summary` endpoint against a temporary synthetic app metadata SQLite DB. It did not open, parse, copy, or mutate any GnuCash book.

## Command

```bash
cd apps/api
python - <<'PY'
# temporary synthetic app DB with admin/viewer users, one book metadata row,
# and create/PATCH/DELETE audit rows containing deliberately unsafe paths/raw payload markers
# then call /books/{book_id}/write-alpha-audit-summary as admin and viewer
PY
```

## Result

```text
phase186_audit_summary_dogfood=PASS
admin_status= 200 viewer_status= 403 items= 3
actions= transaction.delete,transaction.patch,transaction.create
redaction_no_paths= True
redaction_no_raw_payload= True
```

## Evidence boundaries

- Synthetic app metadata DB only; no GnuCash book was read or mutated.
- `GNUCASH_WRITES_ENABLED=false` remained the configured/default test setting for this probe.
- Viewer access was blocked with 403.
- The returned DTO exposed only: action, result, timestamp, bounded transaction ID prefix, backup presence boolean, and safe error text.
- Deliberately unsafe backup/private paths and raw request-payload markers were absent from the returned JSON.
- No runtime app DB, book, backup, export, screenshot, `.env`, token, key, cert, private path, account name, memo, amount, or private data artifact was committed.
