# Issue #22 package 4 guard hardening

Status: complete.

## Goal

Prevent future overclaiming of #22 compatibility status while no Desktop-generated synthetic SQLite fixture evidence exists.

## Existing guards inspected

- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`
- `apps/api/app/compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix.py`
- `scripts/preflight_desktop_fixture_candidate.py`

The existing guards already required #22 blocker language and rejected broad GnuCash Desktop/backend support claims.

## Hardening added

Added a regression test:

- `apps/api/tests/test_public_status_guard.py::test_compatibility_status_guard_rejects_issue_22_closure_without_evidence`

Added fail-closed public-status patterns in `scripts/check_public_status.py` for current compatibility docs:

- `#22 closed` / `Issue #22 is closed` style claims;
- `Desktop-generated synthetic fixture evidence exists` style claims.

This keeps the guard conservative while the required current text still says #22 stays open until an actual isolated Desktop-generated synthetic fixture exists.

## TDD evidence

RED:

```text
pytest -q tests/test_public_status_guard.py::test_compatibility_status_guard_rejects_issue_22_closure_without_evidence
1 failed
```

GREEN:

```text
pytest -q tests/test_public_status_guard.py::test_compatibility_status_guard_rejects_issue_22_closure_without_evidence
1 passed
```

## Current status

The current repository status still passes after hardening. The full gate results are recorded in the final report.

## Safety/privacy summary

The hardening is pure text/regex/test logic. It does not open, copy, mutate, or scan any GnuCash book, app DB, backup, private path, export, screenshot, token, key, cert, account name, memo, description, or amount. It does not change write defaults or `APP_ENV=test` gates.
