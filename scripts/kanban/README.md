# Safe Hermes product-task wrapper

`scripts/kanban/create_product_task.py` is a narrow operator helper for creating
`gnucash-web-companion` Hermes Kanban product tasks. It validates the requested
card, checks local safety gates in live mode, then invokes the installed
`hermes kanban create` command with an argv list (`shell=True` is not used).

## Dry-run template

Dry-run validates the inputs and prints a structured, body-redacted command. It
intentionally creates no subprocesses and skips git/board diagnostics.

```bash
python3 scripts/kanban/create_product_task.py \
  --dry-run \
  --board gnucash-product-run-3 \
  --title "Backend: bounded product task" \
  --assignee backend-worker \
  --branch-suffix issue53-backend \
  --body-file /tmp/gnucash-product-task-body.md \
  --max-runtime 2h \
  --max-retries 1 \
  --parent t_1234abcd \
  --priority 90
```

## Live creation template

Remove `--dry-run` only after reviewing the redacted command:

```bash
python3 scripts/kanban/create_product_task.py \
  --board gnucash-product-run-3 \
  --title "Backend: bounded product task" \
  --profile backend-worker \
  --branch-suffix issue53-backend \
  --body-file /tmp/gnucash-product-task-body.md \
  --max-runtime 2h \
  --max-retries 1 \
  --parent t_1234abcd \
  --priority 90
```

On success the wrapper prints `created_task_id=<task-id>` plus a small JSON
summary. The body is passed only to `hermes kanban create --body`; the wrapper
does not write prompts or task bodies into the repository.

## Fixed fields

The wrapper always sets:

- `--project gnucash-web-companion`
- `--workspace worktree`
- `--created-by gnucash-product-task-wrapper`
- `--branch run/product/<safe-suffix>-<UTC timestamp>-<8 char token>`
- `--json`

Supported assignees are intentionally limited to the configured product-run
profiles: `backend-worker`, `frontend-worker`, `pm-orchestrator`, and
`qa-integrator`.

## Live-mode refusal gates

Live mode refuses to call `hermes kanban create` unless all gates pass:

1. Current git checkout resolves to the `gnucash-web-companion` remote.
2. The current worktree appears in `git worktree list --porcelain`.
3. The main worktree exists, is clean, and `main == origin/main`.
4. `hermes kanban --board <board> diagnostics --json` returns no diagnostics.

The wrapper also rejects empty title/body, unsafe branch suffixes, unsupported
assignees, invalid parent task IDs, option-like board/body-file/path values, and
out-of-range priority/retry values.

## Limitations

- It does not reimplement Hermes Kanban; CLI behavior still comes from the
  installed `hermes` command.
- It does not fetch `origin/main`; operators should fetch/reconcile before live
  creation if local remote refs may be stale.
- Dry-run is command preview only. It is intentionally subprocess-free, so it
  does not prove git or board diagnostics are clean.
