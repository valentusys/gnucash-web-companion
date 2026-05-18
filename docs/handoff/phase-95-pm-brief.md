# Phase 95 PM Brief — Fix CSV export row-count/header mismatch (#39)

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`

## Decision

Plan Phase 95 as the next practical engineering phase: fix GitHub #39, the read-only CSV export row-count/header mismatch.

## Why this phase now

`PROJECT_STATUS.md`, Phase 94 handoff, the analyst 10-phase plan, and GitHub #39 all agree that `v0.1.1-readonly` release preparation is blocked by a user-facing read-only CSV export correctness bug. Recent synthetic benchmark evidence shows `GET /books/{book_id}/transactions/export` advertising a 10,000-row export cap and `X-CSV-Export-Truncated: false` for a 1,000-transaction book while the CSV body contains only 500 data rows.

This is practical product work, not audit-only/docs-only work. It preserves the read-only MVP boundary and directly unblocks later maintenance-release preparation.

## Goal

Make CSV export body row count, `X-CSV-Export-Limit`, `X-CSV-Export-Total`, and `X-CSV-Export-Truncated` internally consistent for exports above the normal transaction-list pagination limit and up to the documented 10,000-row CSV cap.

## Non-goals

- Do not enable or expand write-mode functionality.
- Do not change the default `GNUCASH_WRITES_ENABLED=false` posture.
- Do not add import, OFX/CSV ingestion, async exports, background jobs, new export formats, or streaming infrastructure beyond what is needed for the fix.
- Do not use, create, commit, or screenshot real/private financial data.
- Do not publish a tag or GitHub release.
- Do not prepare `v0.1.1-readonly` release notes/checklist in this phase; that belongs after #39 is fixed and verified.
- Do not turn this into a broad performance/audit phase.

## Acceptance criteria

- A regression test proves the mismatch path for more than 500 matching transactions.
  - Preferred: create synthetic/fake export data with at least 501 rows and assert the CSV body row count matches the response headers.
  - The test should fail before the fix or clearly target the exact bug source.
- `GET /books/{book_id}/transactions/export` returns consistent CSV metadata semantics:
  - `X-CSV-Export-Limit` remains the documented CSV cap, currently `10000`.
  - `X-CSV-Export-Total` reports the total matching transactions before the CSV cap.
  - `X-CSV-Export-Truncated` is `false` when total is at or below the cap and body rows equal total.
  - `X-CSV-Export-Truncated` is `true` only when total exceeds the cap and body rows equal the cap.
- CSV export is not silently capped by the normal list endpoint pagination limit (`limit <= 200`) or by the historical 500-row service/default clamp.
- Existing CSV filters still work: `account_id`, `date_from`, `date_to`, `query`, `min_amount`, `max_amount`.
- The SvelteKit export proxy at `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` forwards the corrected CSV headers unchanged.
- Existing frontend export URLs continue to preserve current filters.
- GitHub #39 is updated with evidence and closed only if the fix is proven by tests and targeted export smoke/benchmark.
- `PROJECT_STATUS.md` and a completion handoff `docs/handoff/phase-95.md` are updated by the engineer with evidence.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` must remain the default in settings/examples/docs.
- No write routes, write services, backup/write-lock behavior, or controlled-write UI should be modified unless a test import path forces harmless refactoring; any such change must be justified in the engineer report.
- Use only generated synthetic/fake data or committed synthetic fixtures.
- Do not commit real GnuCash books, app DBs, backups, `.env`, secrets, tokens, certs, keys, private screenshots, or real CSV exports.
- Preserve Decimal/string money handling; do not introduce float-based money calculations.
- Do not add production-ready, security-audited, broad compatibility, or personal-book dogfood claims.
- Keep `GET /books/{book_id}/transactions/export` declared before `GET /books/{book_id}/transactions/{transaction_id}` to avoid the known `/export` path collision.

## Verification required from engineer

Run and report:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

Also run a targeted CSV export verification above 500 rows, preferably using the existing large-book benchmark path:

```bash
cd apps/api
python apps/api/scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-95-csv-export-check.json
```

If that command path needs adjustment because the script already changes to `apps/api`, use the working repository-relative invocation and document the exact command. The report must include: CSV body data-row count, `X-CSV-Export-Limit`, `X-CSV-Export-Total`, `X-CSV-Export-Truncated`, and whether body rows match the expected total/cap.

## Files/docs to update

Likely code/test files:

- `apps/api/app/routers/transactions.py`
- `apps/api/app/services/gnucash_book.py` or the transaction service file that applies list/export limits, if the root cause is service-level clamping
- `apps/api/tests/test_transaction_export.py`
- `apps/api/app/performance/large_book_benchmark.py` only if benchmark row counting/header recording needs a narrow correction
- `apps/web/src/routes/books/[bookId]/transactions/export/+server.ts` only if proxy header forwarding is missing or needs a regression check
- `apps/web/scripts/test-auth-routes.mjs` or an equivalent frontend test if proxy/header behavior is changed

Required docs/evidence updates after implementation:

- `PROJECT_STATUS.md`
- `docs/handoff/phase-95.md`
- `CHANGELOG.md` if the project convention for user-facing bug fixes requires an Unreleased entry
- `docs/performance/phase-87-large-book-benchmark.md`, `phase-88`, or `phase-89` should not be rewritten historically; instead add Phase 95 evidence in the handoff and, if useful, a new narrow performance/evidence artifact.

## GitHub/backlog note

- GitHub #39 is the primary issue for this phase.
- Update #39 with regression and targeted export evidence.
- Close #39 only if the fix is verified and pushed.
- Keep #38 open; personal copied-book dogfood is separate and blocked until a safe copied SQL book is provided outside git.
- Do not create new backlog issues unless implementation uncovers a distinct blocker that cannot be fixed in this narrow phase.

## Exact engineer instructions

1. Start from current `main` and verify the worktree is clean.
2. Read this brief, `AGENTS.md`, `PROJECT_STATUS.md`, Phase 94 handoff, the analyst 10-phase plan, and GitHub #39.
3. Reproduce or target the mismatch with a test involving more than 500 matching export rows.
4. Identify whether the bug is in the export route, service-layer limit handling, benchmark row counting, or a combination.
5. Fix only the CSV export correctness path. Keep normal transaction-list pagination limits unchanged.
6. Ensure export semantics are consistent for:
   - total below/equal to cap;
   - total above normal list pagination limit;
   - total above CSV cap, if cheap to test with fake data.
7. Ensure the frontend export proxy continues to forward CSV metadata headers unchanged.
8. Run the full required verification plus targeted >500-row export smoke/benchmark.
9. Update `PROJECT_STATUS.md` and create `docs/handoff/phase-95.md` with evidence, row counts/header values, safety statement, GitHub #39 status, checks run, commit hash, and push evidence.
10. Update/close GitHub #39 only when evidence is complete.
11. Commit implementation with a concise message such as `fix: align csv export row counts`, push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 95 title and one-sentence result.
- What changed in code/tests.
- Exact CSV export evidence: body data rows, `X-CSV-Export-Limit`, `X-CSV-Export-Total`, `X-CSV-Export-Truncated` for the >500-row synthetic check.
- Whether GitHub #39 was updated/closed.
- Safety statement: writes remain disabled by default; no real/private financial data committed; no release/tag published.
- Verification summary: backend, frontend check/auth-routes/build, Docker config, `git diff --check`.
- Commit hash and push status.
