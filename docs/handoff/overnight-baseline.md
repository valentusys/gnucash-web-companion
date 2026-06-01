# Overnight baseline audit

Date: 2026-06-01
Repository: valentusys/gnucash-web-companion
Branch: main

## Checks run

- `git status --short --branch`
- `gh issue list --state open --limit 100`
- `gh pr list --state open --limit 50`
- `gh release list --limit 20`
- `gh issue view 43 --json number,state,title,closedAt,labels,url`
- `python3 scripts/check_public_status.py`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `python3 scripts/check_tracked_hygiene.py`
- `git diff --check`

## Baseline result

- Current branch: `main`, tracking `origin/main`.
- Working tree before this handoff was clean: no tracked or untracked changes reported by `git status --short --branch`.
- Open PRs: none.
- Latest visible GitHub release: `v0.5.0-public-readonly-beta`.
- No `v0.5.1-public-readonly-beta` release is visible in the latest release list.
- Open issues matched expected baseline: #36, #29, #28, #22, #17, #13.
- Issue #43 is closed: `https://github.com/valentusys/gnucash-web-companion/issues/43`, closed 2026-06-01T03:02:56Z.
- README, PROJECT_STATUS, and CHANGELOG consistently state that `v0.5.0-public-readonly-beta` remains the current public read-only beta and do not claim a published `v0.5.1-public-readonly-beta`.
- README/PROJECT_STATUS already note that #43 is accepted/closed after owner-writebeta copied-book evidence and PM `NO_RELEASE`.

## Safety checks

- Public/default posture remains read-only.
- `scripts/check_public_status.py`: passed.
- Docker Compose rendered with dummy validation secrets: passed.
- Tracked hygiene scan: passed, 1689 tracked paths inspected.
- `git diff --check`: passed.
- No private books, app DBs, backups, exports, screenshots, `.env`, secrets, or raw private evidence were found by the tracked hygiene guard.
- No copied-book mutation was performed in Cycle 0.

## Stop-condition review

No stop condition triggered:

- No unknown tracked changes at baseline.
- No private tracked artifacts detected.
- Release/status docs are materially consistent with visible GitHub releases.
- Default write-disabled posture and public status guard are intact.

## Decision

Proceed to autonomous safe issue-based cycles. Prefer non-mutating/read-only tasks unless a copied/restorable staged book and exact PM counts are both available and useful.
