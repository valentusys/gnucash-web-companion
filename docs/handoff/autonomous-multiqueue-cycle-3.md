# Autonomous multiqueue cycle 3 — #28 PROJECT_STATUS navigation

## Queue

- Issue: #28 Improve markdown source readability before wider announcement
- PM package: PROJECT_STATUS raw-markdown navigation structure.

## Scope

- Add a compact top-level navigation block before the long repository history.
- Preserve detailed phase history below instead of rewriting it.
- Make current public/write/open-issue posture visible in the first screen of raw Markdown.

## Non-goals

- No historical rewrite.
- No product behavior change.
- No release/tag/package publication.

## Acceptance result

`PROJECT_STATUS.md` now has a `Quick navigation` section with current read-only beta, unpublished
`v0.5.1`, default write-disabled posture, open queues, recently closed queues, and latest multiqueue
handoff links.

## Verification

Planned focused verification:

```bash
git diff --check
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
```

## Safety

- GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- No private evidence or runtime data was touched.
