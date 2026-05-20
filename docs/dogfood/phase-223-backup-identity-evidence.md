# Phase 223 — Backup identity and redacted evidence

Date: 2026-05-21
Status: complete

## Scope

This note records bounded synthetic/disposable evidence for backup identity hardening after the Phase 222 backup filename collision fix.

No real/private/only-copy GnuCash book was used. The route-family regression uses the committed synthetic fixture copied to pytest temporary storage only. No runtime book, app DB, backup artifact, `.env`, screenshot, export, token, key, cert, raw private path, account name, memo, amount, or private financial data is committed here.

## Evidence summary

Targeted backend regression coverage freezes the backup clock at one instant and performs three write-alpha route-family operations against one synthetic disposable fixture:

1. `transaction.create`
2. `transaction.patch`
3. `transaction.delete`

The test proves:

- all three successful writes produce distinct readable backup artifacts;
- backup names advance through deterministic no-overwrite suffixes when the clock is fixed;
- backup artifacts remain under the ignored backup tree adjacent to the disposable fixture;
- each successful audit row preserves the exact internal backup path for recovery/debug correlation;
- the operator-facing audit-summary endpoint returns only an opaque `bkp-...` backup reference, not raw paths or filenames;
- opaque backup refs are unique across the three route-family artifacts;
- redacted summary output excludes raw backup paths, backup filenames, account names, memos, amounts, and raw request payload details.

## Operator-facing redaction contract

The audit summary now exposes:

- action;
- result;
- timestamp;
- transaction GUID prefix;
- `backup_present`;
- opaque `backup_artifact_ref` such as `bkp-<12 hex chars>`;
- safe error text.

It does not expose:

- raw backup paths;
- backup filenames;
- private file paths;
- raw request payloads;
- account names;
- split memos;
- amounts;
- financial row data.

## Verification

Targeted verification run:

```bash
cd apps/api && pytest tests/test_backup_restore.py tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_fast_route_family_writes_have_unique_backups_and_redacted_refs tests/test_write_alpha_audit_summary.py -q
```

Result: passed (`15 passed`, existing piecash/SQLAlchemy warnings only).

Full standard verification is recorded in `docs/handoff/phase-223.md`.

## Safety result

`GNUCASH_WRITES_ENABLED=false` remains default. `APP_ENV=test` was not weakened. This phase did not add production backup service behavior, rewrite retention policy, expand write scope, publish a release, or claim safety for real/private or only-copy books.
