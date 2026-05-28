# Issue #43 final owner verdict

Last phase: Phase M.

Issue #43 status: kept open. Do not close until copied-book routed dogfood has uninterrupted end-to-end state-machine evidence.

Dogfood result: partial pass with an evidence gap. A fresh copied/restorable SQL book was staged outside git, preflight passed, and the PM-locked routed mutation counts executed. Post-run safety evidence passed for read-back, 4 route backups, 4 successful audit rows, restore verification, piecash compatibility read, and disabled CREATE/PATCH/DELETE probes. The final DELETE owner-writebeta verify/reset transition was not captured because the local evidence helper aborted after successful DELETE on an audit payload field-name bug.

Release result: NO_RELEASE. No tag or GitHub release was published.

Mutation counts in this run:
- CREATE: 2 succeeded
- PATCH: 1 metadata/memo-only PATCH succeeded
- DELETE: 1 succeeded

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
After the evidence helper is fixed, provide a new fresh copied/restorable SQL book made after closing GnuCash on the source PC. Then rerun the same locked routed dogfood counts end-to-end and capture final DELETE verify/reset evidence. Do not reuse the already-mutated dogfood target for extra mutations; do not provide or use the original/working/private/only-copy book.
