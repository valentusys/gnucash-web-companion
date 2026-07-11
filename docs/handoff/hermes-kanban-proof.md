# Hermes Kanban proof

Status: PASS for a controlled proof; recommendation: hybrid. This does not replace `scripts/autonomy/supervisor.py`.

## Environment

- Hermes: `v0.18.2 (2026.7.7.2)`, upstream `5e849942`.
- Board: `gnucash-web-companion-kanban-proof`.
- Store: `/home/val/.hermes/kanban/boards/gnucash-web-companion-kanban-proof/kanban.db` (SQLite).
- Worker logs: `/home/val/.hermes/kanban/boards/gnucash-web-companion-kanban-proof/logs/`.
- Project binding: `gnucash-web-companion` → proof board; primary repo is this checkout.
- Baseline: `680baddc77d237743fe3f712829878a4ce4c58aa`, clean and equal to `origin/main`.
- Dispatcher: gateway-embedded (`kanban.dispatch_in_gateway: true`); no standalone daemon was started.

## Profiles

| Profile | Provider/model | Role |
|---|---|---|
| `pm-orchestrator` | `openai-codex / gpt-5.6-sol` | read-only decomposition and scope |
| `backend-worker` | `openai-codex / gpt-5.5` | backend/test worktree |
| `frontend-worker` | `openai-codex / gpt-5.5` | frontend/test worktree |
| `qa-integrator` | `openai-codex / gpt-5.5` | review and isolated integration |

The task CLI has no model flag in the installed `hermes kanban create --help`; models were set at profile level.

## Tasks and worktrees

| Task | Result | Branch/worktree |
|---|---|---|
| `t_adfa43be` PM scope | done | `kanban-proof/pm-scope`, former `.worktrees/t_adfa43be` |
| `t_135da313` backend guard | reclaimed once, then done | `kanban-proof/backend-nonfinite-preview`, former `.worktrees/t_135da313` |
| `t_9c568c8d` frontend redaction | done | `kanban-proof/frontend-preview-redaction`, former `.worktrees/t_9c568c8d` |
| `t_79772480` QA integration | done | `kanban-proof/qa-integration`, former `.worktrees/t_79772480` |

Hermes created each worktree from the project-bound repo. Coding workers never edited `main`. The clean worktrees were removed only after integration and final local checks; proof branches remain for audit. `.worktrees/` is ignored because it was confirmed as the repo-local Kanban worktree location. Board DB, logs, transcripts, prompts, and credentials remain outside Git.

## Restart/reclaim drill

1. Backend task `t_135da313` was `running`, run `2`, PID `1646051`.
2. Operator ran:

   ```bash
   hermes kanban --board gnucash-web-companion-kanban-proof reclaim t_135da313 \
     --reason "controlled proof restart drill after worker claim"
   ```

3. Reclaim sent SIGTERM and recorded `terminated: true`, `sigkill: false`; PID `1646051` disappeared.
4. SQLite retained the task, body, dependency, events, run `2` outcome `reclaimed`, branch, and worktree.
5. The task returned to `ready`; the gateway dispatcher claimed it as run `3` and started PID `1646281`.
6. Run `3` read the prior attempt, reused the same intact worktree, committed the change, and completed successfully.
7. No duplicate worker was observed for the task.

This is retry/reclaim, not continuation of the interrupted model context. Durable board history and filesystem state survive; in-memory LLM context does not.

## Integration

- Backend source commit: `f3e947b1f3b3f8fa636941c78a71994f4b2d7435`.
- Frontend source commit: `beae000f93dc28c1f0cdcdaf72cd0446cf08a688`.
- QA cherry-picked them as `b24a0c0` and `0cac500` and added scoped guard alignment `3b1bf92`.
- Cherry-picks had no Git conflicts. QA corrected one stale static assertion in `apps/web/scripts/test-auth-routes.mjs`.
- Main orchestrator reviewed the six-file diff and fast-forwarded `main` to the exact QA-tested head.
- `scripts/autonomy/supervisor.py` was unchanged.

## Verification

QA worktree passed:

- public-status, write-safety-defaults, markdown-readability, tracked-hygiene, and `git diff --check`;
- backend targeted suite: `72 passed`;
- frontend check, static preview, auth routes, both browser commands;
- Docker Compose config validation.

Final main passed:

- all four repository guard scripts and `git diff --check`;
- backend full suite: `1102 passed`, with 63 existing deprecation warnings;
- frontend check/build, static preview, auth routes, and both browser commands;
- Docker Compose config validation.

GitHub CI for proof/report commit `9d84e28` passed all four jobs:
<https://github.com/valentusys/gnucash-web-companion/actions/runs/29132255675>.

No owner/private/original/working/Syncthing book was opened or mutated. Default `GNUCASH_WRITES_ENABLED=false` and default preview-only UI remain unchanged.

## Commands actually used

```bash
hermes kanban --help
hermes kanban boards create gnucash-web-companion-kanban-proof \
  --name "GnuCash Web Companion Kanban Proof" \
  --default-workdir /home/val/projects/gnucash-web-companion
hermes project bind-board gnucash-web-companion gnucash-web-companion-kanban-proof

hermes kanban --board gnucash-web-companion-kanban-proof create "<title>" \
  --assignee <profile> --project gnucash-web-companion \
  --workspace worktree --branch <branch> --parent <task-id> --json
hermes kanban --board gnucash-web-companion-kanban-proof dispatch --max 2 --json
hermes kanban --board gnucash-web-companion-kanban-proof list --json
hermes kanban --board gnucash-web-companion-kanban-proof show <task-id> --json
hermes kanban --board gnucash-web-companion-kanban-proof runs <task-id> --json
hermes kanban --board gnucash-web-companion-kanban-proof log <task-id> --tail 12000
hermes kanban --board gnucash-web-companion-kanban-proof diagnostics --json
hermes kanban --board gnucash-web-companion-kanban-proof reclaim <task-id> --reason "<reason>"
```

## Operator procedure

Create a task:

```bash
hermes kanban --board gnucash-web-companion-kanban-proof create "<bounded task>" \
  --assignee backend-worker --project gnucash-web-companion \
  --workspace worktree --branch kanban-proof/<name> --max-runtime 30m --json
```

Run or resume dispatch after a restart:

```bash
hermes gateway start
hermes kanban --board gnucash-web-companion-kanban-proof diagnostics --json
hermes kanban --board gnucash-web-companion-kanban-proof dispatch --max 2 --json
```

Stop and retry exactly one worker:

```bash
hermes kanban --board gnucash-web-companion-kanban-proof show <task-id> --json
hermes kanban --board gnucash-web-companion-kanban-proof reclaim <task-id> \
  --reason "operator retry"
hermes kanban --board gnucash-web-companion-kanban-proof dispatch --max 1 --json
```

Inspect audit state:

```bash
hermes kanban --board gnucash-web-companion-kanban-proof runs <task-id> --json
hermes kanban --board gnucash-web-companion-kanban-proof log <task-id> --tail 12000
hermes kanban --board gnucash-web-companion-kanban-proof diagnostics --json
```

Safely close while preserving recovery:

```bash
hermes kanban --board gnucash-web-companion-kanban-proof archive \
  t_adfa43be t_135da313 t_9c568c8d t_79772480
hermes kanban boards rm gnucash-web-companion-kanban-proof
```

`boards rm` archives the board directory by default. Do not add `--delete` when the audit trail must remain recoverable.

## Limits and comparison

### Repo-local supervisor

Strengths: mature project queue/policy, explicit time/task budgets, deterministic long-run stop/report flow, GitHub collection, proven fallback.

Weaknesses: recovery is reconstructed from Git/process/run files; no native per-task run history, atomic claim/reclaim, profile routing, or managed worktrees.

### Hermes Kanban

Strengths: durable per-board SQLite, append-only events, per-attempt runs, atomic claims, supported reclaim with worker termination, project-bound worktrees, profile model routing, gateway dispatch, and inspectable logs.

Weaknesses: retry starts a new model context; integration into `main` still needs a trusted QA/orchestrator gate; profile/global state is outside the repo; npm dependencies were installed independently in worktrees; task-level model selection is absent from installed create CLI; cloned profiles retain broad toolsets unless tightened.

## Recommendation

Use a hybrid workflow pending a separate owner decision:

- Kanban: bounded task graph, persistent status, specialist profiles, worktree execution, restart/reclaim, review handoffs, and audit history.
- `scripts/autonomy/supervisor.py`: fallback and current mechanism for long budget/policy-driven product runs.
- `delegate_task`: optional inside a Kanban worker only for short reasoning/review fan-out; never as the durable task record or as the owner of main integration.

Do not declare migration complete or remove the supervisor from this proof alone.
