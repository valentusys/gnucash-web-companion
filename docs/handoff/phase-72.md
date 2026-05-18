# Phase 72 — Data Model and Money Correctness Audit

## Status

Complete. Phase 72 performed the auditor-first data model and money-correctness audit from the auditor roadmap, created the required audit artifact, created one meaningful GitHub follow-up issue, synchronized durable status docs, ran relevant checks, and pushed the phase commit.

This phase did not publish `v0.1.0-readonly`, did not expand write scope, did not enable writes, did not add fake currency conversion, and did not start Phase 73.

## Auditor report

### Verdict

No new Phase 72 blocker for the current pre-alpha/read-only posture.

Backend core money paths use `Decimal` and string DTOs, JSON responses serialize money as strings, CSV export preserves decimal string amounts, multi-currency report totals remain conservative with no fake conversion, and no newly introduced backend float-based money calculation was found.

This verdict is limited to Phase 72 money correctness. It is not a `v0.1.0-readonly` release approval, not a production-readiness claim, and not a professional security audit.

### Blockers

No new Phase 72 blocker was found.

Carried-forward blockers before any `v0.1.0-readonly` publication:

1. #24 — conservative `v0.1.0-readonly` release notes are still required before publication.
2. #25 — copied/disposable-data runtime smoke/dogfood evidence is still required before publication.

### Audit report

- `docs/audits/phase-72-audit.md`

### Suggested / created GitHub issues

Created:

- #34 — Avoid frontend Number() for money display decisions.

No issue was created for canonical sign/split docs because Phase 72 fixed that directly with `docs/money-model.md`.

### Auditor evidence summary

- AGENTS.md, PROJECT_STATUS.md, README.md, CHANGELOG.md, release docs, latest handoff, Project Lead profile, roadmap file, relevant backend/frontend code, tests, docs, and open GitHub issues were inspected.
- `apps/api/app/services/gnucash_book.py` uses `Decimal`, formats money strings, rejects `float` values in service-layer money conversion, and opens books read-only.
- `apps/api/app/schemas/gnucash.py` exposes money fields as strings for accounts, transactions, splits, cashflow, and reports.
- `apps/api/app/routers/transactions.py` writes CSV `amount` from `TransactionListItemDTO.amount`, preserving string values.
- `apps/api/app/routers/reports.py`, `GnuCashBookService`, and `apps/api/tests/test_multicurrency_reports.py` confirm non-base-currency values are excluded rather than converted.
- Frontend components still use `Number()` on money strings in display-only contexts such as sign styling, proportional bars, and client-side range prevalidation; backend Decimal validation remains authoritative.

## PM report

### Decision

Accept the auditor verdict. Phase 72 may safely record the audit, create a single meaningful GitHub issue for frontend display-only `Number()` money hygiene, add canonical money/sign/split documentation, update README/PROJECT_STATUS/CHANGELOG/handoff, and run verification.

No product feature work, write expansion, currency conversion, release publication, or Phase 73 work is accepted in this phase.

### Why

The roadmap asks for a money-handling audit. The backend core money model is already conservative enough for the current pre-alpha/read-only posture. The safest accepted work is durable documentation/status synchronization plus issue hygiene for the frontend display-only hardening follow-up.

### Phase brief

- Goal: complete Phase 72 as a data model and money-correctness audit; inspect float usage, Decimal/string schemas, JSON/CSV money serialization, multi-currency behavior, fake conversion risk, sign conventions, and split amount clarity.
- Non-goals: no Phase 73, no product feature work, no write-scope expansion, no release/tag publication, no real financial/secrets artifacts, no production/security/safe-write/broad-compatibility claims.
- Acceptance criteria:
  - `docs/audits/phase-72-audit.md` exists.
  - `docs/handoff/phase-72.md` exists.
  - `PROJECT_STATUS.md` reflects completion through Phase 72 and next explicit-only Phase 73.
  - README latest-audit/current-status references are synchronized.
  - CHANGELOG records the release-facing Phase 72 audit/docs result.
  - Canonical money/sign/split docs exist.
  - Meaningful GitHub issue hygiene is completed without noisy issues.
  - Relevant checks pass.
  - A separate commit is created and pushed to `origin/main`.
- Safety checks:
  - Keep MVP read-only by default.
  - Keep `GNUCASH_WRITES_ENABLED=false` as the default.
  - Keep controlled writes experimental/post-MVP only.
  - Do not commit `.env`, real books, app DBs, backups, secrets, keys, certs, real screenshots, or real exports.
  - Do not claim production readiness, security audit, broad compatibility, SaaS readiness, GnuCash replacement, collaborative accounting, safe write mode, or fake currency conversion.
- Verification:
  - Static money-correctness searches.
  - `git diff --check`.
  - `cd apps/api && pytest -q`.
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`.
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`.
  - GitHub issue verification via `gh`.

### Risks

- Frontend `Number()` follow-up could be overread as current backend money corruption. Mitigation: audit/handoff distinguish display-only frontend contexts from backend core Decimal correctness and created #34 as non-blocking hygiene.
- Sign conventions could be oversimplified. Mitigation: `docs/money-model.md` says signs depend on GnuCash/piecash/account-type context and transaction detail preserves all split amounts.
- Money docs could imply release readiness. Mitigation: all status docs keep #24/#25 as v0.1 blockers and do not publish a release.

### Files/docs to update

- `docs/audits/phase-72-audit.md`
- `docs/handoff/phase-72.md`
- `docs/money-model.md`
- `PROJECT_STATUS.md`
- `README.md`
- `CHANGELOG.md`
- `docs/ARCHITECTURE.md`

### GitHub/backlog

- Created #34 for frontend display-only `Number()` money hygiene.
- No duplicate/noisy issue created for the sign/split docs gap because it was fixed directly.
- #24 and #25 remain v0.1 publication blockers.

## Engineer report

Implemented only PM-accepted Phase 72 docs/status/GitHub hygiene work:

- Created `docs/audits/phase-72-audit.md` with auditor verdict, blockers, non-blockers, money correctness findings, GitHub issue decisions, safety notes, test notes, and next actions.
- Created `docs/money-model.md` documenting Decimal/string representation, CSV export behavior, sign conventions, split amount clarity, and multi-currency no-fake-conversion behavior.
- Updated `docs/ARCHITECTURE.md` to link the canonical money model.
- Created GitHub issue #34 for frontend display-only `Number()` money hygiene.
- Updated `PROJECT_STATUS.md` to mark completion through Phase 72, add Phase 72 to completed phases, set Phase 73 as the next explicit-only roadmap phase, and add a Phase 72 status section.
- Updated `README.md` current status through Phase 72 and latest-audit link.
- Updated `CHANGELOG.md` with the release-facing Phase 72 money-correctness audit entry.
- Created this handoff document.

No product code changed. No write behavior/default changed. No tag or GitHub release was published. No Phase 73 work was started.

## Checks

Run during Phase 72:

- `git status --short --branch` — clean against `origin/main` before edits.
- `git --version` — `git version 2.53.0`.
- `~/.local/bin/gh --version` — `gh version 2.46.0`.
- `~/.local/bin/gh auth status` — authenticated as `valentusys`.
- `~/.local/bin/gh issue list --state open --limit 100 --json number,title,labels,url` — reviewed open issues and avoided duplicates.
- `~/.local/bin/gh issue create ...` — created #34.
- Static money-correctness searches:
  - backend core money service uses `Decimal`, formats strings, and rejects floats;
  - read-only schemas expose money fields as strings;
  - CSV export writes DTO string amounts;
  - multi-currency report docs/tests exclude non-base-currency values and do not fake conversion;
  - frontend display-only `Number()` usages were identified and tracked in #34.
- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed, 282 passed, 27 warnings.
- `cd apps/web && npm run check` — passed, 0 errors and 0 warnings.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

Final check results:

- Required audit artifacts: passed.
- GitHub issue hygiene: passed (#34 created; no noisy duplicate issue created).
- Static money-correctness assertions: passed.
- Backend/frontend/Docker checks: passed.
- Diff whitespace: passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- No write scope was expanded.
- No v0.1 release/tag was published.
- No Phase 72 result was represented as production readiness, release approval, security audit, broad compatibility, safe write-mode support, or currency conversion support.
- No broad GnuCash compatibility claim was introduced.
- No XML/PostgreSQL/MySQL/MariaDB/all-version/all-book support claim was introduced.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Phase commit message: `docs: add phase 72 money correctness audit`.
- Phase commit: `f47e4b0` before handoff self-reference update; final pushed commit hash is recorded in the Phase 72 final/Telegram report after amend/push verification.

## Blockers carried forward

1. Create and review conservative `docs/release/v0.1.0-readonly-notes.md` before any release publication (#24).
2. Complete and record copied/disposable-data Docker/runtime smoke and manual dogfood evidence before any release publication (#25).
3. Redact/sanitize full default-book seed log path/URI output and add/adjust tests (#27).
4. Continue gradual markdown source readability cleanup before broader announcement (#28).
5. Add a localization glossary for accounting/safety terms before the Russian translation surface grows (#29).
6. Continue real GnuCash Desktop version fixture coverage in #22 when an explicit compatibility implementation phase is requested.
7. Use #26 to make CORS origin narrowing visible in future release/checklist/deployment hardening work.
8. Implement generated/disposable read-only performance benchmark coverage for #30–#33 before claiming known large-book scalability.
9. Replace frontend display-only `Number()` money decisions with string/sign helpers or a decimal-safe utility in a later hardening phase (#34).

Do not start Phase 73 until explicitly requested.
