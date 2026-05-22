# Phase 294 — Owner copied-book CREATE-to-PATCH chain evidence

Status: ACCEPTED — exactly one new owner copied-book CREATE was attempted/performed, then exactly one metadata/memo-only PATCH was attempted/performed on that same write-alpha-created transaction. DELETE was not run.

## Scope

This phase used the exact same-context owner confirmation for one new copied/restorable CREATE-to-PATCH chain. The working book, app DB, backups, runtime data, scripts, and raw evidence stayed outside git under private local storage.

No original or only-copy book was used. No private book, backup, app DB, raw path, account name, memo, amount, balance, token, screenshot, export, or raw evidence is committed here.

## Internal role review

Analyst: verified the Phase 293 blocker was resolved by the exact owner confirmation, and that the allowed scope was one fresh CREATE followed by one metadata/memo-only PATCH on that same created transaction.

Engineer: executed the bounded chain only after preflight passed with `APP_ENV=test` and temporary explicit write enablement.

PM: invoked internally because this was a private-data/write-mode owner-risk gate. Verdict: proceed only within the exact owner-confirmed scope, keep all artifacts outside git, require backup before each mutation, verify redacted evidence, restore/reset/default-disabled probes, and stop before DELETE.

## Redacted evidence checklist

```text
Owner copied-book CREATE-to-PATCH chain, redacted:
- owner confirmation provided in execution context: yes
- fresh copied/restorable working book outside git: yes
- original/only-copy book used: no
- target/backups/app DB/runtime/evidence outside git: yes
- APP_ENV=test for enabled write-alpha: yes
- GNUCASH_WRITES_ENABLED=false remains default: yes
- preflight before mutation: pass
- exactly one CREATE attempted: yes
- exactly one CREATE performed: yes
- backup before CREATE: pass
- CREATE read-back: pass
- exactly one PATCH attempted: yes
- exactly one PATCH performed: yes
- PATCH target: same write-alpha-created transaction
- PATCH scope: metadata/memo-only
- PATCH invariant checks: amounts/accounts/currency/split-count/reconciliation/schedule/import/account data unchanged
- backup before PATCH: pass
- PATCH read-back: pass
- audit evidence: one create success and one patch success
- backup-bearing audit rows matched readable backup artifacts: pass
- lock evidence: released/stale-safe or not actively held
- compatibility: pass with piecash and installed gnucash-cli; no broad compatibility claim
- restore verification: checksum/read-back proof verified on the copied working book from pre-PATCH backup
- reset/default-disabled verification: pass
- disabled validate/create/PATCH/DELETE probes after reset: all 403
- redaction validation for private evidence: pass
- DELETE attempted/performed: no/no
```

## Important nuance

A local PATCH continuation script first failed after the PATCH because it checked container-visible backup paths as host paths. The mutation had already completed exactly once. I did not rerun PATCH. I verified the existing one-success PATCH audit row and remapped the container `/data/...` audit backup references to the private host runtime directory for readability checks. This was an evidence-script issue, not a second mutation.

Restore verification was run after CREATE and PATCH evidence collection. It restored the copied working book from the pre-PATCH backup, so the restored private working file no longer contains the PATCH marker. The audit/app metadata evidence remains private; the committed record is only this redacted summary.

## Safety posture

- Owner dry-run remains accepted.
- Owner copied-book CREATE evidence now includes the Phase 276 one-CREATE evidence and this Phase 294 fresh-chain CREATE.
- Owner copied-book PATCH evidence is accepted only for this Phase 294 metadata/memo-only PATCH on the same newly created write-alpha-owned transaction.
- Owner DELETE remains not run and blocked.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Enabled write-alpha still requires `APP_ENV=test`.
- No release/tag/package/image was published.
- This does not claim production readiness, security audit status, public-internet safety, broad GnuCash compatibility, or safe writes for real/private/original/only-copy books.
