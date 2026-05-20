# Phase 221 handoff — v0.2.5-writealpha release gate no-release verdict

Date: 2026-05-21
Status: COMPLETE — release gate failed safely; no tag or GitHub pre-release was published.

## Summary

Phase 221 performed the final cycle-2 release gate for candidate `v0.2.5-writealpha`.

The gate accepted that Phases 212–219 and the default-read-only portion of Phase 220 produced useful, safe changes/evidence with `GNUCASH_WRITES_ENABLED=false` intact. However, Phase 220 recorded a bounded write-alpha DELETE backup-count anomaly after a successful synthetic/disposable DELETE route execution: redacted audit evidence showed three successful backup-bearing route-family audit rows but only two backup files.

Because a write-alpha release requires clean bounded create/PATCH/DELETE backup/audit evidence, `v0.2.5-writealpha` was not published.

## Files changed

- `docs/release/v0.2.5-writealpha-notes.md` — conservative no-release release-note artifact.
- `docs/release/v0.2.5-writealpha-checklist.md` — release checklist with failed dogfood evidence gate.
- `docs/release/v0.2.5-writealpha-final-gate.md` — final release gate with explicit FAIL verdict.
- `docs/release/v0.2.5-writealpha-no-release-verdict.md` — blocker and next safe engineering phase.
- `README.md`, `README.ru.md`, `docs/ROADMAP.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, and `scripts/check_public_status.py` — public status synchronized to completed Phase 221 while keeping current public write-alpha release at `v0.2.4-writealpha`.
- `apps/api/tests/test_public_status_guard.py` — guard expectation updated to Phase 221.

No product code, write route, write gate, runtime default, package, image, tag, or release was changed.

## Verification performed

Pre-edit reconnaissance:

- `git fetch origin main --tags --prune` — passed.
- `HEAD == origin/main` at starting commit `f2b2fd6b3160cef7518b6ce270ef26bd9e1c088c` — passed.
- Local tag `v0.2.5-writealpha` absent — passed.
- Remote tag `v0.2.5-writealpha` absent — passed.
- GitHub release `v0.2.5-writealpha` absent — passed.
- `gh auth status` — passed.
- `gh run list --branch main --limit 5` — inspected; current starting-head CI was in progress during reconnaissance, previous failed runs were from earlier non-final commits.
- `gh issue list --state open --limit 20` — inspected; #36 remains the relevant controlled-write readiness tracking issue.

Local checks:

- `cd apps/api && pytest -q` — passed (`521 passed`, existing warnings only).
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- Rendered Compose grep — passed; API and web keep `GNUCASH_WRITES_ENABLED: "false"`.
- `.env.example` grep — passed; `GNUCASH_WRITES_ENABLED=false`.
- `git diff --check` — passed before docs edits; rerun after edits in final verification.
- Sensitive tracked-file hygiene scan — passed.
- `python3 scripts/check_public_status.py` — passed before docs edits; rerun after guard/status edits in final verification.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` gate was not weakened.
- No real/private/only-copy book was used.
- No `.env`, app DB, runtime book, backup, screenshot, export, token, key, cert, raw private path, account name, memo, amount, or private financial data was committed.
- No release tag, GitHub release, package, binary, Docker image, or production deployment was published.
- Release docs explicitly deny production readiness, security audit, broad compatibility, public-internet safety, and real/private-book write safety.

## Risks / blockers

Release blocker: Phase 220 DELETE backup-count anomaly. Default-read-only evidence is green, but cycle-2 write-alpha release evidence is not clean enough for publication.

## Next

Next safe engineering phase: investigate/remediate the DELETE backup-count anomaly with targeted tests/helper checks, rerun bounded synthetic/disposable create/PATCH/DELETE write-alpha evidence and default-read-only reset smoke, then run a fresh release gate only if green.
