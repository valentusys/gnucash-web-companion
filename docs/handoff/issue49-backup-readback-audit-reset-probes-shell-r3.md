# Issue #49 backup/read-back/audit/reset/probes readiness shell r3

Date: 2026-07-07
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: this non-mutating #49 refinement makes the future execution evidence packet explicit without enabling or
running the CREATE trial.

This slice does not execute CREATE, PATCH, DELETE, batch, target probing, GnuCash book opening, backup creation,
read-back, audit writes, environment reset operations, or disabled-write probes.

## What changed

### Server-side readiness shell

`/transactions/new` now includes `executionReadiness.evidence_packet_plan`, a redacted pending-only plan for the
future evidence packet that a bounded web UI CREATE trial must produce:

1. backup evidence captured before CREATE;
2. read-back evidence captured after CREATE;
3. redacted audit evidence captured after CREATE;
4. write-disable reset evidence captured;
5. disabled-probe evidence captured after reset;
6. manual Desktop verification evidence captured.

Every evidence step defaults to `status=pending`, `required=true`, and `evidence_scope=redacted_only`. The plan is a
UI/status shell only. It does not call target, write, backup, lock, audit, reset, probe, or book-read helpers.

### UI shell

`/transactions/new` now renders an `execution-evidence-packet-plan` inside the existing execution-readiness panel.
The panel states that route backup, read-back, audit, reset, disabled-probe, and Desktop-verification evidence are
pending and not collected. It shows only redacted labels, order, phase, scope, and pending status.

Future Create remains disabled. The preview-reviewed checkbox remains local-only and insufficient by itself.

## Guard coverage

Static and synthetic browser guards now assert:

- the evidence packet plan is rendered;
- all six evidence steps remain `pending` by default;
- no `checked`, `passed`, `ready`, or `ok` default evidence state is emitted;
- the exact pending evidence step IDs remain backup, read-back, audit, reset, disabled probes, and Desktop
  verification;
- `create-preview` remains the only transaction-entry submission target;
- no active CREATE path is reachable in default mode;
- the synthetic browser smoke still observes no mutation-capable requests.

## Verification

Required local task commands passed for this r3 slice:

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
