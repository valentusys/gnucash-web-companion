# overnight-v2-worker-11

Target issue: #28
Package name: README.md English overview cleanup

## Summary

Aligned the English README top status with the improved README.ru/CHANGELOG posture: explicit current v0.5.0 status, explicit v0.5.1 not-published wording, default write-disabled wording, and a compact #22/#28/#36 queue map near the current status section.

## Files changed

- `README.md`
- `apps/api/tests/test_markdown_readability_docs.py`
- `docs/handoff/overnight-v2-worker-11.md`

## Tests run and results

- `cd apps/api && pytest -q tests/test_markdown_readability_docs.py::test_readme_en_has_compact_public_status_and_queue_map`: passed.
- `python3 scripts/check_markdown_readability.py`: passed.

## Safety summary

Docs/tests only. No private/runtime/book artifacts touched. No public write beta, production-ready, stable, or security-audited claim added.

## Issue update

#28 should stay open; English README is improved, but public feedback packet, announcement draft, and handoff navigation remain.

## Commit SHA

449a002bc34cc3043bbabb7b0b1142e39a94cf22

## Remaining blockers

Public feedback packet, announcement draft, and handoff navigation readability remain pending.

## Recommendation

Run public feedback packet readability cleanup next.
