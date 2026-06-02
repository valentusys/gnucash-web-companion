# Autonomous multiqueue cycle 2 — #28 README top-level readability

## Queue

- Issue: #28 Improve markdown source readability before wider announcement
- PM package: README top-level current-status readability.

## Scope

- Replace the dense top `Current status` opening with a short public summary.
- Preserve links to detailed status and release docs.
- Correct issue state for the current open queues (#22/#28/#36) and recently closed #13/#41/#42/#43.
- Keep safety warnings and no-release facts explicit.

## Non-goals

- No product behavior change.
- No broad rewrite of historical release lists.
- No release/tag/package publication.

## Acceptance result

README now starts with concise bullets for current read-only beta, unpublished tags, default read-only posture, write safety, open queues, recently closed issues, and linked read-only beta evidence.

## Verification

Planned focused verification for the package:

```bash
git diff --check
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
```

## Safety

- GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- No private evidence or runtime data was touched.
