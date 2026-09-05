# QA remediation handoff

Status: in progress on `fix/qa-20260906`; not merged or released.

## QA-01 — implemented and locally verified

Only `scheduled_recurrence_invalid_metadata` from an individual DTO conversion is isolated.
The row retains authorized identity and redacted template-presence flags, with
`forecast.status=unavailable`, a fixed reason code, no inferred dates/amounts, and zero
materialized transactions. Batch reads, permissions, access denial and recurrence-cycle
failures still fail closed. Scheduled filters do not erase the overall incompleteness warning;
Dashboard discloses it even when reporting currency still needs setup.

Regression evidence is generated, synthetic-only and kept outside git. API cases cover partial
lists (15 valid plus one invalid), all-invalid, empty, invalid fields, stable ordering,
disabled/exhausted rows, permissions and both HTTP aliases. The real-service browser runner
covers valid/partial/all-invalid/empty lists in EN desktop and RU mobile, records both request
boundaries, verifies unchanged book hashes and read-only SQLite quick_check, and stops runtimes.

Commands run successfully during this slice:

- API: `python -m pytest tests/test_qa_regression_fixture.py tests/test_qa_scheduled_isolation.py tests/test_scheduled_transactions.py tests/test_scheduled_recurrence.py -q`.
- Web: `npm run check`, auth/admin static checks, transaction-entry preview and product static
  guards, transactions/report/money/books/accounts/scheduled static guards, `test:qa-loaders`.
- Build once, then `node scripts/test-qa-regressions-browser.mjs` with each of
  `QA_SCENARIO=scheduled_partial|scheduled_valid|scheduled_invalid|empty`.
- Neighbor browser cases: `node scripts/test-dashboard-browser.mjs` and
  `node scripts/test-scheduled-forecast-browser.mjs`.
- Baseline full API suite: 1556 passed (historical synthetic-write tests are separate from new
  read-only acceptance). Final full-suite/exact-head CI results are not yet claimed.

The browser runner uses `API_PYTHON` and `CHROMIUM_BIN`, and optionally `QA_EVIDENCE_DIR`.
Its generated books are not copies of user data. Chromium D-Bus addresses are isolated so XDG
portal startup cannot move test processes to a transient systemd scope. All test servers are
local subprocesses. Existing CREATE browser runners are not imported by this acceptance gate.

## Remaining

QA-02/03 money representation, QA-04/09 date and drilldown, QA-05/06 account groups, QA-07/08/10
form and pagination states, QA-11/12 layout/localization, followed by full exact-head integration
and CI. No independent reviewer agent has been run. No final acceptance is claimed.

Default writes remain disabled. No release, tag, image, package or deployment is authorized by
this handoff. No private data or raw private evidence belongs in this document.
