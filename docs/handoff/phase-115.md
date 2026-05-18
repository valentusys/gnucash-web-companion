# Phase 115 — v0.1.2-readonly maintenance release prep

Date: 2026-05-19
Status: complete
Related roadmap item: analyst Phase 10
Target release candidate: `v0.1.2-readonly`
PM brief: `docs/handoff/phase-115-pm-brief.md`

## Summary

Phase 115 prepared conservative `v0.1.2-readonly` maintenance release artifacts and a final release-gate verdict after the Phase 106–114 read-only UX/filter/books/scheduled/localization/dogfood work.

This phase did not publish a tag, create a GitHub release, upload packages, enable writes, or change public release state.

## PM decision

Proceed with release-prep/gate artifacts because Phases 106–114 delivered meaningful read-only improvements. Keep the result as a non-published maintenance candidate only: no tag, no release, no package publish, and no write-mode or v0.2 scope.

## Implementation

Created release-prep artifacts:

- `docs/release/v0.1.2-readonly-notes.md`
  - summarizes Phases 106–114 as a possible read-only maintenance candidate;
  - keeps pre-alpha, read-only default, not production-ready, not security-audited, test disposable/copy books first, and no direct public-internet exposure language;
  - explicitly states that publication was not authorized in Phase 115.
- `docs/release/v0.1.2-readonly-checklist.md`
  - records candidate scope, completed evidence, safety checklist, open limitations, and exact publish commands as placeholders only;
  - explicitly forbids running publish commands without separate Val authorization.
- `docs/release/v0.1.2-readonly-final-gate.md`
  - records full verification results and verdict `Ready for later authorized publish phase`.

Updated release/status docs:

- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-115-pm-brief.md`
- `docs/handoff/phase-115.md`

## Release-gate verdict

`Ready for later authorized publish phase`.

All required Phase 115 checks passed. A future publish phase may create `v0.1.2-readonly` only after separate explicit Val authorization and immediate re-check of tag/release absence.

## Safety

- `GNUCASH_WRITES_ENABLED=false` remains the release posture.
- No backend, frontend, Docker, auth, or write-mode code was changed.
- No write endpoint/service behavior was changed.
- No tag, GitHub release, package, or public release artifact was published.
- No personal/private GnuCash book was used or searched for.
- No screenshots, CSV exports, app DBs, GnuCash books, backups, `.env`, secrets, tokens, cookies, certs, keys, private paths, account names from real data, transaction descriptions from real data, memos, real amounts, or personal financial data were committed.
- No production-readiness, security-audited, hosted-SaaS, broad compatibility, family-wallet, collaborative-accounting, or personal-book dogfood success claim was added.
- Money logic was not changed; no float money logic or fake currency conversion was added.

## Verification

Passed:

```bash
cd apps/api && pytest -q
# 349 passed, 27 warnings in 131.85s

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed

python sensitive tracked-file scan over git ls-files with synthetic fixture allowlist
# PASS: no unexpected tracked sensitive artifact names

git tag --list 'v0.1.2-readonly'
# no output

gh release view v0.1.2-readonly || true
# release not found

gh run list --limit 10 --json status,conclusion,headBranch,displayTitle,url
# latest 10 listed main runs completed/success
```

## Files changed

- `docs/handoff/phase-115-pm-brief.md`
- `docs/handoff/phase-115.md`
- `docs/release/v0.1.2-readonly-notes.md`
- `docs/release/v0.1.2-readonly-checklist.md`
- `docs/release/v0.1.2-readonly-final-gate.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## GitHub

- `gh` is authenticated as `valentusys`.
- Recent GitHub Actions `main` runs are successful through Phase 114.
- No `v0.1.2-readonly` GitHub release exists.
- No GitHub issue was closed by this release-prep phase.
- #38 remains open/blocked for future personal copied-book dogfood.

## Commit/push

- Commit: pending at handoff creation time; final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
