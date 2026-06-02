# Autonomous multiqueue cycle 4 — #28 developer readability guard

## Queue

- Issue: #28 Improve markdown source readability before wider announcement
- PM package: developer docs readability guard.

## Scope

- Extend the markdown readability guide with a public-announcement checklist.
- Add a focused regression test that proves the checklist preserves the desired guard text.
- Keep the check lightweight and non-brittle.

## TDD evidence

RED command:

```bash
pytest apps/api/tests/test_markdown_readability_docs.py -q
```

Observed RED result before the guide update: `1 failed`, missing `Public announcement docs checklist`.

GREEN command after the guide update is recorded in verification for this package.

## Non-goals

- No repository-wide markdown formatter.
- No product behavior change.
- No release/tag/package publication.

## Safety

- GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- No private evidence or runtime data was touched.
