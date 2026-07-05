# Issue #49 backup/read-back/audit/reset/probes readiness shell

Date: 2026-07-06
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: this non-mutating #49 slice adds a backup/read-back/audit/reset/probes readiness UI and server shell for a future bounded web UI CREATE trial.

This slice does not execute CREATE, PATCH, DELETE, batch, target probing, GnuCash book opening, backup creation, read-back, audit writes, reset operations, or disabled-write probes.

## What changed

### Server-side readiness shell

`/transactions/new` now returns a redacted `executionReadiness` object with safe default state:

- `required=true`;
- `status=not_checked`;
- `backup_state=pending`;
- `read_back_state=pending`;
- `audit_state=pending`;
- `reset_state=pending`;
- `probe_state=pending`;
- every checklist entry `pending`.

The object is UI/status guidance only. It contains no raw private paths, account names, descriptions, memos, amounts, GUIDs, book names, backup paths, screenshots, tokens, keys, certs, or `.env` values.

### UI shell

`/transactions/new` now renders an `execution-readiness-shell` panel:

- `Backup/read-back/audit/reset/probes required`;
- `Execution readiness not checked`;
- explicit `execution_readiness.*` redacted status fields;
- default state copy: backup, read-back, audit, reset, and probe readiness are pending / not checked / not armed;
- pending checklist items for backup plan, readable backup proof, post-CREATE read-back, redacted audit evidence, write reset, disabled CREATE probe, disabled PATCH/DELETE/batch probes, and manual Desktop verification.

Future Create remains disabled/inert. The preview-reviewed checkbox remains local-only and insufficient by itself.

## Guard coverage

Static and synthetic browser guards now assert:

- the execution readiness panel exists;
- readiness defaults to `not_checked` / `pending`;
- backup/read-back/audit/reset/probes labels are present;
- no checked/passed/ready execution-readiness state exists by default;
- no file/book/backup/lock/write helper is referenced by the `/transactions/new` server shell;
- `create-preview` remains the only transaction-entry submission target;
- no active CREATE action/path is reachable in default mode;
- the browser smoke observes no mutation requests.

## Preserved future #49 requirements

Any future real CREATE still requires fresh same-context owner/PM approval with exact target class and exact CREATE count. The first trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.

A future approved session must still prove target preflight, use a reviewed current non-stale UI preview, create a backup before CREATE, read back after CREATE, produce redacted audit evidence, reset writes to disabled, run disabled-write probes, and complete manual Desktop verification.

## Safety summary for this slice

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- no GnuCash book mutation.
- no private/original/working/only-copy book use.
- no actual private target probing.
- no backup/read-back/audit/reset/probe execution.
- no active CREATE action reachable in default mode.
- no public write beta.
- no release/tag/package/image publication.
- no production/stable/security-audited claim.
- no private details leaked.

## Next allowed step

Continue #49 only with non-mutating default-pending readiness work, or request fresh same-context owner/PM approval before any future CREATE. The first mutating trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.
