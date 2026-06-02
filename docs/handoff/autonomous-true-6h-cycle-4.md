# Autonomous true 6h cycle 4 — #22 safe compatibility issue template

## Analyst queue scan

#22 still has safe work. After report helper, matrix vocabulary, and Desktop probe hardening, the next safe package is the public compatibility feedback issue template.

## PM work package

Goal: make the GitHub compatibility report template ask only for safe metadata and explicitly forbid private artifacts/raw financial evidence.

Scope:
- `.github/ISSUE_TEMPLATE/compatibility-report.yml`
- `apps/api/tests/test_compatibility_issue_template.py`

Non-goals:
- no issue closure;
- no real/private book access;
- no screenshots/exports/log ingestion;
- no compatibility guarantee or support claim.

Acceptance criteria:
- template asks for OS, browser, Docker/runtime, GnuCash version, backend, fixture scope, and generic error class only;
- template forbids books, app DBs, backups, exports, screenshots, `.env`, tokens, private paths, account names, transaction descriptions, memos, and amounts;
- template references safe report generation/validation helpers;
- tests guard against broad support claim wording.

Tests:
- `python -m pytest apps/api/tests/test_compatibility_issue_template.py -q`

Stop conditions:
- template invites private files, screenshots, row data, logs with paths, or broad support claims.

## Programmer implementation

Reworked the compatibility report issue template into separate safe metadata fields and added regression tests for field presence, privacy prohibitions, helper references, and no broad support phrases.

## Auditor verification

Command output:

```text
...                                                                      [100%]
3 passed in 0.02s
```

Safety/privacy check:
- no private data requested;
- template explicitly forbids risky artifacts and raw financial data;
- no book opened;
- writes remain disabled by default;
- no release was published.

## PM decision

Cycle accepted. Continue; minimum 5-cycle threshold still not met.
