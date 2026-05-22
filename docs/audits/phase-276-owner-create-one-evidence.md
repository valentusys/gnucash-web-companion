# Phase 276 — Owner CREATE-one evidence intake gate

Status: ACCEPTED — exactly one owner copied-book CREATE was attempted and performed on a copied/restorable working copy outside git.

## Analyst objective

Review whether the current execution context safely authorizes one owner copied-book CREATE, then accept or reject the resulting evidence without exposing private data.

## PM invocation

PM was invoked internally because this phase involved private-data/write-mode owner risk. PM verdict: proceed only because the exact Phase 275 confirmation block was present in the same execution context; execute exactly one CREATE on the copied/restorable working copy; keep all target/backups/evidence outside git; stop before PATCH/DELETE.

## Scope reviewed

- Phase 275 owner CREATE-one packet.
- Exact owner confirmation block provided in the current execution context.
- Earlier owner statement that the uploaded book is a copy and must not be committed.
- Required safety posture: copied/restorable outside-git target only, original untouched, not only copy, no private artifacts in git, `APP_ENV=test` for enabled write-alpha, and default `GNUCASH_WRITES_ENABLED=false`.

## Decision

Verdict: ACCEPTED AS ONE COPIED-BOOK CREATE-ONE EVIDENCE RUN.

This is narrow evidence for one owner-provided copied/restorable working copy only. It is not production-readiness evidence, not a security audit, not public-internet safety evidence, not broad GnuCash compatibility evidence, and not a claim that real/private/original/only-copy books are safe for writes.

## Redacted evidence checklist

```text
Owner copied-book CREATE-one evidence, redacted:
- owner confirmation provided in execution context: yes
- copied/restorable book used: yes
- original book untouched: yes, by confirmation and by using only a copied working target
- target/backups/evidence outside git: yes
- wrapper result: PASS
- redaction checker for wrapper evidence: PASS
- mutation_requested: true
- mutation_performed: true
- create_command_status: passed
- exactly one CREATE attempted: yes
- backup created before CREATE: yes
- read-back after CREATE: PASS
- audit evidence: one-success
- lock evidence: released-or-stale-safe
- compatibility check: PASS
- compatibility broad claim made: false
- restore verification: PASS
- default-disabled reset verified: verified-default-disabled
- disabled validate/create/PATCH/DELETE probes after reset: all 403
- PATCH run: no
- DELETE run: no
- any redaction concern: no
```

## Bounded local verification summary

- Preflight passed only with explicit `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true`.
- The copied working target, wrapper backup, runtime backup, app DB, restore evidence, and compatibility evidence stayed outside git.
- The wrapper created one pre-step backup before the CREATE command and wrote redacted evidence.
- The routed CREATE smoke performed exactly one balanced two-split CREATE, then read the created transaction back through the API.
- Runtime evidence showed one successful create audit and one runtime backup artifact.
- Lock evidence was not actively held after create; a stale released lock artifact may remain only in ignored/private runtime storage.
- Compatibility evidence passed with piecash read and `gnucash-cli`/GnuCash 5.14 report probing; `broad_compatibility_claimed=false`.
- Restore verification restored the copied working target from the pre-mutation backup, checksum matched, piecash read-back passed, and the read-only API probe passed.
- After reset, `GNUCASH_WRITES_ENABLED=false` was verified and disabled validate/create/PATCH/DELETE probes returned 403.
- No raw private path, account name, memo, amount, balance, app DB, book, backup, evidence JSON, `.env`, token, key, cert, screenshot, CSV export, or Desktop stdout/stderr was committed.

## Safety posture

- Owner copied-book dry-run evidence remains accepted as dry-run-only evidence.
- Owner copied-book CREATE status is now accepted for exactly one copied/restorable working-copy CREATE run.
- Owner PATCH remains not run and not authorized by this phase.
- Owner DELETE remains not run and not authorized by this phase.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Enabled write-alpha still requires `APP_ENV=test`.
- No release/tag/package/image was published.
