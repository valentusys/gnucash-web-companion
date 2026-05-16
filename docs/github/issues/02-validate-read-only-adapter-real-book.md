# Validate read-only adapter against a disposable real GnuCash SQL book

Labels: `gnucash, read-only, safety`

Milestone: `v0.1 read-only MVP`

## Goal
Validate the piecash read-only service against an actual disposable GnuCash SQL book.

## Requirements
- Use only a test copy or synthetic fixture.
- Confirm read-only open path.
- Confirm accounts tree.
- Confirm balances.
- Confirm transaction pagination.
- Confirm split transaction detail.
- Confirm missing book errors remain controlled.

## Acceptance criteria
- Integration test or documented smoke test exists.
- README references safe validation procedure.
