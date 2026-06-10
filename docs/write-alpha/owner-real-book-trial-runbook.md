# Owner real-book trial runbook

Issue: [#44 Owner real-book trial safety model](https://github.com/valentusys/gnucash-web-companion/issues/44)
Status: preparation only; this runbook does not authorize mutation.

## Hard boundary

Do not run this runbook unless the owner/PM gives explicit same-context approval for the exact target
class and exact operation count.

Allowed maximum for the first trial after approval:

- CREATE: 1 transaction
- PATCH: 0
- DELETE: 0
- batch: 0
- unattended mutation: 0

Forbidden during this runbook:

- PATCH or DELETE;
- batch operation;
- mutation of an original-only or only-copy unsafe target;
- unattended real-book mutation;
- release, tag, package, or image publication;
- public write beta;
- production, stable, or security-audited claims;
- posting raw private evidence.

## Required same-context approval text

Before any mutation, the owner/PM approval must explicitly state:

```text
I approve exactly one owner real-book CREATE trial for the target class named below.
Target class: <redacted owner-selected trial target class>
Operation count: CREATE 1, PATCH 0, DELETE 0, batch 0.
GnuCash Desktop is closed for the target, and no concurrent writer is active.
An independent backup exists, and restore path/proof was verified before mutation.
Take a route backup before CREATE, then perform read-back, audit capture, reset writes disabled,
and disabled-write probes. Report redacted evidence only.
This does not approve release, public write beta, PATCH, DELETE, batch, unattended mutation,
production readiness, stable status, or security-audited status.
```

If the approval is incomplete, stop before mutation and ask for the missing fields.

## Pre-mutation gate

1. Confirm exact target class and exact count from the same-context approval.
2. Confirm `GNUCASH_WRITES_ENABLED=false` is the committed default.
3. Confirm the explicit write-enabled runtime, if used, remains `APP_ENV=test` gated.
4. Confirm GnuCash Desktop is closed for the target.
5. Confirm no lock or concurrent writer is active.
6. Confirm an independent backup exists before route backup.
7. Verify restore path/proof before mutation.
8. Confirm the route backup step is available and will run immediately before CREATE.
9. Confirm evidence redaction rules can be satisfied without raw private data.
10. Stop if any check fails.

## Route backup before CREATE

Immediately before the one CREATE:

1. Take the route backup for the selected target.
2. Record only redacted backup evidence:
   - route backup present: yes/no;
   - route backup reference: opaque redacted ID only;
   - timestamp window or sequence marker, without raw paths.
3. Stop if the route backup fails or requires exposing raw backup paths.

## CREATE execution boundary

When all gates pass and only after explicit approval:

1. Execute exactly one CREATE transaction.
2. Do not call PATCH, DELETE, or batch routes.
3. Do not retry by creating another transaction unless a new same-context owner/PM approval is given.
4. If CREATE fails, stop and report redacted failure class only.

## Post-CREATE read-back and audit

After the single CREATE:

1. Read back the created transaction through safe app/API paths.
2. Record only redacted verification markers:
   - created transaction was read back: yes/no;
   - split count or structural marker if safe and non-private;
   - app-owned/write-alpha-owned marker if applicable;
   - no raw account names, descriptions, memos, amounts, or book names.
3. Record audit evidence only as redacted references:
   - audit row present: yes/no;
   - audit operation family: CREATE;
   - route backup reference present: yes/no;
   - opaque audit reference only.

## Default-disabled reset

Immediately after read-back/audit:

1. Reset runtime to `GNUCASH_WRITES_ENABLED=false`.
2. Confirm no explicit write-enabled runtime remains active.
3. Keep committed defaults unchanged.
4. Do not publish a release, package, image, or public write beta.

## Disabled-write probes after reset

After reset, run disabled-write probes for the write route families:

- validate/write preflight route, if present;
- CREATE route;
- PATCH route;
- DELETE route.

Expected result: writes are blocked again under the default-disabled posture. Report only route family,
status class, and safe error class. Do not include payloads, private paths, account names, memos,
descriptions, amounts, tokens, keys, certs, or `.env` content.

## Redacted report template

```markdown
# Owner real-book CREATE trial redacted report

Issue: #44
Approval: same-context owner/PM approval present: yes
Target class: <redacted class only>
Operation counts: CREATE 1 / PATCH 0 / DELETE 0 / batch 0
Desktop closed and no concurrent writer: yes
Independent backup existed before mutation: yes
Restore path/proof verified before mutation: yes
Route backup before CREATE: yes, ref <opaque-ref>
CREATE result: success/failure class only
Read-back after CREATE: yes/no, redacted structural markers only
Audit evidence: yes/no, ref <opaque-ref>
Default-disabled reset: yes
Disabled-write probes after reset: validate <status>, CREATE <status>, PATCH <status>, DELETE <status>
Private evidence policy: no raw private paths, account names, descriptions, memos, amounts, books,
backups, screenshots, tokens, keys, certs, or .env content posted or committed.
Release/public posture: no release, no public write beta, no production/stable/security-audited claim.
```

## Abort rules

Abort before mutation if approval, backup, restore proof, Desktop closed state, lock check, route backup,
or redaction cannot be proven. Abort after CREATE if read-back, audit, reset, or disabled probes fail;
then preserve backups and escalate to owner/PM before any further action.
