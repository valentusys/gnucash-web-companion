# Phase 211 — v0.2.4-writealpha release gate/publication

Date: 2026-05-21
Status: COMPLETE — release gate passed; `v0.2.4-writealpha` published as GitHub pre-release
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 10 only)

## Goal

Perform the final release gate for cycle 1 and publish `v0.2.4-writealpha` only if Phases 202–210 produced safe material changes/evidence and exact release-commit CI is green.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-210.md`, and the cycle-1 roadmap file.
- Compared README/README.ru, PROJECT_STATUS, CHANGELOG, release docs, dogfood evidence, GitHub releases, recent GitHub Actions, and open issues.
- Confirmed `v0.2.4-writealpha` local tag, remote tag, and GitHub release were absent before publication.
- Confirmed starting tracked tree was clean except untracked `.hermes/`, and starting `HEAD == origin/main`.
- Prepared conservative release artifacts for `v0.2.4-writealpha`:
  - `docs/release/v0.2.4-writealpha-notes.md`
  - `docs/release/v0.2.4-writealpha-checklist.md`
  - `docs/release/v0.2.4-writealpha-final-gate.md`
  - `docs/release/v0.2.4-writealpha-publication-evidence.md`
- Updated `README.md`, `README.ru.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` to record the Phase 211 release gate/publication state.
- Ran local release-critical verification.
- Committed and pushed the release/status commit to `origin/main`.
- Waited for GitHub Actions on the exact release/status commit to complete successfully before publication.
- Rechecked `HEAD == origin/main`, clean tracked tree except `.hermes/`, and tag/release absence immediately before tagging.
- Created annotated tag `v0.2.4-writealpha`, pushed it, and created the GitHub pre-release from `docs/release/v0.2.4-writealpha-notes.md`.
- Verified local tag, remote tag, and GitHub pre-release point to the release/status commit.

## Files changed

- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/release/v0.2.4-writealpha-notes.md`
- `docs/release/v0.2.4-writealpha-checklist.md`
- `docs/release/v0.2.4-writealpha-final-gate.md`
- `docs/release/v0.2.4-writealpha-publication-evidence.md`
- `docs/handoff/phase-211.md`

No product code, write endpoint behavior, Docker image, package, binary artifact, production deployment, or write default changed in this phase.

## Verification summary

Commands/results:

```text
git status --short --branch
# clean tracked tree except untracked .hermes before release edits; clean tracked tree after publish

git fetch origin main --tags --prune
git rev-parse HEAD origin/main
# starting HEAD matched origin/main; release/status commit matched origin/main before publication

git tag -l v0.2.4-writealpha
git ls-remote --tags origin refs/tags/v0.2.4-writealpha
gh release view v0.2.4-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish
# absent before publication; present after publication and points to the release/status commit

cd apps/api && pytest -q
# passed

cd apps/web && npm run check
# passed

cd apps/web && npm run test:auth-routes
# passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# passed: API and web render GNUCASH_WRITES_ENABLED: "false"

grep -n 'GNUCASH_WRITES_ENABLED' .env.example
# passed: default false

git diff --check
# passed

python3 sensitive tracked-file hygiene scan
# passed

gh run watch <release-status-run-id> --exit-status
# passed for exact release/status commit before tag/release creation
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default in `.env.example` and rendered Compose.
- Write-alpha execution remains explicit local `GNUCASH_WRITES_ENABLED=true` plus `APP_ENV=test` only.
- Release documentation keeps evidence limited to synthetic/disposable fixture/copy paths.
- No stable release, package, binary, Docker image, production deployment, public-hosting claim, production/security claim, broad compatibility claim, or real/private/only-copy write-safety claim was added.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw private path, account name, memo, amount, runtime book, or private financial data was committed.

## Published release

- Tag: `v0.2.4-writealpha`
- GitHub release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.4-writealpha
- Publication type: GitHub pre-release only.

## Risks / follow-up

- Write-alpha remains experimental, disabled by default, and test-gated.
- Real/private-book write safety is not established.
- Compatibility evidence remains intentionally narrow; Desktop-generated synthetic fixture work remains future work.
- The project remains pre-alpha, not production-ready, and not security-audited.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
