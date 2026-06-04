# Autonomous supervisor runner final report

## What was implemented

- Added `scripts/autonomy/supervisor.py`, a repo-local autonomous supervisor with:
  - Markdown queue parsing;
  - one prompt rendered per task;
  - dry-run default with no agent invocation;
  - live mode gated by explicit `AUTONOMY_AGENT_COMMAND`;
  - wall-clock budget ownership;
  - bounded retry/checkpoint behavior for rate limits and transient network failures;
  - git clean-tree guard before and after each worker;
  - best-effort read-only GitHub state snapshot support;
  - ignored local runtime reports/prompts under `.hermes/autonomy/`.
- Added `scripts/autonomy/__init__.py`.
- Added supervisor tests in `apps/api/tests/test_autonomy_supervisor.py`.
- Added sample queues:
  - `docs/autonomy/queues/daytime-write-mode.md`
  - `docs/autonomy/queues/night-maintenance.md`
- Added operator runbook: `docs/autonomy/operator-runbook.md`.
- Added tracked report template: `docs/autonomy/report-template.md`.
- Updated `.gitignore` for `.hermes/autonomy/` runtime artifacts.

## Command examples

Dry-run, no external agent required:

```bash
python3 scripts/autonomy/supervisor.py \
  --budget-hours 5 \
  --queue docs/autonomy/queues/daytime-write-mode.md \
  --mode dry-run
```

Live, only after reviewing prompts and explicitly selecting an agent command:

```bash
export AUTONOMY_AGENT_COMMAND='your-agent-command-that-reads-prompt-from-stdin'
python3 scripts/autonomy/supervisor.py \
  --budget-hours 5 \
  --queue docs/autonomy/queues/daytime-write-mode.md \
  --mode live \
  --collect-github
```

## Dry-run evidence

After the initial supervisor commit left the tracked working tree clean, the documented dry-run command completed without external agent access:

```bash
python3 scripts/autonomy/supervisor.py --budget-hours 5 --queue docs/autonomy/queues/daytime-write-mode.md --mode dry-run
# status=COMPLETED_NO_SAFE_TASKS
# run_root=/home/val/projects/gnucash-web-companion/.hermes/autonomy/runs/20260604T220726Z
# final_report=/home/val/projects/gnucash-web-companion/.hermes/autonomy/runs/20260604T220726Z/final-report.md
```

Rendered prompts were written to the ignored local run directory:

```text
.hermes/autonomy/runs/20260604T220726Z/prompts/001-issue36-docs-reconcile.md
.hermes/autonomy/runs/20260604T220726Z/prompts/002-autonomy-runbook-polish.md
.hermes/autonomy/runs/20260604T220726Z/prompts/003-final-safe-gate-review.md
```

The ignored local report showed all three queue tasks as `SIMULATED` with one attempt each, proving that an early bounded worker completion does not end the session.

## Tests run

Initial targeted implementation gate:

```bash
cd apps/api && pytest tests/test_autonomy_supervisor.py -q
# 7 passed in 0.05s
```

Initial safety guards:

```bash
python3 scripts/check_public_status.py
# public-status-guard: ok

python3 scripts/check_write_safety_defaults.py
# write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; APP_ENV=test gate text present; explicit write enablement present; reset/default-disabled probe wording present
```

Final gate output is recorded below after the final verification pass.

## GitHub state verified

- `#22` is closed: https://github.com/valentusys/gnucash-web-companion/issues/22
- `#28` is closed: https://github.com/valentusys/gnucash-web-companion/issues/28
- `#36` is open: https://github.com/valentusys/gnucash-web-companion/issues/36
- Latest visible release from `gh release list` at start remained `v0.5.0-public-readonly-beta`; no `v0.5.1-public-readonly-beta` or `v0.4.0-owner-writebeta` release was listed.
- No release, tag, package, or image was published.

## Safety/privacy summary

- No original/private/working/only-copy GnuCash book was touched.
- No product dogfood or GnuCash mutation was run.
- No GnuCash book, SQLite book, app DB, backup, CSV export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence was committed.
- `GNUCASH_WRITES_ENABLED=false` defaults are preserved.
- Enabled writes remain `APP_ENV=test` gated.
- No public write beta, stable, production-ready, security-audited, broad compatibility, or only-copy safety claim was added.

## Limitations

- The supervisor does not itself decide product backlog priorities; queue files remain human-authored.
- Live issue comments/closures remain worker responsibility unless a future owner prompt explicitly authorizes supervisor-side GitHub writes.
- Live agent command compatibility depends on the configured command accepting prompts on stdin.
- Runtime reports/prompts are intentionally local/ignored and should not be committed.

## How this prevents manual prompt bouncing

The owner can start a multi-hour run once. The supervisor owns the budget, renders bounded worker prompts from the queue, launches the next task after early success, checkpoints instead of continuing through dirty git state, and handles retryable rate-limit/network failures with bounded backoff. One worker finishing early is no longer treated as the end of the run.

## Remaining follow-ups

- Review rendered prompts from a dry-run before enabling live mode.
- If a specific Hermes/Codex stdin command is standardized, document the exact `AUTONOMY_AGENT_COMMAND` value in a local-only note or future tracked runbook update.
- Consider future supervisor-side structured queue schema validation if Markdown queues become hard to maintain.

## Final gate output

```bash
cd apps/api && pytest tests/test_autonomy_supervisor.py -q
# 7 passed in 0.05s

cd apps/api && pytest -q
# 768 passed, 38 warnings in 273.93s (0:04:33)

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run build
# vite build completed successfully; adapter-node done

python3 scripts/check_public_status.py
# public-status-guard: ok

python3 scripts/check_write_safety_defaults.py
# write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; APP_ENV=test gate text present; explicit write enablement present; reset/default-disabled probe wording present

python3 scripts/check_tracked_hygiene.py
# Tracked hygiene check passed (1848 tracked paths inspected).

python3 scripts/check_markdown_readability.py
# markdown-readability-guard: ok (10 docs checked)

git diff --check
# passed with no output

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed with no output
```
