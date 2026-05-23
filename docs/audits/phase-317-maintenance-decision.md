# Phase 317 maintenance-mode decision

Status: COMPLETE — enter maintenance/wait mode for active write-alpha phase work.

## Inputs reviewed

- Phases 295–316: accepted narrow owner CREATE-to-PATCH evidence, no-release decisions, default-disabled regression, maintenance hardening, owner-feedback gate, and owner digest.
- Open public issues: #36, #29, #28, #22, #17, #13.
- Current release state: `v0.2.8-writealpha` remains the current public experimental write-alpha pre-release.

## PM decision

Enter maintenance/wait mode for active write-alpha phase work.

## Allowed future work

- Read-only bug fixes and small UX improvements.
- Documentation corrections that preserve conservative safety wording.
- Tests/guards using synthetic/disposable data.
- Issue triage without requesting new owner mutation.
- New write-alpha planning only after fresh owner live-stand feedback or exact same-context confirmation.

## Blocked future work without a new gate

- Owner CREATE/PATCH/DELETE mutation steps.
- Owner DELETE planning/request packet.
- Writes on original/private/only-copy books.
- New write-alpha release publication based only on old copied-book evidence.

## Safety result

Write-alpha remains pre-alpha, disabled by default, `APP_ENV=test` gated when explicitly enabled, and not safe for original/private/only-copy books.
