# Phase 86 — Fix Phase 85 Dogfood Blockers

## Status

Complete. Phase 86 was executed as a PM→Engineer phase with no analyst/auditor role. No audit-only phase and no `docs/audits/phase-86-audit.md` were created.

No new tag/release was published. No write-mode work was added or enabled. `GNUCASH_WRITES_ENABLED=false` remains the safe default. No v0.2 work was started. No real financial data, real GnuCash books, `.env`, app DBs, backups, secrets, tokens, certs, keys, private screenshots, or CSV exports with real data were committed.

## PM report

### Decision

Triage Phase 85 findings and do not pretend there is an app bug to fix. Phase 85 found no reproducible product bug such as account display, transaction detail, empty state, filter, CSV export, or dashboard failure. The only Phase 85 finding is a release-blocking dogfood input/environment blocker: no safe copied personal GnuCash SQL book was available outside git.

Because the user explicitly allowed a nearest valid maintenance/no-op result when Phase 85 had no concrete bugs, Phase 86 scope is a narrow maintenance fix for GitHub #38: add a safe redacted preflight helper so future dogfood attempts can classify a copied-book candidate before Docker/browser/API work, without leaking private paths or committing book data.

### Why

The roadmap says Phase 86 should fix only concrete bugs discovered during Phase 85. Phase 85 produced no concrete app bug, and #38 remains open until a safe copied personal book is provided. The useful, narrow result is to make that blocker less ambiguous and easier to verify safely next time.

### Triage

- Release blocker: no safe copied personal GnuCash SQL book was available to the execution environment outside git (#38).
- Usability issue: none found in Phase 85; runtime dogfood did not run.
- Known limitation: real-book dogfood cannot be claimed without a copied personal SQL book mounted outside git.
- Not reproducible: application/runtime bug class is not reproducible because Phase 85 never reached real-book runtime execution.

### Phase brief

- Goal: add a small tested copied-book preflight helper for the Phase 85/#38 blocker, without changing app behavior or expanding scope.
- Non-goals: no new end-user feature, no write-mode work, no broad refactor, no v0.2 work, no new release/tag, no fake dogfood success, no private-data artifact.
- Acceptance criteria:
  - Phase 85 findings are triaged into roadmap categories.
  - A regression test covers the maintenance result.
  - The helper does not expose private full paths in safe summaries.
  - GitHub #38 is updated with evidence and remains open until a safe copied book exists.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are updated.
  - Required checks pass or blockers are explicitly recorded.
  - Commit is pushed to `origin/main` and working tree is clean.
- Safety checks:
  - Keep `GNUCASH_WRITES_ENABLED=false`.
  - Do not open/parse/copy/export/screenshot/commit any real GnuCash book.
  - Do not print private directories or full candidate paths in the safe helper output.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check`
  - `cd apps/web && npm run test:auth-routes`
  - `cd apps/web && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`
  - GitHub issue/release/tag state verification.

### GitHub/backlog

- GitHub #38 is updated with Phase 86 evidence and kept open.
- No new issue is needed because no separate app bug exists.
- No release/tag publication.

## Engineer report

### Concrete result

Added a tested, redacted copied-book preflight helper:

- `apps/api/app/dogfood_preflight.py` — classifies a candidate copied book as `blocked` or `ready`, categorizes the result, and returns filename-only safe summaries.
- `apps/api/scripts/check_dogfood_book_candidate.py` — CLI wrapper for operators. It prints safe summaries only and exits non-zero for blocked candidates.
- `apps/api/tests/test_dogfood_preflight.py` — regression tests for missing candidates, candidates inside git, and existing candidates outside git, including assertions that private paths/directories are not present in safe summaries.

This does not fix an app runtime bug because Phase 85 did not discover one. It fixes the highest-priority dogfood blocker class that can be addressed in-code without private data: unsafe/ambiguous copied-book candidate preflight.

### Dogfood scenario after fix

The real copied personal-book Docker/browser/API dogfood scenario remains blocked until #38 has a safe copied personal SQL book outside git. Phase 86 does not claim a real-book pass.

Safe preflight smoke evidence:

```text
python apps/api/scripts/check_dogfood_book_candidate.py /tmp/missing-private/main.gnucash.sqlite
status=blocked; category=release blocker; book=main.gnucash.sqlite; reason=candidate book path does not exist
exit code 2 as expected for a blocked candidate
```

### Required checks

```text
cd apps/api && pytest -q
312 passed, 27 warnings

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
git tag --list 'v*'
v0.0.1-prealpha
v0.0.2-prealpha
v0.1.0-readonly

gh release list --limit 10
v0.1.0-readonly, v0.0.2-prealpha, and v0.0.1-prealpha are still the only listed pre-releases.
```

### Files changed

- `apps/api/app/dogfood_preflight.py`
- `apps/api/scripts/check_dogfood_book_candidate.py`
- `apps/api/tests/test_dogfood_preflight.py`
- `docs/handoff/phase-86.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`

### GitHub/release

- GitHub #38 updated with Phase 86 triage/preflight evidence and kept open.
- No new issue was created because no concrete Phase 85 app bug exists.
- No new tag or release was created.

### Commit/push

Phase commit: see the pushed `chore: add phase 86 dogfood preflight helper` commit on `origin/main`.
