# Autonomous true 6h cycle 2 — #22 fixture-scope matrix boundary vocabulary

## Analyst queue scan

#22 remains the highest-priority safe queue after cycle 1. The next useful safe package is synthetic fixture compatibility matrix hardening: clarify how synthetic, disposable, copied-restorable, and unverified reports differ without turning report metadata into support claims.

## PM work package

Goal: add code-backed fixture-scope boundary vocabulary for the compatibility matrix/report workflow.

Scope:
- `apps/api/app/compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix.py`
- `docs/gnucash-compatibility.md`

Non-goals:
- no real/private book access;
- no Desktop-generated fixture claim;
- no backend support expansion;
- no write-mode or release change.

Acceptance criteria:
- fixture scopes `synthetic`, `disposable`, `copied-restorable`, and `unknown` map to conservative evidence classes;
- docs explain each boundary and keep private row data forbidden;
- no broad compatibility phrase appears in docs/changelog.

Tests:
- `python -m pytest apps/api/tests/test_compatibility_matrix.py -q`

Stop conditions:
- docs imply broad GnuCash/Desktop/backend/real-book support;
- any private evidence is requested or committed.

## Programmer implementation

Added `fixture_scope_boundaries()` to the compatibility matrix helper and regression tests proving the scope-to-evidence-class vocabulary is explicit and non-claiming. Added a fixture-scope boundary section to `docs/gnucash-compatibility.md`.

## Auditor verification

Command output:

```text
........                                                                 [100%]
8 passed in 0.03s
```

Safety/privacy check:
- no book opened or copied;
- no private path/account/memo/amount evidence added;
- no Desktop-version/backend/real-book support claim added;
- writes remain disabled by default;
- no release was published.

## PM decision

Cycle accepted. Continue with #22; minimum threshold is not met yet.
