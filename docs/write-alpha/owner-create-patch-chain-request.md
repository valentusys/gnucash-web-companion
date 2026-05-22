# Owner copied-book CREATE-to-PATCH chain request

Status: Phase 293 blocker packet. This document does not authorize mutation by itself.

## Purpose

Phase 292 blocked the old PATCH-one path because the current copied working book could not verify the Phase 276 write-alpha-created target transaction. A new CREATE-to-PATCH chain would need a fresh owner confirmation because it would perform a new CREATE and then one PATCH on that newly created transaction.

## Scope if later authorized

Exactly one bounded chain on a copied/restorable working book outside git:

1. Use or make a fresh copied/restorable working book outside git.
2. Back up before CREATE.
3. Run exactly one CREATE test transaction under `APP_ENV=test` with temporary explicit writes enabled.
4. Without restoring away that created transaction, back up before PATCH.
5. Run exactly one metadata/memo-only PATCH on that same write-alpha-created transaction.
6. Do not change amount, account, currency, split count, reconciliation state, schedule, import state, or account data.
7. Run read-back, audit/lock evidence, piecash and `gnucash-cli` compatibility, restore verification, reset/default-disabled verification, disabled validate/create/PATCH/DELETE probes, and redaction validation.
8. Stop before DELETE.

## Exact confirmation required before any new owner mutation

The owner must provide this exact block in the same execution context before the agent runs a new copied-book CREATE-to-PATCH chain:

```text
I authorize one new owner copied-book CREATE-to-PATCH chain.
The target is a copied/restorable GnuCash working book, not the original and not the only copy: yes
The original book is untouched and not used: yes
The target, backups, app DB, runtime data, and evidence are outside git and private artifacts must not be committed: yes
I understand this is write-alpha, APP_ENV=test gated, temporarily explicitly enabled, and not production-safe: yes
Run exactly one CREATE test transaction and no more than one CREATE: yes
Without restoring away that transaction, run exactly one metadata/memo-only PATCH on that same write-alpha-created transaction and no more than one PATCH: yes
The PATCH must not change amounts, accounts, currency, split count, reconciliation state, schedule, import state, or account data: yes
Before each mutation, create a backup; after the chain run read-back, audit/lock evidence, piecash and gnucash-cli compatibility, restore verification, reset/default-disabled verification, disabled validate/create/PATCH/DELETE probes, and redaction validation: yes
Stop before DELETE: yes
```

Any changed wording, missing line, or non-`yes` value means do not run the new owner mutation chain.

## Why the current shorthand is not enough

The owner selected option 1 after Phase 292, but the existing exact confirmations were for earlier, narrower packets:

- Phase 275 authorized exactly one CREATE, already consumed by Phase 276.
- Phase 285 authorized exactly one PATCH only on the Phase 276-created transaction, which Phase 292 could not verify in the current copied working book.
- A new chain requires both a new CREATE and a PATCH on that new write-alpha-created transaction, so it is a new mutation scope and needs the exact block above.

## Evidence boundaries

Allowed public/redacted summary fields only:

- exactly one CREATE attempted/performed: yes/no;
- exactly one PATCH attempted/performed: yes/no;
- copied/restorable book used and original untouched: yes/no;
- backups before each mutation: pass/fail;
- PATCH metadata/memo only and amount/account/currency/split-count unchanged: pass/fail;
- read-back, audit/lock, compatibility, restore, reset, disabled probes, redaction: pass/fail;
- DELETE run: no.

Do not expose raw private paths, file names, account names, memos, amounts, balances, screenshots, exports, app DBs, books, backups, tokens, keys, certs, `.env` values, or desktop stdout/stderr.

## Stop conditions

Stop before mutation or before retry if any condition fails:

- exact confirmation block is missing or altered;
- target may be original, only-copy, not independently restorable, or inside git;
- private artifacts would be committed or exposed;
- more than one CREATE or more than one PATCH would be required;
- PATCH would change amount/account/currency/split count or anything beyond allowed metadata/memo;
- backup, read-back, audit/lock, compatibility, restore, reset, disabled probes, or redaction fails;
- DELETE would be executed.
