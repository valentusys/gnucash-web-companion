# Owner-writebeta operating guide

Use copied/restorable books only after explicit PM authorization, preflight, independent backup,
restore-to-copy plan, state-machine readiness, and redacted evidence. Real working-book mutation
remains blocked until a future exact same-context owner confirmation and PM authorization.

## Current state for #36 and #44

- #36 is closed as `CLOSE_36_AS_MAINTENANCE_BOUNDARY`; this guide is not release approval and not
  mutation authorization.
- #44 is the active owner real-book trial safety-model issue; it is not mutation approval, not release
  approval, and not public write beta approval.
- #43 is closed after routed copied-book dogfood evidence was accepted narrowly.
- W3 copied/restorable CREATE/PATCH/DELETE evidence is accepted narrowly for the recorded staged-copy
  scope only.
- Routed copied/restorable evidence exists for controlled write readiness, but it is not a public write
  beta, not broad GnuCash compatibility, and not a real working-book safety claim.
- `v0.4.0-owner-writebeta` is not published unless a future release gate proves otherwise.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- Enabled write-alpha/writebeta paths remain `APP_ENV=test` gated.
- Real/private/original/working/only-copy books remain blocked as write targets.
- `docs/write-alpha/real-working-book-trial-runbook.md` records the future trial blockers,
  rollback expectations, and owner/PM gates; it does not authorize the trial.

## Owner and PM confirmation checklist before any real working-book trial

A real working-book trial is blocked unless all items below are true in the same execution context:

1. Owner explicitly names the target scope and confirms it is not an original, only-copy, or unbacked
   book.
2. PM explicitly authorizes the exact trial package and mutation count.
3. Desktop is closed for the target book and any app runtime lock/preflight checks pass.
4. An independent restorable backup exists before the trial, with restore steps documented.
5. The trial remains local/test-gated with `APP_ENV=test` and temporary explicit write enablement only.
6. The route preflight, preview, confirmation, audit, backup, read-back, compatibility, reset, and
   disabled-probe evidence is captured in redacted form.
7. No account names, transaction descriptions, memos, amounts, private paths, screenshots, app DBs,
   backups, books, tokens, or `.env` files are committed or posted.

If any item is missing, mark the subtask blocked and continue with non-mutating readiness work.

## Future copied/restorable authorization format

A future copied/restorable dogfood package is allowed only when the owner and PM authorization is in
same execution context as the operation. The authorization must state:

1. copied/restorable target class and outside-git staging location class, without printing a private path;
2. route family and operation counts;
3. backup/read-back/audit/lock/restore/reset expectations;
4. redaction and evidence-publication limits;
5. No original/private/real-working/only-copy book is the target.

If authorization is absent, run non-mutating guards/docs/tests only; #36 stays closed as the maintenance
boundary, and any new real-book trial scope stays under #44.

## Phase 778 addendum

Operating guide refreshed conservatively.

Defaults remain disabled; APP_ENV=test write gate remains; no private/raw evidence or real-book
mutation is authorized.

## Daytime continuation 2026-06-03 addendum

Newly covered safe evidence since the previous daytime checkpoint:

- Synthetic CREATE -> metadata/memo-only PATCH -> DELETE route-family drill:
  routed write-alpha mutations now have regression coverage proving fresh
  owner-writebeta confirmation, write-alpha-owned PATCH/DELETE targets,
  metadata-only PATCH shape, default-disabled reset, and non-owned target
  rejection.
- Synthetic backup/restore drill: post-mutation checks now validate provided
  audit/restore refs as opaque before hard-stop handling, so path-like restore
  evidence cannot enter summaries even on failure.
- Synthetic lock-contention drill: active sessions, expired confirmations,
  reused confirmations, failed-hard-stop stale sessions, and fresh-session-only
  recovery after default-disabled reset are covered by tests.

This does not authorize more copied-book mutation or any real working-book trial. Future copied/restorable
mutation remains blocked unless the owner and PM authorize exact target class, route family, and operation
counts in the same execution context. Real working-book mutation remains forbidden for autonomous runs.

## Repeated backup/restore readiness docs/tests tasks

Generated backup/restore readiness maintenance may update tracked wording, guard assertions, or pytest
assertions only. It must report the conservative docs/tests-only labels when true:
`NOT_RESTORE_DRILL`, `NO_BACKUP_ARTIFACT_CREATED`, `DO_NOT_ENABLE_WRITES`, and
`NO_PRIVATE_DATA_REVIEWED`.

Those labels mean no restore command was run, no restored book was opened, no backup artifact, app DB
record, checksum manifest, runtime log, or private path evidence was created or reviewed, and the work
did not authorize changing `GNUCASH_WRITES_ENABLED=false` or relaxing the `APP_ENV=test` gate. If those
statements cannot be made from tracked docs/tests and guard output alone, the safe result is a checkpoint,
not backup creation, restore execution, dogfood, or private-data inspection.

If a repeated generated task finds the tracked wording and guard assertions already satisfy the boundary,
report an explicit no-change checkpoint. Do not create operational backup/restore evidence, runtime
manifests, or cosmetic edits solely to produce a diff.
