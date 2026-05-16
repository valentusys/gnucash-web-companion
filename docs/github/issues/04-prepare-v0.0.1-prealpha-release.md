# Prepare v0.0.1-prealpha release

Labels: `documentation, pre-alpha, safety`

Milestone: `v0.1 read-only MVP`

## Goal
Prepare the first public pre-alpha tag and release notes.

## Requirements
- Local checks pass.
- README clearly says read-only by default.
- Write code is gated behind `GNUCASH_WRITES_ENABLED=false`.
- Release notes warn users to test only with disposable or backed-up book copies.
- No production-readiness claims.

## Acceptance criteria
- `v0.0.1-prealpha` tag exists.
- GitHub pre-release exists.
