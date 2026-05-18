# Phase 104 — Read-only transaction query semantics over split memos (#11)

## Status

Complete. Phase 104 implemented `docs/handoff/phase-104-pm-brief.md` as a narrow read-only transaction search/filter improvement from GitHub #11.

Verdict: completed.

No `v0.1.1-readonly` tag was created. No GitHub release was created or edited. No package or external release artifact was published.

## Implementation summary

Broadened the existing public `query` contract without adding a new parameter:

- transaction description search remains supported;
- split memo text is now searched too;
- matching is case-insensitive;
- the same service-layer matcher is used by transaction list and count paths, so pagination totals stay consistent;
- CSV export uses the same broadened filter path and keeps its existing corrected CSV metadata headers;
- frontend helper copy now describes the search box as `Description or split memo...`.

No route-level duplicate search logic was added. The frontend still submits the existing `query` value only. No browser persistence/localStorage/sessionStorage behavior was added.

## TDD evidence

RED checks observed before implementation:

- `pytest tests/test_gnucash_book.py::test_transaction_query_matches_split_memo_case_insensitively tests/test_gnucash_book.py::test_transaction_query_without_description_or_memo_match_returns_empty tests/test_transactions.py::TestListTransactionsMVP::test_filter_by_query_matches_split_memo_and_counts_consistently tests/test_transaction_export.py::TestExportTransactionsCSV::test_export_query_filter_matches_split_memo -q` — expected failure on memo-only matches: service list returned `[]`, API total was `0`, CSV had only the header row.
- `npm run test:auth-routes` — expected failure on missing helper copy for `Description or split memo...`.

GREEN checks after implementation:

- Targeted backend memo-query tests passed: `4 passed, 1 warning`.
- Targeted frontend route/static check passed: `auth route checks passed`.

## Verification summary

Initial non-mutating boundary checks before implementation:

| Check | Result |
| --- | --- |
| `git status --short` | PASS — clean output. |
| `git rev-parse --abbrev-ref HEAD` | PASS — `main`. |
| `git rev-parse --short HEAD` | PASS — `c300f44`. |
| `git tag --list 'v0.1.1-readonly'` | PASS — no tag output. |
| `gh auth status` | PASS — authenticated as `valentusys`. |
| `gh release view v0.1.1-readonly || true` | PASS — `release not found`. |
| GitHub #11 inspection | PASS — issue is open and includes broader full-text/search semantics as remaining read-only enhancement scope. |

Final full verification before commit/push:

- `cd apps/api && pytest -q` — PASS, `333 passed, 27 warnings`.
- `cd apps/web && npm run check` — PASS, `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` — PASS, `auth route checks passed`.
- `cd apps/web && npm run build` — PASS.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — PASS.
- `git diff --check` — PASS.

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the required/default posture.
- Controlled writes remain post-MVP/experimental and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- No write routes, write services, write enablement, import/export formats, banking integrations, account editing, delete flows, scheduled/recurring editing, or v0.2 controlled-write scope were changed.
- Money calculations were not changed; no float-based money logic was added.
- No frontend direct GnuCash file/database access was added.
- No browser storage for financial filters was added.
- No tag, GitHub release, package, or external release artifact was published.
- No GnuCash book, app DB, backup, `.env`, screenshot, private CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or real/private financial data was committed.
- Phase 104 does not claim production readiness, audited security, broad GnuCash compatibility, hosted SaaS readiness, family-wallet positioning, collaborative accounting, or personal-book dogfood success.

## GitHub / backlog note

- GitHub #11 was updated with non-sensitive Phase 104 evidence and left open.
- Remaining #11 scope includes transaction state/reconciled filters, saved presets, and broader notes/full-text semantics not implemented in this phase.
- GitHub #38 remains open/blocked until Val provides an explicit safe copied/disposable GnuCash SQL book path outside git and confirms it is not the live authoritative book.
- GitHub #22 remains open for future real GnuCash Desktop/generated version coverage.
- GitHub #39 remains closed; this phase found no CSV export regression.
- No new GitHub issue was created.

## Changed files

- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_gnucash_book.py`
- `apps/api/tests/test_transactions.py`
- `apps/api/tests/test_transaction_export.py`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-104.md`

## Risks / follow-up

- Split memo search is implemented as an in-memory service-layer scan over the read-only transaction objects, consistent with the current pre-alpha list/filter design; future large-book work may need indexing or query pushdown, but no production scalability claim is made.
- GitHub #11 remains open for broader read-only search/filter work; Phase 104 intentionally did not implement transaction state filters, saved presets, localStorage-backed filters, scheduled/recurring transaction parsing/editing, or broader notes/full-text semantics.
- Publication remains unauthorized; do not publish `v0.1.1-readonly` without separate explicit Val authorization.
- Personal copied-book dogfood remains blocked until Val provides a safe copied/disposable book path outside git.

## Next recommended phase

PM should select one narrow practical read-only backlog slice, preferably another GitHub #11 transaction search/filter improvement such as transaction state/reconciled filtering if it can be implemented safely through existing split metadata and synthetic tests. Do not publish a release, run personal-book dogfood, or expand write-mode scope without separate explicit authorization and safe inputs.

## Commit / push

- Implementation commit: `0daca5b` (`feat: search split memos in transactions`).
- Evidence commit: `28c2619` (`docs: record phase 104 commit evidence`).
- Push: PASS — pushed `main` to `origin/main` (`c300f44..28c2619`).
