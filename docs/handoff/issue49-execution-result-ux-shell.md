# Issue #49 execution-result UX shell

Date: 2026-07-08
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: this non-mutating #49 refinement adds browser-visible execution-result, success, failure, rollback, and post-result reporting UX without enabling or running CREATE.

This slice does not execute CREATE, PATCH, DELETE, batch, target probing, GnuCash book opening, backup creation, read-back, audit writes, environment reset operations, disabled-write probes, rollback/restore, or product dogfood.

## What changed

### Server-side result shell

`/transactions/new` now includes `executionResult`, a redacted pending-only result shell for a future bounded web UI CREATE trial:

- `status=not_executed`;
- `create_result_state=blocked`;
- `success_state=pending`;
- `failure_state=pending`;
- `rollback_state=not_run`;
- six pending, redacted-only steps covering success create refs, success read-back, safe failure errors, no success claim on failure/unknown state, rollback decision, and post-result disabled probes.

The result shell is UI/status data only. It does not call target, write, backup, lock, audit, reset, probe, book-read, or restore helpers.

### UI shell

`/transactions/new` now renders `execution-result-shell` inside the existing execution-readiness panel. The panel states that no execution result exists, no success/failure result is claimed, rollback/restore is not run, and rollback is a future owner-approved recovery path only.

The form, disabled Create button, normalized preview, and disabled Future Create button now reference the execution-result shell in their explanatory/ARIA boundary copy. The Future Create readiness list includes execution-result and rollback state alongside write-session, target-preflight, and execution-readiness blockers.

Future Create remains disabled. The preview-reviewed checkbox remains local-only and insufficient by itself.

## Guard coverage

Static and synthetic browser guards now assert:

- the execution-result shell is rendered;
- all six execution-result steps remain `pending` by default;
- default state stays `not_executed` / `blocked` / `pending` / `not_run`;
- no success, failure, rollback-complete, checked, passed, ready, or ok result state is emitted;
- the exact pending success/failure/rollback/post-result step IDs remain stable;
- disabled Create and Future Create controls reference the execution-result shell and remain inert;
- `create-preview` remains the only transaction-entry submission target;
- no active CREATE path is reachable in default mode;
- the synthetic browser smoke observes no mutation-capable requests.

## Verification

Required local task commands run for this slice:

- `cd apps/api && pytest -q` — PASS, 979 passed, 51 warnings.
- `cd apps/web && npm run check` — PASS, 0 errors, 0 warnings.
- `cd apps/web && npm run build` — PASS, Vite/SvelteKit build completed.
- `cd apps/web && npm run test:transaction-entry-preview` — PASS, `transaction-entry-preview-static: ok`.
- `cd apps/web && npm run test:auth-routes` — PASS, `auth route checks passed`.
- `cd apps/web && npm run test:transaction-entry-preview-browser` — PASS, `transaction-entry-preview-browser: ok (synthetic, writes-disabled, no mutation requests)`.
- `python3 scripts/check_write_safety_defaults.py` — PASS, write-safety defaults ok.
- `python3 scripts/check_tracked_hygiene.py` — PASS, 1955 tracked paths inspected.
- `git diff --check` — PASS.

## Safety summary

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- rollback/restore 0.
- no product dogfood.
- no GnuCash book mutation.
- no private/original/working/only-copy book use.
- no target probing.
- no backup/read-back/audit/reset/probe execution.
- no release/tag/package/image publication.
- no public write beta, stable, production-ready, or security-audited claim.

## Next allowed step

Continue only with non-mutating default-pending browser/history/import-export work, or request fresh same-context owner/PM approval before any future CREATE. The first mutating trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.
