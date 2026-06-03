# Daytime W3 copied-book authorization

Status: AUTHORIZE_W3_COPIED_BOOK_DOGFOOD_WITH_EXACT_COUNTS

Timestamp: 2026-06-03T12:42:41+10:00

## PM authorization

PM authorizes W3 copied-book dogfood for the staged outside-git copied target created for this run only.

Authorized operation counts are exact:

- CREATE: 2 attempts, 2 expected successes.
- PATCH: 1 attempt, 1 expected success.
  - Scope: metadata/memo-only on a write-alpha/state-machine-created transaction.
  - Forbidden: amount, account, split-shape, historical/manual transaction changes.
- DELETE: 1 attempt, 1 expected success.
  - Scope: write-alpha/state-machine-created disposable transaction only.

## Required evidence before accepting completion

- Pre-mutation backup exists.
- Routed write-alpha operations match the authorized counts exactly.
- Audit summary reports the expected route-family counts and no failed/unknown results.
- Read-back confirms the retained created transaction exists and the deleted disposable transaction is absent.
- Restore proof confirms the pre-batch backup is restorable.
- Compatibility read opens the mutated copied book read-only.
- Default-disabled reset probes for CREATE/PATCH/DELETE return 403.
- Redacted evidence only; no raw private values in committed docs or issue comments.

## Stop conditions

Stop immediately if backup, mutation, audit, read-back, restore, compatibility, lock/default reset, or redaction validation fails.

## Release decision

NO_RELEASE. This authorization is dogfood-only and does not authorize a public write beta, owner-writebeta pre-release, stable release, production-readiness claim, or security-audited claim.
