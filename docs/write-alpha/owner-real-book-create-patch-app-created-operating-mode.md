# Owner real-book CREATE + PATCH app-created metadata-only operating mode

Issue: [#47 Owner real-book CREATE + PATCH app-created metadata-only operating mode](https://github.com/valentusys/gnucash-web-companion/issues/47)
Status: **operating-mode boundary documented**. This document does not authorize mutation by itself.

## Evidence basis

This boundary is based on owner-verified test-copy evidence only:

- #45 generated CREATE-only test-copy sessions succeeded and were owner-verified.
- #46 PATCH app-created metadata-only trials succeeded and were owner-verified:
  - first PATCH trial: 5 / 5;
  - expanded PATCH trial: 20 / 20.

This evidence is not a public write beta, release, stable, production-ready, or security-audited claim.

## Scope

Future sessions under #47 may include only:

- owner-only sessions;
- test copy / owner-selected real-book target only;
- CREATE as bounded individual operations;
- PATCH only for app-created transactions;
- PATCH scope only description/memo metadata-only;
- explicit same-context owner/PM approval before every session.

## Required per-session approval

Before any CREATE + PATCH app-created metadata-only session, the owner/PM approval must state:

1. exact target class for redacted reporting;
2. exact CREATE count;
3. exact PATCH count;
4. exact app-created identity boundary before PATCH;
5. backup policy, defaulting to backup before each CREATE/PATCH unless explicitly approved otherwise;
6. read-back after each CREATE/PATCH;
7. redacted audit evidence;
8. default-disabled reset after the session;
9. disabled-write probes after reset;
10. Syncthing conflict-copy check before/after if target is under Syncthing;
11. manual GnuCash Desktop verification for early mixed sessions;
12. redacted-only GitHub/tracked reporting.

Absent fresh same-context approval, `GNUCASH_WRITES_ENABLED=false` remains the default and no mutation is authorized.

## PATCH identity and invariant requirements

Before every PATCH:

- app-created identity must be proven exactly;
- the target must not be historical/manual;
- the transaction must be within the approved app-created identity boundary;
- the PATCH payload must be description/memo metadata-only.

After every PATCH, read-back must verify:

- metadata changed as requested;
- amount unchanged;
- account unchanged;
- split structure unchanged;
- date unchanged;
- currency unchanged;
- no balance-affecting field changed.

## Forbidden operations and claims

#47 forbids:

- amount changes;
- account changes;
- split changes;
- date changes;
- currency changes;
- balance-affecting changes;
- historical/manual transaction mutation;
- DELETE;
- batch operations;
- unattended mutation;
- dogfood loops;
- release/tag/package/image publication;
- public write beta;
- production, stable, or security-audited claims;
- committing or posting raw private paths, account names, descriptions, memos, amounts, GUIDs, books,
  backups, screenshots, tokens, keys, certs, or `.env` content.

## Backup, read-back, audit, and reset

Default policy remains backup before each individual CREATE/PATCH unless a safer per-session backup policy
is explicitly approved in the same-context owner/PM approval.

For each CREATE/PATCH:

1. Verify exact target selection and no concurrent writer/lock.
2. Take the approved backup.
3. Execute one individual operation only.
4. Read back the result.
5. Verify operation-specific invariants.
6. Capture redacted audit evidence with opaque refs only.
7. Stop after first failure or after approved counts are reached.

After every session:

1. Reset writes to default disabled.
2. Run disabled-write probes for validate/preflight, CREATE, PATCH, and DELETE route families when available.
3. Check Syncthing conflict-copy state after the session when applicable.
4. Write tracked redacted evidence only.
5. Request owner manual Desktop verification for early mixed sessions.

## Private Telegram verification lists

Private owner verification lists must have correct human-readable columns and must not swap Date, GUID,
Description, or Amounts. Use structured evidence to generate the table when possible.

For CREATE/PATCH sessions, include only in private Telegram context when needed:

- number;
- date;
- transaction GUID;
- selected debit/credit accounts;
- description before/after for PATCH;
- memo before/after if changed;
- amounts.

GitHub/tracked reports remain redacted-only and must not contain those private details.

## Relationship to #45 and #46

#45 remains the CREATE-only evidence/tracker boundary. #46 remains PATCH app-created metadata-only evidence.
#47 is the next boundary for considering future bounded mixed CREATE plus PATCH app-created metadata-only
sessions. #47 is not mutation approval by itself.
