# Package 3 — #36 remaining gates decision

Date: 2026-06-04

## Decision

`REMAIN_OPEN_FOR_SPECIFIC_MISSING_EVIDENCE_AND_RELEASE_DECISION`.

#36 should remain open. The gate set is reduced to exact blockers, but closure would still overstate the current evidence.

## Why #36 is not closed

The original #36 scope includes controlled-write readiness gates. The current evidence is strong but still bounded:

- W3 proves controlled CREATE/PATCH/DELETE on one staged outside-git copied/restorable target only.
- #22 proves read-only compatibility for one Desktop-generated synthetic SQLite fixture only.
- The project still does not have accepted supported-version write compatibility across supported GnuCash versions.
- The project still has no safe real/private/original/working/only-copy mutation claim.
- No PM release authorization has accepted all remaining gates as non-blocking.

## Minimal remaining blockers

1. PM acceptance of #36 closure scope.
2. Supported-version write compatibility remains unaccepted beyond narrow synthetic/copied evidence.
3. Real working-book mutation remains unauthorized and outside current safe evidence.
4. Release/public posture remains no-release unless Package 4 authorizes a conservative owner-only prerelease and Package 6 gates pass.

## What closure would not mean if a later PM closes #36

Even a future #36 closure must not mean:

- real working-book writes are safe;
- only-copy writes are safe;
- public write beta is safe;
- production/stable/security-audited readiness;
- broad database/backend/Desktop compatibility;
- default write enablement.

## Issue/doc state

- GitHub #36 remains open.
- Docs now reflect #22 closure and the still-pending #36 release/closure blockers.

## Safety

Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.

No new dogfood was run and no release/tag/package/image was published.
