# Owner PATCH-one request packet

Status: prepared in Phase 285. This packet does not authorize the agent to run PATCH automatically.

## Purpose

Optional next owner dogfood step: run exactly one metadata/memo-only PATCH on the same copied/restorable working book used for the accepted CREATE-one evidence, and only on the write-alpha-created test transaction.

## Do not proceed unless all are true

- You are using a copied/restorable working book, not the original and not the only copy.
- The original book is untouched.
- The copied working book, backups, app DB, runtime data, and evidence stay outside git.
- The target transaction is the write-alpha-created test transaction from the accepted CREATE-one run.
- You are willing to restore from backup if any check fails.
- You can paste back only the redacted checklist below, not raw paths, screenshots, CSV exports, account names, memos, amounts, book files, app DBs, backups, tokens, keys, or certs.

## Exact confirmation required before any owner PATCH execution

If you want the agent to run the one copied-book PATCH, reply with this exact block and fill only the bracketed yes/no values:

```text
I authorize exactly one owner copied-book PATCH-one run.
The target is a copied/restorable working book, not the original and not the only copy: [yes]
The original book is untouched: [yes]
The target transaction was created by the accepted write-alpha CREATE-one run: [yes]
The PATCH may change only description/date/split memo metadata and must not change amounts/accounts/currency/split count: [yes]
Backups/evidence/runtime data must stay outside git and private artifacts must not be committed: [yes]
After PATCH, run read-back, compatibility, restore, default-disabled reset, and disabled validate/create/PATCH/DELETE probes: [yes]
Stop before DELETE: [yes]
```

Any changed wording, missing line, or non-`yes` value means do not run owner PATCH.

## Allowed PATCH scope

Exactly one metadata/memo-only PATCH:

- description/date and/or split memo test markers only;
- no amount changes;
- no account changes;
- no currency changes;
- no split add/remove/rebalance;
- no DELETE.

## Evidence to paste back if you run it yourself

Paste only this redacted checklist:

```text
Owner copied-book PATCH-one evidence, redacted:
- exact confirmation used: yes/no
- copied/restorable book used: yes/no
- original book untouched: yes/no
- target transaction was write-alpha-created: yes/no
- target/backups/evidence outside git: yes/no
- exactly one PATCH attempted: yes/no
- exactly one PATCH performed: yes/no
- PATCH metadata/memo only: yes/no
- amount/account/currency/split-count unchanged: yes/no
- backup created before PATCH: yes/no
- read-back after PATCH: PASS/FAIL
- audit evidence: one-success/other
- lock evidence: released-or-stale-safe/active/unknown
- compatibility check: PASS/FAIL/BLOCKED
- broad compatibility claimed: false
- restore verification from pre-PATCH backup: PASS/FAIL
- default-disabled reset verified: yes/no
- disabled validate/create/PATCH/DELETE probes after reset: all-403/other
- DELETE run: no
- any redaction concern: yes/no
```

## Abort immediately

Stop and ask for review if any preflight, backup, read-back, compatibility, restore, reset, or redaction check fails; if the target is not the write-alpha-created transaction; if amounts/accounts/currency/split count would change; if an active lock remains; or if any raw private data appears in evidence.
