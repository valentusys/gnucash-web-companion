# Issue #43 final evidence audit

Goal: decide whether issue #43 can close.

Evidence reviewed:
- Routed owner-writebeta API added at `/books/{book_id}/owner-writebeta/*`.
- State visibility/preflight/preview/confirmation/verification/reset route tests added.
- Existing write-alpha mutation routes now call an active owner-writebeta guard when a session for the book is armed.
- UI owner-writebeta state-information shell added.
- Targeted backend route-family and existing write-alpha tests passed.
- Public status guard passed.

Dogfood result: PARTIAL_PASS_WITH_EVIDENCE_GAP. A fresh owner-provided copied/restorable SQL book was staged outside git after the owner closed GnuCash on the source host. Redacted preflight passed and the locked PM mutation counts were executed only through the routed owner-writebeta/write-alpha path: 2 CREATE, 1 metadata/memo-only PATCH of a created disposable transaction, and 1 DELETE of a created disposable transaction. Post-run collected evidence shows read-back, 4 route backup refs, 4 successful audit rows, ownership rows for the 2 created transactions, restore verification, piecash compatibility read, and disabled CREATE/PATCH/DELETE probes returning 403. However, the local evidence helper aborted after the DELETE mutation on an audit payload field-name bug before capturing the final owner-writebeta `verify-reset`/`reset-disabled` transition for that DELETE session. No extra mutation was run after the abort.

PM decision: KEEP_ISSUE_43_OPEN_WITH_EXACT_BLOCKERS.

Exact blockers:
1. Fix the local routed dogfood evidence helper so it reads `AuditLog.payload_json` and cannot abort after a successful mutation while collecting evidence.
2. On a new fresh copied/restorable outside-git book, rerun the same PM-locked routed dogfood counts end-to-end and capture final owner-writebeta `verify-reset`/`reset-disabled` evidence after DELETE.
3. Keep #43 open until the uninterrupted end-to-end evidence exists; do not perform additional mutations on the already-mutated copied dogfood target.

Safety checks:
- Do not close #43 until copied-book dogfood passes.
- Do not claim real working-book safety or public write beta.
- Defaults remain write-disabled and APP_ENV=test gated.

Final verdict: KEEP_ISSUE_43_OPEN_WITH_EXACT_BLOCKERS / NO_RELEASE.
