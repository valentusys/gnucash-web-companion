# overnight-v2-worker-01

Target issue: #28
Package name: README.ru readability cleanup

## Summary

Added a compact open-queue map to `README.ru.md` so terminal readers can see the current #22, #28, and #36 blockers without scanning the long phase history.

## Files changed

- `README.ru.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-v2-worker-01.md`

## Tests run and results

- `cd apps/api && pytest -q tests/test_markdown_readability_docs.py::test_readme_ru_starts_with_compact_public_status_and_safety_navigation`: passed.
- `python3 scripts/check_markdown_readability.py`: passed.

## Safety summary

No private book, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence was opened, copied, committed, or posted. `GNUCASH_WRITES_ENABLED=false`, `APP_ENV=test`, no public write beta, and NO_RELEASE posture are preserved.

## Issue update

#28 should stay open; this package improves README.ru but does not complete all public Markdown readability work.

## Commit SHA

93172bc57444b9ce0d2c527c157932e213a3943f

## Remaining blockers

Continue #28 CHANGELOG/release-doc cleanup and #36/#22 safe guard packets.

## Recommendation

Run #28 CHANGELOG readability cleanup next.
