# Issue #49 CREATE execution gate / armed-session shell

Date: 2026-07-05
Issue: [#49 Owner web UI CREATE execution trial](https://github.com/valentusys/gnucash-web-companion/issues/49)

## Verdict

PASS: the first #49 implementation slice adds a **non-mutating web UI CREATE execution gate / armed-session shell**.

This slice does not execute CREATE, PATCH, DELETE, or batch operations. It does not mutate any GnuCash book and
does not add an active CREATE execution path reachable from `/transactions/new`.

## What changed

### Server-rendered gate state

`/transactions/new` now exposes a safe, redacted write-session gate object from the SvelteKit server load:

- `writes_enabled`;
- `session_armed`;
- `create_execution_allowed`;
- `create_execution_reason`;
- `allowed_create_count`;
- `target_class`.

Defaults are safe/off:

- `session_armed=false`;
- `create_execution_allowed=false`;
- `allowed_create_count=0`;
- `target_class=null`;
- with default `GNUCASH_WRITES_ENABLED=false`, the reason is `write session not armed`.

This gate object contains no private path, account, description, memo, amount, GUID, book, backup, screenshot,
token, key, cert, or `.env` values.

### Frontend shell

`/transactions/new` now shows:

- `Preview mode`;
- `Write session not armed`;
- `CREATE execution unavailable without fresh owner approval`;
- a disabled armed-session requirements panel:
  - target class required;
  - exact CREATE count required;
  - reviewed non-stale preview required;
  - preview-reviewed checkbox alone is not enough;
  - backup/read-back/audit/reset/probes required;
  - manual Desktop verification required.

The existing preview/approval packet remains. The Future Create control remains a disabled `type="button"`.

### Guard/test updates

Static and browser smoke guards now verify:

- the write-session gate defaults to unarmed/off;
- `allowed_create_count=0` and target class is required by default;
- CREATE execution is unavailable without fresh owner approval;
- the disabled requirements panel is present;
- preview-reviewed checkbox alone is insufficient;
- `/transactions/create-preview` remains the only transaction-entry submission target;
- no active CREATE form action/server action is present in default mode.

## Preserved #49 future requirements

Future CREATE still requires fresh same-context owner/PM approval with:

- exact target class;
- exact CREATE count;
- first trial default `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`;
- target preflight;
- reviewed current non-stale UI preview;
- backup before CREATE;
- read-back after CREATE;
- redacted audit evidence;
- reset to `GNUCASH_WRITES_ENABLED=false`;
- disabled-write probes;
- manual Desktop verification for the first UI CREATE trial.

## Safety summary for this slice

- CREATE 0.
- PATCH 0.
- DELETE 0.
- batch 0.
- no GnuCash book mutation.
- no private/original/working/only-copy book use.
- no active CREATE action reachable in default mode.
- no public write beta.
- no release/tag/package/image publication.
- no production/stable/security-audited claim.
- no private details leaked.

## Next allowed step

Implement the next #49 slice only if it remains non-mutating, or request fresh same-context owner/PM approval before
any future CREATE. The first mutating trial, if approved later, remains `CREATE 1 / PATCH 0 / DELETE 0 / batch 0`.
