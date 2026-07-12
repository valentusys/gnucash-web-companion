# Hermes Kanban product-development run 2

Status: **PRODUCT ACCEPTED; FINAL RUN 2 CLOSEOUT RECORDED; ISSUE #53 CLOSED**

This handoff records the second product-development run on the dedicated Hermes Kanban board.
It covers product head `3b094cdb318c017b9a607abe87f98326e8a6ab2b`, parent docs commit
`39a87c011f278a732b2298b2031648f5b31db99e`, corrective final documentation QA task
`t_4e627530`, and final factual addendum task `t_f5f49eef`. The corrective local docs-QA
verdict is **ACCEPT**. After that task, main/origin were fast-forwarded to
`3eeaf5f0bf0f90cffaaa8505e26788bfcc01ebb9`; operational closeout CI
`29180390237` succeeded; issue #53 received the final acceptance comment and was closed as
completed. This docs-only final addendum records those facts. The addendum commit itself is subject
to the same exact-head CI gate after integration; no future CI run ID or head is invented here.

## Environment and baseline

- Run start: `2026-07-11T23:57:24+00:00`.
- Baseline: `d90f97002ade281364627a4214a7fef33e62e9d4`.
- Final accepted product head before docs: `3b094cdb318c017b9a607abe87f98326e8a6ab2b`.
- Operational closeout docs head before this final addendum:
  `3eeaf5f0bf0f90cffaaa8505e26788bfcc01ebb9`.
- Hermes: `v0.18.2 (2026.7.7.2)`, upstream `4281151a`, reported `Up to date`.
- Board: `gnucash-web-companion-product-dev`.
- Board DB: `/home/val/.hermes/kanban/boards/gnucash-web-companion-product-dev/kanban.db`.
- Dispatcher: gateway-embedded; no repo-local supervisor run was started.
- Repo-local supervisor hash remained
  `8d9e0aec155bbe6248b09512077b0b3197c4386d4c8c7a890dc3a56e6055e766`.

## Profiles

| Profile | Provider/model | Run role |
|---|---|---|
| `pm-orchestrator` | `openai-codex / gpt-5.6-sol` | acceptance, product choice, contract, orchestration, docs |
| `backend-worker` | `openai-codex / gpt-5.5` | comparison API, tests, benchmark, performance follow-up |
| `frontend-worker` | `openai-codex / gpt-5.5` | SSR/UI, browser coverage, contract hardening |
| `qa-integrator` | `openai-codex / gpt-5.5` | independent acceptance and two integration gates |

## Starting acceptance: issue #52

Two independent tasks reviewed the exact baseline rather than trusting the previous handoff:

- PM `t_ff454b21`: **ACCEPT**;
- QA `t_2744b8da`: **ACCEPT**;
- action: keep [issue #52](https://github.com/valentusys/gnucash-web-companion/issues/52)
  closed as completed;
- final acceptance comment:
  <https://github.com/valentusys/gnucash-web-companion/issues/52#issuecomment-4949368836>.

## Selected milestone

PM selected [issue #53](https://github.com/valentusys/gnucash-web-companion/issues/53),
**Read-only period comparison with spending-change breakdowns and exact transaction drilldowns**.
The rationale was user value: answer “what changed?” from the already accepted read-only reports
workflow. It was not selected as write readiness and did not expand mutation or release scope.

### User-visible functionality

The accepted `/reports` workflow now:

- compares a primary period with the immediately previous equivalent period, the same period last
  year, or an explicit custom period;
- keeps all selected dates and comparison mode in the URL and loads through authenticated SSR;
- shows primary/comparison totals, signed Decimal-string changes, and deterministic spending changes
  by account;
- distinguishes zero, unchanged, one-sided, empty, partial-error, whole-request-error, and
  not-comparable states;
- preserves base-currency-only reporting and performs no FX conversion;
- provides exact paired `/transactions` drilldowns with `limit=50`, `offset=0`, side-specific dates,
  and account IDs where applicable;
- includes release-critical EN/RU copy, keyboard/fieldset labels, and tested 320 px behavior;
- keeps the existing one-period reports endpoint and behavior compatible.

The backend exposes only authenticated, book-aware
`GET /books/{book_id}/reports/comparison` for the new aggregate. No default-book alias or write route
was added.

## Task graph

```text
PM #52 acceptance t_ff454b21 ─┐
                              ├─> design t_5958d2d3
QA #52 acceptance t_2744b8da ─┘

                         ┌─> backend t_c7cc5a4d ───────────────┐
design t_5958d2d3 ──────┤                                      ├─> QA1 t_8398da6f
                         └─> frontend t_549ef9f1 ─┐             │
                                                  └─> hardening t_4e61c87d ┘

QA1 t_8398da6f ──> performance t_614060f6 ──┐
QA1 t_8398da6f ──────────────────────────────┴─> QA2 t_a23ddfba
QA2 t_a23ddfba ──> docs t_e285b665 ──> corrective final docs QA t_4e627530
                                             └─> final factual addendum t_f5f49eef
```

| Task | Outcome / closeout state | Branch |
|---|---|---|
| `t_ff454b21` PM #52 acceptance | done, ACCEPT | `kanban-product-2/pm-accept-52` |
| `t_2744b8da` QA #52 acceptance | done, ACCEPT | `kanban-product-2/qa-accept-52` |
| `t_5958d2d3` #53 contract/design | done | `kanban-product-2/issue53-design` |
| `t_c7cc5a4d` backend v2 | done after review-required handoff | `kanban-product-2/issue53-backend` |
| `t_549ef9f1` frontend v2 | done after review-required handoff | `kanban-product-2/issue53-frontend` |
| `t_4e61c87d` frontend contract hardening | done after review-required handoff | `kanban-product-2/issue53-frontend-hardening` |
| `t_8398da6f` QA gate 1 | done, ACCEPT | `kanban-product-2/issue53-qa-gate1` |
| `t_614060f6` performance follow-up | done after review-required handoff | `kanban-product-2/issue53-comparison-performance` |
| `t_a23ddfba` QA gate 2 | done, ACCEPT | `kanban-product-2/issue53-qa-gate2` |
| `t_e285b665` documentation closeout | done; source commit `39a87c0` | `kanban-product-2/run2-docs` |
| `t_8d77ebb9` superseded final docs QA | archived; rejected operational correction | `wt/t_8d77ebb9` |
| `t_4e627530` corrective final docs QA | done, ACCEPT; operator closeout completed after task | `kanban-product-2/run2-docs-qa-corrective` |
| `t_f5f49eef` final factual addendum | docs-only addendum recording exact CI, issue closure, and runtime evidence | `kanban-product-2/run2-final-addendum` |

Before the completion of final addendum task `t_f5f49eef`, the live run-2 board subset showed `16`
task rows: `11` done, `1` running for this addendum, and `4` archived. The final run-2 count after
this addendum completes is `16` task rows: `12` useful done including `t_e285b665`, `t_4e627530`,
and `t_f5f49eef`, plus `4` archived cards (`t_9229b35a`, `t_041eca69`, `t_4a5c208e`, and
`t_8d77ebb9`).

The live run-2 board subset showed `17` task-run rows before this addendum completed: `11` completed
outcomes, `5` blocked outcomes, and `1` running outcome for `t_f5f49eef`. The final run count after
this addendum completes is `17`: `12` completed outcomes plus `5` blocked handoff outcomes. The five
blocked outcomes are the accepted review-required source handoffs for `t_c7cc5a4d`, `t_549ef9f1`,
`t_4e61c87d`, and `t_614060f6`, plus the rejected `t_8d77ebb9` run. There were no failed, crashed,
timed-out, or content-retry runs in the run-2 subset.

## Corrected malformed cards

The design task initially created `t_9229b35a`, `t_041eca69`, and `t_4a5c208e` without the required
project/worktree linkage. They were archived before any worker run:

- no worker started;
- no PID or reclaim race occurred;
- no source or workspace artifact was produced;
- corrected v2 cards used the project-linked deterministic worktrees and branches listed above.

Operational finding: every project coding/QA card must set both project linkage and worktree scope.
Dependency correctness alone is insufficient if the dispatcher cannot build the intended isolated
branch workspace.

## Corrected final docs QA card

The original final docs QA card `t_8d77ebb9` is archived and rejected for final-record purposes. Its
instructions were over-broad because they assigned push/main integration, exact-head CI watching, and
issue #53 comment/closure to a worker; those actions were operator-only and were later completed
outside that rejected worker. Its
GitHub check also omitted the operator `gh` setup (`/home/val/.local/bin/gh` with `HOME=/home/val`),
which produced a false auth-blocker conclusion. The process had ended before archive, no active PID
remained, and no push, main update, issue comment, issue closure, release, tag, package, or container
mutation occurred. Its local commits `de44e89954f2c2c8296a5da004258fda4e761b0d` and
`a1b557107219a65fe60954cdf8be6ae9ba5d4d8b` are rejected and are not reused by this corrective
branch.

## Worktrees, source scope, and integration

Each corrected card used its isolated project worktree under `.worktrees/<task-id>`. Coding workers
did not edit the product branch directly. The accepted product changed only these 14 paths:

Backend/API/test scope:

- `apps/api/app/performance/large_book_benchmark.py`
- `apps/api/app/routers/reports.py`
- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_large_book_benchmark.py`
- `apps/api/tests/test_multi_book_access.py`
- `apps/api/tests/test_multibook_readonly_access.py`
- `apps/api/tests/test_reports.py`

Frontend/UI/test scope:

- `apps/web/scripts/test-reports-browser.mjs`
- `apps/web/scripts/test-reports-static.mjs`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/reports/+page.server.ts`
- `apps/web/src/routes/reports/+page.svelte`

### Commit ancestry and deduplication

Original source commits were:

- backend: `f9a6395c5d12ce0bf27cafb105647c5e9ad331eb`;
- frontend: `4afaca9953c5dbdce24746c6d939570e2eb9eba6`;
- frontend hardening: `3a47e17203928529c177923da03ad62f02cd97e4`, on the cumulative rewritten
  frontend source;
- performance: `4b649fd9f1dab0c3de02cf2bf92f4bf8000e2fed`.

QA gate 1 integrated reviewed equivalents and ended at
`d89d668429534eabbfcdd74ab4f87125995b842f`. QA gate 2 rebuilt from the exact baseline with the
original QA1-tested patches plus only the performance delta, producing:

| Accepted product commit | Meaning |
|---|---|
| `64580e0` | comparison API and backend tests |
| `efe3e7a` | comparison frontend |
| `7ceaebc` | frontend contract/browser hardening |
| `3b094cd` | request-local read-only comparison performance optimization |

The source hashes are not ancestors of the final product head because QA used cherry-pick-based
integration. QA gate 2 compared patch IDs and skipped rewritten duplicates `59f0778`, `c794e5c`, and
`f8ac46f`. There were no Git conflicts and no QA fix commit.

## Contract hardening finding

Independent frontend/backend alignment found a real mismatch before integration: backend expense
rows can be `not_comparable` with nullable delta fields and safe detail, while the first frontend
source required strings and omitted the row status. `t_4e61c87d` fixed the types, mapper, rendering,
redaction, and browser assertions. Non-comparable values no longer reach Decimal/BigInt/bar helpers
and raw backend detail is not rendered.

## Performance follow-up

QA gate 1 exposed severe local synthetic comparison latency. The bounded follow-up changed only the
comparison service and focused tests:

- previous behavior opened/scanned the same book independently for report sections on both periods;
- accepted behavior uses one request-local read-only open and bounded cached account/transaction
  iterables;
- context is restored in `finally` and does not persist across requests;
- the existing one-period report keeps its prior behavior;
- shared-open failure falls back to historical section-isolated behavior.

### Final generated benchmark

Method: local generated synthetic SQLite fixtures, FastAPI `TestClient`, comparison GET only, one
warm-up plus three measured requests, no mutation-adjacent cases, and no production performance
claim.

| Transactions | Min / median / max | Bytes | Rows | Status | Change vs QA1 median |
|---:|---:|---:|---:|---:|---:|
| 1,000 | `605.95 / 608.78 / 667.01 ms` | 11,744 | 12 | 200 | `77.51%`, `4.45x` |
| 10,000 | `5876.47 / 5948.77 / 6048.30 ms` | 11,866 | 12 | 200 | `77.12%`, `4.37x` |

QA gate 1's 10,000-transaction median was `26003.68 ms`. These figures are reproducible local
synthetic evidence, not production capacity, hosted-service, or broad GnuCash scalability evidence.

## Verification

Final product QA gate 2 reported:

- focused backend matrix: `270 passed`, 24 warnings;
- full backend: `1134 passed`, 62 warnings;
- frontend `npm run check`: 0 errors and 0 warnings;
- auth, reports, money-string, transaction preview, production build, reports browser, dashboard
  browser, preview browser, and disposable browser alias: passed;
- public status, write-safety defaults, Markdown readability, tracked hygiene, Docker Compose,
  sensitive-diff scan, and `git diff --check`: passed;
- reports browser: `api_report_requests=7`, `api_forbidden=0`, `browser_forbidden=0`;
- dashboard browser: `api_requests=13`, `api_forbidden=0`, `browser_forbidden=0`.

Exact accepted-product GitHub CI succeeded at
`3b094cdb318c017b9a607abe87f98326e8a6ab2b`:
<https://github.com/valentusys/gnucash-web-companion/actions/runs/29179124360>.

Operational closeout after corrective docs QA is now recorded:

- main/origin were fast-forwarded to exact head
  `3eeaf5f0bf0f90cffaaa8505e26788bfcc01ebb9`;
- exact-head operational closeout CI `29180390237` completed with conclusion `success` at
  `2026-07-12T05:00:18Z`:
  <https://github.com/valentusys/gnucash-web-companion/actions/runs/29180390237>;
- issue #53 received final acceptance comment
  <https://github.com/valentusys/gnucash-web-companion/issues/53#issuecomment-4950026271> at
  `2026-07-12T05:01:25Z` and was closed as completed at `2026-07-12T05:01:29Z`;
- issue #52 remains closed as completed, with independent run-2 acceptance comment
  <https://github.com/valentusys/gnucash-web-companion/issues/52#issuecomment-4949368836>;
- local final-main backend `pytest -q`: `1134 passed`, 63 warnings in `375.49s`;
- final-main root guards passed: public status, write-safety defaults, Markdown readability, tracked
  hygiene, `git diff --check`, Docker Compose config, and supervisor hash
  `8d9e0aec155bbe6248b09512077b0b3197c4386d4c8c7a890dc3a56e6055e766` unchanged;
- frontend `npm run check`, production build, auth routes, preview, reports, money-string,
  reports-browser, and dashboard-browser checks passed;
- the first local transaction-entry preview-browser attempt used system `python3` and failed only
  because `piecash` was not visible; rerunning with
  `PATH=/home/val/projects/gnucash-web-companion/apps/api/.venv/bin:$PATH` passed both
  transaction-entry-preview-browser and transaction-entry-create-disposable-browser. This is recorded
  as an environment prerequisite/retry, not a product defect or weakened test;
- final browser counters stayed non-mutating: reports browser `api_report_requests=7`,
  `api_forbidden=0`, `browser_forbidden=0`; dashboard browser `api_requests=13`, `api_forbidden=0`,
  `browser_forbidden=0`.

Runtime checkpoints from run start `2026-07-11T23:57:24Z`:

| Checkpoint | Timestamp | Elapsed |
|---|---:|---:|
| Useful product through product CI `29179124360` | `2026-07-12T04:07:53Z` | `4:10:29` |
| Through operational closeout CI `29180390237` | `2026-07-12T05:00:18Z` | `5:02:54` |
| Through issue #53 close | `2026-07-12T05:01:29Z` | `5:04:05` |

Final addendum live checks observed that only the main worktree and this final addendum worktree were
registered. Previous clean run-2 worktrees were removed; audit branches were retained for provenance.
Before this addendum completed, the only running run-2 card was `t_f5f49eef`. User `hermes serve` PID
`1641127`, the gateway, and the current orchestrator were intentionally left alone.

Final addendum GitHub verification used read-only commands. `/home/val/.local/bin/gh` was invoked only
with read operations; the configured token was invalid and a no-auth public `gh` attempt required
login, so public GitHub API `GET` requests were used as the read-only fallback to confirm the issue
and CI facts above. This addendum does not push, comment, close, tag, release, publish, or mutate
GitHub state.

## Safety and publication counters

Protected owner/private/original/working/Syncthing books:

| Observation | Count |
|---|---:|
| Books accessed | 0 |
| CREATE | 0 |
| PATCH | 0 |
| DELETE | 0 |
| batch | 0 |

Reports/dashboard product paths:

| Operation | Count |
|---|---:|
| CREATE | 0 |
| PATCH | 0 |
| DELETE | 0 |
| batch | 0 |

The existing synthetic disposable transaction browser drill exercised test-mode operations. It did
not emit aggregate CREATE/PATCH/DELETE counts, so aggregate counts are **unavailable** and are not
invented here.

Publication actions in run 2 through issue #53 closeout and this final addendum:

- release: 0;
- tag: 0;
- package publication: 0;
- container publication: 0;
- default write-posture changes: 0.

GitHub mutations by this final addendum task:

- pushes: 0;
- issue comments: 0;
- issue closures: 0;
- releases/tags/packages/containers: 0.

The #53 comment and closure recorded above were operator closeout actions before this addendum card.

`GNUCASH_WRITES_ENABLED=false` remains the default. No FX conversion, public write beta, stable,
production-ready, or security-audited claim was added.

## Comparison with product run 1

Run 1 recorded `10` useful done tasks and `1` archived task. Run 2 had `9` useful done tasks and
`3` malformed archived cards before docs; after docs, corrective docs QA, and this final factual
addendum, its final board count is `12` useful done tasks and `4` archived cards. Raw task counts are
not comparable productivity metrics.

Run 2 added:

- dynamic independent acceptance before choosing work;
- an implementation-ready contract before parallel backend/frontend work;
- explicit contract/browser hardening after source review;
- two independent QA integration gates;
- a measured performance follow-up triggered by QA1 evidence;
- patch-ID deduplication when rebuilding the final integration head;
- no reclaim/PID race, unlike the first run's non-atomic reclaim/archive incident.

The negative operational result was the PM-created child-card omission: three cards lacked project
and worktree linkage and had to be archived before dispatch.

## Remaining backlog

Run-2 closeout:

- issue #53 is closed as completed;
- operational closeout CI `29180390237` is green on exact head
  `3eeaf5f0bf0f90cffaaa8505e26788bfcc01ebb9`;
- this docs-only final factual addendum is subject to the same exact-head CI gate after integration,
  and this file intentionally records no future run ID or future head.

Product limitations/backlog:

- no FX conversion; unknown or mismatched currencies remain explicitly not comparable;
- no saved server-side comparisons, export, chart library, forecasting, or budget feature in #53;
- synthetic `TestClient` timing does not establish production or real-book scalability;
- future read-only work should be selected by PM value review across account/transaction discovery,
  onboarding/book management, mobile/PWA, compatibility, and scheduled/budget visibility;
- controlled-write trackers remain a separate experimental post-MVP boundary and are not implied by
  #53 acceptance.

## Recommendation

Continue the **hybrid** operating model:

- use Hermes Kanban for bounded product graphs, specialist worktrees, review-required coding
  handoffs, and independent QA integration;
- retain `scripts/autonomy/supervisor.py` unchanged for policy-driven long queues;
- require `project` plus `workspace_kind=worktree` on every project coding/QA card;
- create dependent cards only when parent IDs and workspace metadata are final;
- let measurable QA findings create bounded follow-ups before final acceptance.

## Reusable Hermes launch without ChatGPT

Run from the repository root with the gateway already hosting the embedded dispatcher. Keep the owner
brief outside the repository at this reusable template path:

```text
$HOME/tmp/kanban-product-run-N/owner-brief.md
```

Exact Hermes command:

```bash
hermes --profile pm-orchestrator chat \
  --source kanban-product-run \
  --max-turns 160 \
  -q "$(cat "$HOME/tmp/kanban-product-run-N/owner-brief.md")"
```

The external owner brief should contain these sections:

1. repository/project and dedicated board slug;
2. exact clean baseline and required current-state/GitHub checks;
3. profile roster and role boundaries;
4. PM acceptance and milestone-selection criteria;
5. safety, privacy, publication, and mutation prohibitions;
6. card requirements: `project`, `workspace_kind=worktree`, explicit parents, bounded file scope,
   verification commands, and review-required coding handoffs;
7. independent QA1 and QA2 gates with exact-head CI requirements;
8. benchmark method and “no production claim” wording when performance is in scope;
9. docs/status/README closeout plus issue update/closure rules;
10. final report fields: task/run outcomes, branches, commits/dedup, checks, counters, artifacts,
    remaining backlog, and recommendation.

The command starts Hermes directly with the `pm-orchestrator` profile; the orchestrator then uses
Kanban tools and the gateway dispatcher to create and route durable cards. No ChatGPT session is
required.
