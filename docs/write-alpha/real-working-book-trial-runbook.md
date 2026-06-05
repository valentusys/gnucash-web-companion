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

## R2 approval packet requirements

A future approval request must be self-contained and bounded. It must include all
of these fields before an operator may ask the owner and PM to decide:

1. Trial name and one-sentence purpose.
2. Route family and exact mutation count.
3. Target class stated without private path, account name, amount, memo, or
   transaction description.
4. Statement that the target is not an original, only-copy, unbacked, or
   irreplaceable book.
5. Backup checkpoint and restore-to-copy checkpoint, both described with
   redacted location classes only.
6. Abort conditions for preflight, backup, lock, preview, confirmation, route
   response, audit, read-back, compatibility check, restore proof, reset, and
   disabled probe.
7. Evidence packet shape limited to redacted summaries and pass/fail statuses.
8. Reset command plan that returns writes to default-disabled posture.
9. Explicit non-release statement: no tag, package, image, public write beta,
   production-ready claim, stable claim, security-audited claim, broad
   compatibility claim, or only-copy safety claim.

If the packet omits any field, the only allowed result is blocked. Do not fill in
missing private details from local knowledge or runtime inspection.

## R2 owner and PM gate wording

The owner approval must be explicit, current, and scoped to the exact packet. A
safe approval record may say only that the owner approves the named packet and
confirms the target class is restorable and not original or only-copy. It must
not include private paths, account names, transaction descriptions, memos, or
amounts.

The PM approval must independently approve the same packet, route family,
mutation count, rollback proof, reset proof, and evidence shape. If owner and PM
approvals refer to different packet versions, operation counts, target classes,
or evidence expectations, the trial remains blocked.

Prior acceptance of copied/restorable evidence, issue #36 work, or this runbook
is not approval. Approval must appear in the same execution context as the future
trial package.

## R2 rollback decision tree

A future authorized packet must stop before mutation when preflight, lock,
backup, or preview fails. It must stop after mutation and enter rollback review
when route response, audit, read-back, compatibility, or restore-to-copy proof is
missing or inconsistent. It must stop after reset if the disabled probe does not
prove writes are blocked again.

Rollback review may use only a restored copy or independently prepared backup
copy. It may not overwrite an original, working, private-only, or only-copy book.
Any raw recovery material must stay outside git and outside public reports.

## R3 prerequisite proof matrix

Before any future operator asks for approval, the packet must map every gate to a
safe proof source. The proof source may be a redacted summary, a command name with
exit status, or an owner/PM statement, but it must not include private paths,
account names, transaction descriptions, memos, amounts, screenshots, books,
backups, databases, secrets, or raw logs.

| Gate | Required safe proof | If proof is absent |
| --- | --- | --- |
| Exact packet scope | Packet name, route family, operation shape, and mutation count | Blocked before approval request |
| Target class | Redacted class statement and not-original/not-only-copy confirmation | Blocked before approval request |
| Backup readiness | Independent backup checkpoint and restore-to-copy checkpoint, both redacted | Blocked before runtime arming |
| Writer exclusion | GnuCash Desktop and other writers closed for the target class | Blocked before preflight |
| Test-gated writes | `APP_ENV=test` scoped session and default-disabled reset plan | Blocked before write enablement |
| Rollback path | Decision tree with stop points and no overwrite of source target | Blocked before mutation |
| Evidence hygiene | Redacted evidence packet shape that can pass tracked hygiene | Blocked before reporting |
| Non-release posture | Explicit no-release and no-public-write statement | Blocked before any status claim |

A packet that cannot fill this matrix with safe, non-private proof remains a
planning artifact only. Do not inspect local books or runtime data to complete the
matrix for this issue #36 task.

## R3 blocker response expectations

When a blocker is found, the expected response is conservative and non-mutating:

1. Stop the trial path immediately.
2. Record only the blocker category and the redacted gate name.
3. Do not attempt a workaround by broadening scope, changing defaults, enabling
   writes outside `APP_ENV=test`, or substituting copied-book evidence for a real
   working-book approval.
4. Leave runtime state default-disabled or reset it before any status report.
5. Continue only with docs, guard checks, tests, or a new approval packet draft.

A blocker is not a partial authorization. Reaching any blocker does not permit
opening, copying, inspecting, or mutating a real/private/original/working/only-copy
book.

## R3 future operator checklist

A future authorized operator should be able to answer yes to all questions below
before the first mutation. If any answer is no or unknown, the trial remains
blocked:

- Are the owner and PM approvals current, explicit, same-context, and tied to the
  same packet version?
- Is the approved mutation count exact and narrow?
- Is the target class restorable, not original, and not only-copy?
- Are Desktop and other writers closed before preflight?
- Does the session preserve default-disabled writes outside the temporary
  `APP_ENV=test` window?
- Is rollback based on a backup/restored copy rather than overwriting the source
  target?
- Can all tracked reports omit private data and still state pass/fail results?
- Does the report explicitly avoid release, public write beta, production-ready,
  stable, security-audited, broad compatibility, and only-copy safety claims?

For the current issue #36 task, these questions are documentation gates only and
must not be used to run a trial.

## Stop result for the current task

For issue #36, this runbook records that a real working-book trial remains
blocked and is not authorized. The only allowed current work is non-mutating
maintenance such as documentation, guard checks, and conservative handoff notes.
