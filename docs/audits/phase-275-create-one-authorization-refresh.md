# Phase 275 — CREATE-one authorization refresh and owner packet

Status: COMPLETE — PM invoked; asking the owner for one copied-book CREATE is authorized, but execution is not run by this phase.

## Analyst objective

Revisit the Phase 274 compatibility blocker conservatively after host `gnucash-cli` became available. Do not hide Phase 274 history; record new evidence and a new Phase 275 decision before preparing any owner-facing packet.

## Engineer objective

Run only a synthetic/disposable compatibility recheck and update the owner request documentation. Do not run owner copied-book CREATE/PATCH/DELETE.

## Inputs reviewed

- Phase 271 accepted owner copied-book evidence as dry-run-only evidence.
- Phase 272 prepared a no-mutation CREATE-one readiness plan.
- Phase 273 synthetic/disposable CREATE-one rehearsal passed routed CREATE, backup, audit, lock, read-back, restore, redaction, and default-disabled reset checks.
- Phase 274 kept owner CREATE blocked because host Desktop/CLI compatibility was blocked by unavailable `gnucash-cli`.
- Current host check: `/usr/bin/gnucash-cli` exists and reports `GnuCash 5.14`.

## New compatibility recheck

A synthetic/disposable fixture copy outside the git checkout was checked with `scripts/write_alpha_compatibility_check.py` after `gnucash-cli` installation.

Safe allowlisted results:

```text
compat_result=pass
compat_piecash_status=pass
compat_desktop_status=pass
compat_desktop_available=true
compat_desktop_version=GnuCash 5.14
compat_broad_claimed=false
```

This closes the specific Phase 274 blocker for the local synthetic/disposable compatibility probe only. It does not prove broad GnuCash Desktop/version compatibility and does not make real/private, original, production, shared, or only-copy books safe for writes.

## PM invocation

PM was invoked because this changes an owner-risk write authorization decision: whether to ask the owner for one mutation on a copied private financial book.

PM decision: AUTHORIZE_OWNER_CREATE_ONE_REQUEST_PACKET.

## Authorized state

- Owner copied-book dry-run: accepted as dry-run-only evidence.
- Owner copied-book CREATE request: authorized to ask for exactly one minimal two-split CREATE on a copied/restorable outside-git book, if the owner explicitly confirms the required text at run time.
- Owner copied-book CREATE execution: not run by this phase and still blocked unless the owner explicitly authorizes that mutation in the execution context.
- Owner copied-book PATCH/DELETE: blocked.
- Original/only-copy book writes: forbidden.

## Safety boundaries

- No owner copied-book mutation was run.
- No owner/private/original/only-copy book was used.
- The compatibility recheck used synthetic/disposable fixture data only.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Explicit write-alpha execution remains `APP_ENV=test` gated.
- No production, stable, security-audited, public-internet, broad compatibility, or safe real/private write claim is made.
- No private financial artifact is committed.

## Next action

Stop after preparing the owner CREATE-one request packet. Do not run CREATE/PATCH/DELETE unless the owner explicitly authorizes the mutation later using the required confirmation text.
