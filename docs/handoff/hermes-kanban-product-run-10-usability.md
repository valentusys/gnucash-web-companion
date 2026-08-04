# Hermes Kanban product run 10 — issue #60 usability handoff

Status: factual closeout after the accepted product head was integrated and pushed by fast-forward
only, exact-head CI succeeded, and issue #60 was closed.

This is pre-alpha software. Use generated fixtures or test copies first. This handoff is not a
release note, hosted-SaaS claim, production-readiness guarantee, or security-audit claim.
`GNUCASH_WRITES_ENABLED=false` remains the default. The product performs no FX conversion, uses no
external currency rates, and does not combine different currencies into a converted total.

## Run and PM contract

- Run start: `2026-07-23T23:36:03Z`.
- Baseline: `51ae5b3598678e6e09bfbd2024e5df5fe8a4a2c3`, tree
  `778bd0327435d3e385115ffef1a7aadf90c6c107`.
- PM card: `t_370f3ba5`, runs `240`–`241`, verdict `ACCEPT`.
- Authoritative PM contract comment:
  [#issuecomment-5065027596](https://github.com/valentusys/gnucash-web-companion/issues/60#issuecomment-5065027596).

The accepted contract froze one shared canonical account-visibility policy, deterministic
reporting-currency resolution, a typed split-derived transaction direction DTO, compact account
labels and placeholder behavior, complete touched-surface EN/RU copy, and a generated/disposable
browser acceptance flow. It did not authorize FX, external rates, PATCH/DELETE expansion, a
release, or owner/private-book work.

The permitted QA defect/recheck cycle was not used. Operator review before clean QA corrected exact
Decimal direction serialization and the localized BookSwitcher accessibility label on the original
implementation cards. Clean QA accepted the resulting cumulative candidate on its first run. An
unintended run `255` auto-specifier redispatch was terminated and reclaimed before source mutation.

## Ordered source and integration map

1. Baseline: `51ae5b3598678e6e09bfbd2024e5df5fe8a4a2c3`, tree
   `778bd0327435d3e385115ffef1a7aadf90c6c107`.
2. Local backend commit: `d61124f6d799a3dd4cea0016f5cbc86452bb3025`, tree
   `78e3fc0db5e0c1dcfaf0170ae65e98ae0bcfb2d5`, stable patch ID
   `12581227794ec3c66ac019248de84f757a569c97`. Its patch is identical to accepted backend source
   `d441752acd06ab0b40bc40ce5b95c352e7e0ea97`.
3. Frontend and final product head: `73f55ea11f6581056449dcecf5219367d984b456`, tree
   `46eb7f940b4fb78727138f73d197e641a89e2361`, stable patch ID
   `7a9f486b163bb49e4264d5ee73647fd3d885e6fe`.

Backend card `t_be9f9eed`, runs `242`–`247`, produced accepted source
`d441752acd06ab0b40bc40ce5b95c352e7e0ea97`. Frontend card `t_accfb426`, runs `250`–`255`,
produced the accepted corrected cumulative head `73f55ea11f6581056449dcecf5219367d984b456`.

QA verified that each accepted patch appears exactly once. Task `t_6132dd89`, run `257`, rebuilt the
candidate from the baseline by fast-forward only and returned `FINAL ACCEPT` on the exact unchanged
head and tree. The operator then integrated and pushed the exact product head by fast-forward only.
`main` and `origin/main` were clean and synchronized at that head before this docs-only card.

## Reporting currency and dashboard behavior

Only visible, active, non-hidden, non-placeholder leaf accounts are eligible. Their type must be one
of `ASSET`, `BANK`, `CASH`, `RECEIVABLE`, `LIABILITY`, `CREDIT`, `PAYABLE`, `EQUITY`, `INCOME`, or
`EXPENSE`; their commodity namespace must be exactly `CURRENCY`; and the normalized mnemonic must be
non-empty and not `XXX`.

A candidate needs at least one eligible leaf and one finite, non-zero Decimal `split.value` in an
ordinary visible transaction. Zero technical splits do not count. Ranking never uses floats,
`quantity`, absolute amount magnitude, or cross-currency numeric comparison. The exact descending
score is:

1. `distinct_transaction_count`;
2. `nonzero_split_count`;
3. `active_leaf_account_count`;
4. `eligible_leaf_account_count`.

A valid configured currency remains the explicit operator preference. Otherwise, a unique highest
score is selected with `source=detected`. No candidates or an exact top-score tie returns
`status=setup_required`, `source=none`, and no selected currency or fabricated zero totals. Lexical
order is display order only and never breaks a score tie.

Configured-currency status is typed as `valid`, `missing`, `xxx`, `absent`, `template_only`,
`non_monetary`, or `inactive`. The dashboard does not display legacy `XXX`. A ready response retains
`reporting_basis=base_currency_only`, uses exact Decimal strings, and reports the selected currency
plus the actual sorted `excluded_currencies`. A setup-required summary has no money-total fields;
other currency-dependent report endpoints return typed `REPORTING_CURRENCY_SETUP_REQUIRED` detail.
Non-currency commodities are excluded without being described or valued as currencies.

The accepted fixture selects RUB uniquely, reports USD in `excluded_currencies`, excludes BTC as a
non-`CURRENCY` commodity, and performs no conversion or RUB/USD/BTC mixing.

## Transaction direction

Normal transaction list and explorer rows now carry a typed direction object while legacy fields
remain for compatibility. Direction is derived from exact signed `split.value`:

- negative values are `from_accounts` (`From` / `Откуда`);
- positive values are `to_accounts` (`To` / `Куда`);
- zero values are ignored;
- repeated splits aggregate by account and sign with exact Decimal sums and a `split_count`, while
  preserving first-split order.

One distinct account on each side with equal absolute totals is `resolved/balanced`. A balanced side
with multiple accounts is `composite/multiple_accounts`. No non-zero splits, a one-sided or
unbalanced transaction, or one account on both signs returns the corresponding honest `ambiguous`
state; the UI does not invent a representative account, amount, or arrow.

Observed cases include salary income, a two-split expense, transfer, credit-card expense, balanced
three-split purchase, repeated same-account destination splits, a zero technical split, an empty
description, and a same-account-both-sign ambiguity. Exact direction values are serialized with
`format(value, "f")`; the frontend localizes the direction and empty-description text.

## Canonical accounts, labels, and placeholders

Canonical Template Root identity comes from GnuCash `books.root_template_guid`, exposed by piecash as
`book.root_template_guid` / `book.root_template`. The account and all descendants are excluded by
bounded, cycle-safe GUID/parent ancestry. Canonical normal Root Account identity similarly comes from
`books.root_account_guid` / `book.root_account`; the structural row is suppressed and its visible
children are promoted to ordinary top-level roots.

The fallback is used only when canonical identity is absent or unresolvable: Template Root requires
exactly one parentless `ROOT` account named exactly `Template Root`, and the normal root is the unique
remaining parentless `ROOT`. Ambiguity suppresses structural `ROOT` rows without classifying
ordinary descendants by name. A legitimate non-root account named `Template Root` remains visible.
Direct requests for excluded accounts or template transactions use the existing safe not-found
behavior, and CREATE preview rejects root, template, and placeholder IDs as
`ACCOUNT_NOT_POSTABLE` before backup, lock, or write.

Compact labels use the normalized leaf name. Duplicate leaves add the shortest meaningful parent
suffix that makes the label unique, then account code, type plus commodity, or a stable ordinal as
bounded fallbacks. Full paths remain tooltip/accessibility metadata; GUIDs remain internal IDs and
are not ordinary-tree display text. Placeholder accounts render as compact, non-postable groups with
children rather than normal balance/activity cards. Root, Template, placeholder, hidden,
unsupported-type, and non-`CURRENCY` accounts do not appear as CREATE posting choices.

## EN/RU status and viewport behavior

Touched dashboard, account, direction, placeholder, setup, exclusion, CREATE-selector, and safety
copy is present in English and Russian. The shared signed-in status is a compact accessible row with
`Read-only by default` / `Только чтение по умолчанию`, active-book context, the GnuCash Desktop
editor boundary, and a safety-details disclosure that retains the pre-alpha, test-copy-first, and
not-production-ready limitations. The BookSwitcher accessibility label is localized and tests use a
locale-neutral selector.

Generated browser acceptance passed independently for Russian desktop, Russian 320 px, and English
desktop dashboard views plus a 320 px account view. Horizontal overflow was `0` in all four checks;
console events and browser-forbidden mutations were also `0`.

## Generated fixture and issue #59 CREATE regression

The generator is
`apps/api/tests/support/generate_issue60_usability_fixture.py`. Seed `60060` creates one read-only
source under a caller-owned temporary `source/` directory and one separate writable disposable copy
under `working/`. No generated raw book is tracked.

The fixed hierarchy contains:

- canonical Root Account and canonical Template Root;
- RUB placeholder groups for assets, banks, business, investments, liabilities, income, expenses,
  and equity;
- duplicate RUB `Сбербанк` leaves under `Банки` and `Бизнес`, plus RUB bank, cash, card, income,
  expense, and opening-balance leaves;
- active USD cash/travel leaves;
- a BTC commodity in namespace `CRYPTO` under investments;
- a legitimate visible RUB account named `Template Root`;
- canonical Template Root descendants named `Сбербанк` and `Продукты`, which stay excluded.

The fixed source has 14 transactions and 35 splits: opening balance, salary, Unicode expense,
transfer, balanced three-split purchase, credit-card expense, repeated-account split, zero technical
split, empty description, USD activity, BTC/security activity, same-account-both-sign ambiguity,
visible Template-named account activity, and a hidden canonical-template transaction.

The issue #59 regression enabled controlled CREATE only for the disposable target. It performed one
preview and exactly one successful expense CREATE, then repeated the same confirmation key. The
repeat returned the existing transaction with HTTP `200`; idempotency read-back found one row and no
second transaction. Target counts changed from 14 to 15 transactions and 35 to 37 splits. Evidence
also found one ownership row, four audit rows, one backup file, and one verified-backup marker. The
new transaction was visible through ordinary transaction and dashboard/account read paths with the
expected direction. Outside this isolated generated target, writes remained default OFF. Target
CREATE was `1`, duplicate confirm `1`, PATCH `0`, and DELETE `0`.

The source SHA-256 remained unchanged before and after:
`84cbd2827bc6f0869ff73cd249a3e0587cf3c869c295cd33461aa238ad20bf20`.
The disposable target hash changed, and the temporary root was cleaned by the browser trap.

## Independent QA matrix

Clean QA task `t_6132dd89`, run `257`, returned `FINAL ACCEPT` on exact product head
`73f55ea11f6581056449dcecf5219367d984b456` and tree
`46eb7f940b4fb78727138f73d197e641a89e2361`.

Root checks all passed:

- `python3 scripts/check_public_status.py`;
- `python3 scripts/check_write_safety_defaults.py`;
- `python3 scripts/check_markdown_readability.py`;
- `python3 scripts/check_tracked_hygiene.py`;
- `git diff --check`;
- Docker Compose validation with dummy local validation credentials.

Backend checks all passed with the canonical API Python:

- issue #60 usability: `6 passed`;
- reporting currency and reports: `70 passed`;
- direction and latest transactions: `101 passed`;
- accounts and Template visibility: `60 passed`;
- issue #59 CREATE/control/write regression: `300 passed`;
- metadata, authentication, and access: `165 passed`;
- full backend: `1490 passed`, `98 warnings`, `690.68s`.

Frontend checks passed with Node `v22.22.2` and npm `12.0.2`: `npm run check` reported zero
errors/warnings, `npm run build` passed, and all required auth, preview, CREATE, reports, dashboard,
accounts, admin, books, transaction explorer, and money-string static gates passed. All required
browser gates passed, including the product CREATE, real disposable CREATE, preview/disposable,
reports, dashboard, issue #60 usability, admin users, books onboarding, accounts explorer, and
transactions explorer gates.

## Product-head CI and issue closeout

These are observed product-head facts:

- Product head: `73f55ea11f6581056449dcecf5219367d984b456`.
- GitHub Actions CI
  [30864811558](https://github.com/valentusys/gnucash-web-companion/actions/runs/30864811558)
  completed with conclusion `success` on that exact head.
- [Foundation checks](https://github.com/valentusys/gnucash-web-companion/actions/runs/30864811558/job/91854248342):
  success.
- [Frontend checks](https://github.com/valentusys/gnucash-web-companion/actions/runs/30864811558/job/91854248396):
  success.
- [Backend tests](https://github.com/valentusys/gnucash-web-companion/actions/runs/30864811558/job/91854248420):
  success.
- [Docker Compose validation](https://github.com/valentusys/gnucash-web-companion/actions/runs/30864811558/job/91854248452):
  success.
- [Issue #60](https://github.com/valentusys/gnucash-web-companion/issues/60) is closed.
- Factual closeout comment:
  [#issuecomment-5173158786](https://github.com/valentusys/gnucash-web-companion/issues/60#issuecomment-5173158786).

## Safety and artifact counters

Accepted product evidence recorded:

- owner/private/original/Syncthing list/access/probe/hash/copy: `0`;
- owner/private/original/Syncthing CREATE/PATCH/DELETE/batch/source-delete: `0`;
- generated source create: `1`;
- disposable working copy: `1`;
- source modification/deletion: `0`; source hash unchanged;
- generated target CREATE: `1`; duplicate confirm: `1`; PATCH: `0`; DELETE: `0`;
- browser-forbidden mutations: `0`;
- committed raw/runtime/private artifacts: `0`;
- cleanup: `true`.

## Bounded remaining UX backlog

Issue #60 is complete within its accepted boundary. The following remain explicit limitations or
separate future work rather than unfinished claims in this closeout:

- an ambiguous or absent reporting currency still requires an administrator to choose an observed
  working currency through existing book settings;
- FX conversion, external rates, cross-currency totals, and security valuation remain unsupported;
- scheduled-transaction metadata was not redesigned;
- broader account/reporting rewrites and full-application localization were not part of this issue;
- release publication, hosted operation, production readiness, and security audit remain outside
  this product-run closeout.

## Docs-only pending state

The product head CI success and issue closure above are observed facts. This handoff and status
update form a newer docs-only commit on top of that product head. Its future commit SHA and its own
exact-head GitHub Actions result do not exist at edit time and are not predicted here. The operator
must verify this docs-only head after merge and push.
