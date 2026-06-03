# Phase W3 v0.4 decision

Status: NO_RELEASE_KEEP_MAINTENANCE

## Decision

Do not prepare, tag, publish, or claim `v0.4.0-owner-writebeta` in this continuation.

## Rationale

W3 satisfies the copied-book dogfood gate for #36, but only for a staged outside-git copied/restorable
target. It does not prove real working-book safety, broad supported-version compatibility, public write
readiness, stable readiness, production readiness, or security-audited status.

#36 remains open. #22 remains open. Release/no-release stays `NO_RELEASE`.

## Current release baseline

- Public read-only beta: `v0.5.0-public-readonly-beta`.
- Not published: `v0.5.1-public-readonly-beta`.
- Latest observed write-alpha pre-release: `v0.2.8-writealpha`.
- No owner-writebeta release is published by this package.

## If a later PM gate prepares RC artifacts

Any later RC notes must say owner-only, experimental, disabled by default, `APP_ENV=test` gated,
copied/restorable evidence only, no real/private/original/working/only-copy safety claim, no public
write beta, no stable/production/security-audited claim, and no broad GnuCash compatibility claim.
