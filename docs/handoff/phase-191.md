# Phase 191 — Cycle-2 release-readiness gate and publication/no-release artifact

Date: 2026-05-20
Status: COMPLETE — release-readiness gate passed; `v0.2.2-writealpha` published as GitHub pre-release after exact release-commit CI
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 10 only)

## Goal

Perform the final cycle-2 release-readiness gate and publish only if evidence warrants it and the exact release commit is green; otherwise produce an honest no-release artifact.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-190.md`;
  - roadmap file named by the phase contract;
  - relevant README/README.ru/CHANGELOG/release/dogfood docs;
  - GitHub releases, Actions, and open issues.
- Compared actual `main` against public docs and release evidence.
- Selected target release `v0.2.2-writealpha` because cycle-2 contains write-alpha evidence and safety/operator hardening beyond `v0.2.1-writealpha`; a read-only-only maintenance tag would not match the scope.
- Confirmed local/remote tag and GitHub release absence before publication.
- Confirmed `GNUCASH_WRITES_ENABLED=false` in `.env.example` and rendered Docker Compose config.
- Ran local backend/frontend/Docker/diff/hygiene checks.
- Updated release notes/checklist/final gate/publication evidence and public status docs.
- Committed and pushed the release/status commit, waited for GitHub Actions on that exact commit to pass, then published the annotated tag and GitHub pre-release.

## Files changed

- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/release/v0.2.2-writealpha-notes.md`
- `docs/release/v0.2.2-writealpha-checklist.md`
- `docs/release/v0.2.2-writealpha-final-gate.md`
- `docs/release/v0.2.2-writealpha-publication-evidence.md`
- `docs/handoff/phase-191.md`

No product code or runtime default was changed.

## Verification summary

Commands/results recorded for this phase:

```bash
git status --short --branch
git fetch origin main --tags --prune
git rev-parse HEAD origin/main
git tag -l v0.2.2-writealpha
git ls-remote --tags origin refs/tags/v0.2.2-writealpha
gh release view v0.2.2-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
grep -n 'GNUCASH_WRITES_ENABLED' .env.example
git diff --check
# sensitive tracked-file hygiene scan from phase execution playbook
# after commit/push: gh run watch for the exact release/status commit
# after publication: local tag, remote tag, and GitHub release view checks
```

Results:

- Starting tracked tree was clean except untracked `.hermes/`, and starting `HEAD == origin/main`.
- `v0.2.2-writealpha` local tag, remote tag, and GitHub release were absent before publication.
- Backend suite passed.
- Frontend `npm run check`, `npm run test:auth-routes`, and `npm run build` passed.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `.env.example` kept `GNUCASH_WRITES_ENABLED=false`.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.
- GitHub Actions on the exact release/status commit passed before tagging.
- Post-publication tag/release checks passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-alpha remains explicit/local/test-gated via `APP_ENV=test` when enabled.
- Cycle-2 write evidence remains synthetic/disposable only.
- No real/private/only-copy book, app DB, backup, `.env`, token, key, cert, screenshot, raw CSV export, private path, account name, memo, amount, or private financial data was committed.
- No package, Docker image, binary artifact, production deployment, public-internet safety claim, production-readiness claim, security-audit claim, broad compatibility claim, or real/private-book write-safety claim was added.

## Release result

Published GitHub pre-release:

https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.2-writealpha

## Risks / follow-up

- Write-alpha remains experimental and unsafe for real/private or only-copy books.
- The project remains pre-alpha, not production-ready, and not security-audited.
- Open issues #36, #29, #28, #22, #17, and #13 remain non-blocking future work under the conservative release wording.
- GitHub Actions emitted a non-blocking Node.js 20 deprecation warning for `actions/checkout@v4`; handle in a later maintenance phase.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
