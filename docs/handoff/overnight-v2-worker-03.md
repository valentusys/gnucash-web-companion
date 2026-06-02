# overnight-v2-worker-03

Target issue: #28
Package name: Release docs source cleanup

## Summary

Added a reader shortcut to the v0.5.0 publication evidence doc and expanded the Markdown readability guard/test coverage so current notes, final gate, and publication evidence preserve public-read-only and no-release boundaries.

## Files changed

- `docs/release/v0.5.0-public-readonly-beta-publication-evidence.md`
- `scripts/check_markdown_readability.py`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-v2-worker-03.md`

## Tests run and results

- `cd apps/api && pytest -q tests/test_markdown_readability_docs.py::test_release_docs_have_conservative_readable_status_boundaries`: passed.
- `python3 scripts/check_markdown_readability.py`: passed.

## Safety summary

Release docs still state pre-release/read-only boundaries: no public write beta, no production/stable/security-audited claim, no original/private/real-working/only-copy book safety claim, and `GNUCASH_WRITES_ENABLED=false` default.

## Issue update

#28 should stay open; current v0.5.0 release docs are easier to review, but closure audit is still pending.

## Commit SHA

8bf7e98eec58f9522af95b0f7dd3e9a583240c75

## Remaining blockers

Continue #28 guard expansion/closure audit and #36/#22 safe work.

## Recommendation

Run a #36 controlled-write readiness dashboard/index package next.
