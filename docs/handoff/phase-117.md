# Phase 117 — publish v0.1.2-readonly

Date: 2026-05-19
Status: in progress at handoff creation; final publish verification is recorded in executor stdout
Target: `v0.1.2-readonly`
Previous phase: `docs/handoff/phase-116.md`
Release notes: `docs/release/v0.1.2-readonly-notes.md`

## Summary

Phase 117 is the explicitly authorized release-executor phase for `v0.1.2-readonly` after Phase 116 / GitHub #38 copied personal-book dogfood completed PASS and issue #38 was closed.

This phase is intentionally narrow:

- update release/status documentation to include Phase 116/#38 evidence;
- re-run publication preflight;
- commit/push documentation/status updates;
- create an annotated git tag;
- create a GitHub pre-release from the local release notes;
- publish no packages.

## Preflight required before publication

Required immediate checks before tag/release creation:

- `git status --short` clean before edits.
- `git fetch origin main --tags`.
- `HEAD == origin/main`.
- GitHub #38 state is `CLOSED`.
- `git tag --list v0.1.2-readonly` has no output.
- `gh release view v0.1.2-readonly` reports release not found.
- Recent GitHub Actions for `main` are completed/success through the Phase 116 pushed commit.

## Documentation/status updates

Updated in this phase before publication:

- `docs/release/v0.1.2-readonly-notes.md` — includes Phase 116 redacted copied personal-book dogfood PASS and publication status.
- `docs/release/v0.1.2-readonly-checklist.md` — includes Phase 116 evidence, issue #38 closed, and Phase 117 publication commands.
- `docs/release/v0.1.2-readonly-final-gate.md` — refreshes the Phase 115 gate with Phase 116/#38 evidence and Phase 117 authorization.
- `PROJECT_STATUS.md` — advances baseline through Phase 117 and records publication intent/state.
- `CHANGELOG.md` — opens `0.1.2-readonly` section and records the publish phase.
- `docs/handoff/phase-117.md` — this handoff.

## Verification for this docs/publish phase

Required checks:

```bash
git diff --check
python sensitive tracked-file scan over git ls-files with synthetic fixture allowlist
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Full backend/frontend suites are not required for this phase because no product code changes are made; Phase 115 full backend/frontend release gate and Phase 116 dogfood evidence are referenced instead.

## Publication commands

Only after all checks pass:

```bash
git add PROJECT_STATUS.md CHANGELOG.md docs/release/v0.1.2-readonly-notes.md docs/release/v0.1.2-readonly-checklist.md docs/release/v0.1.2-readonly-final-gate.md docs/handoff/phase-117.md
git commit -m "docs: publish v0.1.2-readonly release"
git push origin main
git tag -a v0.1.2-readonly -m "v0.1.2-readonly"
git push origin v0.1.2-readonly
gh release create v0.1.2-readonly --title "v0.1.2-readonly" --notes-file docs/release/v0.1.2-readonly-notes.md --prerelease
```

## Safety

- `GNUCASH_WRITES_ENABLED=false` remains default.
- Controlled writes remain post-MVP/experimental and disabled by default.
- No packages are published.
- No private GnuCash book, source archive, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or real/private financial data is committed.
- GnuCash Desktop remains the authoritative editor.
- The release remains pre-alpha, read-only by default, not production-ready, and not security-audited.

## Final verification after publication

Required final checks:

```bash
git ls-remote --tags origin refs/tags/v0.1.2-readonly
gh release view v0.1.2-readonly --json tagName,isPrerelease,url,targetCommitish,publishedAt
git status --short
```

The final commit SHA, tag object/target, release URL, and check results are reported in the release executor stdout and Telegram report.
