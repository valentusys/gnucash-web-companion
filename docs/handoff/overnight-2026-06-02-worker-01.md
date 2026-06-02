# Overnight worker handoff: overnight-2026-06-02-worker-01

## Target issue/package

- Target issue: #28, "Improve markdown source readability before wider announcement".
- Package: CHANGELOG/release docs readability cleanup.

## Summary of changes

- Improved `CHANGELOG.md` raw Markdown navigation by adding a top `Quick navigation` block before
  `[Unreleased]`.
- Reworked the top changelog Unreleased/current release-history entries into shorter grouped bullets.
- Added source-readable navigation/sectioning to the key current public read-only beta release docs:
  - `docs/release/v0.5.0-public-readonly-beta-notes.md`
  - `docs/release/v0.5.0-public-readonly-beta-final-gate.md`
- Added a focused markdown-readability regression test proving the changelog starts with release
  navigation and preserves conservative release/write-safety wording.
- Added a short `PROJECT_STATUS.md` status entry for this worker package.

## Files changed

- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/release/v0.5.0-public-readonly-beta-notes.md`
- `docs/release/v0.5.0-public-readonly-beta-final-gate.md`
- `docs/handoff/overnight-2026-06-02-worker-01.md`

## Tests run and results

- RED check: `cd apps/api && pytest tests/test_markdown_readability_docs.py -q`
  - Result: failed as expected before the changelog navigation existed (`1 failed, 1 passed`).
- Final focused readability test: `cd apps/api && pytest tests/test_markdown_readability_docs.py -q`
  - Result: passed (`2 passed`).
- `git diff --check`
  - Result: passed.
- `python3 scripts/check_public_status.py`
  - Result: passed (`public-status-guard: ok`).
- `python3 scripts/check_tracked_hygiene.py`
  - Result: passed (`Tracked hygiene check passed (1726 tracked paths inspected).`).
- `gh release list --limit 20`
  - Result: confirmed `v0.5.0-public-readonly-beta` is the latest public read-only beta listed;
    no `v0.5.1-public-readonly-beta` release appears.
- Independent review:
  - Result: passed with no security concerns or logic errors.
  - Follow-up: incorporated the non-blocking ordering assertion suggestion.

## CI link if available

- Not available at handoff creation time because this worker had not pushed the handoff commit yet.
  Supervisor should verify the post-push GitHub Actions run for the final pushed head.

## Safety summary

- No app or write-mode behavior changed.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` write gating was not weakened.
- No GnuCash book, SQLite book, app DB, backup, export, screenshot, `.env`, secret, token, key,
  private path, account name, transaction description, memo, amount, or raw private evidence was added.
- No release, tag, package, image, or publication was created.
- No public write beta, stable, production, public-internet-safe, or security-audited claim was added.
- `v0.5.0-public-readonly-beta` remains current; `v0.5.1-public-readonly-beta` is not published.

## Issue update link/comment summary

- Issue comment: https://github.com/valentusys/gnucash-web-companion/issues/28#issuecomment-4598406710
- Summary: reported changed files, RED/GREEN/final checks, safety notes, and recommended keeping #28
  open for older release docs/README.ru/older handoff cleanup.

## Commit SHA

- Implementation commit: `924c085` (`docs: improve changelog release readability`).
- Handoff commit: this file is expected to be committed immediately after creation.

## Remaining blockers

- #28 should stay open because the original issue covers broader raw-Markdown readability than this slice.
- Older release docs still contain long historical lines and should be cleaned gradually when touched.
- README.ru and older handoff/status docs may still need source readability cleanup before a wider
  announcement, but a noisy whole-repo reflow is still not recommended without maintainer approval.

## Recommendation for supervisor's next package

- Keep #28 open.
- Next high-value #28 package: clean the highest-impact older `docs/release/` files with long raw lines,
  preserving exact no-release/public-beta/default-disabled wording and avoiding broad history rewrites.
