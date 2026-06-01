# Overnight cycle 3

## Selected task / issue

Issue #28: Improve markdown source readability before wider announcement.

## Why this task was chosen

After closing completed localization issues, #28 was the safest remaining docs task. The issue explicitly discourages noisy whole-repository churn and asks for a gradual approach. A lightweight guide improves future consistency without reflowing historical handoff/status files.

Analyst candidates considered:

1. #28 markdown readability policy/guidance.
2. #13 read-only book-management UI slice.
3. #22 compatibility report workflow.

PM selected #28 because it is safe, documentation-only, and reduces future review friction without touching product behavior.

## Goal

Add a concise Markdown source-readability guide and update #28 with evidence.

## Scope

- Add guidance for wrapping new prose and touched docs.
- Add guidance for language-tagged code fences.
- Preserve safety/release wording requirements.
- List minimal docs/status checks.
- Comment on #28 and keep it open for gradual cleanup.

## Non-goals

- No whole-repo reflow.
- No changes to release/status claims.
- No product behavior changes.
- No write-mode work.
- No release publication.

## Files changed

- `docs/development/markdown-readability.md`
- `docs/handoff/overnight-cycle-3.md`

## Tests/checks run

- `gh issue view 28 --comments --json number,title,body,comments,labels,state,url`
- `git diff --check`
- `python3 scripts/check_public_status.py`
- `python3 scripts/check_tracked_hygiene.py`
- `gh issue comment 28 ...`

## Safety checks

- No GnuCash book, app DB, backup, export, screenshot, `.env`, secret, or raw private evidence was accessed or committed.
- No write-alpha/writebeta route was executed.
- `GNUCASH_WRITES_ENABLED=false` posture was not changed.
- Public/default app posture remains read-only.
- Public-status guard passed after the doc change.

## Issue updates

Commented on #28 with the new guide path and verification results. Kept #28 open because gradual cleanup should happen when substantive docs are touched, not as broad formatting churn.

## Release/no-release decision

NO_RELEASE. This cycle was internal documentation hygiene and does not justify a public patch pre-release.

## Next recommended task

Use #13 for a narrow read-only UX slice only if implementation scope is clear, or #22 for a safe compatibility report/workflow improvement that does not request private artifacts.
