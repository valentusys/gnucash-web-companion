# Copied-book write-alpha posture

Status: Phase 293 posture refresh after a new CREATE-to-PATCH chain was blocked before mutation pending exact owner confirmation.

## Evidence that exists

- Synthetic/disposable write-alpha evidence exists for the earlier route-family and copied-book package rehearsals.
- Owner copied-book dry-run evidence is accepted as dry-run-only evidence.
- Exactly one owner copied-book CREATE evidence run is accepted for one copied/restorable working copy outside git.

The accepted owner CREATE evidence covered a pre-mutation backup, read-back, bounded audit evidence, lock release/stale-safe status, compatibility through piecash plus installed `gnucash-cli`, restore verification from the pre-mutation backup, reset to default-disabled config, and disabled validate/create/PATCH/DELETE probes returning 403.

## Evidence that does not exist

- No owner copied-book PATCH evidence exists. Phase 292 blocked before PATCH because the Phase 276 target transaction was not verifiable in the current copied working book.
- No owner copied-book CREATE-to-PATCH fresh-chain evidence exists; Phase 293 blocked before mutation pending exact same-context owner confirmation for that new scope.
- No owner copied-book DELETE evidence exists.
- No evidence here proves broad GnuCash compatibility.
- No evidence here proves production readiness, public-internet safety, security audit status, or safe writes for real/private/original/only-copy books.

## Current operating boundary

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Explicitly enabled write-alpha still requires `APP_ENV=test`.
- Original and only-copy books remain forbidden for write-alpha dogfood.
- Owner copied-book PATCH, fresh CREATE-to-PATCH chain, and DELETE remain blocked unless the owner gives the exact required same-context confirmation for the relevant scope.
- Historical/imported/manual transactions remain read-only in this app. Existing PATCH/DELETE write-alpha code is constrained to write-alpha-owned transactions, but that code is not authorized for owner copied-book PATCH/DELETE by this posture.

## Practical verdict

Read-only use remains the practical default. Write-alpha remains experimental post-MVP work for synthetic/disposable or copied/restorable test targets only, with strict local/test gating and no broad safety claim.
