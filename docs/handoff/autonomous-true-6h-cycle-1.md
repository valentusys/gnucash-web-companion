# Autonomous true 6h cycle 1 — #22 compatibility report redaction hardening

## Analyst queue scan

Open queue checked: #22, #28, #36 remain open; #22 is the highest-priority safe queue. README/PROJECT_STATUS/CHANGELOG still describe public read-only beta `v0.5.0-public-readonly-beta` and default-disabled writes.

## PM work package

Goal: harden the safe public compatibility report path so account-like, memo-like, description-like, amount-like, and path-like values cannot leak through the report helper or validator.

Scope:
- `scripts/safe_compatibility_report.py`
- `scripts/validate_compatibility_report.py`
- focused tests for both scripts

Non-goals:
- no real/private book access;
- no Desktop fixture generation;
- no write-mode or release changes;
- no broad compatibility claim.

Acceptance criteria:
- helper redacts path/account/memo/description/amount-like text from operator-provided fields;
- validator rejects unsafe account/memo/description-like values in submitted JSON;
- existing evidence-class behavior remains conservative.

Tests:
- `python -m pytest apps/api/tests/test_safe_compatibility_report.py apps/api/tests/test_validate_compatibility_report.py -q`

Stop conditions:
- any private-data leak, write-mode change, or validator overclaim.

## Programmer implementation

Added redaction patterns for account/memo/description labels in the report helper, preserving existing path and amount redaction. Added validator rejection of account/memo/description-like values while keeping the static privacy notice allowed.

## Auditor verification

Command output:

```text
.........                                                                [100%]
9 passed in 0.67s
```

Safety/privacy check:
- no GnuCash book opened;
- no app DB, backup, export, screenshot, path, account, memo, description, amount, secret, or token committed;
- `GNUCASH_WRITES_ENABLED=false` remains default;
- compatibility wording remains a redacted report only, not a guarantee.

## PM decision

Cycle accepted. Continue with #22; do not final-report after one slice.
