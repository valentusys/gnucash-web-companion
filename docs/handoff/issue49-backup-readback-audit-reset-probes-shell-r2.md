# Issue #49 backup/read-back/audit/reset/probes readiness shell r2

Date: 2026-07-07
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: this non-mutating #49 refinement makes the disabled-probe readiness shell more explicit for a future
bounded web UI CREATE trial.

This slice does not execute CREATE, PATCH, DELETE, batch, target probing, GnuCash book opening, backup creation,
read-back, audit writes, reset operations, or disabled-write probes.

## What changed

### Server-side readiness shell

`/transactions/new` now includes `executionReadiness.disabled_probe_plan`, a redacted pending-only plan for the
future post-reset disabled probes:

- validate probe after reset;
- preflight probe after reset;
- CREATE probe after reset;
- PATCH probe after reset;
- DELETE probe after reset;
- batch probe after reset.

Each entry defaults to `status=pending` and `expected_disabled_result=blocked_or_unavailable`. The plan is a
UI/status shell only. It does not call target, write, backup, lock, audit, reset, or probe helpers.

### UI shell

`/transactions/new` now renders a `disabled-probe-readiness-matrix` inside the existing execution-readiness panel.
The matrix states that validate/preflight/CREATE/PATCH/DELETE/batch probes are pending and not executed, shows only
route-family/verb labels, and keeps Future Create disabled.

## Guard coverage

Static and synthetic browser guards now assert:

- the disabled-probe matrix is rendered;
- all six probe entries remain `pending` by default;
- no `checked`, `passed`, `ready`, or `ok` default probe state is emitted;
- the exact pending probe IDs remain validate, preflight, CREATE, PATCH, DELETE, and batch;
- `create-preview` remains the only transaction-entry submission target;
- no active CREATE path is reachable in default mode;
- the synthetic browser smoke still observes no mutation-capable requests.

## Verification

Required local task commands passed:

- `cd apps/web && npm run check`;
- `cd apps/web && npm run test:transaction-entry-preview`;
- `cd apps/web && npm run test:transaction-entry-preview-browser`;
- `python3 scripts/check_public_status.py`;
- `python3 scripts/check_write_safety_defaults.py`;
- `python3 scripts/check_markdown_readability.py`;
- `python3 scripts/check_tracked_hygiene.py`;
- `git diff --check`.

## Safety summary

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- no product dogfood.
- no GnuCash book mutation.
- no private/original/working/only-copy book use.
- no target probing.
- no backup/read-back/audit/reset/probe execution.
- no release/tag/package/image publication.
- no public write beta, stable, production-ready, or security-audited claim.

## Next allowed step

Continue #49 only with non-mutating default-pending readiness work, or request fresh same-context owner/PM approval
before any future CREATE. The first mutating trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.
