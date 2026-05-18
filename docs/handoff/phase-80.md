# Phase 80 — Publish v0.1.0-readonly Pre-release

## Status

Complete. Phase 80 was a narrow publish-only PM→Engineer phase. The annotated git tag `v0.1.0-readonly` was created on the current `main` HEAD from the Phase 79 release gate, pushed to GitHub, and published as a GitHub pre-release using `docs/release/v0.1.0-readonly-notes.md`.

No auditor role was used. No audit-only phase or `docs/audits/phase-80-audit.md` was created.

No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Publish `v0.1.0-readonly` exactly as the Phase 79 gate requested: create an annotated git tag on the current `main` HEAD, push the tag, and create a GitHub pre-release from the already-prepared conservative release notes.

### Why

Phase 79 recorded the final gate verdict as ready for publication. The required Phase 80 direction was publish-only for `v0.1.0-readonly`, with no product/code scope expansion, no write enablement, and no v0.2 planning.

### Phase brief

- Goal: publish the existing `v0.1.0-readonly` pre-alpha read-only release artifact.
- Non-goals: no feature work, no write-mode work, no v0.2 planning, no audit-only output, no release-note broadening, no real-data artifacts.
- Acceptance criteria:
  - Re-check local `main` and Phase 79 CI.
  - Verify no `v0.1.0-readonly` tag or GitHub release exists before publication.
  - Create annotated git tag `v0.1.0-readonly` on current `main` HEAD.
  - Push the tag.
  - Create GitHub pre-release using `docs/release/v0.1.0-readonly-notes.md`.
  - Update `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff with publication evidence.
  - Commit/push status docs to `origin/main`.
- Safety checks:
  - Keep `GNUCASH_WRITES_ENABLED=false`.
  - Do not commit `.env`, real books, app DBs, backups, exports/screenshots with real financial data, secrets, tokens, certs, or keys.
  - Preserve positioning: GnuCash Desktop is authoritative; project is not SaaS, not a GnuCash replacement, and not collaborative accounting.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - `git tag -l 'v0.1*'`, `git ls-remote --tags origin 'v0.1*'`, and `gh release view v0.1.0-readonly` before and after publication.

### GitHub/backlog

No issues were closed in Phase 80. Open follow-up issues #22 and #26–#36 remain non-blocking hardening/future-release backlog for later phases.

## Engineer report

### Publication result

Published:

- Annotated git tag: `v0.1.0-readonly`.
- Tagged commit: `8180d555d71feaaf008d3edafeaa24dffd3dcfdb` (`docs: record phase 79 ci result`).
- Remote tag: `refs/tags/v0.1.0-readonly` pushed to `origin`.
- GitHub release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly
- GitHub release type: pre-release.
- Release notes source: `docs/release/v0.1.0-readonly-notes.md`.
- Published at: `2026-05-18T06:04:26Z`.

### Pre-publication checks

Repository/GitHub preflight:

```text
git --version
2.53.0

gh --version
2.46.0

gh auth status
Logged in to github.com as valentusys

local HEAD
8180d555d71feaaf008d3edafeaa24dffd3dcfdb

origin/main
8180d555d71feaaf008d3edafeaa24dffd3dcfdb
```

Phase 79 main-branch CI before tagging:

```text
CI run 26013957098
status: completed / success
commit: docs: record phase 79 ci result
```

Absence check before publication:

```text
git tag -l 'v0.1*'
(no output)

git ls-remote --tags origin 'v0.1*'
(no output)

gh release view v0.1.0-readonly
release not found
```

Required local checks before publication:

```text
cd apps/api && pytest -q
282 passed, 27 warnings

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

git diff --check
passed
```

### Post-publication verification

```text
git tag -l 'v0.1*'
v0.1.0-readonly

git ls-remote --tags origin 'v0.1*'
refs/tags/v0.1.0-readonly
refs/tags/v0.1.0-readonly^{} -> 8180d555d71feaaf008d3edafeaa24dffd3dcfdb

gh release view v0.1.0-readonly --json tagName,isPrerelease,url,publishedAt,targetCommitish
{"isPrerelease":true,"publishedAt":"2026-05-18T06:04:26Z","tagName":"v0.1.0-readonly","targetCommitish":"main","url":"https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly"}
```

### Files updated after publication

- `README.md` — current release/status links now point to `v0.1.0-readonly`.
- `CHANGELOG.md` — Phase 80 publication evidence entry added.
- `PROJECT_STATUS.md` — baseline advanced through Phase 80 and next-work guidance updated.
- `docs/handoff/phase-80.md` — this handoff.

### Safety confirmation

- `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default.
- Controlled writes remain experimental/post-MVP and disabled by default.
- GnuCash Desktop remains authoritative.
- The release remains pre-alpha, read-only by default, not production-ready, not security-audited, not hosted SaaS, not a GnuCash replacement, and not collaborative accounting.
- Phase 80 did not add application features, enable writes, start v0.2 work, or commit real financial/secrets/runtime artifacts.
