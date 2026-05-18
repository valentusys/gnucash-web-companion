# Phase 96 PM Brief — Synthetic large-export benchmark and UX confirmation

Date: 2026-05-18
Role: Project Lead / PM
Status: planned for engineer implementation
Source roadmap: `docs/audits/2026-05-18-analyst-10-phase-plan.md`
Previous phase evidence: `docs/handoff/phase-95.md`

## Decision

Plan Phase 96 as the next practical engineering phase: confirm the Phase 95 CSV export fix through the synthetic large-export benchmark path and verify that user-facing CSV export copy stays honest and consistent.

## Why this phase now

Phase 95 fixed GitHub #39 and closed the release-blocking row-count/header mismatch for read-only CSV export. Before moving into `v0.1.1-readonly` release-prep documents, the project should record one practical follow-up evidence phase from the analyst roadmap: the existing synthetic benchmark path should prove the fixed behavior above the historical 500-row clamp, and the frontend copy should still explain that CSV exports are read-only, filtered, synchronous, and capped.

This is not an audit-only or docs-only phase. Documentation updates are allowed only as evidence/handoff around the benchmark and any narrow UX copy/test correction.

## Goal

Re-run or extend the synthetic large-book benchmark focused on CSV export after the Phase 95 fix, and confirm the UI/export copy does not mislead users about filtering, row caps, truncation, or read-only behavior.

## Non-goals

- Do not enable or expand write-mode functionality.
- Do not change the default `GNUCASH_WRITES_ENABLED=false` posture.
- Do not add async/background export infrastructure, streaming exports, new export formats, CSV customization, CSV/OFX import, or banking integrations.
- Do not use, create, commit, screenshot, or export real/private financial data.
- Do not publish a tag or GitHub release.
- Do not prepare `v0.1.1-readonly` release notes/checklist in this phase; that is Phase 97 after Phase 96 evidence is recorded.
- Do not make performance overclaims; benchmark evidence is local synthetic pre-alpha evidence only.
- Do not reopen #39 unless the benchmark disproves the Phase 95 fix.
- Do not turn this into an audit report or broad roadmap cleanup.

## Acceptance criteria

- A Phase 96 synthetic benchmark/evidence artifact exists, preferably `docs/performance/phase-96-large-export-benchmark.md`.
- The benchmark uses generated synthetic/disposable data only and covers at least one export above 500 transactions.
- The benchmark records and explains:
  - CSV body data-row count;
  - `X-CSV-Export-Limit` / benchmark `csv_limit`;
  - `X-CSV-Export-Total` / benchmark `csv_total`;
  - `X-CSV-Export-Truncated` / benchmark `truncated`;
  - whether body rows match `min(total, limit)`;
  - that the export remains synchronous and capped.
- The benchmark path does not commit generated `.gnucash.sqlite` files, app DBs, backups, real CSV files, screenshots, or private data.
- If the existing benchmark tooling is missing row/header consistency assertions, add a narrow test or helper check so future benchmark output cannot silently omit the Phase 95 evidence fields.
- Frontend CSV export copy remains honest and user-visible:
  - export is read-only;
  - current filters apply to the export;
  - synchronous export is capped at 10,000 rows;
  - truncation/large-export limitations are not hidden or overstated.
- If UI copy changes, frontend route/static checks are updated to cover the important text.
- `PROJECT_STATUS.md`, `CHANGELOG.md`, and `docs/handoff/phase-96.md` are updated with concise evidence.
- GitHub #39 is left closed if Phase 96 confirms the fix; add a short evidence comment only if useful and authenticated `gh` is available.
- GitHub #38 remains open and separate; do not claim personal copied-book dogfood success.

## Safety checks

- `GNUCASH_WRITES_ENABLED=false` must remain the default in settings/examples/docs.
- No write routes, write services, backup/write-lock behavior, controlled-write UI, auth storage, or release publication flow should be modified.
- Use only generated synthetic data or committed synthetic fixtures.
- Do not commit real GnuCash books, generated benchmark SQLite books, app DBs, backups, `.env`, secrets, tokens, certs, keys, private screenshots, real CSV exports, or private paths.
- Preserve Decimal/string money handling; do not introduce float-based money calculations.
- Do not add production-ready, security-audited, broad compatibility, or personal-book dogfood claims.
- Keep GnuCash Desktop positioned as the authoritative editor and the web app as read-only for MVP v0.1.

## Verification required from engineer

Run and report the exact commands used. Minimum expected commands:

```bash
cd apps/api
python scripts/run_large_book_benchmark.py --transactions 1000 --expense-accounts 12 --repeats 1 --json-output /tmp/phase-96-large-export-benchmark.json
```

If benchmark code/tests change:

```bash
cd apps/api && pytest -q
```

If frontend copy or route checks change:

```bash
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
```

Always run:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

The Phase 96 report must include: CSV body data-row count, CSV limit header/value, CSV total header/value, truncation flag, body rows vs `min(total, limit)`, benchmark artifact path, and whether any UI copy changed.

## Files/docs to update

Likely files:

- `apps/api/app/performance/large_book_benchmark.py` only if the benchmark output needs a narrow evidence/consistency improvement.
- `apps/api/tests/test_large_book_benchmark.py` only if benchmark evidence fields or consistency assertions need test coverage.
- `apps/web/src/routes/transactions/+page.svelte` or related transaction/export UI files only if copy is misleading or missing required cap/read-only/filter wording.
- `apps/web/scripts/test-auth-routes.mjs` if frontend copy changes need static route coverage.
- `docs/performance/phase-96-large-export-benchmark.md` as the preferred benchmark evidence artifact.
- `PROJECT_STATUS.md`.
- `CHANGELOG.md` if project convention records this user-facing evidence/UX confirmation.
- `docs/handoff/phase-96.md` as the completion handoff.

Do not rewrite historical Phase 87/88/89 benchmark documents except to add a forward link only if absolutely necessary; Phase 96 should have its own evidence artifact.

## GitHub/backlog note

- GitHub #39 should remain closed if benchmark evidence confirms Phase 95.
- Add a concise #39 comment with Phase 96 evidence only if helpful and `gh` is authenticated.
- Keep #38 open; copied personal-book dogfood remains blocked until Val provides or approves a safe copied SQL book outside git.
- Do not create new backlog issues unless Phase 96 uncovers a distinct practical blocker that cannot be fixed narrowly.
- Do not start v0.2 controlled-write work.

## Exact engineer instructions

1. Start from current `main` and verify the worktree is clean.
2. Read this brief, `AGENTS.md`, `PROJECT_STATUS.md`, `docs/handoff/phase-95.md`, and `docs/audits/2026-05-18-analyst-10-phase-plan.md`.
3. Confirm Phase 95/#39 is already complete and #39 is closed before beginning; if not, stop and report the blocker.
4. Run the existing synthetic large-book benchmark for at least 1,000 transactions and capture JSON outside git under `/tmp/`.
5. Inspect benchmark output for CSV body rows, limit, total, truncation flag, and expected body-row consistency.
6. If the benchmark output does not clearly record the Phase 95 fields or consistency result, make the narrowest benchmark/test change needed.
7. Review the transaction CSV export UI copy for read-only/filter/cap/truncation honesty. If it is already clear, document that no UI change was needed; if not, make a minimal copy/test update.
8. Create a Phase 96 performance/evidence artifact using synthetic-only numbers and no private data.
9. Update `PROJECT_STATUS.md`, `CHANGELOG.md` if appropriate, and create `docs/handoff/phase-96.md` with evidence, commands, safety statement, GitHub #39/#38 status, commit hash, and push evidence.
10. Run the required verification for every area touched, plus Docker config validation and `git diff --check`.
11. Commit implementation with a concise message such as `test: record large csv export benchmark` or `docs: record large csv export benchmark`, push to `origin/main`, and leave `git status --short` clean.

## Required Telegram phase report contents

The engineer's Telegram report to Val must be in Russian and include:

- Phase 96 title and one-sentence result.
- Whether benchmark tooling changed, UI copy changed, or both were already sufficient.
- Exact synthetic CSV evidence: body data rows, `X-CSV-Export-Limit`/`csv_limit`, `X-CSV-Export-Total`/`csv_total`, `X-CSV-Export-Truncated`/`truncated`, and body rows vs expected `min(total, limit)`.
- Benchmark/evidence artifact path.
- GitHub #39 state and #38 reminder.
- Safety statement: writes remain disabled by default; no real/private financial data committed; no release/tag published.
- Verification summary: backend tests if run, frontend check/auth-routes/build if run, Docker config, `git diff --check`.
- Commit hash and push status.
