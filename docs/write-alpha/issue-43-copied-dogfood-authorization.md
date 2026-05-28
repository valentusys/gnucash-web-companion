# Issue #43 copied-dogfood authorization

PM authorization status: CONDITIONAL_ONLY / BLOCKED_SAFETY.

Exact operation counts are locked for a future copied-book dogfood attempt:
- 2 CREATE
- 1 metadata/memo-only PATCH on a routed state-machine/write-alpha-created disposable transaction
- 1 DELETE of a routed state-machine/write-alpha-created disposable transaction

Conditions before any mutation:
1. Owner-provided copied/restorable GnuCash SQL book is staged outside git on this host. Current status: satisfied.
2. Copied-book GnuCash lock/read gate passes safely. Current status: blocked by a source-environment lock marker in the copied SQL book.
3. Preflight passes and returns only redacted evidence.
4. Pre-mutation backup succeeds.
5. Restore helper/plan is available.
6. Read-back, audit row, lock lifecycle, restore verification, compatibility check where tooling exists, and default-disabled reset are all performed.
7. Abort immediately on read-back, restore, compatibility, audit, lock release, or default-reset failure.

Forbidden:
- original/working/private/only-copy mutation;
- historical/manual transaction deletion;
- amount/account/split mutation;
- raw private evidence in git.

Current verdict: BLOCKED_SAFETY / BLOCKED_NEEDS_DOGFOOD_RUN. The owner copy is staged, but routed dogfood stopped before mutation because the copied SQL book carries a GnuCash lock marker from the source environment and the API fails closed. No copied-book mutation occurred in this session.
