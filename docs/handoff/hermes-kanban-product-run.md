# Hermes Kanban product-development run

Status: **PASS**

This document records the first production-development run on the dedicated Hermes Kanban board. It does not declare Hermes Kanban the only project workflow and does not replace `scripts/autonomy/supervisor.py`.

## Environment

- Run start: `2026-07-11T06:09:51Z`.
- Operational completion: `2026-07-11T10:17:59Z`, after final issue closure.
- Actual runtime: `14,888` seconds (`4h 8m 8s`).
- Hermes: `v0.18.2 (2026.7.7.2)`, upstream `4aa499ff`.
- Board: `gnucash-web-companion-product-dev`.
- Persistent store: `~/.hermes/kanban/boards/gnucash-web-companion-product-dev/kanban.db`.
- Baseline: `c345ce1521a19efab63b6a3a1347338889b8af1f`, clean and equal to `origin/main`.
- Tested final integration head before documentation: `56ec97156a4f9c79f289dba83251cae5c2cb5d58`.
- Final product/CI head: `e3d4aae3f40ea59d657c0300c8b1e31e45065a9f`.
- Dispatcher: gateway-embedded. No standalone Kanban daemon or repo-local supervisor run was started.

## Profiles

| Profile | Provider/model | Role |
|---|---|---|
| `pm-orchestrator` | `openai-codex / gpt-5.6-sol` | product state, issue acceptance, milestone selection |
| `backend-worker` | `openai-codex / gpt-5.5` | backend/API/domain/tests in worktrees |
| `frontend-worker` | `openai-codex / gpt-5.5` | SvelteKit/UI/browser tests in worktrees |
| `qa-integrator` | `openai-codex / gpt-5.5` | independent review and tested integration heads |

Models were configured at profile level because the installed `hermes kanban create` command has no per-task model flag.

## PM choice

PM reviewed the live #51 issue, README files, `PROJECT_STATUS.md`, current handoffs, routes, tests, open issues, and exact-head CI. It selected **Reports/analytics: read-only period reports explorer** as the next product milestone and opened [#52](https://github.com/valentusys/gnucash-web-companion/issues/52).

Reasons recorded by PM:

- the baseline product is read-only and should receive user-value work before more write-readiness shells;
- transaction history already had mature filtering, pagination, detail, and CSV parity;
- account browsing already had hierarchy-preserving search and account-detail transaction filtering;
- reports were limited to fixed current-month dashboard views;
- dashboard report failures could look like genuine empty activity;
- a bounded read-only reports explorer adds product value without expanding mutation, import, FX conversion, or release scope.

## #51 acceptance

- PM verdict on the baseline: **ACCEPT**.
- Independent QA baseline verdict: **REJECT for closure at that checkpoint**, not because of a product write-safety defect, but because the current worker could not reproduce the browser smoke on the host and CI did not run that browser gate.
- The run added the existing disposable browser rehearsal to CI and reproduced it locally.
- Both QA integration gates passed the normal preview-only and explicit synthetic/disposable test-mode browser coverage.
- The first integration CI run found a real CI-only dependency defect: the frontend job did not install `piecash`, which the disposable drill requires. Commit `e3d4aae` added the backend dependency setup without weakening the drill.
- Final PM/QA verdict: **ACCEPT**. Final CI with the browser gate passed and #51 was closed as completed.

Redacted evidence:

- checkpoint: <https://github.com/valentusys/gnucash-web-companion/issues/51#issuecomment-4943175533>;
- final acceptance: <https://github.com/valentusys/gnucash-web-companion/issues/51#issuecomment-4944834883>;
- closed issue: <https://github.com/valentusys/gnucash-web-companion/issues/51>.

## Task graph and results

The board recorded `11` created tasks, `10` completed tasks, `0` failed tasks, and one superseded archived task.

| Task | Result | Dependency role | Branch |
|---|---|---|---|
| `t_780313c4` PM product state/#51/milestone | done | root | `kanban-product/pm-state-and-milestone` |
| `t_2deb1074` independent QA #51 review | done | root | `kanban-product/qa-issue51-acceptance` |
| `t_cec897d9` #51 browser gate in CI | done | PM + QA | `kanban-product/issue51-browser-ci` |
| `t_01b5f369` reports API vertical slice | done after orchestrator review | PM + QA | `kanban-product/reports-api` |
| `t_4ac086ba` reports frontend base | done after orchestrator review | PM + QA | `kanban-product/reports-page` |
| `t_41a51663` reports API semantic hardening | done | backend base | `kanban-product/reports-api-hardening` |
| `t_5d2d5970` reports UX/i18n/mobile/browser hardening | done | frontend base | `kanban-product/reports-ux-hardening` |
| `t_cd4cdc70` first QA integration gate | done | all preceding review/coding tasks | `kanban-product/qa-integration` |
| `t_843883dc` dashboard honest report errors | done after orchestrator review | first QA gate | `kanban-product/dashboard-honest-report-errors` |
| `t_412efc17` final QA integration gate | done | first QA gate + dashboard continuation | `kanban-product/final-integration-v2` |
| `t_37029d3f` premature final-gate placeholder | archived, not counted as completed | incorrect dependency | `kanban-product/final-integration` |

Dependency summary:

```text
PM review ─┬─> CI browser gate ────────────────┐
QA review ─┘                                    │
PM + QA ────> backend base -> backend hardening ├─> QA gate 1
PM + QA ────> frontend base -> frontend hardening┘
QA gate 1 -> dashboard honest errors -> QA gate 2
```

The run did not stop after the first milestone integration gate. It continued with the PM-identified dashboard empty-versus-failure defect and a second QA gate.

## Worktrees

Hermes assigned one worktree and branch per task under ignored `.worktrees/<task-id>` paths. Coding workers did not edit `main`. After final CI, every task worktree was verified clean and removed; local audit branches and the durable board history remain.

The final main integration used only:

```bash
git merge --ff-only kanban-product/final-integration-v2
```

## Reclaim and retry events

No coding task required a content retry. One orchestrator dependency error created `t_37029d3f` without the intended dashboard parent and the dispatcher claimed it immediately.

- Run `11`, PID `1781483`, was manually reclaimed with `terminated=true`, `sigkill=false`.
- The gateway reclaimed/redispatched it before the archive command completed; run `12` was archived as superseded.
- The exact archived task process tree was terminated and no source commit was produced.
- Correct replacement task `t_412efc17` was created with both required parents and completed successfully.

Operational finding: when gateway dispatch is active, `reclaim` followed by `archive` is not atomic. A task can be reclaimed between the two commands. A safe operator sequence should pause dispatch or archive through one supported atomic operation if Hermes adds one.

## Product implementation

### Read-only period reports

- Added authenticated `GET /books/{book_id}/reports` with validated required date bounds.
- Added explicit typed period report and per-section status DTOs.
- Kept money as Decimal-derived strings; no currency conversion was added.
- Made genuine empty data distinct from partial section failures.
- Kept balance summary semantics as-of `date_to`; arbitrary-period income/expense/net totals come from period cashflow, not dashboard month fields.
- Added base-currency-only and unknown/mixed-currency limitations.
- Added `/reports` with URL-backed This month, Last month, Year to date, and custom ranges.
- Added exact `/transactions` drilldowns for period, month, and expense account.
- Added fixed redacted error states, empty states, navigation, active-route state, EN/RU release-critical copy, and 320px browser coverage.

### Honest dashboard report errors

- Dashboard summary, expenses, cashflow, and recent-transactions calls now expose per-section failure state.
- A failed section no longer renders as a genuine empty result.
- Unaffected sections remain visible.
- Error copy is fixed/redacted and does not expose backend details or private sentinels.
- Synthetic browser coverage asserts zero mutation-capable API/browser requests.

### CI

The frontend CI job now runs:

- type/static/auth/report/money guards;
- the build-backed #51 disposable browser rehearsal;
- reports browser coverage against the existing build output;
- dashboard browser coverage against the existing build output.

The first pushed CI run, `29148609359`, failed only in the frontend job because the newly enforced disposable drill could not import `piecash`. This was a genuine missing CI prerequisite rather than a product or safety failure. The frontend job now sets up Python 3.12 and installs the existing backend requirements before running the drill. The replacement run `29148850587` passed all jobs.

## Source and integration commits

Original worker/source commits included:

- `1b2c386` — add #51 disposable browser gate to CI;
- `39dd2b8` — read-only period reports API;
- `9d8e5b7` — reports API period semantics hardening;
- `7d6a850` — reports frontend base;
- `0bbe755` — reports UX/i18n/mobile/browser hardening;
- `95574a9` — honest dashboard section errors.

The final integration branch contains the reviewed equivalents:

- `c9362b8` — #51 disposable browser CI gate;
- `37e95d6` — reports API;
- `bc14d53` — backend semantic hardening;
- `ace3fce` — reports frontend;
- `bb75126` — frontend UX hardening;
- `288c245` — API/frontend contract alignment;
- `b6062b3` — honest dashboard section errors;
- `56ec971` — deterministic reports/dashboard CI gates.

Post-integration commits:

- `03e2d49` — product-run handoff and project status;
- `e3d4aae` — install backend dependencies for the browser drill in frontend CI.

Cherry-picks applied without Git conflicts. QA added narrow contract-alignment and CI integration commits after independent review.

## Verification before main merge

Final QA gate results:

- focused backend reports: `45 passed`;
- full backend: `1115 passed`, 62 existing warnings;
- frontend `npm run check`: 0 errors, 0 warnings;
- auth, transaction preview static, reports static, and money-string guards: passed;
- frontend production build: passed;
- reports browser: `api_report_requests=4`, forbidden API/browser mutations `0/0`;
- dashboard browser: `api_requests=13`, forbidden API/browser mutations `0/0`;
- transaction-entry preview browser and disposable alias: passed;
- public status, write defaults, markdown readability, tracked hygiene, and diff checks: passed;
- Docker Compose config: passed;
- tracked sensitive/artifact paths: 0;
- non-allowlisted added-line secret matches: 0.

The host `/tmp` quota was insufficient for repeated pytest/browser fixtures. Workers reran the same gates with short clean external temporary directories. Tests were not weakened and dependency/lock files were not changed merely to install worktree dependencies.

## Final main and CI verification

After the fast-forward merge, the orchestrator reran the required gates on `main`:

- full backend: `1115 passed`, 62 existing warnings;
- frontend check/build, auth, transaction preview, reports, money strings, reports browser, dashboard browser, transaction preview browser, and disposable browser alias: passed;
- public status, write defaults, markdown readability, tracked hygiene, diff, and Docker Compose checks: passed;
- first pushed CI: failure in the new browser gate because frontend CI lacked backend dependencies;
- corrected final CI: **success**, all four jobs green: <https://github.com/valentusys/gnucash-web-companion/actions/runs/29148850587>.

Final operational state after issue closure and cleanup:

- #51: closed as completed;
- #52: closed as completed;
- Kanban diagnostics: `[]`;
- board status: ten `done`, no ready/running/blocked tasks;
- active/orphan task or supervisor workers: none;
- `main == origin/main` at `e3d4aae3f40ea59d657c0300c8b1e31e45065a9f` before this documentation-only update;
- repository clean before this documentation-only update.

## Safety counters

Owner/private/original/working/Syncthing/only-copy books during this run:

| Operation | Count |
|---|---:|
| CREATE | 0 |
| PATCH | 0 |
| DELETE | 0 |
| batch | 0 |

Product reports/dashboard implementation paths:

| Operation | Count |
|---|---:|
| CREATE | 0 |
| PATCH | 0 |
| DELETE | 0 |
| batch | 0 |

Synthetic/disposable verification exercised the existing bounded CREATE/PATCH/DELETE drills repeatedly on fresh temporary targets. The harness does not emit a durable aggregate operation counter across repeated successful and quota-interrupted invocations, so this document does not invent an exact aggregate. Verified facts are: CREATE exercised, metadata-only PATCH exercised, app-owned DELETE exercised, batch 0, and forbidden mutation requests in reports/dashboard browser suites 0. `GNUCASH_WRITES_ENABLED=false` remained the default and enabled execution remained `APP_ENV=test` gated.

## Remaining product backlog

- Evaluate report performance and pagination/aggregation behavior on large synthetic books.
- Consider saved client-side URL presets only if they can remain URL/share based without auth state in browser storage.
- Add an ESLint configuration only if the project chooses to enforce the existing `npm run lint` script.
- Reconcile older issue/status drift such as completed disposable drill trackers separately; do not turn it into product busywork.
- Continue account/search, transaction-history, mobile/PWA, import/registration, and compatibility work through explicit product issues selected by PM value review.

## Operational comparison

Compared with the previous repo-local supervisor run:

- Kanban completed ten useful tasks plus one archived dependency correction in `4h 8m 8s`; the earlier supervisor run had higher raw task count, but its tasks were not equivalent in scope, so no like-for-like productivity claim is made.
- Kanban provided stronger task isolation, durable dependency state, explicit per-attempt history, profile routing, and independent QA worktrees.
- Recovery was more transparent, but the reclaim/archive redispatch race requires operator care.
- Integration overhead was higher because dependent cumulative branches needed explicit cherry-pick handoffs and two QA heads.
- Specialist context quality was good: PM found a real product priority, backend/frontend workers stayed in lane, and QA found both browser-CI and API/frontend semantic gaps.
- The repo-local supervisor still has stronger built-in long-run budget/minimum-task policy and remains the fallback.

Recommendation remains **hybrid**: continue Kanban for durable bounded product graphs and isolated integration; retain `scripts/autonomy/supervisor.py` for policy-driven long queues until a separate owner decision.
