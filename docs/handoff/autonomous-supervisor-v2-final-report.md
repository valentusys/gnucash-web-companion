# Autonomous supervisor v2 final report

## Summary

Implemented autonomy supervisor v2 for sustained local autonomous runs while preserving fail-closed safety and backward-compatible default queue-runner behavior.

## Implemented changes

- Added CLI options:
  - `--min-runtime-hours FLOAT`
  - `--min-tasks INT`
  - `--on-empty {stop,repeat-safe-final,generate-from-policy}`
  - `--backlog-policy PATH`
- Preserved default behavior:
  - with no new options, finite queues still stop when exhausted with `COMPLETED_NO_SAFE_TASKS`.
- Added generated backlog mode:
  - reads Markdown backlog policy files;
  - filters policy tasks fail-closed;
  - only uses tasks marked `generated-safe`, `no-private-data`, and `no-release`;
  - rejects unsafe flags such as `release`, `touches-private-data`, `dogfood`, and `gnucash-mutation`;
  wording deny-list checks are intentionally narrow so negative statements such as "no public write beta" remain valid;
  - writes generated prompts under ignored `.hermes/autonomy/runs/.../prompts/`;
  - stops with `HARD_NO_SAFE_TASKS` if no safe generated task exists before configured minimums are met.
- Added minimum completion semantics:
  - `--budget-hours` remains the hard upper bound;
  - `--min-runtime-hours` and `--min-tasks` prevent early final-report completion while safe generated tasks remain.
- Added report metadata:
  - minimum runtime/task settings;
  - empty-queue strategy;
  - backlog policy path;
  - stop reason.

## New tracked docs

- `docs/autonomy/backlog-policies/issue36-owner-writebeta.md`
- `docs/autonomy/queues/issue36-long-run.md`
- Updated `docs/autonomy/operator-runbook.md`

## Backlog policy coverage

`docs/autonomy/backlog-policies/issue36-owner-writebeta.md` covers these safe generated task families:

- A. owner-writebeta remaining-gates audit
- B. release/no-release decision docs
- C. real-working-book trial blocker/runbook, without authorizing trial
- D. backup/restore readiness docs/tests, non-mutating
- E. default-disabled/write-safety guard improvements
- F. audit/privacy wording guards
- G. final full gate report
- H. discovered safe test/doc/code quality fixes related to #36

Policy invariants explicitly prohibit:

- GnuCash mutations by default;
- dogfood;
- real/private/original/working/only-copy books;
- release/tag/package/image publication;
- public write beta claims;
- production/stable/security-audited claims;
- changing `GNUCASH_WRITES_ENABLED=false` defaults;
- weakening `APP_ENV=test` write gates.

## Tests added

`apps/api/tests/test_autonomy_supervisor.py` now verifies:

- finite queues still exit as before by default;
- `--min-tasks` with generated policy continues after queue exhaustion;
- `--min-runtime-hours` does not final-report early if safe generated tasks remain;
- `generate-from-policy` stops fail-closed if policy has no safe tasks;
- dirty tree still checkpoints;
- live mode still requires `AUTONOMY_AGENT_COMMAND`;
- dry-run never invokes a real agent;
- v2 CLI options parse correctly;
- rendered prompts retain required safety rules.

## Verification run

```bash
cd apps/api && pytest tests/test_autonomy_supervisor.py -q
# 13 passed in 0.06s

cd apps/api && pytest -q
# 774 passed, 38 warnings in 273.55s

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run build
# vite build completed successfully; adapter-node done

JWT_SECRET=dummy-...cret APP_ADMIN_PASSWORD=*** docker compose config --quiet
# passed with no output

python3 scripts/check_public_status.py
# public-status-guard: ok

python3 scripts/check_write_safety_defaults.py
# write-safety defaults ok: GNUCASH_WRITES_ENABLED=false; APP_ENV=test gate text present; explicit write enablement present; reset/default-disabled probe wording present

python3 scripts/check_markdown_readability.py
# markdown-readability-guard: ok (10 docs checked)

python3 scripts/check_tracked_hygiene.py
# Tracked hygiene check passed (1848 tracked paths inspected).

git diff --check
# passed with no output
```

## Safety notes

- No GnuCash mutation was run.
- No dogfood was run.
- No private/original/working/only-copy GnuCash book was touched.
- No releases, tags, packages, or images were published.
- No public write beta claim was added.
- No production/stable/security-audited claim was added.
- Runtime `.hermes/autonomy/` dry-run artifacts remain ignored/local only.
