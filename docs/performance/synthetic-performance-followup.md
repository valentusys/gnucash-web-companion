# Synthetic performance follow-up — non-mutating write-path checks

## Scope

This follow-up extends the local synthetic benchmark helper with bounded checks for non-mutating write-adjacent paths:

- owner create-preview API path;
- service-level transaction CREATE validation against a generated synthetic book opened read-only;
- existing synthetic transaction read-back verification using `_verify_transaction_create_readback` against an already-present fixture transaction.

Boundaries:

- local synthetic/generated GnuCash SQLite data only;
- no owner/private book, app DB, CSV export body, screenshot, `.env`, secret, token, key, cert, backup, or raw private evidence committed;
- no CREATE/PATCH/DELETE mutation route is benchmarked;
- `GNUCASH_WRITES_ENABLED=false` remains the default and is not enabled by this benchmark helper;
- these are local synthetic measurements only, not production performance, scalability, public-write, stable, broad compatibility, or security-audit claims.

## Code change

`app.performance.large_book_benchmark` now includes two additional non-mutating cases after the existing create-preview case:

- `transaction_create_validation_service` — builds a synthetic balanced `TransactionCreateRequestDTO` and times `GnuCashWriteService.validate_transaction_create`; account validation opens the generated fixture read-only.
- `transaction_create_readback_existing_synthetic` — reads the existing synthetic many-splits transaction, builds a matching request DTO, and times `_verify_transaction_create_readback`; it verifies through the read-only transaction service without creating a transaction.

The JSON output scope now records that validation and existing-synthetic read-back checks are included and that mutation routes were not called.

## Local synthetic smoke command

From the repository root:

```bash
cd apps/api && python -m app.performance.large_book_benchmark \
  --transactions 24 \
  --expense-accounts 4 \
  --account-branches 3 \
  --account-depth 3 \
  --many-splits 8 \
  --repeats 1 \
  --json-output tests/generated-fixtures/synthetic-performance-followup.json
```

Generated fixture and JSON output are under `apps/api/tests/generated-fixtures/`, which is ignored by git and not committed.

## Local synthetic result excerpt

Environment: local development host, FastAPI `TestClient`, generated synthetic SQLite fixture, 24 transactions, 4 synthetic expense accounts, one 8-split existing synthetic transaction, 1 repeat per case.

```text
transaction_create_preview_validation: status=200, median=39.74 ms, min=39.74 ms, max=39.74 ms, bytes=921, items=2
transaction_create_validation_service: status=200, median=8.47 ms, min=8.47 ms, max=8.47 ms, bytes=182, items=2
transaction_create_readback_existing_synthetic: status=200, median=15.69 ms, min=15.69 ms, max=15.69 ms, bytes=117, items=8
```

Interpretation: the new checks executed successfully on a small generated fixture and produced local synthetic timings for preview, validation, and read-back paths only. No private data and no GnuCash mutation were used.
