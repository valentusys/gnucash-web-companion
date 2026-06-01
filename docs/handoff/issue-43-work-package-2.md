# Issue #43 work package 2 — evidence helper audit payload fix

- goal: Fix the local copied-book dogfood helper so audit payload evidence does not assume obsolete `.payload`.
- scope: added `audit_payload_from_log()` and `redacted_audit_payload_status()` to `scripts/write_alpha_copied_book_dogfood.py`; added regression tests.
- non-goals: no route behavior changes; no mutation.
- acceptance criteria: helper reads `payload_json`; malformed diagnostic payloads no longer abort evidence summary; redacted summary omits transaction IDs and paths.
- safety checks: tests assert raw synthetic transaction refs and private-like paths are not emitted in helper summary.
- verification: `pytest apps/api/tests/test_write_alpha_copied_book_dogfood.py -q` => 7 passed.
- artifacts: code/tests above.
- verdict: CONTINUE.
