# Phase 181 — final release-readiness gate and publication decision artifact

Date: 2026-05-20
Status: COMPLETE — unpublished `v0.2.1-writealpha` candidate prepared; no tag/release published
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 10 only)

## Goal

Produce a final release-readiness gate/artifact for the completed Phase 173–180 cycle; publish only if explicitly authorized and the gate is green.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-180.md`;
  - roadmap file named by the phase contract;
  - relevant release notes/checklists/final gates, changelog, README files, dogfood evidence, GitHub releases/actions, and Docker config.
- Compared docs/status/changelog/release notes against actual repository evidence and Phase 173–180 dogfood artifacts.
- Reviewed GitHub release state and recent GitHub Actions state.
- Confirmed default Docker Compose rendering keeps `GNUCASH_WRITES_ENABLED=false`.
- Prepared conservative unpublished release-readiness artifacts for a possible `v0.2.1-writealpha` maintenance pre-release.
- Updated public status docs to Phase 181 while keeping `v0.2.0-writealpha` as the current published write-alpha pre-release.
- Stopped before publication because this phase did not include explicit owner authorization to create a tag/GitHub release.

## Files changed

- `docs/release/v0.2.1-writealpha-notes.md`
- `docs/release/v0.2.1-writealpha-checklist.md`
- `docs/release/v0.2.1-writealpha-final-gate.md`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-181.md`

## Gate verdict

`Ready for release after explicit owner authorization — prepared but unpublished`.

A release candidate is warranted because Phases 173–180 produced meaningful copied/disposable dogfood evidence and write-alpha UX/API hardening after the published `v0.2.0-writealpha` pre-release. However, Phase 181 is not explicit owner authorization to publish. No tag, GitHub release, package, binary artifact, image, production deployment, or upload was created.

## Verification summary

Commands/results recorded for this phase:

```bash
git status --short
git rev-parse HEAD origin/main
gh release list --limit 10
gh run list --limit 10
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
git diff --check
# sensitive tracked-file hygiene scan over git ls-files
```

Results:

- Starting tracked tree was clean except untracked `.hermes/`, intentionally excluded.
- Starting `HEAD` and `origin/main` both pointed to `869879879f0b69cf62ea39714c3f69a2d6c11e11`.
- `gh release list --limit 10` showed existing releases through `v0.1.7-readonly` and `v0.2.0-writealpha`; no `v0.2.1-writealpha` release existed.
- `gh run list --limit 10` showed latest ten `main` CI runs completed/success, including Phase 180.
- Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- Backend suite passed: `404 passed, 33 warnings in 156.90s`.
- Frontend check passed: `svelte-check found 0 errors and 0 warnings`.
- Frontend auth-route checks passed: `auth route checks passed`.
- Frontend production build passed.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Write-alpha execution remains experimental and requires explicit local enablement plus `APP_ENV=test`.
- Write-alpha evidence remains synthetic/disposable or copied-test-book only.
- No real/private/only-copy book was used in this phase.
- No production readiness, security audit, hosted SaaS readiness, broad GnuCash compatibility, or real/private-book write-safety claim was added.
- No real/private book, app DB, backup, `.env`, token, key, cert, screenshot, export, package/image artifact, private path, or private financial data was committed.

## Next

If publication is desired, run a separate explicitly authorized publish phase. Before any tag/GitHub release, re-check clean tracked `main`, `HEAD == origin/main`, local/remote tag absence, GitHub release absence, local checks, rendered `GNUCASH_WRITES_ENABLED=false`, sensitive tracked-file hygiene, and GitHub Actions success for the exact release commit.
