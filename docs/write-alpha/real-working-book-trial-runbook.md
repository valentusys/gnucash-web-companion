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

## R4 future trial pre-authorization runbook

A future operator must treat the trial as blocked until a separate approval packet
passes every gate. The safe pre-authorization runbook is:

1. Identify the packet version, route family, operation shape, and exact mutation
   count using only redacted labels.
2. Fill the prerequisite proof matrix with safe proof sources. Leave any unknown
   field blank rather than inspecting private books, paths, screenshots, logs, or
   runtime databases.
3. Check that the packet states writes remain default-disabled outside a temporary
   `APP_ENV=test` session and that the reset plan returns to that posture.
4. Check that the rollback plan restores only to a copy and never overwrites an
   original, working, private-only, or only-copy book.
5. Check that the evidence packet can report pass/fail results without account
   names, transaction descriptions, memos, amounts, private paths, screenshots,
   raw logs, books, app DBs, backups, exports, `.env`, tokens, keys, or certs.
6. Check that the report wording does not imply a release, public write beta,
   stable state, production readiness, security audit, broad compatibility, or
   only-copy safety.
7. Request owner and PM approval only after the packet is complete. If approval is
   absent, stale, mismatched, or broader/narrower than the packet, stop.

This pre-authorization runbook is non-mutating. It does not allow opening,
copying, inspecting, or changing a real, private, original, working, or only-copy
book.

## R4 approval freshness and mismatch rules

Approval is valid only when owner and PM approvals are current, explicit, and
attached to the same packet version in the same execution context as the future
trial. The trial remains blocked if:

- owner approval and PM approval name different packet versions;
- either approval omits the route family, operation shape, mutation count,
  rollback proof, reset proof, or evidence shape;
- either approval introduces private details that cannot be stored safely;
- either approval asks for a broader target class or operation count than the
  packet describes;
- approval was inherited from copied-book evidence, previous issue #36 reports,
  this runbook, or any earlier phase.

When approvals mismatch, do not merge assumptions. Record only the mismatch
category in a redacted handoff and continue with non-mutating documentation or
checks.

## R4 minimum rollback proof expectations

A future approved packet must define rollback proof before runtime arming. Minimum
acceptable proof is a redacted pass/fail summary for:

- pre-mutation independent backup checkpoint;
- restore-to-copy checkpoint that does not overwrite the source target;
- route response and audit trail consistency;
- read-back consistency with the approved operation count;
- compatibility check result when available for the target class;
- post-trial reset to default-disabled writes;
- disabled probe proving writes are blocked after reset.

If any proof is unavailable or inconsistent, the expected result is blocked or
rollback-review, not success. A future report may summarize the failed gate but
must not commit raw private evidence.

## R5 same-context approval gate checklist

A future operator must not treat a prepared packet, prior issue #36 evidence, or
this runbook as approval. Before any future real working-book trial can even be
armed, the same execution context must contain a complete approval checkpoint:

1. Packet version, route family, operation shape, and exact mutation count match
   across the packet, owner approval, PM approval, rollback plan, and evidence
   plan.
2. Owner approval is current, explicit, limited to that packet, and states only a
   redacted target class that is restorable and not original or only-copy.
3. PM approval is current, explicit, limited to that packet, and approves the
   route family, mutation count, abort conditions, rollback proof, reset proof,
   and evidence shape.
4. Approval text contains no private paths, account names, transaction
   descriptions, memos, amounts, screenshots, raw logs, books, app DBs, backups,
   exports, `.env`, tokens, keys, or certs.
5. Approval text does not authorize release publication, a public write beta,
   stable status, production readiness, security-audited status, broad
   compatibility, or only-copy safety.

If any checklist item is missing, stale, contradictory, broader than the packet,
or dependent on private evidence, the only valid status is blocked. Do not repair
that status by inspecting local books, copying a private book, running dogfood, or
enabling writes.

## R5 blocker and rollback stop table

The future trial packet must predeclare what happens at each stop point. The
minimum conservative table is:

| Stop point | Required status when it fails | Allowed follow-up |
| --- | --- | --- |
| Approval checkpoint | Blocked before runtime arming | Redacted packet revision only |
| Target restorable/not-only-copy proof | Blocked before backup | Owner/PM clarification only |
| Independent backup checkpoint | Blocked before lock or preview | Backup plan correction only |
| Writer-closed confirmation | Blocked before preflight | Close writers and re-check only |
| `APP_ENV=test` and default-disabled reset plan | Blocked before write enablement | Config correction only |
| Preview or explicit confirmation | Blocked before mutation | Packet revision only |
| Route response, audit, or read-back mismatch | Rollback review | Use restored copy; do not overwrite source |
| Restore-to-copy proof mismatch | Rollback review | Owner/PM decision with redacted evidence only |
| Reset or disabled probe failure | Blocked after reset attempt | Keep reporting blocked until writes are disabled |

A rollback-review result is not success and is not release evidence. It may be
reported only as a redacted pass/fail gate result.

## R5 non-authorizing dry-run review path

The only safe activity this issue #36 runbook authorizes is a non-mutating review
of a future packet's shape. That review may check whether the packet contains the
required fields, whether wording preserves `GNUCASH_WRITES_ENABLED=false`, whether
enabled writes are still `APP_ENV=test` scoped, and whether the evidence plan can
pass tracked-hygiene rules. It must not open, copy, inspect, or mutate a real,
private, original, working, or only-copy book.

## R6 authorization expiry and revalidation rules

A future approval packet expires immediately when any safety-relevant input
changes. The trial must return to blocked status and require a fresh owner/PM
checkpoint when any of these changes occur:

- packet version, route family, operation shape, or mutation count changes;
- target class, backup plan, restore-to-copy plan, or writer-closed proof changes;
- runtime configuration, Compose rendering, default write posture, or `APP_ENV`
  gate behavior changes;
- evidence shape would newly require private paths, account names, transaction
  descriptions, memos, amounts, screenshots, books, app DBs, backups, exports,
  raw logs, `.env`, tokens, keys, or certs;
- a previous run reached rollback review, reset failure, disabled-probe failure,
  or any other blocked stop point.

Expired approval cannot be revived by referring to this runbook, prior issue #36
reports, copied-book evidence, or local/private knowledge. Revalidation is a new
non-mutating approval review until the owner and PM both approve the exact updated
packet in the same future execution context.

## R6 interruption and resume expectations

A future operator must predefine what happens if the session is interrupted before
or after a mutation. Minimum expectations:

1. If interrupted before write enablement, leave the trial blocked and resume only
   at packet review.
2. If interrupted after temporary write enablement but before mutation, reset to
   default-disabled writes before reporting.
3. If interrupted after mutation, resume only to collect redacted pass/fail status
   for audit, read-back, restore-to-copy, reset, and disabled probe. Do not run a
   new mutation to compensate.
4. If the reset or disabled probe cannot be verified, report blocked and do not
   claim recovery, readiness, release status, or public write beta status.
5. Any resume report must omit raw private evidence and must not inspect local
   books or runtime data unless the future owner/PM packet explicitly authorizes
   that exact non-public, non-tracked evidence handling.

For the current issue #36 task, these are documentation-only expectations. They
are not permission to open, copy, inspect, or mutate a real/private/original/
working/only-copy book.

## R7 prerequisite custody checklist

Before a future real working-book trial can request approval, the operator must
separate custody of each prerequisite from the tracked repository. The approval
packet may record only redacted pass/fail summaries for these prerequisites:

1. Target custody: the target class is owner-controlled, restorable, not original,
   not only-copy, and not inside the repository or an ignored runtime artifact that
   could be accidentally committed.
2. Backup custody: an independent backup exists before arming writes, and restore
   is proven only against a copy that is safe to discard.
3. Runtime custody: the temporary write-enabled runtime is isolated to
   `APP_ENV=test`, has an explicit reset step, and cannot change committed
   defaults or rendered Compose to write-enabled.
4. Evidence custody: raw logs, screenshots, books, backups, app DBs, exports,
   `.env` files, tokens, keys, certs, private paths, account names, transaction
   descriptions, memos, and amounts remain outside git and outside public status
   reports.
5. Decision custody: owner and PM approvals are recorded as same-context,
   same-packet decisions without private details.

If custody for any prerequisite is unclear, the future packet remains blocked.
Do not inspect private books or local runtime data to repair the packet for this
issue #36 documentation task.

## R7 no-trial dry review checklist

A safe dry review of a future packet may only answer these questions from the
packet text and conservative guard output:

- Does the packet name one route family, one operation shape, and an exact
  mutation count?
- Does it keep `GNUCASH_WRITES_ENABLED=false` as the default and preserve
  `APP_ENV=test` as the only enabled-write gate?
- Does it define backup, restore-to-copy, reset, and disabled-probe checkpoints
  before any mutation could run?
- Does it state that missing, stale, mismatched, or broader approvals leave the
  trial blocked?
- Does it forbid release publication, public write beta wording, stable status,
  production-ready status, security-audited status, broad compatibility claims,
  and only-copy safety claims?
- Can the final report be written with command names, exit statuses, approved
  operation count, redacted IDs, and pass/fail results only?

A dry review that answers no or unknown to any item must stop as blocked. The
review must not open, copy, inspect, or mutate a real/private/original/working/
only-copy book, and it must not run product dogfood.

## R7 rollback communication requirements

A future approved packet must define how rollback status is communicated before
runtime arming. The minimum communication contract is:

1. Report `blocked before mutation` when approval, target custody, writer closure,
   backup, lock, preview, or confirmation fails.
2. Report `rollback review` when route response, audit trail, read-back,
   compatibility check, or restore-to-copy proof is missing or inconsistent after
   a mutation.
3. Report `blocked after reset attempt` when the reset command or disabled probe
   cannot prove writes are disabled again.
4. Never report success, readiness, release status, public write beta status, or
   only-copy safety when any rollback checkpoint is missing, private-only, or
   inconsistent.
5. Keep all rollback communication redacted enough to pass tracked-hygiene and
   public-status guards.

Rollback communication is status reporting only. It does not authorize another
mutation, a compensating write, or restoration over an original or only-copy book.

## R8 pre-mutation stop/go register

A future approval packet must include a stop/go register before any runtime
arming. The register is a decision aid, not authorization by itself. It must use
only redacted labels and pass/fail statuses:

| Register item | Required entry | Unsafe entry that blocks |
| --- | --- | --- |
| Packet identity | Packet version and one route family | Multiple route families or inherited scope |
| Mutation budget | Exact operation count and shape | Open-ended count or broad dogfood wording |
| Target class | Restorable, not original, not only-copy | Private path, account name, or only-copy hint |
| Backup checkpoint | Independent backup plus restore-to-copy proof | Backup-only claim without restore proof |
| Writer exclusion | Desktop and other writers closed | Unknown writer state |
| Runtime gate | Temporary `APP_ENV=test` session and reset plan | Default write enablement or non-test writes |
| Evidence shape | Redacted pass/fail summary only | Raw logs, screenshots, books, DBs, paths, or amounts |
| Release posture | Explicit no-release and no-public-write statement | Readiness, stable, production, or public beta wording |

Any unsafe or missing entry makes the future trial blocked before mutation. Do not
repair the register by opening, copying, inspecting, or mutating a real/private/
original/working/only-copy book.

## R8 owner approval wording constraints

A future owner approval may be accepted only if it is narrow and same-context. It
may approve the named packet, exact route family, operation count, target class,
rollback proof, reset proof, and redacted evidence shape. It must not include or
request private paths, account names, transaction descriptions, memos, amounts,
screenshots, raw logs, books, app DBs, backups, exports, `.env`, tokens, keys, or
certs.

Unsafe approval wording blocks the trial even when the intent sounds positive.
Examples of unsafe wording include approval to use the only copy, approval to
"just try dogfood", approval to broaden operation counts during the run, or any
approval that implies a public write beta, release, stable state, production
readiness, security audit, broad compatibility, or only-copy safety.

## R8 rollback evidence minimum

After any future same-context authorized mutation, the minimum rollback evidence
for review is a redacted pass/fail row for each item below:

1. Pre-write independent backup existed before mutation.
2. Route response matched the approved operation count and route family.
3. Audit entry was written with non-sensitive metadata only.
4. Read-back used read-only app routes and matched the expected narrow result.
5. Restore-to-copy proof succeeded without overwriting the source target.
6. Runtime reset returned writes to disabled posture.
7. Disabled probe proved the write route was blocked after reset.

Missing or inconsistent rollback evidence means `rollback review` or blocked
status, not success. It does not authorize a compensating write, another trial, a
release, or a public write beta claim.

## R9 future approval-to-runtime gate sequence

A future same-context approval packet must keep approval review separate from
runtime arming. Passing a documentation review is not permission to arm writes.
The minimum sequence is:

1. Complete the approval packet using only redacted target-class labels and
   pass/fail proof sources.
2. Obtain owner and PM approval for the same packet version, route family,
   operation shape, exact mutation count, rollback proof, reset proof, and
   evidence shape.
3. Re-check that the packet still preserves `GNUCASH_WRITES_ENABLED=false` in
   committed defaults and rendered Compose, and that any temporary enabled-write
   runtime remains `APP_ENV=test` scoped.
4. Re-check blockers immediately before arming writes: target not original or
   only-copy, independent backup and restore-to-copy proof available, Desktop and
   other writers closed, and evidence still redacted.
5. Arm only the approved temporary test-scoped runtime, perform only the approved
   operation count, then reset to disabled writes and run the disabled probe.

If any step is absent, stale, mismatched, broader than the packet, or requires
private tracked evidence, the future status is blocked before mutation. Do not
continue by relying on prior copied-book evidence, this runbook, or local/private
knowledge.

## R9 approval revocation and post-reset blockers

A future trial must treat approval as revoked and return to blocked status when:

- the owner or PM changes, narrows, broadens, or withdraws approval;
- the route family, operation count, target class, backup plan, restore plan,
  writer state, runtime gate, evidence shape, or reset plan changes;
- reset cannot be performed or the disabled probe does not prove write routes are
  blocked again;
- any report would need private paths, account names, transaction descriptions,
  memos, amounts, screenshots, books, app DBs, backups, exports, raw logs,
  `.env`, tokens, keys, or certs.

Revoked, expired, or post-reset-blocked approval is not a partial success. It does
not authorize a compensating mutation, a second trial, a release, a public write
beta, stable wording, production-ready wording, security-audited wording, broad
compatibility wording, or only-copy safety wording.

## R10 future blocker ledger and rollback owner acknowledgement

A future real working-book packet must include a blocker ledger before approval is
requested. The ledger is documentation only until the owner and PM approve the
same packet in the future execution context. It must record only redacted
pass/fail values for:

1. Approval identity: packet version, route family, operation shape, and exact
   mutation count match across owner approval, PM approval, rollback plan, and
   evidence plan.
2. Target safety: the target class is owner-controlled, restorable, not original,
   not only-copy, not inside git, and not represented by a private path in tracked
   files.
3. Runtime safety: committed defaults and rendered Compose preserve
   `GNUCASH_WRITES_ENABLED=false`, and temporary write enablement is limited to
   `APP_ENV=test`.
4. Rollback readiness: independent backup, restore-to-copy, reset, and disabled
   probe steps are defined before arming writes.
5. Evidence hygiene: reports can be written without books, SQLite DBs, app DBs,
   backups, exports, screenshots, raw logs, `.env`, tokens, keys, certs, private
   paths, account names, transaction descriptions, memos, or amounts.
6. Non-release posture: the packet does not imply release publication, public
   write beta, stable status, production readiness, security-audited status,
   broad compatibility, or only-copy safety.

If any ledger row is missing, stale, contradictory, or requires private evidence,
the future trial remains blocked before mutation. The operator must not repair the
ledger by opening, copying, inspecting, or mutating a real/private/original/
working/only-copy book.

Before any future mutation, the owner acknowledgement must explicitly accept the
rollback expectations for the same packet: a failed route response, audit,
read-back, compatibility check, restore-to-copy proof, reset, or disabled probe
means `rollback review` or blocked status, not success. That acknowledgement does
not authorize overwriting an original or only-copy book, running a compensating
mutation, publishing a release, or claiming public write beta readiness.

## Stop result for the current task

For issue #36, this runbook records that a real working-book trial remains
blocked and is not authorized. The only allowed current work is non-mutating
maintenance such as documentation, guard checks, and conservative handoff notes.
