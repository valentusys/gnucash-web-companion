# Phase 96 — Synthetic large-export benchmark

Date: 2026-05-18

## Scope

Phase 96 re-ran the existing synthetic large-book benchmark after the Phase 95 / GitHub #39 CSV export row-count/header fix.

Safety scope:

- generated synthetic/disposable GnuCash SQLite data only;
- read-only authenticated API paths only;
- no real/private book data, app DB, CSV export file, screenshot, `.env`, secret, token, key, cert, or backup committed;
- `GNUCASH_WRITES_ENABLED=false` remains the default;
- no tag or GitHub release was published.

## Command

Run from `apps/api`:

```bash
python scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-96-large-export-benchmark.json
```

The JSON output was intentionally written under `/tmp/` and is not committed.

## CSV export evidence

Synthetic fixture size:

- transactions: 1,000
- expense accounts: 12
- many-splits transaction splits: 60

CSV benchmark case:

| Field | Value |
| --- | ---: |
| Endpoint | `GET /books/{book_id}/transactions/export` |
| HTTP status | `200` |
| CSV body data rows / `item_count` | `1000` |
| `X-CSV-Export-Limit` / `csv_limit` | `10000` |
| `X-CSV-Export-Total` / `csv_total` | `1000` |
| `X-CSV-Export-Truncated` / `truncated` | `false` |
| Expected body rows, `min(total, limit)` | `1000` |
| Body rows match expected | `true` |
| Median duration in local TestClient run | `610.97 ms` |
| Response bytes | `237387` |

Result: the synthetic export above the historical 500-row clamp returned all 1,000 matching rows, reported a 10,000-row export cap, reported `csv_total=1000`, and was not truncated. Body rows matched `min(csv_total, csv_limit)`.

## Benchmark tooling change

The benchmark result JSON now records two explicit CSV consistency fields for the `csv_export_up_to_cap` case:

- `csv_expected_body_rows`
- `csv_body_matches_expected`

This keeps the Phase 95 evidence visible in future benchmark output instead of requiring manual comparison of row count, total, and limit.

## UX confirmation

Frontend CSV export copy was updated narrowly so the visible transaction-list export helper states that export is read-only, respects the current filtered view, remains capped at 10,000 rows, runs synchronously, and may need narrower filters if a request times out or the export is truncated.

The existing SvelteKit CSV export URL continues to preserve active filters and the proxy continues to forward CSV metadata headers.

## Limitations

This is local synthetic pre-alpha evidence only. It is not a broad performance claim, not personal-book dogfood, not broad GnuCash compatibility evidence, and not a production-readiness/security-audit claim.

CSV export remains synchronous and capped at 10,000 rows. Larger or slower exports should be narrowed by filters; async/background export infrastructure is out of scope for Phase 96.
