# Phase 85 — Post-v0.1 Personal Copied-Book Dogfood

## Status

Complete with blocker recorded. Phase 85 was a PM→Engineer post-release dogfood/runtime phase with no analyst/auditor role. No audit-only phase or `docs/audits/phase-85-audit.md` was created.

The requested copied personal GnuCash SQL book was not available to this execution environment outside git, so the phase did not claim a successful real-book dogfood pass. A durable redacted dogfood result artifact was created, a GitHub follow-up issue was opened, required non-real-book checks were run, and the blocker is recorded without private data.

No new tag/release was published. No scope expansion was made. Writes were not enabled. `GNUCASH_WRITES_ENABLED=false` remains the documented/configured default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DB, backups, screenshots/exports with real financial data, secrets, tokens, certs, or keys were committed.

## PM report

### Decision

Execute exactly Phase 85 as a safe copied personal-book dogfood attempt. If a safe copied personal SQL book is unavailable, do not invent success; record a redacted blocker/result artifact and track the follow-up.

### Why

The roadmap explicitly requires post-v0.1 real personal copied-book dogfood after `v0.1.0-readonly` publication and after Phase 84. This phase touches real-data handling, so the scope must stay narrow and safety-first: copied book only, original untouched, writes disabled, local-only access, and no private output committed.

### Phase brief

- Goal: run the read-only Docker app against a copied personal GnuCash SQL book outside git, or safely record the blocker if such a copy is unavailable.
- Non-goals: no analyst/auditor, no audit-only docs, no new release/tag, no write enablement, no v0.2 planning, no screenshots/exports/private data in git, no synthetic-only success claim.
- Acceptance criteria:
  - `docs/dogfood/phase-85-personal-copied-book-results.md` exists.
  - Real-book results are either recorded honestly or blocked honestly.
  - Any follow-up needed for real-book dogfood is tracked with evidence.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or skipped/runtime checks are explicitly justified by the unavailable private book.
  - Commit is pushed to `origin/main` and the working tree is clean.
- Safety checks:
  - Keep `GNUCASH_WRITES_ENABLED=false`.
  - Do not commit real books, `.env`, app DB, backups, secrets, screenshots, CSV exports, private account names, private amounts, or sensitive paths.
  - Keep local-only dogfood posture; no public exposure.
- Verification:
  - Required backend/frontend/docker config checks.
  - GitHub open issues and release/tag state verified.
  - Docker/browser/API real-book smoke is blocked because no safe copied personal SQL book is available.

### GitHub/backlog

- Created #38 to track rerunning the Phase 85 copied personal-book dogfood pass when a safe copied personal SQL book is available.
- No existing bug was closed without runtime evidence.

## Engineer report

### Concrete result

Created `docs/dogfood/phase-85-personal-copied-book-results.md`, documenting the safe scenario and the actual blocked result without private data.

Non-sensitive environment discovery found no usable copied personal GnuCash SQL book outside git. The local configuration keeps writes disabled, but the configured default-book target was not present in this environment. Only repo synthetic fixtures and temporary test-generated fixture books were discoverable, so a personal real-book Docker/browser/API dogfood pass could not be run honestly.

### Real-book dogfood checklist

Blocked because no copied personal SQL book was available:

- `/api/health`
- login
- dashboard
- accounts
- account detail
- transactions
- transaction detail
- filters
- CSV export
- write UI hidden
- write endpoints return 403

No screenshots, CSV exports, app DB, backups, real GnuCash books, `.env`, secrets, private account names, private amounts, or sensitive private paths were committed.

### Required checks

```text
cd apps/api && pytest -q
309 passed, 27 warnings

cd apps/web && npm run check
svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
auth route checks passed

cd apps/web && npm run build
built successfully

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
passed

git diff --check
passed
```

Release-state verification:

```text
git tag --list 'v0.1.0-readonly'
v0.1.0-readonly

gh release view v0.1.0-readonly --json tagName,isPrerelease,url,targetCommitish,publishedAt
{"isPrerelease":true,"publishedAt":"2026-05-18T06:04:26Z","tagName":"v0.1.0-readonly","targetCommitish":"main","url":"https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.0-readonly"}

gh issue view 38 --json number,state,url,title
{"number":38,"state":"OPEN","title":"Run Phase 85 copied personal-book dogfood when safe book is available","url":"https://github.com/valentusys/gnucash-web-companion/issues/38"}
```

Docker/browser/API smoke against the copied personal book was not feasible because no safe copied personal SQL book was available. This is recorded as a blocker, not a pass.

### Files changed

- `docs/dogfood/phase-85-personal-copied-book-results.md`
- `docs/handoff/phase-85.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

### GitHub/release

- GitHub #38 created for the blocked copied personal-book dogfood rerun.
- Existing `v0.1.0-readonly` remains the latest published GitHub pre-release.
- No new tag or release was created.

### Commit/push

To be filled after commit and push.
