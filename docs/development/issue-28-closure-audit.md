# Issue #28 closure audit

Status: keep #28 open. This is a scoped raw-Markdown readability audit, not a release decision.

## What is now acceptable

- `README.ru.md` has a compact current public status and open-queue map.
- `CHANGELOG.md` has top quick navigation and a current queue map before historical entries.
- Current v0.5.0 public read-only beta notes/final-gate/publication evidence keep read-only and no-release boundaries visible near the top.
- `PROJECT_STATUS.md` starts with quick navigation and active issue links.
- `docs/gnucash-compatibility.md` starts with #22 blocker and synthetic/disposable-only compatibility scope.
- `scripts/check_markdown_readability.py` covers the current public/status docs and selected current release/readability docs.

## Remaining work before closure

Keep #28 open until a maintainer confirms all public/wider-announcement raw Markdown entry points below are readable in a terminal without weakening safety wording:

1. `README.md` English overview: quick current status should match the improved README.ru/CHANGELOG posture.
2. `docs/community/public-readonly-beta-feedback-packet.md`: public tester instructions should keep no-private-artifact and no-production-claim wording visible near the top.
3. `docs/community/announcement-draft.md`: announcement source should not imply v0.5.1, public write beta, stable, production-ready, or security-audited status.
4. Current handoff index/navigation: new overnight-v2 handoffs should be easy to find without mass-rewriting historical phase files.

## Closure rule

Close #28 only after `scripts/check_markdown_readability.py`, `scripts/check_public_status.py`, and `git diff --check` pass from a clean tree and the audit comment names the remaining public docs as either accepted or intentionally out of scope.

## Safety summary

No private/runtime/book artifacts are needed for #28. `GNUCASH_WRITES_ENABLED=false`, `APP_ENV=test`, no public write beta, no stable/production/security-audited claim, and `v0.5.1-public-readonly-beta` not-published status must remain visible.
