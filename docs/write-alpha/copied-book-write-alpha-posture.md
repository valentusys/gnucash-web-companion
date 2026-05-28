# Copied-book write-alpha posture

Status: Phase 399 posture refresh after the Phase 398 audit accepted the bounded realistic copied-book session narrowly.

## Evidence that exists

- Synthetic/disposable write-alpha evidence exists for the earlier route-family and copied-book package rehearsals.
- Owner copied-book dry-run evidence is accepted as dry-run-only evidence.
- Owner copied-book CREATE evidence is accepted for bounded copied/restorable working-copy runs: the Phase 276 CREATE-one evidence and the Phase 294 fresh-chain CREATE.
- Owner copied-book PATCH evidence is accepted only for bounded metadata/memo-only PATCH evidence: the Phase 294 fresh-chain PATCH on its same write-alpha-created transaction, the current Cycle 2 Phase 333 PATCH on the verified existing Cycle 1 write-alpha-created copied-book test transaction as narrowly audited in Phase 335, and the Phase 395 metadata/memo-only PATCH on a transaction created in the same Phase 391-398 bounded realistic session.

The Phase 294 chain evidence covered pre-mutation backups before CREATE and PATCH, read-back, bounded audit evidence, backup-bearing audit rows matched to readable backup artifacts, lock release/stale-safe status, compatibility through piecash plus installed `gnucash-cli`, restore verification after chain evidence collection, reset to default-disabled config, and disabled validate/create/PATCH/DELETE probes returning 403.

The current Cycle 2 evidence covered ownership verification of the existing write-alpha-created copied-book test transaction, a pre-PATCH backup, exactly one metadata/memo-only PATCH, unchanged amount/account/currency/split-count fingerprint, read-back, audit/lock and backup evidence, piecash plus installed `gnucash-cli` compatibility, restore verification from the pre-PATCH backup, default-disabled reset, and disabled validate/create/PATCH/DELETE probes returning 403.

## Evidence that does not exist

- No owner copied-book DELETE evidence exists; DELETE remains blocked/not run for owner dogfood.
- No evidence here proves broad GnuCash compatibility.
- No evidence here proves production readiness, public-internet safety, security audit status, or safe writes for real/private/original/only-copy books.
- No evidence here authorizes changing amounts, accounts, currency, split count, reconciliation state, schedule, import state, or account data.

## Current operating boundary

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Explicitly enabled write-alpha still requires `APP_ENV=test`.
- Original and only-copy books remain forbidden for write-alpha dogfood.
- Historical/imported/manual transactions remain read-only in this app. Existing PATCH/DELETE write-alpha code is constrained to write-alpha-owned transactions, but owner DELETE remains blocked and no DELETE packet is prepared.

## Practical verdict

Read-only use remains the practical default. Write-alpha remains experimental post-MVP work for synthetic/disposable or copied/restorable test targets only, with strict local/test gating and no broad safety claim.

## Phase 351-380 posture update

Write-alpha has narrow copied-book dogfood evidence for CREATE, metadata/memo-only PATCH, one disposable write-alpha-owned DELETE chain, and one small batch of 2 CREATE + 1 metadata/memo-only PATCH. This is not a broad safety claim. Use only copied/restorable books outside git; keep GNUCASH_WRITES_ENABLED=false by default and require APP_ENV=test for explicit write-alpha runs.

## Phase 391-398 posture update

A bounded realistic copied-book session was accepted narrowly: exactly 2 CREATE, exactly 1 metadata/memo-only PATCH on a same-session write-alpha-created transaction, and 0 DELETE. Backup/read-back/audit/ownership/restore/piecash compatibility/default-disabled reset evidence passed. This still does not authorize original/private/only-copy books, production use, amount/account/split changes, historical/manual transaction mutation, or default write enablement.
