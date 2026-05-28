# Issue #43 final evidence audit

Goal: decide whether issue #43 can close.

Evidence reviewed:
- Routed owner-writebeta API added at `/books/{book_id}/owner-writebeta/*`.
- State visibility/preflight/preview/confirmation/verification/reset route tests added.
- Existing write-alpha mutation routes now call an active owner-writebeta guard when a session for the book is armed.
- UI owner-writebeta state-information shell added.
- Targeted backend route-family and existing write-alpha tests passed.
- Public status guard passed.

Dogfood result: NOT RUN. No copied-book mutation occurred.

PM decision: KEEP_ISSUE_43_OPEN_WITH_EXACT_BLOCKERS.

Exact blockers:
1. Stage an owner-provided outside-git copied/restorable book on this host.
2. Run the locked routed dogfood counts: 2 CREATE, 1 metadata/memo-only PATCH, 1 DELETE of a created disposable transaction.
3. Record redacted backup/read-back/audit/lock/restore/compatibility/default-reset evidence.
4. Add final verification that routed mutation sessions complete/reset after dogfood.

Safety checks:
- Do not close #43 until copied-book dogfood passes.
- Do not claim real working-book safety or public write beta.
- Defaults remain write-disabled and APP_ENV=test gated.

Final verdict: KEEP_ISSUE_43_OPEN_WITH_EXACT_BLOCKERS.
