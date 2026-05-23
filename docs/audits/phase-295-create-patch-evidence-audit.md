# Phase 295 — CREATE-to-PATCH evidence audit

Status: ACCEPTED — Phase 294 owner copied-book CREATE-to-PATCH evidence is accepted narrowly.

## Scope reviewed

Reviewed repository status, Phase 294 handoff, Phase 294 redacted audit report, current write-alpha evidence matrix/posture, GitHub releases/issues/runs, public status guard output, and tracked-file hygiene scan.

## Evidence accepted

Phase 294 is accepted only as this bounded evidence item:

- one fresh copied/restorable owner working book outside git;
- exactly one write-alpha CREATE attempted and performed;
- exactly one metadata/memo-only PATCH attempted and performed on that same Phase 294 write-alpha-created transaction;
- backups before both mutations;
- read-back, audit/lock, readable backup artifact, piecash, installed `gnucash-cli`, restore, reset/default-disabled, disabled validate/create/PATCH/DELETE probe, and redaction checks recorded as passing in the redacted committed evidence.

## Safety findings

- No original or only-copy book use is claimed.
- DELETE was not attempted or performed.
- PATCH evidence is metadata/memo-only; no amount, account, currency, split-count, reconciliation, schedule, import, or account-data write is accepted.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default posture.
- Explicit write-alpha remains `APP_ENV=test` gated.
- Public release state remains `v0.1.7-readonly` and `v0.2.8-writealpha`; no `v0.2.9-writealpha` release exists.
- Latest visible GitHub Actions run for Phase 294 is successful.
- Public status guard passed.
- Tracked sensitive-file hygiene scan found only committed test fixtures and `.gitkeep` placeholders; `.hermes/` remains untracked and must not be committed.

## Non-claims

This audit does not claim production readiness, security audit coverage, public-internet safety, broad GnuCash compatibility, DELETE readiness, or safe writes for real/private/original/only-copy books.

## Verdict

ACCEPTED_NARROWLY. Continue to Phase 296 posture reconciliation. Do not authorize DELETE. Do not publish a release from this phase.
