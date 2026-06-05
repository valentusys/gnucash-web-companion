# release-no-release-decision-docs-r4 handoff

Task area: issue #36 release and no-release decision documentation.

## Status

Completed as docs-only maintenance. No release artifacts were prepared or
published.

## Changed documentation

- Updated `docs/release/v0.4-owner-writebeta-readiness-unreleased.md` with an
  owner-approval boundary section that keeps readiness evidence separate from
  release-candidate authorization.
- Updated `docs/release/v0.4-owner-writebeta-no-release-decision.md` with a
  release-state invariant: owner-writebeta readiness docs do not authorize an
  owner-writebeta release.
- Updated `docs/release/owner-writebeta-owner-approval-boundary.md` to define
  what future explicit owner/PM approval must say and what this documentation
  pass does not create.
- Updated `PROJECT_STATUS.md` navigation/current snapshot to point at this r4
  handoff and the clarified no-release documentation boundary.

## Safety posture

- `NO_RELEASE_KEEP_MAINTENANCE` remains current.
- Public release remains `v0.5.0-public-readonly-beta`.
- `v0.4.0-owner-writebeta` remains unpublished.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Enabled write-alpha/writebeta remains `APP_ENV=test` gated.
- No public write beta, stable, production-ready, security-audited, broad
  compatibility, or only-copy safety claim was added.
- No release notes, checklist, tag, package, image, or publication evidence was
  created.
- Mutation counts: CREATE 0 / PATCH 0 / DELETE 0.

## Verification

Run after the documentation changes:

```text
python3 scripts/check_public_status.py
python3 scripts/check_markdown_readability.py
python3 scripts/check_tracked_hygiene.py
git diff --check
```
