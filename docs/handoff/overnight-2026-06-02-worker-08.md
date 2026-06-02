# Overnight worker handoff: overnight-2026-06-02-worker-08

## Target issue/package

- Target issue: #28, "Improve markdown source readability before wider announcement".
- Package: `PROJECT_STATUS.md` navigation/index cleanup with regression guard.

## Summary of changes

- Reworked the top `PROJECT_STATUS.md` navigation into a terminal-friendly index before the long
  historical ledger.
- Added direct links to `README.md`, `README.ru.md`, `CHANGELOG.md`, active issues #22/#28/#36, the
  current public read-only beta release, copied-book write-alpha posture, and latest handoffs.
- Added `## Current status snapshot` near the top so maintainers can quickly find current public
  status, safety posture, active queues, and recent closures without scanning the phase history.
- Added a focused regression guard in `apps/api/tests/test_markdown_readability_docs.py` for the
  `PROJECT_STATUS.md` navigation/current-status section and conservative safety wording.
- Added a short `PROJECT_STATUS.md` repository entry for this worker.

## TDD evidence

- RED: after adding the new `PROJECT_STATUS.md` regression test, `cd apps/api && pytest
  tests/test_markdown_readability_docs.py -q` failed as expected because `## Current status snapshot`
  was not present (`1 failed, 3 passed`).
- GREEN: after updating `PROJECT_STATUS.md`, the same focused readability test passed (`4 passed`).

## Files changed

- `PROJECT_STATUS.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-2026-06-02-worker-08.md`

## Tests run and results

- `cd apps/api && pytest tests/test_markdown_readability_docs.py -q`
  - RED result before docs update: failed as expected (`1 failed, 3 passed`).
  - GREEN result after docs update: passed (`4 passed`).
- `cd apps/api && pytest tests/test_markdown_readability_docs.py tests/test_public_status_guard.py -q`
  - Result: passed (`32 passed`).
- First combined root/script run was corrected because it stayed in `apps/api` for root scripts.
- `python3 scripts/check_public_status.py`
  - Result: passed (`public-status-guard: ok`).
- `python3 scripts/check_tracked_hygiene.py`
  - Result: passed (`Tracked hygiene check passed (1735 tracked paths inspected).`).
- `git diff --check`
  - Result: passed.
- `JWT_SECRET=dummy-...cret APP_ADMIN_PASSWORD=dummy-...word docker compose config --quiet`
  - Result: passed.

## CI link/status

- Pushed implementation commit: `ab31c511a5164a3008cc4ca96353457964793c57`.
- CI run for implementation commit: https://github.com/valentusys/gnucash-web-companion/actions/runs/26800616791
- Status at issue-update time: in progress.

## Safety summary

- Documentation/test-only change; no product code or write-mode behavior changed.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` write gating was not weakened.
- No GnuCash book, SQLite book, app DB, backup, CSV export, screenshot, `.env`, token, key, cert,
  private path, account name, transaction description, memo, amount, or raw private evidence was
  added.
- No release, tag, package, image, or publication was created.
- No public write beta, stable, production-ready, or security-audited claim was added.
- Public status remains conservative: `v0.5.0-public-readonly-beta` is current;
  `v0.5.1-public-readonly-beta` is not published.

## Issue update

- Issue comment: https://github.com/valentusys/gnucash-web-companion/issues/28#issuecomment-4599014814
- Recommendation: keep #28 open. This package materially improves `PROJECT_STATUS.md`, but the
  original issue still covers gradual cleanup of older release/handoff/status docs.

## Commit SHA

- Implementation commit: `ab31c511a5164a3008cc4ca96353457964793c57`
  (`docs: improve PROJECT_STATUS navigation`).
- Handoff issue/CI refresh commit: pending.

## Remaining blockers

- #28 should stay open for gradual raw-Markdown cleanup of older release docs, older handoffs, and
  status/history-heavy docs when those files are substantively touched.
- Avoid whole-repo noisy reflow unless maintainers explicitly request it.

## Next supervisor recommendation

- Keep #28 open.
- Next useful package: choose one older release-doc or handoff cluster with high review value and clean
  it incrementally, preserving release/no-release and default-disabled safety wording.
