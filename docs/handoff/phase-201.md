# Phase 201 — Cycle-3 release-readiness gate and publication

Date: 2026-05-20
Status: COMPLETE — cycle-3 release gate passed; `v0.2.3-writealpha` published as conservative GitHub pre-release after exact release-commit CI passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 10 only)

## Goal

Perform the final release-readiness gate after cycle-3 Phases 192–200 and publish only if evidence warrants it and GitHub Actions for the exact release/status commit are green; otherwise create a no-release blocker artifact.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-200.md`, cycle-3 roadmap file, current README/README.ru/CHANGELOG, existing release artifacts, and Phase 199–200 dogfood evidence.
- Compared current public status and evidence against the cycle-3 candidate scope.
- Selected `v0.2.3-writealpha` because cycle-3 materially changed or validated write-alpha/operator readiness evidence after `v0.2.2-writealpha`.
- Confirmed candidate tag/release were absent before release artifact work.
- Prepared conservative release notes/checklist/final-gate/publication-evidence artifacts.
- Updated README, Russian README, CHANGELOG, PROJECT_STATUS, and this handoff.
- Ran local release-critical checks.
- Committed and pushed the release/status commit.
- Watched GitHub Actions for the exact release/status commit to success before publication.
- Rechecked clean main, `HEAD == origin/main`, tag/release absence, and write-disabled defaults immediately before publication.
- Published only the annotated git tag and GitHub pre-release.

## Files changed

- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/release/v0.2.3-writealpha-notes.md`
- `docs/release/v0.2.3-writealpha-checklist.md`
- `docs/release/v0.2.3-writealpha-final-gate.md`
- `docs/release/v0.2.3-writealpha-publication-evidence.md`
- `docs/handoff/phase-201.md`

## Verification summary

Commands/results:

```text
git status --short --branch
# clean tracked tree before release artifacts; only untracked .hermes/ excluded

git rev-parse HEAD && git rev-parse origin/main
# starting HEAD == origin/main: 3c306e6d72f9d3a1f883301f5162ead48676362d

git tag -l v0.2.3-writealpha
# absent before publication

git ls-remote --tags origin refs/tags/v0.2.3-writealpha
# absent before publication

gh release view v0.2.3-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish
# release not found before publication

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
# false rendered for API and web

grep -n 'GNUCASH_WRITES_ENABLED' .env.example
# GNUCASH_WRITES_ENABLED=false

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed

GitHub Actions on exact release/status commit
# passed before tag/release publication

post-publication checks
# local tag, remote tag, and GitHub pre-release exist and match the release/status commit
```

## Publication result

- Tag: `v0.2.3-writealpha`.
- Release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.3-writealpha
- Publication type: GitHub pre-release only.
- No package, binary artifact, Docker image, or production deployment was published.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and was verified in `.env.example` and rendered Docker Compose config.
- Write-alpha execution remains explicit local-only/test-only and requires `APP_ENV=test` when enabled.
- Release notes remain conservative: pre-alpha, experimental, synthetic/disposable evidence only, not production-ready, not security-audited, not safe for real/private or only-copy books.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.
- No `.hermes/` files were staged.

## Risks / follow-up

- Write-alpha remains experimental and disabled by default.
- Cycle-3 evidence is synthetic/disposable only and does not prove production or real/private-book write safety.
- Broad GnuCash Desktop/backend compatibility remains unclaimed; Phase 197 recorded the next safe Desktop-generated synthetic fixture requirement.
- Project remains pre-alpha and not security-audited.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
