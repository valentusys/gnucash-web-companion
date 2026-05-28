# Issue #43 dogfood readiness

Goal: decide whether copied-book routed dogfood can run.

Scope reviewed: routed owner-writebeta API, preview/confirmation, active-session mutation guard, verification/reset endpoint, UI warning shell, tests.

Decision: BLOCKED_NEEDS_FIX / BLOCKED_MISSING_OWNER_COPY.

Reasons:
- Routed foundation is implemented, but copied-book dogfood was not run in this session.
- Local direct source path for the owner-provided copied-book location was not available on this Linux host.
- Full routed dogfood would require an outside-git copied/restorable book staged on this host plus a disposable run environment.
- PM operation counts are locked but must only execute after all preflight/backup/restore/redaction gates pass.

Authorized counts if dogfood resumes after owner copy is staged:
- CREATE: 2
- PATCH: 1 metadata/memo-only PATCH on a state-machine/write-alpha-created disposable transaction
- DELETE: 1 DELETE of a state-machine/write-alpha-created disposable transaction

Safety checks:
- Original/working/private/only-copy books remain forbidden.
- No mutation was performed here.
- No private artifact was committed.

Verification: local check for a mounted copied-book source returned unavailable; targeted backend tests passed.

Final verdict: BLOCKED.
