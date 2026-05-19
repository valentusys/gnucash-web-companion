# Phase 125 — publish v0.1.3-readonly pre-release

Date: 2026-05-19
Status: DONE

## Goal

Stop and remove the temporary owner live-stand runtime artifacts, then publish the prepared `v0.1.3-readonly` GitHub pre-release after explicit Val authorization.

## Scope

- Stop Docker/Caddy runtime for the local personal-book stand.
- Remove ignored local `.env`, copied personal-book runtime file, and temporary smoke/cookie files.
- Re-check release prerequisites.
- Sync release/status docs.
- Create annotated tag and GitHub pre-release for `v0.1.3-readonly`.

## Non-goals

- No package/binary upload.
- No real/private data publication.
- No production-readiness, security-audit, or safe production write-mode claim.
- No enabling writes by default.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Personal-book runtime copy was ignored and removed before release.
- `.env` was ignored and removed before release.
- Sensitive tracked-file scan passed.

## Verification

- Docker containers stopped/removed.
- `HEAD == origin/main` before release-doc edits.
- `v0.1.3-readonly` tag/release absent before publication.
- Recent GitHub Actions on `main` successful through Phase 124.
- Docker Compose config validation passed.
- `git diff --check` passed.
- Release docs/status/changelog updated, committed, pushed.
- Annotated tag pushed.
- GitHub pre-release created.

## Expected artifacts

- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/release/v0.1.3-readonly-notes.md`
- `docs/release/v0.1.3-readonly-publish.md`
- `docs/handoff/phase-125.md`
- Git tag: `v0.1.3-readonly`
- GitHub release: `v0.1.3-readonly`
