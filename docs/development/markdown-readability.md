# Markdown source readability guide

This guide keeps raw Markdown reviewable in terminals, plain-text diffs, and small editor panes
without doing noisy whole-repository formatting sweeps.

## Default rule for new prose

Wrap new prose at a review-friendly width when practical, especially in:

- `README.md` and `README.ru.md`;
- `CHANGELOG.md`;
- `PROJECT_STATUS.md`;
- release notes, checklists, final gates, and publication evidence;
- public deployment, safety, privacy, compatibility, and localization docs.

A target around 100 characters is usually comfortable. Use judgement: keep tables, URLs, badges,
generated snippets, shell commands, and intentionally long identifiers readable rather than forcing
awkward wraps.

## When touching existing docs

When a doc is already being edited for a substantive reason:

1. Wrap the surrounding touched paragraph/list item if it is very long.
2. Preserve exact safety wording and release/status meaning.
3. Do not reflow large unrelated sections just to reduce line length.
4. Keep code fences and command blocks mechanically copyable.
5. Prefer small, reviewable formatting patches over repository-wide churn.

## Status/readability triage

Long-lived status files are useful, but they are also easy to make unreadable. Split long
status docs before rewriting them when a smaller index plus focused handoff/audit/release
notes would be clearer. Rule of thumb: Split long status docs before rewriting them in place.
Prefer links to detailed phase artifacts over repeating full blocks
inside README, CHANGELOG, or PROJECT_STATUS.

When cleaning release/status language:

1. Do not hide release/no-release decisions, current tags, issue state, or safety blockers.
2. Keep the newest public read-only beta and unpublished/missing-release facts explicit.
3. Preserve mutation counts and whether copied-book evidence is synthetic, owner-copied, or absent.
4. If a long paragraph mixes product status, release evidence, and write-safety posture, split it
   into bullets rather than changing the meaning.
5. Avoid whole-file reflow unless the task is explicitly a readability phase.

## Public announcement docs checklist

Before wider announcement or public-facing issue cleanup, check the source Markdown, not only the
rendered page:

1. README top status is concise and points to deeper status docs instead of repeating long history.
2. PROJECT_STATUS starts with a quick navigation block before detailed phase history.
3. Recent handoff and release docs keep safety verdicts visible: release/no-release, mutation counts,
   current tag, blocked issue state, and remaining owner-only gates.
4. Links to release notes, final gates, publication evidence, handoffs, and safety docs still resolve
   from the repository root.
5. Safety warnings remain explicit: no production guarantee, no public write beta, no real/private or
   only-copy write target, and default-disabled writes.

## Code fences

Use language tags when the language is known:

```bash
python3 scripts/check_public_status.py
```

```text
v0.5.0-public-readonly-beta remains the current public read-only beta.
```

Use `text` for plain output, release status snippets, prompts, and deliberately non-executable examples.

## Automated guard

`scripts/check_markdown_readability.py` enforces a small fail-closed source-readability guard for
selected public/status docs and the current worker handoff. It intentionally avoids noisy historical
whole-file reflow by checking current top navigation/readability in long archives plus focused
handoff/status files.

The guard fails closed when selected docs are missing top status/safety signals, PROJECT_STATUS or
handoff issue navigation, guidance that safety warnings must be preserved, or unstructured long prose
outside allowlisted code fences, URLs, tables, and command-like lines.

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
python3 scripts/check_markdown_readability.py
python3 scripts/check_public_status.py
python3 scripts/check_tracked_hygiene.py
```

If release/status wording changes, also inspect visible releases with `gh release list --limit 20` before committing.
