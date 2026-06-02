# Overnight worker handoff: overnight-2026-06-02-worker-06

## Target issue/package

- Target issue: #28, "Improve markdown source readability before wider announcement".
- Package: README.ru source readability and status posture cleanup.

## Summary of changes

- Reworked the top `README.ru.md` public-status section into a compact terminal/diff-friendly
  summary instead of duplicating long phase history.
- Added `## Где смотреть подробности` navigation to point readers to `PROJECT_STATUS.md`, handoffs,
  current public beta release notes, copied-book write-alpha posture, and compatibility boundaries.
- Preserved conservative public posture:
  - `v0.5.0-public-readonly-beta` remains the current public read-only beta.
  - `v0.5.1-public-readonly-beta` is not published.
  - `v0.4.0-owner-writebeta` remains deferred; no public write beta exists.
  - `v0.2.8-writealpha` remains the current published experimental write-alpha pre-release.
  - `GNUCASH_WRITES_ENABLED=false` remains default.
  - Enabled writes remain experimental and `APP_ENV=test` gated.
  - real/private/original/only-copy books remain unsafe write targets.
- Added a focused README.ru readability regression test in
  `apps/api/tests/test_markdown_readability_docs.py`.
- Added a short `PROJECT_STATUS.md` entry for this package.

## Files changed

- `README.ru.md`
- `PROJECT_STATUS.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-2026-06-02-worker-06.md`

## Tests run and results

- RED check: `cd apps/api && pytest tests/test_markdown_readability_docs.py -q`
  - Result: failed as expected before the README.ru navigation existed (`1 failed, 2 passed`).
- Focused GREEN/final: `cd apps/api && pytest tests/test_markdown_readability_docs.py -q`
  - Result: passed (`3 passed`).
- `python3 scripts/check_public_status.py`
  - Result: passed (`public-status-guard: ok`).
- `python3 scripts/check_tracked_hygiene.py`
  - Result: passed (`Tracked hygiene check passed (1732 tracked paths inspected).`).
- `git diff --check`
  - Result: passed.
- `JWT_SECRET=dummy-...cret APP_ADMIN_PASSWORD=*** docker compose config --quiet`
  - Result: passed.

## CI link/status

- Pushed commit: pending.
- CI run: pending.
- Status: pending until after push.

## Safety summary

- No product code or write-mode behavior changed.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` write gating was not weakened.
- No GnuCash book, SQLite book, app DB, backup, export, screenshot, `.env`, token, key, cert,
  private path, account name, transaction description, memo, amount, or raw private evidence was
  added.
- No release, tag, package, image, or publication was created.
- No public write beta, stable, production-ready, or security-audited claim was added.

## Issue update

- Pending until after commit/push.
- Recommendation: keep #28 open. This package materially improves README.ru, but the original issue
  remains broader and still includes gradual cleanup of older release/handoff/status docs.

## Commit SHA

- Pending.

## Remaining blockers

- #28 should stay open for gradual raw-Markdown cleanup of older release docs, older handoffs, and
  status/history-heavy docs when they are substantively touched.
- Avoid whole-repo noisy reflow unless maintainers explicitly request it.

## Next supervisor recommendation

- Keep #28 open.
- Next useful package: clean a small cluster of older status/release/handoff docs with the longest raw
  Markdown lines while preserving release/no-release and default-disabled safety wording.
