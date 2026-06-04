# Real working-book trial runbook - blocked until owner gate

Date: 2026-06-05

This runbook is a blocker checklist for a possible future real working-book trial.
It does not authorize that trial, does not authorize dogfood, and does not
permit opening, copying, inspecting, or mutating any real, private, original,
working, or only-copy GnuCash book.

Current repository posture remains unchanged:

- `GNUCASH_WRITES_ENABLED=false` is the committed/default write posture.
- Enabled write routes remain `APP_ENV=test` gated.
- Real/private/original/working/only-copy books remain blocked write targets.
- No release, tag, package, image, public write beta, production-ready claim,
  stable claim, security-audited claim, broad compatibility claim, or only-copy
  safety claim is made here.

## Authorization boundary

A real working-book trial may not start from this document. It is blocked until
all gates below are satisfied in the same execution context as the future trial:

1. Owner explicitly approves a real working-book trial and names the exact target
   class without exposing a private path, account name, amount, memo, or
   transaction description in tracked files.
2. PM explicitly approves the exact route family, operation shape, mutation
   counts, abort conditions, evidence shape, and rollback proof required for that
   single trial package.
3. The target is not an original, unbacked, only-copy, or otherwise
   irreplaceable book.
4. GnuCash Desktop and any other writer are confirmed closed for the target
   before the app runtime can be armed.
5. The future operator accepts that a successful trial would be narrow evidence
   for that one local owner-controlled case only.

Missing any item is a hard blocker. The correct action is to stop the trial path
and continue only with non-mutating docs, guards, tests, or planning.

## Prerequisites before any future approval request

Before asking for an approval decision, prepare only non-private facts:

- A short scope statement listing the planned route family and exact operation
  count.
- A redaction plan that forbids tracked or posted private paths, account names,
  transaction descriptions, memos, amounts, screenshots, books, backups, app DBs,
  `.env` files, tokens, keys, certs, and raw evidence.
- A backup/restore plan that describes where independent backups and restore
  checks will happen without printing private paths in tracked docs.
- A rollback decision tree with stop conditions before, during, and after the
  route call.
- A confirmation that writes remain default-disabled and that any temporary
  enabled-write session is `APP_ENV=test` scoped.
- A verification list that includes route preflight, preview, explicit
  confirmation, audit trail, read-back, compatibility check where available,
  restore-to-copy proof, disabled reset, and post-reset disabled probe.

These prerequisites are documentation inputs only. They are not permission to
open, copy, inspect, or mutate a book.

## Hard blockers

Do not proceed if any blocker is present:

- Owner and PM approval are not both present in the future execution context.
- The target might be original, only-copy, unbacked, private-only, inside git, or
  otherwise not independently restorable.
- The operator cannot prove a pre-trial independent backup and a restore-to-copy
  check without exposing raw private evidence.
- GnuCash Desktop or another writer may have the target open.
- `GNUCASH_WRITES_ENABLED=false` would be weakened in defaults or rendered
  Compose.
- Enabled writes would run outside `APP_ENV=test`.
- The route family or mutation count is broader than the approved package.
- Evidence would require committing or posting private data, raw books, app DBs,
  backups, exports, screenshots, secrets, or private paths.
- A release, public write beta, production-ready, stable, security-audited,
  broad compatibility, or only-copy safety claim would be implied.

## Rollback expectations for a future authorized trial

Rollback must be designed before any mutation is attempted. A future approved
trial package must define:

1. Pre-trial state capture using redacted identifiers only.
2. Independent backup creation before the first route mutation.
3. Restore-to-copy procedure that never restores over the source target.
4. Abort-on-failure behavior for preflight, backup, lock, preview,
   confirmation, route response, audit write, read-back, compatibility check,
   restore proof, reset, and disabled probe.
5. Post-trial reset that returns the runtime to disabled writes.
6. A disabled-probe check proving no further write can route after reset.
7. A rollback owner decision point if read-back, audit, compatibility, or restore
   evidence disagrees with the expected result.

No rollback step may rely on overwriting an original or only-copy book. Any
rollback evidence committed to git must be redacted and synthetic enough to pass
tracked-hygiene checks.

## Evidence allowed in tracked docs

Allowed tracked evidence after a future approved trial is limited to conservative
summaries:

- command names and exit status;
- route family and approved operation count;
- redacted opaque IDs that are not account names, descriptions, memos, amounts,
  private paths, or raw book data;
- backup, restore, read-back, audit, reset, and disabled-probe pass/fail status;
- explicit statement that no release or public write beta was published.

Forbidden tracked evidence includes books, SQLite databases, app databases,
backups, exports, screenshots, `.env`, tokens, keys, certs, account names,
transaction descriptions, memos, amounts, private paths, and raw private logs.

## Stop result for the current task

For issue #36, this runbook records that a real working-book trial remains
blocked and is not authorized. The only allowed current work is non-mutating
maintenance such as documentation, guard checks, and conservative handoff notes.
