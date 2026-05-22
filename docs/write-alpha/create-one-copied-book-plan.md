# CREATE-one copied-book readiness plan

Status: Phase 272 plan only — no mutation authorized.

## Goal

Define the narrowest possible owner copied-book CREATE-one procedure that may be considered later after separate authorization. This plan exists because Phase 271 accepted owner copied-book dry-run evidence. It does not authorize running CREATE.

## Allowed scope if later authorized

Only one minimal two-split test transaction may be created, and only on an outside-git copied/restorable GnuCash book with the original untouched.

The operation must:

- use a copied/restorable target, never the original or only copy;
- keep the working book, backups, evidence, and logs outside git;
- use `GNUCASH_WRITES_ENABLED=true` only for the explicit local test step;
- keep `APP_ENV=test` required;
- create exactly one pre-mutation backup before the routed CREATE;
- create exactly one minimal test transaction;
- verify routed read-back after CREATE;
- verify audit, backup, and lock-release evidence;
- run the compatibility harness if available;
- run restore verification against the copied working book from the pre-mutation backup;
- reset to `GNUCASH_WRITES_ENABLED=false` and prove disabled validate/create/PATCH/DELETE behavior afterward;
- produce only redacted evidence.

## Required owner confirmation before any owner CREATE run

A future run is blocked until the owner explicitly confirms all of the following in the same context as the requested run:

```text
I want one CREATE test on a copied/restorable GnuCash book.
The original book is untouched and not used.
This is not my only copy.
The target, backups, and evidence are outside git.
I understand this is write-alpha, test-gated, and not production-safe.
```

Without that explicit confirmation, do not run owner copied-book CREATE.

## Synthetic/disposable prerequisite before asking owner

Before any owner CREATE request packet is prepared, run the same planned procedure on a synthetic/disposable fixture copy only and verify:

- backup created before mutation;
- exactly one CREATE was attempted and succeeded;
- audit row exists for the routed CREATE;
- lock is released or stale-released safely;
- read-back shows the synthetic test transaction;
- restore verification from the pre-mutation backup passes;
- redacted evidence validates;
- default-disabled reset passes.

This synthetic rehearsal is Phase 273. It must not use the owner copied-book.

## Abort conditions

Stop immediately and do not continue to CREATE if any of these occur:

- target appears to be original, production, shared, or only copy;
- target, backup, or evidence would be inside git or exposed in committed docs;
- `APP_ENV=test` is missing for explicit write-alpha execution;
- default config would enable writes;
- backup is not created before mutation;
- lock cannot be acquired or released cleanly;
- read-back fails;
- audit row is missing or mismatched;
- restore verification fails;
- compatibility harness fails where available;
- redaction validation fails;
- evidence includes private path, account name, memo, amount, balance, payload, screenshot, export, app DB, token, key, cert, or other private financial data.

## Explicit non-goals

- No CREATE is run by this plan.
- No PATCH is authorized.
- No DELETE is authorized.
- No original or only-copy book is allowed.
- No production, stable, security-audited, public-internet, broad compatibility, or safe real/private write claim is made.

## Current verdict

Ready for Phase 273 synthetic/disposable CREATE-one rehearsal only. Owner copied-book CREATE remains blocked until a later authorization gate and explicit owner request.
