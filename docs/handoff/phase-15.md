# Phase 15 Handoff — Public Pre-Alpha Release Readiness

## Status

Complete.

## Summary

Prepared the repository for a responsible first public pre-alpha release candidate:

```text
v0.0.1-prealpha
```

This phase did not add product features. It added release documentation, backlog/issue drafts, manual GitHub release instructions, and explicit v0.2 controlled-write design boundaries.

## Safety status

Confirmed/maintained:

- writes disabled by default: yes (`GNUCASH_WRITES_ENABLED=false`)
- v0.1 remains read-only: yes
- no production-readiness claim: yes
- no security-audit claim: yes
- controlled writes documented as post-MVP/experimental only: yes

## Files changed

Important files:

- `README.md`
- `PROJECT_STATUS.md`
- `docs/v0.2-controlled-writes.md`
- `docs/release/v0.0.1-prealpha-checklist.md`
- `docs/release/v0.0.1-prealpha-notes.md`
- `docs/github/labels-to-create.md`
- `docs/github/milestones-to-create.md`
- `docs/github/manual-release-instructions.md`
- `docs/github/issues/*.md`
- `docs/handoff/phase-15.md`

## Checks run

Passed on 2026-05-17:

- `cd apps/api && pytest -q` — 167 passed, 1 skipped, 7 warnings
- `cd apps/web && npm run check` — 0 errors, 0 warnings
- `cd apps/web && npm run test:auth-routes` — passed
- `cd apps/web && npm run build` — passed
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed
- `git diff --check` — passed

## GitHub automation

- `git`: available.
- `gh`: not installed.
- `GITHUB_TOKEN`: not available in environment.
- labels: local instruction file created.
- milestones: local instruction file created.
- issues: local issue files created under `docs/github/issues/`.
- release/tag: tag can be pushed with git after checks; GitHub pre-release requires manual UI steps or future `gh`/API auth.

## Release status

- tag: `v0.0.1-prealpha` pushed with git
- pre-release: blocked for automation because `gh` is unavailable and no `GITHUB_TOKEN` is available
- manual instructions: `docs/github/manual-release-instructions.md`

## Known blockers

- GitHub issue/label/milestone/release automation is blocked by missing `gh` and missing `GITHUB_TOKEN`.
- Real disposable GnuCash SQL fixture validation is still pending and should be Phase 16.

## Next recommended phase

Phase 16 — Synthetic GnuCash fixture and real read-only integration validation.
