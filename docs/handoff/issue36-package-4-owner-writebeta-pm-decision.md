# Package 4 — owner-writebeta PM decision

Date: 2026-06-04

## Decision

`NO_RELEASE_KEEP_MAINTENANCE`.

See `docs/release/v0.4.0-owner-writebeta-pm-decision.md`.

## Why no release

The PM decision is conservative:

- #22 state drift is resolved, but #22 remains read-only synthetic SQLite evidence only.
- #36 remains open with exact remaining closure/release blockers.
- W3 copied-book write evidence is accepted narrowly but does not prove real-book or only-copy safety.
- A GitHub prerelease named owner-writebeta could be read as broader than the accepted evidence unless #36 closure and release wording are accepted in a separate gate.

## Release scope if a future PM authorizes it

A future authorized release would need to be described as all of the following:

- GitHub pre-release only;
- owner-only;
- experimental;
- scoped to staged copied/restorable evidence;
- writes disabled by default;
- enabled writes `APP_ENV=test` gated;
- no public write beta;
- no real/private/original/working/only-copy safety;
- no production/stable/security-audited guarantee.

## Safety

Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.

No release/tag/package/image was published.
