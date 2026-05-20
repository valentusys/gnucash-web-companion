# Phase 192 — CI/toolchain warning cleanup

Date: 2026-05-20
Status: COMPLETE — CI/toolchain wiring updated; local checks passed; exact pushed CI passed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 1 only)

## Goal

Remove the known non-blocking Node.js 20 deprecation warning in GitHub Actions after `v0.2.2-writealpha` without changing product behavior.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-191.md`;
  - roadmap file named by the phase contract;
  - relevant CI workflow and support docs.
- Updated only CI/toolchain wiring that caused Node.js 20 action-runtime warnings:
  - all existing `actions/checkout@v4` uses in `.github/workflows/ci.yml` now use `actions/checkout@v5`;
  - the frontend setup action now uses `actions/setup-node@v6`;
  - the backend setup action now uses `actions/setup-python@v6`.
- Preserved existing CI jobs and checks:
  - `foundation` still verifies required publication files and tracked sensitive-file guard;
  - `frontend` still installs the web app, conditionally runs lint, then runs `npm run check`, `npm run test:auth-routes`, and `npm run build`;
  - `backend` still installs API dependencies and runs `python -m pytest tests/ -q`;
  - `compose` still runs Docker Compose config validation.
- Updated support artifacts only:
  - `PROJECT_STATUS.md`;
  - `CHANGELOG.md`;
  - this handoff.

## Files changed

- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-192.md`

No API/UI business logic, Docker runtime defaults, write behavior, release/tag, or GitHub issue state was changed.

## Before / after evidence

Before:

- Phase 191 recorded a non-blocking GitHub Actions Node.js 20 deprecation warning for `actions/checkout@v4`.
- The workflow used `actions/checkout@v4` in all four existing jobs.

After:

- The workflow uses Node 24-compatible action major versions in the same jobs: `actions/checkout@v5`, `actions/setup-node@v6`, and `actions/setup-python@v6`.
- No workflow steps were added that print secrets.
- The exact pushed CI run passed without Node.js 20 action deprecation warnings.

## Verification summary

Local commands/results:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
grep -n 'GNUCASH_WRITES_ENABLED' .env.example
git diff --check
# sensitive tracked-file hygiene scan from phase execution playbook
```

Results:

- Backend test suite passed.
- Frontend `npm run check` passed.
- Frontend `npm run test:auth-routes` passed.
- Frontend `npm run build` passed.
- Docker Compose config validation passed.
- Rendered Compose kept `GNUCASH_WRITES_ENABLED: "false"`.
- `.env.example` kept `GNUCASH_WRITES_ENABLED=false`.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.
- GitHub Actions exact pushed run passed after `git push origin main`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No `.env`, real/private book, app DB, backup, token, key, cert, screenshot, export, or private financial artifact was created or committed.
- No write-enabled dogfood was run.
- No release/tag was published.
- No GitHub issue was created, closed, or modified.

## Risks / follow-up

- The project remains pre-alpha, not production-ready, and not security-audited.
- Write-alpha remains experimental and unsafe for real/private or only-copy books.
- This phase is CI/toolchain-only; it does not change product behavior or evidence from `v0.2.2-writealpha`.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
