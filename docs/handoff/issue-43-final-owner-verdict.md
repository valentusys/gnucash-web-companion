# Issue #43 final owner verdict

Last phase: Phase M.

Issue #43 status: kept open. Do not close until copied-book routed dogfood passes.

Dogfood result: attempted and blocked before mutation. The owner copy is staged outside git, but the copied SQL book has a GnuCash lock marker from the source environment, so routed API data access failed closed before any CREATE/PATCH/DELETE mutation.

Release result: NO_RELEASE. No tag or GitHub release was published.

Mutation counts in this run:
- CREATE: 0
- PATCH: 0
- DELETE: 0

What changed safely:
- Routed owner-writebeta backend endpoints now expose redacted preflight/status, preview, confirmation, verification/reset, and disabled-reset state.
- Existing write-alpha mutation routes now fail closed when an owner-writebeta session for that book is armed and the request does not supply the matching preview/token pair.
- UI has a conservative owner-writebeta state-machine information page with owner-only/copied-book warnings.

Checks:
- Targeted API tests passed.
- Existing write-alpha transaction route tests passed.
- Public status guard passed.
- Full final verification recorded in Phase M handoff.

Owner action required to continue #43:
Provide a fresh copied/restorable SQL book made after closing GnuCash on the source PC, or let PM define an explicit safe copied-book stale-lock release procedure. Then rerun the locked routed dogfood counts. Do not provide or use the original/working/private/only-copy book.
