# Hermes Kanban product-development run 3

Status: **FINAL CLOSEOUT COMPLETED; HISTORICAL PRE-CLOSEOUT NARRATIVE PRESERVED BELOW**

This handoff records the third product-development run on the dedicated Hermes Kanban board. It
covers the #53 acceptance correction, safe product-task wrapper, and [issue #54](https://github.com/valentusys/gnucash-web-companion/issues/54): an advanced read-only transaction explorer with bounded
filtering, pagination, and report drilldowns.

This file was originally part of the final docs/status integration commit. The closeout addendum below
records the later operator push, exact-head GitHub CI, issue #54 final comment, closure time, and run ID;
historical pre-closeout sections are preserved as author-time narrative rather than current status.

## Final closeout addendum

- Push/main closeout completed at accepted head `0d9381544118a64795827b24d787d1a8e7d998c0`.
- Exact-head GitHub Actions CI run
  [29197662815](https://github.com/valentusys/gnucash-web-companion/actions/runs/29197662815)
  completed success for Backend, Frontend, Docker Compose, and Foundation.
- Issue #54 is closed as completed at `2026-07-12T15:21:40Z`; final closeout comment:
  [#issuecomment-4951703096](https://github.com/valentusys/gnucash-web-companion/issues/54#issuecomment-4951703096).
- Main/origin exact-head state is clean at the accepted head; no #54 implementation follow-up remains in
  this run. Public status drift after this closeout is corrected by the run-4 factual closeout update.

## Environment and baseline

- Run-3 baseline: `2d6d7a4d3ade7bcf3aa0714a8ce5b0b2d3555254` (`origin/main` and `main` at QA start).
- Final QA task: `t_420c32ab`, branch `run/product/issue54-final-qa-20260712T142445Z-91a4b227`.
- Final QA source-inclusive head before docs: `cb545363c59abe6a158e5c39c39003363914c9d6`.
- Hermes: `v0.18.2 (2026.7.7.2)`, upstream `7b5ba205`, reported `Update available: 54 commits behind`.
- Board: `gnucash-web-companion-product-dev`.
- Board DB: `/home/val/.hermes/kanban/boards/gnucash-web-companion-product-dev/kanban.db`.
- Repo-local supervisor hash:
  `8d9e0aec155bbe6248b09512077b0b3197c4386d4c8c7a890dc3a56e6055e766`.
- Final QA used `/home/val/tmp/issue54-finalqa` for logs/benchmark artifacts after `/tmp` refused new
  writes with a quota error. No generated benchmark DB/JSON was committed.

## Profiles

| Profile | Provider/model | Run role |
|---|---|---|
| `pm-orchestrator` | `openai-codex / gpt-5.6-sol` | #53 acceptance, #54 scope/contract/design |
| `backend-worker` | `openai-codex / gpt-5.5` | wrapper, backend explorer, performance, CI/readability hardening |
| `frontend-worker` | `openai-codex / gpt-5.5` | README status, frontend explorer, no-date/reset hardening |
| `qa-integrator` | `openai-codex / gpt-5.5` | #53 recheck, QA gate 1, final QA gate 2 |

## #53 prerequisite closeout

Run 3 began only after issue #53 was independently rechecked on exact baseline
`2d6d7a4d3ade7bcf3aa0714a8ce5b0b2d3555254`:

- PM acceptance `t_6474aa27`: accepted keeping #53 closed and proposed #54.
- README status defect fix `t_71a5cd95`: source commit
  `a0181659c63f8260852e3e2dc8af9bee07e3dd4a`.
- QA recheck `t_3e14796f`: accepted README.md, README.ru.md, PROJECT_STATUS.md, live #53, and exact-head
  CI evidence as consistent. #54 was allowed to start.

## #54 user-visible functionality

The integrated #54 implementation adds a bounded, authenticated read-only transaction explorer:

- `GET /books/{book_id}/transactions/explorer` with required paired inclusive `date_from`/`date_to`;
- stable date/GUID keyset pagination with signed, filter-bound cursors and no exact total count;
- repeated `account_ids`, selected-account direction, income/expense type mode, exact Decimal-string
  min/max amount filtering, Unicode description/memo search, reconciliation state, and date asc/desc sort;
- no default-book explorer API alias and no write route; the existing legacy transaction list/export paths
  remain compatible;
- bounded scan metadata (`candidate_rows`, `split_rows`, `query_count`, `scan_limited`, `exhausted`) and
  redacted typed validation errors;
- URL-backed `/transactions` SSR filters, chips, reset, Previous/Next/Continue links, stale/invalid/empty/end/
  scan-limited states, safe detail `return_to`, EN/RU release-critical copy, and 320 px browser coverage;
- canonical first-page report/dashboard drilldowns to `/transactions?...` without cursors;
- honest CSV behavior: advanced explorer combinations that do not have legacy export parity are disabled.

Reporting remains base-currency-only and performs no FX conversion. GnuCash Desktop remains the authoritative
editor. `GNUCASH_WRITES_ENABLED=false` remains the default; write-alpha/writebeta code remains experimental,
post-MVP, test-gated, and not safe for real/private/original/only-copy books.

## Task graph and runtime notes

At documentation time, before final `kanban_complete`, the run-3 subset listed below had `12` tasks:
`11` done and `1` running final QA task. It had `22` task-run rows before final completion: `11`
completed outcomes, `8` blocked review-required outcomes, `2` timed-out iteration-budget outcomes, and
`1` running final QA outcome. No failed or crashed outcomes were recorded. All task `max_retries` values were
`2`.

| Task | Outcome / note | Branch |
|---|---|---|
| `t_6474aa27` | PM accepted #53 state and proposed #54 | `kanban-product-3/pm-accept-53` |
| `t_37213826` | wrapper source accepted after review-required handoff | `kanban-product-3/task-wrapper` |
| `t_71a5cd95` | #53 README status fix accepted after review-required handoff | `run/product/accept53-readme-status-20260712T104250Z-466c0ad8` |
| `t_3e14796f` | QA reaccepted #53 after README fix | `run/product/qa-reaccept53-20260712T104742Z-d9a85e0a` |
| `t_157028a3` | #54 PM design accepted bounded date/GUID keyset scan | `run/product/issue54-design-20260712T105725Z-c00f58b1` |
| `t_93cd2d8e` | backend source accepted after one iteration-budget timeout and review-required handoff | `run/product/issue54-backend-explorer-20260712T111115Z-5ff14cea` |
| `t_37561300` | frontend source accepted after one iteration-budget timeout and review-required handoff | `run/product/issue54-frontend-explorer-20260712T111116Z-2d61a40f` |
| `t_383fa451` | frontend no-date/reset hardening accepted | `run/product/issue54-frontend-reset-hardening-20260712T123748Z-80f1725c` |
| `t_d800e379` | performance source accepted after review-required handoff | `run/product/issue54-performance-budget-20260712T124940Z-af833adf` |
| `t_9f0f6730` | QA gate 1 rejected two bounded defects, then operator accepted routing to hardening | `run/product/issue54-qa-gate1-20260712T133733Z-d9650fdf` |
| `t_476ccb39` | QA1 hardening accepted after review-required handoff | `run/product/issue54-qa1-hardening-20260712T140328Z-96689551` |
| `t_420c32ab` | final QA exact-head integration and this docs/status handoff | `run/product/issue54-final-qa-20260712T142445Z-91a4b227` |

## Source commits, deduplication, and integration method

Final QA started from exact `2d6d7a4d3ade7bcf3aa0714a8ce5b0b2d3555254`, computed stable patch IDs,
and cherry-picked only the reviewed ordered set. Duplicate parents were intentionally not applied.

| Source commit | Local commit | Stable patch ID | Meaning |
|---|---|---|---|
| `a0181659c63f8260852e3e2dc8af9bee07e3dd4a` | `14dee51051069bc6609259177d4fee4c89b340aa` | `6ce95801c72ac9c38983925174b0bafcf474ce9a` | #53 README acceptance status fix |
| `1de8ef9af287bc27e50bab2b65c38f96a74e130a` | `b76b2568644814b2b46a7ea4b78e489293d9ee8f` | `4dbdaaa42455af61b35d59f873743fb20a90a61f` | safe Kanban product-task wrapper |
| `ef21701fb8a2efd995368cceaa574da3978837b7` | `03fb0c4371a88fde3d71808d3452cc5804cdcc59` | `9a75ac114a8df855ba7a9864ad15e725c955da6e` | backend bounded explorer |
| `c8fa740e8b80bb7aa8588b2fe341e07de7d6d539` | `050ac353e0617c2ae731ad35fa9b9b481e64ca5e` | `1becaa5ed85d6c784404fed5fbaadeb57e7d3bbf` | performance-only explorer/read-budget coverage |
| `83291d86bb4535506ad71051b466a6a3aa33bbd2` | `ec2419f5b8305b723a54c48e6ffb6c784e642b82` | `579bb9153d4ac1ac5172fa0eee78ec401fb0ca42` | frontend explorer and drilldowns |
| `eb7085cf265a727f7bf546d450fa509631a5142b` | `5ba676cda6afd09a6afb6232d8950dee34dc9563` | `7954224fe1ea5cb5d1efb1a14f754cc5bfbc0be4` | frontend no-date/reset hardening |
| `49bd50847a2ae451679301bbc44ba3b815f824cf` | `cb545363c59abe6a158e5c39c39003363914c9d6` | `7a8fd63c416487a20e3bc6e2c1c8d637cca2c633` | QA1 CI/readability hardening |

Rejected duplicate source parents:

- `c8537858206ebf0519d1efb2cb701a76203c157a`, patch ID
  `9a75ac114a8df855ba7a9864ad15e725c955da6e`, duplicate of backend `ef21701`.
- `3ac6218dc995981696d7ffced3d83dcf2f43b84e`, patch ID
  `579bb9153d4ac1ac5172fa0eee78ec401fb0ca42`, duplicate of frontend `83291d8`.

The integrated source changed 33 tracked paths before this docs/status commit: CI workflow, README status,
backend explorer/router/service/schema/tests/benchmark, frontend explorer SSR/components/scripts/i18n/types,
report/dashboard drilldown builders, and the repo-local Kanban wrapper/docs/tests.

## QA1 reject and hardening

QA gate 1 (`t_9f0f6730`) rejected the first integration head for two exact defects only:

1. The new release-critical transaction explorer static/browser gates existed in `apps/web/package.json` but
   were not wired into `.github/workflows/ci.yml`.
2. Full backend pytest failed two stale README heading assertions after the #53 README status fix renamed the
   EN/RU status-map headings.

Hardening commit `49bd50847a2ae451679301bbc44ba3b815f824cf` fixed only those defects: it added
`npm run test:transactions-explorer` and `npm run test:transactions-explorer-browser` to the frontend CI job
without removing existing gates, and updated the stale EN/RU heading expectations in
`apps/api/tests/test_markdown_readability_docs.py`. Source+hardening validation reported full API
`1182 passed` and explorer browser mutation counters `0`.

## Verification on the source-inclusive head

Final QA ran the required matrix on source-inclusive head `cb545363c59abe6a158e5c39c39003363914c9d6`
before authoring this docs/status commit.

Root and Docker:

- `python3 scripts/check_public_status.py`: `public-status-guard: ok`.
- `python3 scripts/check_markdown_readability.py README.md README.ru.md PROJECT_STATUS.md docs/handoff/hermes-kanban-product-run-2.md`:
  `markdown-readability-guard: ok (27 docs checked)`.
- `python3 scripts/check_write_safety_defaults.py`: write-safety defaults ok, including
  `GNUCASH_WRITES_ENABLED=false`.
- `python3 scripts/check_tracked_hygiene.py`: `1986` tracked paths inspected.
- `git diff --check`: passed.
- Corrected tracked private-artifact scan: `1986` tracked paths inspected; no committed raw/private runtime
  artifacts. An earlier over-broad scan falsely matched an existing Markdown filename containing the word
  `screenshots`, then was corrected to artifact paths/extensions.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`: passed.
- `sha256sum scripts/autonomy/supervisor.py`:
  `8d9e0aec155bbe6248b09512077b0b3197c4386d4c8c7a890dc3a56e6055e766`.

Backend:

- `cd apps/api && python -m pytest -q tests/test_kanban_create_product_task.py`: `10 passed in 0.05s`.
- Focused explorer/access/reports/benchmark/wrapper/markdown matrix:
  `240 passed, 26 warnings in 196.87s`.
- Full API: `1182 passed, 64 warnings in 412.40s`.

Frontend:

- `cd apps/web && npm install --package-lock=false`: up to date; npm audit reported 3 existing low severity
  vulnerabilities.
- `npm run check`: `svelte-check found 0 errors and 0 warnings`.
- `npm run build`: passed.
- `npm run test:auth-routes`: passed.
- `npm run test:transaction-entry-preview`: `transaction-entry-preview-static: ok`.
- `npm run test:reports`: `reports static checks passed`.
- `npm run test:money-strings`: `money string checks passed`.
- `npm run test:transactions-explorer`: `transactions explorer static checks passed`.
- `npm run test:transactions-explorer-browser`: passed with
  `explorer_requests=5`, `no_date_explorer_requests=0`, `api_forbidden=0`, `browser_forbidden=0`,
  `mobile_width=320/320`, `scroll_width=320/320`.
- `node scripts/test-reports-browser.mjs`: passed with `api_report_requests=7`, `api_forbidden=0`,
  `browser_forbidden=0`.
- `node scripts/test-dashboard-browser.mjs`: passed with `api_requests=13`, `api_forbidden=0`,
  `browser_forbidden=0`.
- `npm run test:transaction-entry-preview-browser`: passed.
- `npm run test:transaction-entry-create-disposable-browser`: passed.

Performance-focused tests and local synthetic benchmarks:

- `cd apps/api && python -m pytest -q tests/test_large_book_benchmark.py -k "explorer or comparison_benchmark_summary or benchmark_plan"`:
  `6 passed, 11 deselected, 23 warnings in 11.29s`.
- Method: local generated synthetic SQLite fixtures, FastAPI `TestClient`, one warm-up plus three measured
  samples per case, selected comparison/explorer GET cases only, no private book data, no writes executed, and
  no production performance claim.

| Dataset | Case | Min / median / max | Bytes | Items | Guard counters |
|---:|---|---:|---:|---:|---|
| 1k | `transaction_explorer_first_page` | `48.08 / 49.40 / 50.77 ms` | 13,134 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget pass |
| 1k | `transaction_explorer_sparse_scan_limited` | `152.18 / 155.58 / 213.35 ms` | 1,418 | 1 | opens `1-1`, count calls `0`, materializations `0`, scan `998/2054/5`, budget pass |
| 1k | `transaction_explorer_later_forward_page` | `46.04 / 47.33 / 49.62 ms` | 13,420 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget pass |
| 1k | `transaction_explorer_previous_page` | `49.09 / 49.19 / 50.07 ms` | 13,414 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget pass |
| 1k | `period_comparison_previous_equivalent` | `655.54 / 693.46 / 717.43 ms` | 11,744 | 12 | opens `1-1`, count calls `0`, materializations `1`, budget pass |
| 10k | `transaction_explorer_first_page` | `46.48 / 50.07 / 99.53 ms` | 13,172 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget pass |
| 10k | `transaction_explorer_sparse_scan_limited` | `295.89 / 336.43 / 343.01 ms` | 2,337 | 2 | opens `1-1`, count calls `0`, materializations `0`, scan-limited `2000/4000/10`, budget pass |
| 10k | `transaction_explorer_later_forward_page` | `45.37 / 47.49 / 110.42 ms` | 13,419 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget and relative pass |
| 10k | `transaction_explorer_previous_page` | `48.01 / 48.24 / 49.79 ms` | 13,435 | 25 | opens `1-1`, count calls `0`, materializations `0`, scan `26/52/1`, budget and relative pass |
| 10k | `period_comparison_previous_equivalent` | `6189.58 / 6233.92 / 7483.85 ms` | 11,866 | 12 | opens `1-1`, count calls `0`, materializations `1`, budget pass |

## Safety counters

- GitHub push/main mutation/issue comment/issue close/release/tag/package/container actions: `0`.
- Owner/private/original/working/Syncthing/only-copy GnuCash books opened, copied, or mutated: `0`.
- Product dogfood/private target probes: `0`.
- Committed raw books/backups/exports/screenshots/app DBs/secrets/benchmark DBs/benchmark JSON: `0`.
- Explorer/report/dashboard browser mutation-forbidden counters: `0` API and `0` browser in the final browser
  evidence listed above.
- Write posture flips: `0`; `GNUCASH_WRITES_ENABLED=false` remains default.
- FX conversion: `0`; reporting/explorer copy remains base-currency-only/no-FX.

## Historical pre-closeout backlog and operator closeout

This section preserves the author-time operator-pending state before the final closeout addendum above.

- Operator-only pending after the original run-3 docs commit: fast-forward or merge the QA-tested branch,
  push, watch exact-head GitHub CI, comment on issue #54 with exact evidence, and close #54 only after CI
  succeeds. This is historical and was completed by the final closeout addendum above.
- Explicit operator merge instruction for this branch:
  `git merge --ff-only run/product/issue54-final-qa-20260712T142445Z-91a4b227`.
- Public read-only beta remains `v0.5.0-public-readonly-beta`; `v0.5.1-public-readonly-beta` is not published,
  `v0.4.0-owner-writebeta` is not published, and no stable/production/security-audited claim is made.
- Controlled-write trackers #45-#50 remain historical/experimental post-MVP boundaries and do not authorize
  owner/private DELETE, batch, release publication, or public write beta.

## Reusable operator command template

Use the repo-local wrapper for future product-run cards instead of a raw malformed `hermes kanban create`
or free-form ChatGPT prompt. Example:

```bash
cat > /home/val/tmp/gnucash-product-task-body.md <<'TASK'
Write the exact task body here. Include baseline, allowed file scope, safety boundaries,
required checks, source-commit handoff rules, and explicit non-goals.
TASK

python3 scripts/kanban/create_product_task.py \
  --board gnucash-web-companion-product-dev \
  --title "Issue NN: bounded implementation/review task" \
  --assignee backend-worker \
  --branch-suffix issueNN-bounded-task \
  --body-file /home/val/tmp/gnucash-product-task-body.md \
  --max-runtime 2h \
  --max-retries 2 \
  --parent t_parentid \
  --priority 140 \
  --dry-run
```

Review the redacted dry-run output first. Remove `--dry-run` only after confirming the board, branch suffix,
assignee, parents, max runtime, retries, and body file are correct.
