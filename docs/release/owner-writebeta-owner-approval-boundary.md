# Owner-writebeta owner-approval boundary

Status: `NO_RELEASE_KEEP_MAINTENANCE`.

This page is a reviewer-facing explanation of why owner-writebeta readiness stays
unreleased. It is not release notes, a checklist, a publication gate, or evidence
that owner-writebeta is available.

## Current decision

Do not publish a tag, GitHub release, package, image, or public write-beta
announcement for owner-writebeta until a later task carries explicit owner/PM
release-candidate approval.

The public release line remains `v0.5.0-public-readonly-beta`. The owner-writebeta
line remains maintenance-only and unreleased.

## Decision ladder for reviewers

Use this order when reading owner-writebeta readiness material:

1. Repository checks can show that guarded docs and tests remain internally
   consistent.
2. Narrow W3 evidence can show only that the approved copied/restorable target
   survived the accepted operation counts.
3. Those two facts are maintenance evidence, not a release decision.
4. Owner/PM approval is the first step that can change the state from
   `NO_RELEASE_KEEP_MAINTENANCE` to release-candidate preparation.
5. Without that approval, do not draft publication notes, final gates, packages,
   images, or announcement wording.

This ladder prevents a clean verification run from being mistaken for consent to
ship owner-writebeta.

## Why readiness is not release authorization

Readiness evidence can show that selected guards and copied-book checks were
reviewed. It does not authorize a release because the remaining decision is about
scope, risk ownership, and public signal, not only repository health.

The current evidence is still bounded by these limits:

- #36 remains open for controlled-write readiness closure.
- W3 dogfood evidence covers one staged outside-git copied/restorable target only.
- Accepted W3 operation counts are exact: CREATE 2, PATCH 1, DELETE 1.
- Supported-version write compatibility is not accepted as a public claim.
- Real/private/original/working/only-copy book mutation remains unauthorized.
- Passing checks prove only that guarded docs/code satisfy local policy.

Because of those limits, publishing any owner-writebeta artifact would create a
stronger public signal than the accepted evidence supports.

## What explicit approval must say

A future approval is valid only if it is explicit in the task prompt or owner/PM
handoff. It should name at least:

- the exact release-candidate scope;
- whether #22 and #36 blockers are accepted, cleared, or still blocking;
- whether release notes, final-gate docs, tags, packages, images, or announcements
  may be prepared;
- the permitted write target class, if any;
- the safety wording that must remain unchanged.

Absent that explicit packet, workers should treat owner-writebeta as unreleased
maintenance work even when all local checks pass.

## Approval absence checklist

If any item below is missing, the only safe release decision remains no-release:

- explicit owner/PM approval for release-candidate preparation;
- named release-candidate scope and intended audience;
- stated handling of remaining #36 gates;
- stated handling of compatibility posture before any public write claim;
- permission, if any, to draft release notes, final gates, packages, images, or
  announcements.

When one of those items is absent, preserve `NO_RELEASE_KEEP_MAINTENANCE` and link
back to this page instead of inventing release readiness.

## What this documentation pass does not create

This page and companion no-release docs do not create:

- a release checklist;
- a publication gate;
- package or image instructions;
- public write-beta availability;
- real/private/original/working/only-copy write safety;
- permission to mutate any GnuCash book.

## Allowed wording

Use conservative maintenance wording:

- owner-writebeta readiness remains unreleased;
- owner approval is required before any release-candidate package;
- `GNUCASH_WRITES_ENABLED=false` remains the default;
- enabled write-alpha/writebeta paths remain `APP_ENV=test` gated;
- copied-book W3 evidence is narrow and redacted;
- no public write beta is available.

When in doubt, say what remains blocked before saying what passed. Passing checks
belong in evidence history; the current state remains no-release.

## Blocked wording

Do not describe owner-writebeta as released, public beta, stable, production-ready,
security-audited, broadly compatible, or safe for real/private/original/working or
only-copy books.

Do not say that clean verification output authorizes release publication. Clean
verification output supports repository hygiene only.

Do not turn this page into a release checklist. A checklist would imply that a
worker may finish the remaining items and publish. The current task state does
not authorize that path.

## Reconsideration trigger

A later worker may revisit release-candidate preparation only when the task prompt
explicitly changes the state from `NO_RELEASE_KEEP_MAINTENANCE` to release-candidate
preparation, with owner/PM approval and a named scope.

Until then, documentation should explain the no-release state and must not create
release artifacts or broaden write-safety claims.
