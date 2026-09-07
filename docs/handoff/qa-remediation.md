# QA remediation handoff

Status: in progress on `fix/qa-20260906`; not merged or released.

## QA-12 — implemented and locally verified

Validated locale determines SSR HTML language; calendar presets and filter chips use the shared
dictionary without changing dates, URLs, IDs or backend contracts. Russian primary explorer,
form, error and recovery text no longer mixes developer terminology into the main task.
Technical metadata is disclosed after transaction results; expanded filters and form policy
help start closed. Structural account warnings, incomplete scans, unavailable/partial/truncated
account choices and direct/nested recovery warnings remain visible. A populated final page
still renders the actual last-page message. No submission or authorization gate is loosened.

The real generated-book UX gate covers EN/RU at 320x800 and 390x844 across accounts, transactions
and the draft form. Search/tree, filters/first result and form input begin above the mobile
navigation. Keyboard help disclosure, actual filter submission and visible malformed-cursor
and invalid-filter errors are exercised. Synthetic RU screenshots were visually reviewed;
native date-input formatting and currency/account identifiers are not claimed translated.
Supplementary stub browser cases cover unavailable/partial/truncated choices, direct/nested
recovery and incomplete scans, with no hidden warnings or book mutations. Existing geometry,
bounded DOM, focus, request and preview-safety guards remain enforced, not relaxed.

Local check/build and all 18 registered non-browser test scripts pass. Real UX, form-state and
pagination browser runs pass with identical generated-book hashes, zero book mutation requests
and stopped child runtimes. Both neighboring explorer browser suites pass. These slice checks
do not replace the pending full final-head integration and exact-head CI. No private book or
independent reviewer agent was used for this slice.

## QA-11 — implemented and locally verified

Desktop header content wraps into bounded rows, leaving logout and other controls visible
rather than hiding overflow. Mobile Escape dismisses the menu and returns focus to its trigger.
No routes, permissions, or logout authorization semantics changed.

The generated real-backend runner checks bounding rectangles and center hit tests for navigation,
locale/theme and logout controls with a long synthetic book name. EN/RU widths are 320, 390, 768,
1024, 1280, 1440 and 1920; desktop widths also run at a CDP effective CSS viewport equivalent
to 200% browser zoom. This is reflow emulation, not a native-browser-chrome zoom or real-phone
claim. Each case reaches logout via Tab, verifies focus visibility, activates it with Enter,
then logs in again. Collapsed-menu cases also exercise Enter/Escape and focus restoration.
The 24 session logout requests are separately counted and are not book mutations. Real API
logout responses succeed; generated book hashes stay identical and child runtimes stop.
Synthetic desktop/mobile screenshots were visually reviewed: logout is visible and unoverlapped.

## QA-10 — implemented and locally verified

Nonempty final results now have a dedicated localized `final_page` status. Empty continuation,
true empty, ordinary ready and scan-limited states remain separate, including conservative
handling of scan-limited responses with an exhausted flag. No backend cursor/export semantics
were changed. Unit state branches cover first-page finals and empty continuations in EN/RU.

A deterministic generated book contains 32 transactions. Real browser navigation verifies
20 then 12 results, the last-page message, all IDs without duplicates or omissions, previous-page
round-trip, the actual CSV link with the same filters, and an invalid-cursor alert. Exported IDs
exactly equal both cursor pages. Generated source remains unchanged; no book writes occur.
API explorer/export suites also pass, including their stale-cursor regression coverage.

## QA-08 — implemented and locally verified

The form loads the same real Summary resolution as Dashboard, uses only a ready valid monetary
code, and passes it to bounded account choices. Empty, tied, unavailable or invalid resolutions
leave a blank required currency field with localized guidance. Valid returned explicit choices
remain above the default after validation errors; no configured metadata or book is changed.
Backend commodity/configuration validation and all confirmation/write gates remain unchanged:
an inferred form default is not permission to convert currencies or save a transaction.

Generated RUB/EUR, tie and empty fixtures prove resolver behavior and deterministic hashes.
Real browser checks exercise EN/RU default fields and the actual mobile/desktop BookSwitcher
in both directions. This exposed a related console error: `goto` was used for a server-only
GET endpoint. Navigation now uses its existing encoded, server-validated URL directly, with
no missing-page fallback. Actual navigation is a document reload; state-reset branch tests
also exercise same-component book changes. Both generated book hashes stay unchanged.
Explicit USD choice plus exact decimal strings survive an actual validation response on a
configured RUB test book. Read-only acceptance executes no confirm or book mutation requests.

## QA-07 — implemented and locally verified

Absent form errors now produce no error summary; unknown real failures keep a fixed catalog
fallback. Backend preview warnings carry snake_case message keys: their known codes map to
localized restriction messages, while unknown warnings have neutral safe fallback copy.
Static background safety guidance uses a status role on this form; other write-warning
callers retain alert by default. Example created/already-created results are removed, not
the existing server-confirmed success redirect or its catalog entries.

Real generated-book browser checks in EN desktop/RU mobile cover fresh GET, actual preview
button click, exact decimal strings and controlled IDs, blocked confirmation, edited/stale
draft, actual validation failure and an explicitly injected transport disconnect. No response
DTO is rewritten. Known blocked warnings no longer masquerade as generic request errors.
The network classifier tests exact preview action/query and API path allowlists, rejecting
confirm/CREATE/PATCH/DELETE/settings and malformed preview requests at both boundaries.
Book hashes remain unchanged; zero mutations and stopped runtimes are recorded separately
from non-mutating preview POST counts. Form/request-policy units, check/build, preview/product
and auth guards pass; historical synthetic CREATE browser drills are not this acceptance.

## QA-06 — implemented and locally verified

Account records retain structural-root evidence from the full visibility index before root
suppression. Known structural-root children become top-level `root` nodes without losing
`source_parent_id`; unknown parents remain orphans. Ordinary accounts named Root are not
special-cased. Filtered ancestors, self/multi-node cycles and duplicate diagnostics remain.

RED: generated real-service browser and six API assertions showed false orphan status. GREEN:
`test_qa_account_hierarchy.py`, `test_accounts.py`, `test_account_overview_activity.py` passed
(62 tests); SQL aggregation suite passed. Generated SQLite and in-memory node DTOs match;
the real-service account-group browser passes with unchanged book hash and zero mutations.
All new evidence is synthetic; no book is repaired or modified by the hierarchy view.

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

QA-04 is also locally verified: shared API calendar, metadata-only authorized date
endpoint, Summary fallback, Reports/quick presets and explicit scheduled as-of.
See [reporting calendar contract](../reporting-date.md). Clock-controlled real API
browser runs passed for east/west offsets, new year, leap-month rollover and DST,
each EN desktop/RU mobile, unchanged generated-book hashes and no book mutations.
The native clock remains the API process local date; no new timezone/freeze setting.
Reports, dashboard, scheduled and transaction neighboring browser gates passed.
QA-01–QA-04 full API integration passed locally: 1620 tests, 149 warnings in 741.44s.
Historical synthetic-write suites remain separate from new read-only acceptance. These are
incremental checks, not final roadmap acceptance.

QA-04 follow-up: exact-head CI for `03b113caac373bf40304458622682906b04580b6`
failed in the umbrella auth guard, which still required a scheduled URL without a date query.
Local RED reproduced that assertion. The reconciled guard requires the encoded explicit query,
active-book prefix and auth token, and forbids a frontend-computed scheduled today. Svelte
check and all current non-browser npm test scripts passed after reconciliation; replacement
exact-head CI is not yet claimed here. No product write/auth/date behavior was weakened.

The next CI run at `438cc7e97849fdcbcb58337aafe91b2f21ad283d` passed backend,
foundation and Compose checks but exposed an onboarding browser stub missing the reporting-date
endpoint. Its Reports assertion was reproduced locally. The deterministic stub now models that
endpoint and asserts exact selected-book month/date query values; the onboarding browser passed.
This is explicitly a stub-backed lifecycle regression, not replacement real-backend acceptance.
The replacement commit `6994dda13180397cd5fb0dcbf769fac783ea09c9` passed all four
exact-head CI jobs in run [34003063011](https://github.com/valentusys/gnucash-web-companion/actions/runs/34003063011),
as verified by the parent before the approved continuation. This does not replace final integration.

## QA-09 — implemented and locally verified

The loader groups actual recent dates into disjoint periods of at most 366 inclusive days.
The header opens the latest period; every older group has a visible dated, localized link.
Empty data uses the authoritative reporting-month range; unavailable authority does not invent
a date. Active-book cookies, UI locale, descending date sort and page size remain unchanged;
no stale cursor or all-time query is introduced.

RED reproduced missing date parameters in the real browser and a missing bounded helper in
the unit guard. GREEN covers leap bounds, duplicate/invalid dates, old and sparse history,
empty/unavailable dates and actual loader-to-component wiring. A generated sparse book has
nine transactions across three distant dates; real clicks reach all IDs in both EN desktop
and RU mobile, with exact API query/date/ID assertions. The empty generated-book click returns
a genuine zero-row result. Money-scenario header click also passes. Hashes are unchanged,
SQLite quick_check is ok, book mutation requests are zero and runtimes stop.

Local checks: eight fixture tests; all registered non-browser npm tests; Svelte check and build;
real money/sparse/empty browser scenarios; neighboring dashboard and explorer browser gates.
CI includes the new unit and sparse real-backend scenario; this slice's exact-head CI and final
roadmap matrix are still pending. An existing static HTML lang=en despite RU UI was discovered
and is tracked for QA-12; this slice verifies visible translated UI, not corrected HTML language.

## Next

QA-05 is implemented and locally verified. Placeholder detail now shows the API's complete
recursive currency buckets without calculating totals from the child prefix. The group remains
non-postable with no direct-activity form. Truncated child lists explicitly link to the existing
paged tree including hidden accounts. No endpoint bounds or write gates changed.

A deterministic generated group has 205 immediate children, including nested multi-currency
envelopes and a hidden tail beyond the 200-child overview bound. Real API/browser RED reproduced
the missing total. GREEN verified separate RUB/USD/EUR buckets, zero/negative leaf amounts,
every immediate child through tree paging, and opening the hidden tail and nested group in
EN desktop/RU mobile. The source hash remains unchanged, quick_check is ok, book mutations
and direct-activity requests are zero, and runtime cleanup passes. The API fixture/overview
suite passed 30 tests (36 existing dependency warnings); Svelte check/build, account/auth/recent
guards and the neighboring account browser passed. Final exact-head acceptance remains pending.

All QA-01 through QA-12 fixes are now locally verified. The remaining work is the full exact-head
integration, real-backend browser matrix, safety/performance review and CI, followed by human
review. No independent reviewer agent has been run. No final acceptance is claimed.

Default writes remain disabled. No release, tag, image, package or deployment is authorized by
this handoff. No private data or raw private evidence belongs in this document.
