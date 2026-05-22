# Copied-book write-alpha posture

Status: Phase 294 posture refresh after one owner-confirmed fresh CREATE-to-PATCH chain was accepted.

## Evidence that exists

- Synthetic/disposable write-alpha evidence exists for the earlier route-family and copied-book package rehearsals.
- Owner copied-book dry-run evidence is accepted as dry-run-only evidence.
- Owner copied-book CREATE evidence is accepted for bounded copied/restorable working-copy runs: the Phase 276 CREATE-one evidence and the Phase 294 fresh-chain CREATE.
- Owner copied-book PATCH evidence is accepted only for the Phase 294 fresh-chain metadata/memo-only PATCH on the same Phase 294 write-alpha-created transaction.

The Phase 294 chain evidence covered pre-mutation backups before CREATE and PATCH, read-back, bounded audit evidence, backup-bearing audit rows matched to readable backup artifacts, lock release/stale-safe status, compatibility through piecash plus installed `gnucash-cli`, restore verification after chain evidence collection, reset to default-disabled config, and disabled validate/create/PATCH/DELETE probes returning 403.

## Evidence that does not exist

- No owner copied-book DELETE evidence exists.
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
