# Phase 182 — authorized v0.2.1-writealpha publication under fresh gate

Date: 2026-05-20
Status: COMPLETE — `v0.2.1-writealpha` published as an authorized GitHub pre-release
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 1 only)

## Goal

Publish the already prepared `v0.2.1-writealpha` only if a fresh pre-publish gate on current `main` is green and confirms no existing local/remote tag or GitHub release. If the gate fails, stop with a no-release artifact.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-181.md`;
  - roadmap file named by the phase contract;
  - relevant release notes/checklist/final gate, README files, CHANGELOG, `.env.example`, Docker Compose render, GitHub releases/actions, and backend write-gate references.
- Re-ran fresh pre-publish gate on current `main`.
- Confirmed tracked tree was clean except untracked `.hermes/`, intentionally excluded.
- Confirmed `HEAD == origin/main` before release/status doc updates.
- Confirmed local tag, remote tag, and GitHub release `v0.2.1-writealpha` were absent before publication.
- Confirmed `gh` authentication.
- Confirmed rendered Docker Compose kept `GNUCASH_WRITES_ENABLED=false` for API and web and `.env.example` default remained false.
- Ran local backend/frontend/Docker checks, `git diff --check`, and sensitive tracked-file hygiene scan.
- Updated publication/status artifacts and committed/pushed the release/status commit.
- Waited for GitHub Actions run `26140519337` on exact release/status commit `8c316b9f5c8028b519b603da0ba3cb37542bc4c0` to pass before tag/release publication.
- Published annotated tag and GitHub pre-release `v0.2.1-writealpha` from the prepared notes.
- Verified post-publication tag/release state and default-false Compose render.

## Files changed

- `docs/release/v0.2.1-writealpha-publication-evidence.md`
- `docs/release/v0.2.1-writealpha-notes.md`
- `docs/release/v0.2.1-writealpha-checklist.md`
- `docs/release/v0.2.1-writealpha-final-gate.md`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-182.md`

## Gate verdict

`PASS — publish authorized pre-release`.

The fresh gate passed and Phase 182 explicitly authorized publication if green. No no-release blocker was needed.

## Verification summary

Commands/results recorded for this phase:

```bash
git status --short
git fetch origin main --tags --prune
git rev-parse HEAD origin/main
git tag -l v0.2.1-writealpha
git ls-remote --tags origin refs/tags/v0.2.1-writealpha
gh auth status
gh release view v0.2.1-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish || true
gh run list --limit 10
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
git diff --check
# sensitive tracked-file hygiene scan over git ls-files
git push origin main
gh run watch <release-commit-run> --exit-status
git tag -a v0.2.1-writealpha -m "v0.2.1-writealpha"
git push origin v0.2.1-writealpha
gh release create v0.2.1-writealpha --title "v0.2.1-writealpha" --notes-file docs/release/v0.2.1-writealpha-notes.md --prerelease
gh release view v0.2.1-writealpha --json tagName,url,isPrerelease,isDraft,targetCommitish
git ls-remote --tags origin refs/tags/v0.2.1-writealpha
```

Results:

- Starting tracked tree was clean except untracked `.hermes/`, intentionally excluded.
- Starting `HEAD` and `origin/main` both pointed to `ee134ea221db89a83388ba64967a8c3a41fd4c2b`.
- Local tag, remote tag, and GitHub release `v0.2.1-writealpha` were absent before publication.
- `gh auth status` passed for account `valentusys`.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `.env.example` contains `GNUCASH_WRITES_ENABLED=false`.
- Backend suite passed: `404 passed` with existing warnings.
- Frontend `npm run check` passed with 0 errors / 0 warnings.
- Frontend auth-route checks passed.
- Frontend production build passed.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.
- GitHub Actions run `26140519337` on exact release/status commit `8c316b9f5c8028b519b603da0ba3cb37542bc4c0` passed before tag/release publication.
- Post-publication tag/release checks passed.

## Publication result

- Release URL: https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.2.1-writealpha
- Annotated tag: `v0.2.1-writealpha`
- GitHub release type: pre-release
- Release target: Phase 182 release/status commit `8c316b9f5c8028b519b603da0ba3cb37542bc4c0`; annotated tag object `a86bbcb3e70972b57eff89c1a305805f72ad0908`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-alpha execution remains experimental and requires explicit local enablement plus `APP_ENV=test`.
- Write-alpha evidence remains synthetic/disposable or copied-test-book only.
- No real/private/only-copy book was used in this phase.
- No production readiness, security audit, hosted SaaS readiness, broad GnuCash compatibility, public-internet safety, or real/private-book write-safety claim was added.
- No real/private book, app DB, backup, `.env`, token, key, cert, screenshot, export, package/image artifact, private path, or private financial data was committed.

## Next

Proceed only to the next roadmap phase when explicitly requested by the controller/user. Do not expand write-alpha scope or start Phase 2 from this session.
