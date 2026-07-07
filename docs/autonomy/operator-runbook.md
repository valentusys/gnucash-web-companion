# Autonomous supervisor operator runbook

The repo-local supervisor in `scripts/autonomy/supervisor.py` owns the
wall-clock budget for a local autonomous run. It launches one bounded worker
prompt per queue task, verifies that the repository is clean before/after each
worker, retries common transient failures conservatively, and checkpoints rather
than fabricating success.

Default posture: dry-run/no-agent. Live execution is fail-closed unless
`AUTONOMY_AGENT_COMMAND` is explicitly configured.

## One-command dry-run

From the repository root:

```bash
python3 scripts/autonomy/supervisor.py \
  --budget-hours 5 \
  --queue docs/autonomy/queues/daytime-write-mode.md \
  --mode dry-run
```

Dry-run behavior:

- parses the queue;
- renders worker prompts under `.hermes/autonomy/runs/<timestamp>/prompts/`;
- does not invoke Hermes, Codex, or any other agent;
- writes an ignored local final report under the run directory;
- continues to later queue tasks when an earlier task is simulated as complete.

## Sustained v2 runs

By default the supervisor remains a finite queue runner: when the queue is exhausted it exits with `COMPLETED_NO_SAFE_TASKS`. To request a sustained run, add explicit minimums and an empty-queue strategy:

```bash
python3 scripts/autonomy/supervisor.py \
  --budget-hours 5 \
  --min-runtime-hours 4.75 \
  --min-tasks 8 \
  --queue docs/autonomy/queues/issue36-long-run.md \
  --on-empty generate-from-policy \
  --backlog-policy docs/autonomy/backlog-policies/issue36-owner-writebeta.md \
  --mode dry-run
```

New v2 controls:

- `--min-runtime-hours FLOAT`: keep going until this runtime is reached when safe tasks remain. `--budget-hours` is still the hard upper bound.
- `--min-tasks INT`: keep going until this many tasks have run when safe tasks remain.
- `--on-empty stop`: backward-compatible default; stop when the finite queue is exhausted.
- `--on-empty repeat-safe-final`: repeat the final queue task only if it is marked with safe privacy/release flags.
- `--on-empty generate-from-policy`: load a Markdown backlog policy and generate additional safe worker prompts.
- `--backlog-policy PATH`: required for `generate-from-policy`.

`generate-from-policy` is fail-closed. It only uses policy tasks marked `generated-safe`, `no-private-data`, and `no-release`, and rejects tasks with unsafe flags such as `release`, `touches-private-data`, `dogfood`, or `gnucash-mutation`. If no safe policy task exists before the configured minimums are met, the supervisor stops with `HARD_NO_SAFE_TASKS` and records the reason.

The generated-safe filter is only an eligibility check for prompt rendering. It is not semantic approval to broaden a task, bypass repository safety rules, or follow unsafe wording. When a rendered prompt, policy task, queue task, owner instruction, and repository safety rule differ, the strictest safety boundary wins. Non-goals remain binding even though they may name forbidden activities to exclude them.

Dry-run previews render at most one pass through safe generated policy tasks and never invoke a real agent. When `generate-from-policy` is selected, dry-run continues through the safe policy template list until the list is exhausted or the hard budget expires; it does not stop early just because `--min-tasks` or `--min-runtime-hours` is already satisfied. Operators must review the rendered prompt files before live use, especially each generated task's allowed scope, non-goals, verification commands, and stop/continue recommendation. If a prompt is ambiguous, narrow the tracked policy/runbook wording and re-run dry-run before live use.

Live mode may cycle safe policy templates until minimums are met or the hard budget expires. A repeated generated task is not a request to invent new work: if no safe, scoped improvement remains, the worker should run the relevant gates it can safely run, report a no-op checkpoint or clean completion, and avoid broadening scope.

## Issue #49 safe sustained run recipe

Use this recipe only after issue #49 product/code/test slices have made progress
and the finite queue would otherwise stop before the requested runtime. It does
not replace product work. It only keeps the supervisor supplied with bounded,
non-mutating follow-up tasks when safe work remains.

Dry-run first from the repository root:

```bash
python3 scripts/autonomy/supervisor.py \
  --budget-hours 6 \
  --min-runtime-hours 5.5 \
  --min-tasks 15 \
  --queue docs/autonomy/queues/issue49-long-run.md \
  --on-empty generate-from-policy \
  --backlog-policy docs/autonomy/backlog-policies/issue49-web-ui-create-trial-safe-nonmutating.md \
  --mode dry-run
```

Review the rendered prompts before switching to live mode:

- every generated task must keep its own allowed scope as a ceiling;
- the `issue49-autonomy-workflow-improvement` task must stay limited to
  `docs/autonomy/**`, `scripts/autonomy/**`,
  `apps/api/tests/test_autonomy_supervisor.py`, and `docs/handoff/**`;
- no generated task may authorize CREATE, PATCH, DELETE, batch operations,
  target probing, product dogfood, releases, public write beta claims, or write
  default changes;
- repeated generated tasks may end as explicit no-op checkpoints when no useful
  scoped change remains;
- runtime prompts and reports must stay under ignored `.hermes/autonomy/`
  unless the owner explicitly requests a tracked handoff.

For live mode, reuse the reviewed switches with `--mode live` only after
`AUTONOMY_AGENT_COMMAND` has been tested against stdin and the repository is
clean. Do not treat repeated `issue49-autonomy-workflow-improvement` prompts as
permission to broaden into product code, private data inspection, or release
work.

## Live execution

Only after reviewing the rendered prompts and choosing a command interface:

```bash
export AUTONOMY_AGENT_COMMAND='your-agent-command-that-reads-prompt-from-stdin'
python3 scripts/autonomy/supervisor.py \
  --budget-hours 5 \
  --queue docs/autonomy/queues/daytime-write-mode.md \
  --mode live \
  --collect-github
```

The supervisor feeds the rendered prompt to the configured command on stdin.
It does not hard-code Hermes or Codex. If `AUTONOMY_AGENT_COMMAND` is unset in
live mode, the supervisor exits with a clear fail-closed error.

Do not configure a command that spawns unbounded nested supervisors, cron jobs,
tmux sessions, or release publishers.

## Queue format

Queue files live under `docs/autonomy/queues/` and use Markdown task blocks:

```markdown
## Task: short-id
- target: issue or area
- goal: bounded task goal
- allowed scope: exact allowed files/areas
- non-goals: explicit exclusions
- verification commands:
  - command one
  - command two
- safety flags: no-private-data, no-release
- stop/continue recommendation: continue if gates pass
```

Every task must define id, target, goal, allowed scope, non-goals,
verification commands, safety flags, and stop/continue recommendation.

## Gate presets and known commands

The supervisor exposes named presets internally for reports and future queue
helpers:

- `quick-docs`
- `api`
- `web`
- `full`

Known project gates include:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
python3 scripts/check_public_status.py
python3 scripts/check_markdown_readability.py
python3 scripts/check_write_safety_defaults.py
python3 scripts/check_tracked_hygiene.py
git diff --check
```

The supervisor does not force the full gate after every task. Queue authors
should put the smallest safe verification set in each task and reserve full gate
runs for final-gate tasks.

## Git state guard

Before each task the supervisor records HEAD and requires a clean working tree,
except ignored/local `.hermes/autonomy/` runtime artifacts. After each task it
checks git status again. If the tree is dirty, it checkpoints with
`CHECKPOINT_DIRTY_TREE` instead of blindly continuing.

Recovery after interruption or dirty tree:

1. Inspect status: `git status --short`.
2. Review changed tracked files with `git diff --stat` and `git diff`.
3. Delete ignored runtime artifacts only if they are no longer needed:
   `.hermes/autonomy/runs/<timestamp>/`.
4. For safe intended tracked changes, run the relevant task gates and commit.
5. For unsafe/private/runtime artifacts, remove them from the worktree and rerun
   `python3 scripts/check_tracked_hygiene.py`.
6. Restart the supervisor with the same queue after the repository is clean.

Never stash or commit private GnuCash books, app DBs, backups, exports,
screenshots, `.env`, keys, tokens, private paths, account names, transaction
descriptions, memos, amounts, or raw private evidence.

## Transient failures and rate limits

The supervisor treats common strings as retryable/transient: `429`, `rate
limit`, `timeout`, `TLS reset`, `TLS handshake timeout`, `EOF`, and network
reset variants. Retries are bounded by `--max-retries` and
`--backoff-seconds`. After retry exhaustion it writes a checkpoint report and
stops with `CHECKPOINT_RETRYABLE_FAILURE`.

## GitHub state

With `--collect-github`, the supervisor records best-effort read-only snapshots
using `gh` when available:

- open issues;
- open PRs;
- release list;
- recent workflow runs.

GitHub mutation is not performed by the supervisor in dry-run mode. Live issue
comments/closures remain worker responsibility unless a future owner prompt
explicitly authorizes supervisor-side GitHub writes.

## Reports

Runtime reports default to ignored local paths:

```text
.hermes/autonomy/runs/<timestamp>/final-report.md
.hermes/autonomy/runs/<timestamp>/github-state.txt
```

Use `--final-report <path>` only when you intentionally want a specific report
path. Tracked final handoffs should summarize evidence, not include private run
logs or rendered prompts.

## Safety boundaries

The supervisor prompt always includes repository safety rules:

- never touch original/private/working/only-copy GnuCash books;
- never commit books, app DBs, backups, exports, screenshots, `.env`, secrets,
  private paths, account names, descriptions, memos, amounts, or raw evidence;
- do not publish releases/tags/packages/images;
- preserve `GNUCASH_WRITES_ENABLED=false` defaults;
- preserve `APP_ENV=test` write gates;
- do not claim public write beta, stable, production-ready, security-audited,
  broad compatibility, or only-copy safety.
