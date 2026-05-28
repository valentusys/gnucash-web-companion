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

Second attempt result: PARTIAL_PASS_WITH_EVIDENCE_GAP.

Safe redacted evidence:
- A fresh owner copy was staged outside the git working tree after the owner closed GnuCash on the source host.
- Redacted owner-write session preflight passed: external copied/restorable target class, external backup class, default write-disabled posture intact, `APP_ENV=test` gate intact, restore helper available, and no desktop lock-file hint.
- Routed owner-writebeta preflight/preview/confirmation was exercised before each mutation request.
- Mutation requests were sent only through the existing write-alpha routes with matching owner-writebeta preview hash and confirmation token headers.
- Post-run collected evidence shows route backups, read-back, audit, restore, compatibility, and default-disabled probes passed.
- Evidence collection has one gap: after the DELETE mutation succeeded, the local evidence helper aborted on an audit payload field-name bug before it captured the final owner-writebeta `verify-reset`/`reset-disabled` transition for that DELETE session. No extra mutation was run after that abort.

Mutation counts:
- CREATE: 2 succeeded
- PATCH: 1 metadata/memo-only PATCH succeeded on a write-alpha/state-machine-created disposable transaction
- DELETE: 1 succeeded on a write-alpha/state-machine-created disposable transaction

Safety checks:
- Original/working/private/only-copy book remained untouched.
- Only the staged outside-git copied/restorable book was mutated.
- No other book was opened for mutation.
- No raw path, checksum, account name, memo, description, amount, backup filename, screenshot, export, app DB, secret, or token is committed here.
- Historical/manual transaction mutation remained blocked by ownership validation; PATCH/DELETE targeted only state-machine/write-alpha-created disposable transaction refs.

Verification:
- Outside-git staged copy existence, size, and local/source checksum match were verified privately before mutation; raw values are not committed.
- Redacted non-mutating preflight passed.
- Read-back verified one created/patched disposable transaction remains present and the deleted disposable transaction is absent.
- Route backup evidence count: 4 backup refs for 4 successful mutations.
- Audit evidence count: 4 successful audit rows (`transaction.create`: 2, `transaction.patch`: 1, `transaction.delete`: 1).
- Restore verification from the pre-batch backup passed by checksum and piecash read-back.
- Compatibility check: piecash read-only open on the mutated copy passed.
- Default-disabled reset probe passed: CREATE/PATCH/DELETE route probes returned 403 with writes disabled.
- Final DELETE owner-writebeta verify/reset transition was not captured because of the local evidence-helper bug described above.

Expected artifacts:
- This redacted dogfood record.
- Updated issue #43 blocker comment.

Final verdict: DOGFOOD_MUTATIONS_PASSED_BUT_FINAL_RESET_EVIDENCE_GAP / KEEP_ISSUE_43_OPEN.
