# Phase 53 — Community Announcement Draft

## Status

Complete. Phase 53 refreshed conservative community announcement materials, added where-to-share guidance, synchronized status/release-facing docs, updated GitHub #16, passed required checks, and pushed the phase commit. No blockers remain.

## PM report

### Decision

Execute exactly Phase 53 from the roadmap: prepare cautious announcement drafts and sharing guidance for interested GnuCash/self-hosted users without publishing anything, creating a release, or expanding write scope.

### Why

The project now has a public pre-alpha release, read-only UX improvements, compatibility fixture work, deployment/backup docs, and i18n foundation. It is reasonable to prepare feedback-seeking community copy, but the messaging must stay conservative because the project is still pre-alpha, not production-ready, and not security-audited.

### Phase brief

- Goal: create/update community announcement materials that explain the short pitch, what works, what is not ready, safety warnings, who should test, wanted feedback, and suggested posts for r/GnuCash, r/selfhosted, later Show HN, and Mastodon/Linux/self-hosted communities.
- Non-goals: no posting to communities, no release/tag publication, no production marketing, no write-safety overclaim, no write-scope expansion, no product code changes.
- Acceptance criteria:
  - `docs/community/announcement-draft.md` exists and includes the requested announcement content.
  - `docs/community/where-to-share.md` exists and explains where/how to share cautiously.
  - Announcement copy says pre-alpha, not production-ready, not security-audited, read-only by default, and test disposable copies first.
  - Controlled writes are described only as experimental post-MVP and disabled by default with `GNUCASH_WRITES_ENABLED=false`.
  - Feedback requests are clear and actionable.
  - `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff are synchronized.
  - Related GitHub issue #16 is updated if `gh` is available.
- Safety checks:
  - MVP remains read-only by default.
  - No write route, write UI, write settings, release/tag, real financial data, `.env`, app DB, backup, secret, key, token, certificate, real screenshot, or real export is added.
  - Wording does not imply production readiness, audited security, hosted SaaS, collaborative accounting, GnuCash replacement, or safe write mode.
- Verification:
  - `cd apps/api && pytest -q`
  - `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
  - `git diff --check`

### Risks

- Community wording could sound like marketing for financial software. Mitigation: every draft includes explicit pre-alpha, not-production-ready, not-security-audited, disposable-copy-first warnings.
- Write support could be overclaimed. Mitigation: all write mentions describe controlled writes as experimental post-MVP and disabled by default.
- Wider sharing could produce too much feedback too early. Mitigation: `where-to-share.md` separates cautious narrow channels from later broader channels and adds posting gates.

### Files/docs to update

- `docs/community/announcement-draft.md`
- `docs/community/where-to-share.md`
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-53.md`

### GitHub/backlog

- Related issue: GitHub #16 (`Improve project discoverability before wider announcement`) was already closed after Phase 27, but Phase 53 is directly related to community announcement readiness, so it should receive a follow-up comment.
- Next planned phase after completion: Phase 54 — Observability and diagnostics.

## Engineer report

Implemented Phase 53 only:

- Rewrote `docs/community/announcement-draft.md` into a fuller conservative announcement package with:
  - short pitch;
  - what works today;
  - what is not ready;
  - who should test;
  - safety warning;
  - feedback prompts;
  - suggested posts for r/GnuCash, r/selfhosted, later Show HN, and Mastodon/Linux/self-hosted communities;
  - maintainer pre-post checklist.
- Added `docs/community/where-to-share.md` with cautious channel guidance, posting gates, anti-channels, feedback prompts, and a safety checklist.
- Updated `README.md` current status through Phase 53 and linked `where-to-share.md` from the community materials list.
- Updated `CHANGELOG.md` with a Phase 53 Unreleased entry.
- Updated `PROJECT_STATUS.md` through Phase 53 and set next planned phase to Phase 54.

No product code was changed. No release/tag was published. No community post was published. No write route, write UI, auth storage path, real data, fixture binary, secret, or backup was added.

## Verification

Passed:

- `git diff --check` — passed.
- `cd apps/api && pytest -q` — passed (`280 passed`, 27 existing warnings).
- `cd apps/web && npm run check` — passed (`0 errors`, `0 warnings`).
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.

## Safety confirmation

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default state.
- Controlled writes remain experimental post-MVP and disabled by default.
- The announcement drafts explicitly warn against production use, direct public-internet exposure, and enabling write mode on a real/only book.
- No write scope was expanded.
- No production/security-audited claims were introduced.
- No GnuCash replacement, hosted SaaS, family-wallet baseline, collaborative accounting, banking integration, import/sync, or safe write-mode positioning was introduced.
- No real financial data, new GnuCash book, `.env`, app DB, backup, secret, key, token, cert, real screenshot, or real CSV export was added.

## Commit / push

- Commit message: `docs: add phase 53 community announcement guidance`.
- Commit: this Phase 53 handoff is included in the phase commit pushed to `origin/main`.

## GitHub issue status

- GitHub #16: updated with Phase 53 follow-up comment https://github.com/valentusys/gnucash-web-companion/issues/16#issuecomment-4472738106 and remains closed.

## Blockers

None.
