# Phase 72 Audit — Data Model and Money Correctness

## Executive summary

Phase 72 audited the current money-handling model. The backend core paths use `Decimal` and string DTOs for money, CSV export preserves string amounts, report aggregation avoids fake currency conversion, and no newly introduced float-based money calculation was found in core backend paths.

The main non-blocking gap was documentation clarity: canonical docs described Decimal/string and no-fake-conversion rules, but did not provide a single concise reference for sign conventions and split amount interpretation. A second non-blocking follow-up is frontend hygiene: some Svelte components use JavaScript `Number()` for display-only sign/proportion decisions. Backend validation remains authoritative, so this is not a current release blocker, but it should be hardened later.

## Verdict

No new Phase 72 blocker for the current pre-alpha/read-only posture.

This is not a `v0.1.0-readonly` release approval, not a production-readiness claim, and not a professional security audit. `v0.1.0-readonly` publication remains blocked by the carried-forward release-gate items #24 and #25.

## Top blockers

No new Phase 72 blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

## Important non-blockers

1. Canonical money/sign documentation needed a clearer single reference for sign conventions and split interpretation. This was accepted for Phase 72 docs cleanup and addressed in `docs/money-model.md`.
2. Frontend display components still use JavaScript `Number()` on money strings for sign/proportion decisions. This does not change backend correctness and is not a release blocker for the current posture, but it is tracked in GitHub #34.
3. Existing performance follow-ups #30–#33 still matter for large-book confidence and should not be confused with money correctness.

## Product consistency

Observed consistent positioning:

- README keeps the project pre-alpha / MVP in progress.
- README says the app is read-only-first, self-hosted, a companion, not a GnuCash replacement, not SaaS, not collaborative accounting, and not production/security guaranteed.
- `PROJECT_STATUS.md` carried the baseline through Phase 71 before this phase.
- Release plan/checklist keep `v0.1.0-readonly` as planned but not published.
- Controlled writes remain documented as experimental post-MVP work, disabled by default.

No Phase 72 contradiction was found in release posture.

## Safety boundary

Phase 72 did not enable writes, expand write scope, publish a release, or add real financial/secrets artifacts.

Verified from inspected code/docs:

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default safety posture.
- `GnuCashBookService` opens books with `readonly=True`.
- Core read-only money formatting rejects `float` values in `format_money()` / `_decimal()` and formats `Decimal` values as strings.
- Read-only schemas expose account balances, transaction amounts, splits, cashflow, and reports as strings.
- Write DTOs require decimal strings for split amounts and remain behind disabled-by-default controlled-write gates from prior phases.

## Data model and money correctness

### No float arithmetic in core backend money paths

Evidence:

- `apps/api/app/services/gnucash_book.py` imports `Decimal`, defines `MONEY_QUANT = Decimal("0.01")`, aggregates report/cashflow totals with `Decimal("0")`, and converts non-Decimal values through `Decimal(str(value))`.
- `format_money()` and `_decimal()` explicitly raise `TypeError` for `float` values.
- Repository search found no backend `float()` conversions in core money paths; float mentions are limited to the guardrails above.

### Decimal/string schemas and JSON responses

Evidence:

- `apps/api/app/schemas/gnucash.py` defines money fields as strings: `MoneyDTO.amount`, `AccountDTO.balance`, `TransactionSplitDTO.amount`, `TransactionListItemDTO.amount`, report summary totals, cashflow values, expense totals.
- Router responses serialize DTO `model_dump()` output, preserving string amounts rather than JSON numeric money.

### CSV export preserves decimal strings

Evidence:

- `apps/api/app/routers/transactions.py` writes `item.amount` directly to CSV, where `item.amount` is produced by `TransactionListItemDTO` as a string.
- `docs/transactions-filters.md` says amount filters are decimal strings and that CSV export performs no currency conversion.
- Existing CSV export tests cover headers, data rows, filters, access denial, and filename. They do not introduce float money calculations.

### Multi-currency totals are conservative

Evidence:

- `apps/api/app/routers/reports.py` states non-base-currency values are excluded and no fake conversion is performed.
- `apps/api/app/services/gnucash_book.py` filters report/cashflow/expense totals to account/split currency matching `base_currency`.
- `apps/api/tests/test_multicurrency_reports.py` verifies EUR values are excluded from SEK report totals.
- `docs/ARCHITECTURE.md` documents non-base-currency exclusion rather than conversion.

### Sign and split clarity

Before Phase 72, sign conventions were scattered across architecture/handoff docs and code behavior. The PM accepted a docs-only cleanup. `docs/money-model.md` now records:

- API/CSV money values are decimal strings.
- Transaction list item amount is the selected/relevant split amount.
- Transaction detail shows all splits with signed amounts.
- Multi-split transaction list items use `counter_account_name = "Split transaction"`.
- Negative/positive display depends on account-type/context and should not be interpreted without context.

## Release/readme/docs consistency

Release docs remain conservative:

- `docs/release/v0.1.0-readonly-plan.md` says publication requires a later gate and copied/disposable dogfood evidence.
- `docs/release/v0.1.0-readonly-checklist.md` keeps unchecked publication gates and prohibits tag/release publication until required checks are satisfied.
- README did not claim broad compatibility, production readiness, audited security, safe writes, SaaS readiness, or collaborative accounting.

Phase 72 updates should keep README/PROJECT_STATUS/latest audit synchronized but must not claim v0.1 release readiness.

## GitHub project hygiene

`gh` is authenticated as `valentusys`. Existing open issues were reviewed to avoid duplicates.

Created:

- #34 — Avoid frontend Number() for money display decisions.

No issue was created for the docs gap because Phase 72 fixed it directly with `docs/money-model.md`.

## Security notes

No new security blocker was found in this money-correctness audit.

Relevant carried-forward security/safety issue:

- #27 — Avoid logging full GnuCash book paths during default book seed.

This phase did not inspect every security control again and must not be represented as a professional security audit.

## Test/CI notes

Recommended verification for this docs/audit plus money-correctness phase:

- Static searches for float/Decimal/money/schema/frontend `Number()` usage.
- `git diff --check`.
- Backend full suite: `cd apps/api && pytest -q`.
- Frontend checks: `cd apps/web && npm run check && npm run test:auth-routes && npm run build`.
- Docker Compose config validation with dummy secrets.

## Recommended next actions

1. Keep #24 and #25 as release blockers before any `v0.1.0-readonly` tag/release.
2. Address #34 in a later frontend-hardening phase by replacing display-only `Number()` money decisions with string/sign helpers or a decimal-safe utility.
3. Continue #30–#33 before claiming large-book scalability.
4. Do not expand controlled writes while read-only release gates remain unresolved.

## Suggested GitHub issues

Created:

- #34 — Avoid frontend Number() for money display decisions (`audit`, `safety`, `read-only`).

No other new issue is recommended for Phase 72.

## What not to do next

- Do not publish `v0.1.0-readonly` until #24/#25 are resolved by explicit later phases.
- Do not start Phase 73 from this phase.
- Do not enable writes by default.
- Do not introduce float-based money arithmetic in backend core paths.
- Do not add fake currency conversion.
- Do not market the project as production-ready, security-audited, SaaS, collaborative accounting, a GnuCash replacement, or safe for writes.
