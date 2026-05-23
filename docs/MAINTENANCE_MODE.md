# Maintenance mode

Status: Phase 318 maintenance/wait mode for active write-alpha phase work.

## Summary

Active write-alpha phase work is paused/waiting. The project should not continue a phase treadmill or request new owner mutations without fresh owner live-stand feedback and a new exact same-context gate.

## Current practical path

Use and improve read-only mode. GnuCash Desktop remains the authoritative editor.

## Release posture

- Current public read-only pre-release: `v0.1.7-readonly`.
- Current public experimental write-alpha pre-release: `v0.2.8-writealpha`.
- No `v0.2.9-writealpha` or later write-alpha release is authorized or published by Phases 295–320.

## Write-alpha posture

- `GNUCASH_WRITES_ENABLED=false` remains default.
- Explicit write-alpha remains backend `APP_ENV=test` gated.
- Owner copied-book evidence is narrow: dry-run only, one CREATE-one, and one fresh CREATE-to-PATCH chain.
- Owner DELETE is blocked/not run/no packet.
- Original/private/only-copy books remain forbidden for write-alpha.

## Allowed maintenance

- Fix read-only bugs.
- Improve docs while preserving conservative safety language.
- Maintain tests/status guards with synthetic/disposable data.
- Triage issues without noisy comments.
- Prepare planning briefs only when they do not imply owner mutation approval.

## Requires new owner/PM gate

- Any owner copied-book CREATE/PATCH/DELETE mutation.
- Any owner DELETE request packet.
- Any release/publication decision.
- Any claim expansion around production, security, public-internet, broad compatibility, or real/private-book write safety.
