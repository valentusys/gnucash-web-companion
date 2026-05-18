# Phase 94 — Post-v0.1 maintenance release decision

## Status

Complete. Phase 94 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-94-audit.md` were created.

No new tag/release was published. No `v0.1.1-readonly` release notes/checklist were created because PM did not approve release preparation yet. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

More fixes required before maintenance release.

Do not prepare or publish `v0.1.1-readonly` yet.

### Why

The post-`v0.1.0-readonly` change set is meaningful, but GitHub #39 remains an open and repeatedly reproduced read-only CSV export correctness issue: synthetic benchmark evidence showed the CSV body capped at 500 rows while headers reported a 10,000-row cap and `truncated=false`. Because CSV export is a user-facing read-only feature and Phase 84 changed export limit/truncation signaling, PM decision is to fix #39 before preparing a maintenance release candidate.

GitHub #38 also remains open for a future copied personal-book dogfood rerun when a safe copied SQL book is available. #38 does not by itself block a synthetic-data-only maintenance fix, but it prevents any personal-book dogfood success claim for a maintenance release.

### Phase brief

- Goal: decide whether enough post-v0.1 changes exist for `v0.1.1-readonly` and record a concrete maintenance-release decision without publishing a tag/release.
- Non-goals: no analyst/auditor, no audit-only artifact, no release publication, no `v0.1.1-readonly` notes/checklist unless PM approves release prep, no write-mode enablement, no v0.2 planning/work, no real/private data artifacts.
- Acceptance criteria:
  - One explicit Phase 94 verdict is recorded: prepare next, no release needed, or more fixes required.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Roadmap-specific release decision artifact exists.
  - GitHub issues/release state are verified and updated with evidence where relevant.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - `GNUCASH_WRITES_ENABLED=false` remains default.
  - No tag/GitHub release is published.
  - No real GnuCash book, private export, secret, `.env`, app DB, backup, key, cert, or token is committed.
  - No production-ready/security-audited/broad compatibility claim is added.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - `git tag`, `gh release list`, and open issue verification.

### GitHub/backlog

- GitHub #39 blocks `v0.1.1-readonly` release preparation until fixed with regression coverage and targeted export evidence.
- GitHub #38 remains open for copied personal-book dogfood rerun; do not claim personal-book coverage until completed safely.
- No new GitHub release or tag was created.

## Engineer report

### Concrete result

Created a durable maintenance-release decision artifact:

- `docs/release/v0.1.1-readonly-decision.md`

The artifact records:

- reviewed release/tag state;
- reviewed Phase 81–93 post-release changes;
- final verdict: `More fixes required before maintenance release`;
- specific blocker: GitHub #39 CSV export row-count/header mismatch;
- non-blocking-but-relevant open evidence gap: GitHub #38 copied personal-book dogfood rerun;
- minimum requirements before a future `v0.1.1-readonly` release-prep phase;
- safety constraints confirming no writes, no v0.2, no tag/release, and no private artifacts.

Updated required roadmap files:

- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-94.md`

### Required checks

```text
cd apps/api && pytest -q
PASS — 326 passed, 27 warnings

cd apps/web && npm run check
PASS — svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
PASS — auth route checks passed

cd apps/web && npm run build
PASS — production build completed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
PASS

git diff --check
PASS
```

### GitHub/release

- Release/tag state verified before and after the decision: existing tags/releases are only `v0.1.0-readonly`, `v0.0.2-prealpha`, and `v0.0.1-prealpha`.
- No `v0.1.1-readonly` tag or GitHub release exists or was created.
- Open issues verified. Relevant to this decision:
  - #39 remains open and blocks `v0.1.1-readonly` release preparation until fixed.
  - #38 remains open for copied personal-book dogfood rerun when a safe copied SQL book exists.
  - #36 remains open for post-MVP controlled-write readiness and is explicitly out of scope for this phase.

### Commit/push

Phase implementation commit:

- Current commit: `docs: record phase 94 maintenance decision`

Push evidence to be recorded after `git push origin main` succeeds.
