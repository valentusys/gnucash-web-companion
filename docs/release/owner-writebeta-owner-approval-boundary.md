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

## Allowed wording

Use conservative maintenance wording:

- owner-writebeta readiness remains unreleased;
- owner approval is required before any release-candidate package;
- `GNUCASH_WRITES_ENABLED=false` remains the default;
- enabled write-alpha/writebeta paths remain `APP_ENV=test` gated;
- copied-book W3 evidence is narrow and redacted;
- no public write beta is available.

## Blocked wording

Do not describe owner-writebeta as released, public beta, stable, production-ready,
security-audited, broadly compatible, or safe for real/private/original/working or
only-copy books.

Do not say that clean verification output authorizes release publication. Clean
verification output supports repository hygiene only.

## Reconsideration trigger

A later worker may revisit release-candidate preparation only when the task prompt
explicitly changes the state from `NO_RELEASE_KEEP_MAINTENANCE` to release-candidate
preparation, with owner/PM approval and a named scope.

Until then, documentation should explain the no-release state and must not create
release artifacts or broaden write-safety claims.
