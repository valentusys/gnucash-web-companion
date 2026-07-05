# Issue #49 target preflight/readiness UI shell

Date: 2026-07-05
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: this non-mutating #49 slice adds a **target preflight/readiness UI shell** for a future bounded web UI
CREATE trial.

This slice does not execute target preflight against a private target. It does not probe private files, open any
book, create backups, inspect locks, call write helpers, or execute CREATE/PATCH/DELETE/batch operations.

## What changed

### Safe server-side readiness state

`/transactions/new` now returns a read-only `targetPreflight` object with safe default state:

- `required=true`;
- `status=not_checked`;
- `target_class=null`;
- checklist entries all `pending`.

The object is redacted-only and contains no raw target paths, account names, descriptions, memos, amounts, GUIDs,
book names, backup paths, screenshots, tokens, keys, certs, or `.env` values.

### UI shell

`/transactions/new` now shows a `Target preflight required` panel with default `Target readiness not checked` state.
The panel states that it is UI/status-only and that no private preflight/file/book/backup/lock/write helper runs in
this slice.

The future CREATE checklist is visible and pending by default:

- target class selected;
- target file exists/readable;
- target is outside repo;
- GnuCash Desktop closed;
- no concurrent writer/lock;
- no `.LCK`/`.LNK` lock;
- no Syncthing conflict copy before session if applicable;
- independent backup exists;
- restore proof available;
- reviewed non-stale preview;
- exact CREATE count = 1;
- writes reset/disabled probes required after session;
- manual Desktop verification required.

Future Create remains disabled/inert. The preview-reviewed checkbox remains local-only and insufficient by itself.

### Guard coverage

Static and synthetic browser guards now assert:

- the target preflight panel exists;
- target readiness defaults to `not_checked` / `pending`;
- all future readiness checklist items are present;
- no checked/passed/ready target state exists by default;
- no file/book/backup/lock/write helper is referenced by the `/transactions/new` server shell;
- `create-preview` remains the only transaction-entry submission target;
- no active CREATE action/path is reachable in default mode;
- the browser smoke observes no mutation requests.

## Preserved future #49 requirements

Any future real CREATE still requires fresh same-context owner/PM approval with exact target class and exact CREATE
count. The first trial remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.

A future approved session must still prove target preflight, use a reviewed current non-stale UI preview, create a
backup before CREATE, read back after CREATE, produce redacted audit evidence, reset writes to disabled, run disabled
probes, and complete manual Desktop verification.

## Safety summary for this slice

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- no GnuCash book mutation.
- no private/original/working/only-copy book use.
- no actual private target probing.
- no active CREATE action reachable in default mode.
- no public write beta.
- no release/tag/package/image publication.
- no production/stable/security-audited claim.
- no private details leaked.

## Next allowed step

Another non-mutating #49 slice may add read-only approval/session readiness plumbing or UI validation. Any actual
CREATE still requires fresh same-context owner/PM approval; the first mutating trial remains
`CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.
