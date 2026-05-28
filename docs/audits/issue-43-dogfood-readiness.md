# Issue #43 dogfood readiness

Goal: decide whether copied-book routed dogfood can run.

Scope reviewed: routed owner-writebeta API, preview/confirmation, active-session mutation guard, verification/reset endpoint, UI warning shell, tests.

Decision: BLOCKED_NEEDS_FIX / BLOCKED_SAFETY.

Reasons:
- Routed foundation is implemented.
- The owner-provided copied/restorable SQL book is now staged outside git on this host.
- Redacted copied-book path-class preflight passed for the staged external copied/disposable target.
- The routed dogfood attempt stopped before mutation because the copied SQL book carries a GnuCash lock marker from the source environment; API data routes fail closed rather than opening it.
- PM operation counts remain locked but must only execute after the copied-book lock gate, preflight, backup, read-back, audit, restore, compatibility, and default-disabled reset gates pass.

Authorized counts if dogfood resumes after the copied-book lock blocker is resolved safely:
- CREATE: 2
- PATCH: 1 metadata/memo-only PATCH on a state-machine/write-alpha-created disposable transaction
- DELETE: 1 DELETE of a state-machine/write-alpha-created disposable transaction

Safety checks:
- Original/working/private/only-copy books remain forbidden.
- No mutation was performed here.
- No private artifact was committed.
- Raw staged path, source path, full checksum, GnuCash lock contents, account names, memos, descriptions, amounts, backup paths, screenshots, exports, app DBs, secrets, and tokens are not recorded in git.

Verification: outside-git staged copy was verified locally; redacted copied-book preflight passed; routed API read failed closed on the copied-book GnuCash lock marker before mutation.

Final verdict: BLOCKED.
