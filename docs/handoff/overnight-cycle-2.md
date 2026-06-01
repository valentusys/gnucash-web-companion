# Overnight cycle 2

## Selected task / issue

Issue #17: Plan Russian documentation and UI localization.

## Why this task was chosen

After #29 was closed, #17 was the safest adjacent high-value task. It requested a localization plan, UI string extraction notes, and clear post-MVP/community boundaries. Existing docs had most of the foundation but lacked one concise future-plan section tying the acceptance criteria together.

Analyst candidates considered:

1. #17 localization planning closeout.
2. #13 read-only book-management UI slice.
3. #22 compatibility report workflow.

PM selected #17 because it is documentation-only, non-mutating, and directly reduces ambiguity for future contributors.

## Goal

Add a concise future localization plan and close #17 if acceptance criteria are satisfied.

## Scope

- Extend `docs/localization.md` with a post-MVP/community future localization plan.
- List candidate documentation pages worth translating first.
- Document UI string extraction checks before translating a new page.
- Keep English canonical and Russian partial/opt-in.
- Close #17 with evidence after verification.

## Non-goals

- No complete Russian translation claim.
- No new locale defaults.
- No backend/API localization rewrite.
- No controlled-write expansion.
- No release publication.

## Files changed

- `docs/localization.md`
- `docs/handoff/overnight-cycle-2.md`

## Tests/checks run

- `gh issue view 17 --comments --json number,title,body,comments,labels,state,url`
- `git diff --check`
- `python3 scripts/check_public_status.py`
- `python3 scripts/check_tracked_hygiene.py`

## Safety checks

- No GnuCash book, app DB, backup, export, screenshot, `.env`, secret, or raw private evidence was accessed or committed.
- No write-alpha/writebeta route was executed.
- `GNUCASH_WRITES_ENABLED=false` posture was not changed.
- Public/default app posture remains read-only.
- Public-status guard passed after the doc change.

## Issue updates

Closed #17 with evidence comment. The plan now lives in `docs/localization.md` and includes:

- English-canonical policy;
- current localized UI surface;
- accounting/safety glossary;
- future localization plan;
- candidate docs priority table;
- UI string extraction checklist.

## Release/no-release decision

NO_RELEASE. This cycle was documentation/planning only and does not justify a public patch pre-release.

## Next recommended task

Continue with #13 only if selecting a narrow read-only UX slice, or #22 if creating a safe compatibility report workflow that does not request private books/screenshots/exports.
