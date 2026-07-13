# Issue 55 — Synthetic account performance benchmark

## Scope and safety

- Local synthetic/disposable GnuCash SQLite fixtures only; no owner/private/original/working/Syncthing book was inspected, copied, or probed.
- FastAPI `TestClient` in-process measurements; timings are local evidence only, not CI thresholds and not production/scalability guarantees.
- Non-mutating read API paths only; product CREATE/PATCH/DELETE/batch mutation routes were not called and per-case `mutation_capable_request_count` stayed `0`.
- No FX conversion, price lookup, persistent private cache, or write-default change is involved in these benchmark cases.
- Generated SQLite/JSON artifacts were written under ignored `apps/api/tests/generated-fixtures/` and are intentionally not committed.

## Commands

From `apps/api`:

```bash
PYTHONWARNINGS=ignore python -m app.performance.large_book_benchmark \
  --issue55-account-dataset 1k \
  --output tests/generated-fixtures/issue55-account-1k.gnucash.sqlite \
  --json-output tests/generated-fixtures/issue55-account-1k-results.json \
  --repeats 3 \
  --warmups 1

PYTHONWARNINGS=ignore python -m app.performance.large_book_benchmark \
  --issue55-account-dataset 10k \
  --output tests/generated-fixtures/issue55-account-10k.gnucash.sqlite \
  --json-output tests/generated-fixtures/issue55-account-10k-results.json \
  --repeats 3 \
  --warmups 1
```

## Dataset `1k`

| Fixture field | Value |
| --- | ---: |
| `candidate_account_count` | 1000 |
| `transaction_count` | 1000 |
| `synthetic_account_count` | 1000 |
| `hidden_account_count` | 450 |
| `placeholder_account_count` | 11 |
| `commodity_count` | 4 |
| `duplicate_account_name_count` | 2 |
| `unicode_account_name_count` | 14 |
| `account_depth` | 13 |
| `account_branch_count` | 5 |
| `contains_real_data` | false |
| `synthetic` | true |

| Case | Status | Median ms | Min ms | Max ms | Bytes | Opens | Data queries | Candidates | Returned | Depth | Buckets | Rollup cells | Split scan rows | Aggregate rows | Recent | Count calls | Tx materializations | Error | Budget |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `issue55_1k_account_unfiltered_tree` | 200 | 86.94 | 82.66 | 153.48 | 464322 | 1-1 | 2 | 1000 | 550 | 12 | 4 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_account_text_filtered_tree` | 200 | 64.67 | 60.74 | 128.74 | 13795 | 1-1 | 2 | 1000 | 15 | 6 | 4 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_account_flat_search` | 200 | 63.51 | 61.16 | 117.98 | 4504 | 1-1 | 2 | 1000 | 4 | 6 | 1 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_account_type_filtered_explorer` | 200 | 62.84 | 62.72 | 62.97 | 60469 | 1-1 | 2 | 1000 | 75 | 5 | 4 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_root_overview` | 200 | 63.86 | 62.05 | 64.25 | 5498 | 1-1 | 2 | 1000 | 6 | 1 | 4 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_recursive_native_buckets` | 200 | 61.88 | 61.19 | 129.47 | 9186 | 1-1 | 2 | 1000 | 10 | 3 | 4 | 121 | 2000 | 107 | — | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_direct_period_activity` | 200 | 32.39 | 31.95 | 32.86 | 3938 | 1-1 | 5 | — | 10 | — | — | — | 1000 change / 22 recent | — | 10 | 0 | 0 | — | 1k <= 2500 ms (true) |
| `issue55_1k_account_transaction_explorer_first_page` | 200 | 63.37 | 62.97 | 118.97 | 6038 | 1-1 | 2 | 11 transaction candidates | 10 | — | — | — | 22 transaction split rows | — | — | 0 | 0 | — | 1k <= 2500 ms (true) |

1k overview details: `root_overview` reported `overview_subtree=1000`, `overview_children=5/5`; `recursive_native_buckets` reported `overview_subtree=181`, `overview_children=9/9`.

## Dataset `10k`

| Fixture field | Value |
| --- | ---: |
| `candidate_account_count` | 10000 |
| `transaction_count` | 10000 |
| `synthetic_account_count` | 10000 |
| `hidden_account_count` | 103 |
| `placeholder_account_count` | 112 |
| `commodity_count` | 4 |
| `duplicate_account_name_count` | 2 |
| `unicode_account_name_count` | 137 |
| `account_depth` | 30 |
| `account_branch_count` | 5 |
| `contains_real_data` | false |
| `synthetic` | true |

| Case | Status | Median ms | Min ms | Max ms | Bytes | Opens | Data queries | Candidates | Returned | Depth | Buckets | Rollup cells | Split scan rows | Aggregate rows | Recent | Count calls | Tx materializations | Error | Budget |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `issue55_10k_account_filtered_tree` | 200 | 690.38 | 679.47 | 735.27 | 327656 | 1-1 | 2 | 10000 | 330 | 28 | 4 | 1999 | 20000 | 1979 | — | 0 | 0 | — | 10k <= 8000 ms (true) |
| `issue55_10k_account_unfiltered_tree_expected_422` | 422 | 656.31 | 629.80 | 680.91 | 144 | 1-1 | — | — | — | — | — | — | — | — | — | 0 | 0 | result_too_large | — |
| `issue55_10k_root_overview` | 200 | 671.53 | 630.09 | 681.75 | 5514 | 1-1 | 2 | 10000 | 6 | 1 | 4 | 1999 | 20000 | 1979 | — | 0 | 0 | — | 10k <= 8000 ms (true) |
| `issue55_10k_direct_activity` | 200 | 86.36 | 85.48 | 87.12 | 3936 | 1-1 | 5 | — | 10 | — | — | — | 10000 change / 22 recent | — | 10 | 0 | 0 | — | 10k <= 8000 ms (true) |
| `issue55_10k_drilldown_first_page` | 200 | 272.47 | 267.66 | 306.10 | 6159 | 1-1 | 2 | 11 transaction candidates | 10 | — | — | — | 22 transaction split rows | — | — | 0 | 0 | — | 10k <= 8000 ms (true) |

10k overview details: `root_overview` reported `overview_subtree=10000`, `overview_children=5/5`.

## Observed acceptance checks

- 1k success cases: all medians were below the local guidance budget of `<=2.5s`; one warm-up plus three measured samples were recorded for every case.
- 10k success cases: all medians were below the local guidance budget of `<=8s`; the unfiltered 10k tree returned the expected bounded `422` with `error_code=result_too_large`.
- Explorer and overview success cases used one book open and `2` account data queries, within the `<=8` guard.
- Direct activity used one book open and `5` data queries on success, within the `<=10` guard; recent fetches returned `10` items from `limit=10`.
- Transaction-explorer drilldown first pages matched account activity recent IDs and Decimal amount strings (`activity_ids_match=true`, `activity_amounts_match=true`).
- Response-size guards held for success cases: account explorer/overview `<=512 KiB`; activity `<=256 KiB`.
- `read_only_api_paths_only=true`, `write_alpha_mutation_routes_called=false`, and `production_performance_claim=false` in both JSON result scopes.
