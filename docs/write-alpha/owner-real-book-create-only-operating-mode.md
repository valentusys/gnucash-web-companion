# Owner real-book CREATE-only operating mode

Issue: [#45 Owner real-book CREATE-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/45)
Status: planning and operating-boundary definition only; this document does not authorize mutation.

## Scope

This mode is strictly owner-only, real-book, and CREATE-only. It does not authorize PATCH, DELETE,
batch operations, unattended mutation, dogfood loops, public write beta, release/tag/package/image
publication, or production/stable/security-audited claims.

## Entry approval required

Before entering CREATE-only operating mode, the owner must give explicit same-context approval stating:

1. target class;
2. CREATE-only mode approval;
3. permitted CREATE count or per-session limit;
4. PATCH 0 / DELETE 0 / batch 0;
5. no unattended mutation;
6. route-backup or approved backup policy;
7. read-back, redacted audit, default-disabled reset, and disabled-probe policy;
8. redacted-only reporting boundaries.

Absent that approval, `GNUCASH_WRITES_ENABLED=false` remains the default and no mutation is authorized.

## Per-CREATE requirements

For each approved CREATE, unless a stricter approved policy says otherwise:

1. Verify exact target selection and no concurrent writer/lock.
2. Take route backup before CREATE, or apply the owner-approved backup policy.
3. Execute one CREATE only within the approved count.
4. Do not retry by creating another transaction without new owner approval.
5. Read back the created transaction with redacted structural markers only.
6. Capture redacted audit evidence with opaque references only.
7. Reset to default disabled according to the approved reset policy.
8. Run disabled-write probes for validate/preflight, CREATE, PATCH, and DELETE route families according to
   the approved probe policy.
9. Request manual GnuCash Desktop verification for early transactions.

## Recovery and rollback

Stop immediately and preserve backup evidence if backup, CREATE, read-back, audit, reset, disabled probes,
or manual Desktop verification fails. Do not perform a second CREATE, PATCH, DELETE, batch operation, or
manual repair through this app without a new owner/PM recovery approval. Recovery instructions must name
only redacted target classes and opaque backup/audit references in committed or GitHub-posted evidence.

## Future PATCH boundary

PATCH is out of scope for #45. PATCH of app-created transactions may be considered later only under a
separate owner/PM issue or approval packet that defines app-created ownership boundaries, exact editable
fields, backup/read-back/audit/rollback policy, manual Desktop verification expectations, and explicit
exclusions for historical/manual transactions, DELETE, and batch operations.

## Evidence policy

Tracked docs and GitHub comments must include only redacted class names, operation counts, pass/fail
markers, structural markers, and opaque references. They must not include raw private paths, account names,
descriptions, memos, amounts, books, backups, screenshots, tokens, keys, certs, or `.env` content.
