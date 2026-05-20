# Phase 172 — public status reconciliation after v0.1.7/v0.2.0 publications

Date: 2026-05-20
Status: COMPLETE — docs/status/release artifacts reconciled; no product-code change
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-1-roadmap.md` (Phase 1 only)

## Goal

Synchronize public repository status after the already published `v0.1.7-readonly` and `v0.2.0-writealpha` GitHub pre-releases, without changing backend/frontend/Docker runtime behavior.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-171.md`;
  - roadmap file named by the phase contract.
- Kept this as Phase 172 only; no Phase 173 work was started.
- Updated public status docs to say Phase 0–172 are complete and `v0.1.7-readonly` is the current public read-only pre-alpha release.
- Reconciled `README.ru.md`, which still said Phase 0–169 and `v0.1.6-readonly` as current.
- Reconciled `docs/ROADMAP.md`, which still described the Phase 162 / `v0.1.6-readonly` baseline.
- Corrected stale current-state wording in `docs/release/v0.2.0-writealpha-*` that could still read as prepared / unpublished / not authorized, while preserving the historical fact that Phase 132 itself did not publish the tag/release.
- Preserved write-alpha warnings: experimental, pre-alpha, disabled by default, `APP_ENV=test` gate when enabled, synthetic/disposable or copied-test-book scope only, not safe for real/private or only-copy books.

## Files changed

- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/ROADMAP.md`
- `docs/release/v0.2.0-writealpha-notes.md`
- `docs/release/v0.2.0-writealpha-checklist.md`
- `docs/release/v0.2.0-writealpha-final-gate.md`
- `docs/handoff/phase-172.md`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the documented/default posture.
- No backend, frontend, Docker runtime, write gate, auth, product behavior, package, image, deployment, tag, or GitHub release was changed.
- No real/private book, app DB, backup, committed `.env`, screenshot/export, token, key, cert, private path, or private financial data was added.
- `v0.2.0-writealpha` remains an experimental pre-release only; no real/private-book write safety is claimed.

## Verification

Planned/required checks for this docs-only phase:

```bash
grep -R "GNUCASH_WRITES_ENABLED" .env.example docker-compose.yml apps/api/app/config.py docs/release README.md README.ru.md PROJECT_STATUS.md CHANGELOG.md
git diff --check
gh release list --limit 10
gh run list --limit 5
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git status --short
git diff --cached --name-only
# sensitive tracked-file hygiene scan
```

Results:

- `grep -R "GNUCASH_WRITES_ENABLED" .env.example docker-compose.yml apps/api/app/config.py docs/release README.md README.ru.md PROJECT_STATUS.md CHANGELOG.md` confirmed the write flag remains documented across config/status/release docs.
- Default confirmation: `.env.example` contains `GNUCASH_WRITES_ENABLED=false`; rendered Docker Compose config contains `GNUCASH_WRITES_ENABLED: "false"` for API and web at lines 15 and 65.
- `git diff --check` passed with no output.
- `gh release list --limit 10` confirmed the published GitHub pre-releases include `v0.1.7-readonly` and `v0.2.0-writealpha`.
- `gh run list --limit 5` showed the latest five `main` CI runs completed successfully.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` passed with no output.
- `git status --short` showed only intended docs/status changes plus untracked repo-local `.hermes/`.
- `git diff --cached --name-only` was empty before staging.
- Sensitive tracked-file hygiene scan passed.
- Docs-only diff review showed only markdown/status/release files changed; no product-code diff.

## Next

Continue only with the next explicitly requested phase. Do not start write-alpha copied-book dogfood or Phase 173 from this handoff unless a later phase contract explicitly asks for it.
