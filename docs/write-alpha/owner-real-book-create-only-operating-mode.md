# Owner real-book CREATE-only operating mode

Issue: [#45 Owner real-book CREATE-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/45)
Status: **CREATE-only operating policy v1 documented**. This document does not authorize mutation by itself.

## Policy v1 scope

Policy v1 permits only owner-only real-book CREATE-only sessions under a fresh explicit same-context owner
approval for each session. It is based on the manually verified #44 first real-book CREATE trial and the
manually verified #45 CREATE-only operating sessions.

Policy v1 does not make the app production-ready, stable, security-audited, or safe for general public
write use. It is a narrow owner-only operating policy for bounded CREATE sessions on the owner-approved
real-book target class.

## Required per-session approval

Before any CREATE-only operating session, the owner must give explicit same-context approval stating:

1. target class only for public/tracked reporting;
2. CREATE-only mode approval for this session;
3. bounded CREATE count for this session;
4. PATCH 0 / DELETE 0 / batch 0;
5. no unattended mutation;
6. route backup before each CREATE, unless a later explicitly approved safer per-session backup policy exists;
7. read-back after each CREATE;
8. redacted audit evidence after each CREATE;
9. reset writes to disabled after the session;
10. disabled-write probes after reset;
11. owner manual GnuCash Desktop verification after the session;
12. redacted-only reporting boundaries.

Absent that approval, `GNUCASH_WRITES_ENABLED=false` remains the default and no mutation is authorized.

## Allowed operations

Policy v1 allows only:

- owner-only real-book CREATE-only sessions;
- explicit same-context owner approval per session;
- bounded CREATE count per session;
- individual CREATE operations, not batch;
- preflight before mutation and stop-before-mutation unless READY;
- route backup before each CREATE;
- read-back after each CREATE;
- redacted audit evidence after each CREATE;
- reset writes to disabled after each session;
- disabled-write probes after reset;
- owner manual GnuCash Desktop verification after each session.

## Forbidden operations and claims

Policy v1 forbids:

- PATCH;
- DELETE;
- batch operations;
- unattended mutation;
- dogfood loops;
- release/tag/package/image publication;
- public write beta;
- production, stable, or security-audited claims;
- committing or posting raw private paths, account names, descriptions, memos, amounts, books, backups,
  screenshots, tokens, keys, certs, or `.env` content.

## Backup policy v1

For now, the default safe backup policy remains **route backup before each individual CREATE**.

Do not collapse multiple CREATEs behind one backup in Policy v1. A future per-session backup relaxation may
be considered only after more successful owner-verified CREATE-only sessions and explicit owner approval.
This task does not relax the backup policy.

## Per-CREATE requirements

For each approved CREATE:

1. Verify exact target selection and no concurrent writer/lock.
2. Take route backup before the CREATE.
3. Execute one CREATE only within the approved count.
4. Do not retry by creating another transaction without new owner approval if outcome is uncertain.
5. Read back the created transaction with redacted structural markers only.
6. Capture redacted audit evidence with opaque references only.
7. Stop immediately after first failure or after the approved count is reached.

## Session closeout requirements

After every session:

1. Reset writes to default disabled.
2. Run disabled-write probes for validate/preflight, CREATE, PATCH, and DELETE route families when available.
3. Write a tracked redacted report using target class and opaque refs only.
4. Update #45 with a redacted summary only.
5. Keep runtime/private artifacts outside git.
6. Request owner manual GnuCash Desktop verification and record only a redacted confirmation if completed.

## Recovery and rollback

Stop immediately and preserve backup evidence if backup, CREATE, read-back, audit, reset, disabled probes,
or manual Desktop verification fails. Do not perform a second CREATE, PATCH, DELETE, batch operation, or
manual repair through this app without a new owner/PM recovery approval. Recovery instructions must name
only redacted target classes and opaque backup/audit references in committed or GitHub-posted evidence.

## Future PATCH boundary

PATCH is out of scope for #45. Generated CREATE-only test-copy sessions are sufficiently validated for
CREATE-only on the test copy, but they do not authorize PATCH. PATCH of app-created transactions may be
considered only under [#46 Owner real-book PATCH app-created transaction trial](https://github.com/valentusys/gnucash-web-companion/issues/46)
or a later separate owner/PM issue or approval packet that defines app-created ownership boundaries,
exact editable fields, backup/read-back/audit/rollback policy, manual Desktop verification expectations,
and explicit exclusions for historical/manual transactions, DELETE, and batch operations.

## Evidence policy

Tracked docs and GitHub comments must include only redacted class names, operation counts, pass/fail
markers, structural markers, and opaque references. They must not include raw private paths, account names,
descriptions, memos, amounts, books, backups, screenshots, tokens, keys, certs, or `.env` content.
