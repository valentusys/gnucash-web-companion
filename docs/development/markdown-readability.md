# Markdown source readability guide

This guide keeps raw Markdown reviewable in terminals, plain-text diffs, and small editor panes without doing noisy whole-repository formatting sweeps.

## Default rule for new prose

Wrap new prose at a review-friendly width when practical, especially in:

- `README.md` and `README.ru.md`;
- `CHANGELOG.md`;
- `PROJECT_STATUS.md`;
- release notes, checklists, final gates, and publication evidence;
- public deployment, safety, privacy, compatibility, and localization docs.

A target around 100 characters is usually comfortable. Use judgement: keep tables, URLs, badges, generated snippets, shell commands, and intentionally long identifiers readable rather than forcing awkward wraps.

## When touching existing docs

When a doc is already being edited for a substantive reason:

1. Wrap the surrounding touched paragraph/list item if it is very long.
2. Preserve exact safety wording and release/status meaning.
3. Do not reflow large unrelated sections just to reduce line length.
4. Keep code fences and command blocks mechanically copyable.
5. Prefer small, reviewable formatting patches over repository-wide churn.

## Code fences

Use language tags when the language is known:

```bash
python3 scripts/check_public_status.py
```

```text
v0.5.0-public-readonly-beta remains the current public read-only beta.
```

Use `text` for plain output, release status snippets, prompts, and deliberately non-executable examples.

## Safety wording

Formatting changes must not weaken safety claims. Keep these meanings intact:

- the public/default app is read-only;
- `GNUCASH_WRITES_ENABLED=false` remains the default;
- enabled write-alpha/writebeta flows are experimental and gated;
- real/private/original/only-copy GnuCash books are not safe write targets;
- the project is not production-ready, not security-audited, and not public-internet safe by default.

## Suggested checks

For formatting-only or docs-heavy changes, run at least:

```bash
git diff --check
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
```

If release/status wording changes, also inspect visible releases with `gh release list --limit 20` before committing.
