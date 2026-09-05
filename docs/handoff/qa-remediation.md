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

## QA-02 — implemented and locally verified

`RecentTransaction` now types the report endpoint independently of explorer-only fields.
The backend adds `amount_is_unambiguous`: two balanced splits in distinct monetary accounts,
with quantities equal to values and all commodities matching the transaction currency. Missing
metadata, securities, mixed currencies and non-simple shapes fail closed. Raw legacy amount
fields remain compatible; the recent UI displays their exact unsigned string magnitude only
when the classification permits it. Zero is displayed, not treated as missing. RU/EN explain
neutral magnitude versus From/To direction.

The generated money scenario covers income, expense, refund, transfer, credit, zero, a value
beyond JavaScript safe-integer precision, composite and multi-currency transactions. Browser RED
observed `Amount not shown` instead of the actual income amount. GREEN verifies the actual API
amount/currency and DOM for all nine rows in RU/EN. No response rewrite is used. Book hashes are
unchanged, quick_check is read-only, mutation requests are zero, and test runtimes stop.

- API generated/recent/reports/transactions suite: 153 passed, 24 warnings.
- Real-service money browser and neighboring dashboard browser: PASS.
- Svelte check, auth, money, transaction/account/scheduled static and QA loader checks: PASS.
- QA-01 commit `2ec96bb0d710caacdd606a981352d8f9a4a28ea9` CI run
  [33997832744](https://github.com/valentusys/gnucash-web-companion/actions/runs/33997832744)
  succeeded for all four jobs. This is not final roadmap CI.

## QA-03 — implemented and locally verified

Unscoped explorer DTOs expose `neutral_magnitude` only for proven simple pairs,
otherwise `multiple_amounts` with no representative total. Reordering splits and
changing synthetic split GUIDs must not choose the amount sign. Account scopes
use signed net quantities of the selected accounts; type scopes use quantities
of matching accounts. The existing configured-currency restrictions remain.
The legacy list/CSV account amount and amount filter now use account quantities,
including repeated account splits; CSV IDs and monetary basis are covered.

Both responsive views share a decimal-string display adapter and label unsigned
magnitude versus account change. Its cases include zero, negative scoped amounts,
large fractional values, missing/unknown bases and unavailable complex totals.
The real synthetic browser checks unscoped and scoped amounts (including a net
zero transfer) at mobile/desktop EN/RU, with unchanged book hash and zero book
mutation requests. Synthetic app metadata currency setup is counted separately.

Targeted API, money helper, neighboring explorer browser and static guards pass.
A full API integration run is pending at this checkpoint; final acceptance is
still pending all remaining QA IDs and exact-head CI/full matrix.

## Remaining

QA-04/09 date and drilldown, QA-05/06 account groups, QA-07/08/10
form and pagination states, QA-11/12 layout/localization, followed by full exact-head integration
and CI. No independent reviewer agent has been run. No final acceptance is claimed.

Default writes remain disabled. No release, tag, image, package or deployment is authorized by
this handoff. No private data or raw private evidence belongs in this document.
