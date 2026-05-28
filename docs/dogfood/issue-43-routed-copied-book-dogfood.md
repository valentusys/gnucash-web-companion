# Issue #43 routed copied-book dogfood

Goal: run the owner-writebeta routed state-machine dogfood on the owner-provided copied/restorable SQL book.

Scope:
- Only the staged outside-git copied/restorable book was considered.
- Locked PM operation counts remained: 2 CREATE, 1 metadata/memo-only PATCH on a state-machine/write-alpha-created transaction, 1 DELETE of a state-machine/write-alpha-created transaction.
- No other book was opened or mutated.

Non-goals:
- No original/working/private/only-copy mutation.
- No public write beta.
- No release publication.

Attempt result: BLOCKED_SAFETY before mutation.

Safe redacted evidence:
- Owner copy is now staged outside the git working tree.
- Redacted copied-book preflight classified the target as an external copied/disposable SQL book and the intended runtime/backup classes as ignored local dogfood storage.
- The first routed read/preflight setup attempt failed closed before any mutation because the copied SQL book carries a GnuCash lock marker from the source environment.
- The API returned a safe read failure instead of exposing raw storage details.
- No CREATE/PATCH/DELETE request was executed.
- No backup/audit/read-back/restore/default-reset mutation evidence exists because mutation was not reached.

Mutation counts:
- CREATE: 0
- PATCH: 0
- DELETE: 0

Safety checks:
- Original/working/private/only-copy book remained untouched.
- Staged copied book was not mutated.
- No raw path, checksum, account name, memo, description, amount, backup filename, screenshot, export, app DB, secret, or token is committed here.
- Because the lock gate did not pass, the dogfood run stopped immediately.

Verification:
- Outside-git staged copy existence was verified locally.
- Redacted dogfood plan preflight returned ready for copied/disposable path class.
- Runtime routed API read failed closed on the copied-book GnuCash lock marker before mutation.
- Disabled write probe was prepared but not used for mutation because the lock/read gate blocked first.

Expected artifacts:
- This redacted dogfood record.
- Updated issue #43 blocker comment.

Final verdict: BLOCKED_SAFETY / NO_MUTATION.
