# Autonomous true 6h cycle 5 — #22 compatibility report validator schema gates

## Analyst queue scan

#22 remains the primary queue. After safe helper/template hardening, the next safe package is strengthening the report validator so maintainers can reject malformed compatibility JSON before classification.

## PM work package

Goal: add schema-like validation for compatibility report field types, bounded text length, and allowed backend/fixture-scope enums.

Scope:
- `scripts/validate_compatibility_report.py`
- `apps/api/tests/test_validate_compatibility_report.py`

Non-goals:
- no real/private book access;
- no broader backend support;
- no Desktop fixture generation;
- no release.

Acceptance criteria:
- validator rejects invalid backend and fixture-scope enum values;
- validator rejects non-string field values;
- validator rejects overlong non-notice text fields;
- generated safe reports still validate successfully.

Tests:
- `python -m pytest apps/api/tests/test_validate_compatibility_report.py -q`
- generated report smoke: `safe_compatibility_report.py` output validates with `validate_compatibility_report.py`.

Stop conditions:
- validator permits unsafe enum/type drift;
- validator leaks rejected private values in stderr;
- any book access would be required.

## Programmer implementation

Added allowed enum sets, a maximum text field length, and string type checks before evidence-class matching. Extended validator tests with bad enum/type/length cases.

## Auditor verification

Focused test output:

```text
......                                                                   [100%]
6 passed in 0.51s
```

Generated report validation output:

```text
{
  "accepted": true,
  "evidence_class": "tested-synthetic-fixture",
  "report_schema": "gnucash-web-companion-safe-compatibility-v1",
  "support_claim": "redacted report only; not a compatibility guarantee"
}
```

Safety/privacy check:
- no book opened;
- no private data requested or committed;
- rejected values are reported with generic errors;
- writes remain disabled by default;
- no release was published.

## PM decision

Cycle accepted. Minimum cycle-count threshold is now met, but run continues to full gates/final audit before any final report.
