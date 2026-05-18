# Phase 97 — v0.1.1-readonly release-prep checklist and notes

## Status

Complete. Phase 97 implemented `docs/handoff/phase-97-pm-brief.md`: conservative draft `v0.1.1-readonly` release notes and a release-prep checklist were prepared without publishing a tag or GitHub release.

No product code, backend routes, frontend routes, Docker config, auth behavior, or write-mode behavior was changed. `GNUCASH_WRITES_ENABLED=false` remains the safe default. Controlled writes remain post-MVP/experimental. No v0.2 work was started.

No real/private financial data, GnuCash books, app DBs, backups, `.env`, screenshots, CSV exports, secrets, tokens, certs, keys, or private paths were committed.

## PM brief followed

Goal: prepare honest, conservative `v0.1.1-readonly` release notes and a release-prep checklist summarizing post-`v0.1.0-readonly` maintenance changes, required checks, known limitations, and explicit non-claims before any publication phase.

Non-goals preserved:

- no `v0.1.1-readonly` tag;
- no GitHub release publication;
- no package upload;
- no Phase 98 final release gate in this phase;
- no production-ready, security-audited, broad compatibility, hosted SaaS, personal-book dogfood success, family-wallet, or collaborative-accounting claims;
- no write-mode enablement or write-scope expansion;
- no real/private financial data artifacts;
- no broad markdown cleanup or backlog theater.

## Implementation

Created:

- `docs/release/v0.1.1-readonly-notes.md`
  - Draft GitHub pre-release notes for a later authorized publish phase.
  - States pre-alpha/read-only/default-write-disabled posture.
  - Summarizes maintenance value since `v0.1.0-readonly`, including Phase 95/#39 and Phase 96 benchmark evidence.
  - Explicitly says `v0.1.1-readonly` is not published yet.
  - Keeps personal-book dogfood, compatibility, security, production, and performance language conservative.

- `docs/release/v0.1.1-readonly-checklist.md`
  - Separates completed Phase 95/96 evidence, Phase 97 artifacts, required Phase 98 release-gate checks, intentionally unauthorized publication commands, known limitations, and future publish safety checks.
  - Records that publication commands are placeholders only and not authorized in Phase 97.

Updated:

- `CHANGELOG.md`
  - Added an Unreleased Phase 97 entry for release-prep artifacts.

- `PROJECT_STATUS.md`
  - Advanced completed baseline through Phase 97.
  - Added Phase 97 summary and handoff section.
  - Set next planned phase to Phase 98 release-gate verification.

## Release state

No tag or release was created by Phase 97.

Observed before completion:

```text
git tag --list 'v0.1.1-readonly'
(no output)

gh release view v0.1.1-readonly
release not found

gh release list --limit 10
v0.1.0-readonly     Pre-release
v0.0.2-prealpha     Pre-release
v0.0.1-prealpha     Pre-release
```

## GitHub / backlog

Observed issue state:

```text
#39 CLOSED — CSV export row count is capped at 500 despite 10,000-row export headers
#38 OPEN — Run Phase 85 copied personal-book dogfood when safe book is available
```

Phase decision:

- GitHub #39 remains closed based on Phase 95/96 synthetic evidence.
- GitHub #38 remains open and blocked until a safe copied personal GnuCash SQL book is available outside git.
- No new GitHub issue was created.
- No GitHub release was published.

## Verification

Required docs/release-prep-only check:

```text
git diff --check
PASS
```

Conservative wording inspection:

```text
PASS — release notes and checklist state pre-alpha/read-only/default-write-disabled posture, no production/security-audited/broad-compatibility/personal-book dogfood claims, and publication not authorized in Phase 97.
```

Additional backend/frontend/Docker checks:

```text
Not run in Phase 97 because this phase changed only docs/release/status/handoff files and did not touch backend code, frontend code, or deployment config.
```

These checks are explicitly required for the next Phase 98 release gate:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the documented/default posture.
- GnuCash Desktop remains the authoritative editor.
- Controlled writes remain post-MVP/experimental and are not release-marketed as safe for production books.
- Money/multi-currency claims remain conservative; no currency conversion is claimed or faked.
- No real/private financial data, GnuCash books, `.env`, app DBs, backups, screenshots, exports, secrets, tokens, certs, keys, or private paths were committed.

## Risks / follow-up

- Phase 97 is release preparation only; `v0.1.1-readonly` is not ready to publish until a separate Phase 98 release-gate artifact records a passing verdict.
- #38 remains a real evidence gap for personal copied-book dogfood; do not claim it passed unless a safe copied SQL book is provided and tested outside git in a later phase.
- Compatibility evidence remains narrow; do not claim broad GnuCash version/backend coverage.
- CSV export remains synchronous and capped at 10,000 rows; the maintenance candidate fixes the row/header mismatch but does not add async export architecture.

## Next recommended phase

Phase 98 — run `v0.1.1-readonly` release-gate verification: backend tests, frontend checks/build, Docker config validation, disabled-write safety confirmation, sensitive-data hygiene, GitHub Actions/release state if authenticated, and a final gate verdict artifact. Do not publish a tag/release in Phase 98 unless a later explicit publish phase authorizes it.

## Commit / push

Implementation commit: recorded in git history for this handoff commit and reported in the final Phase 97 stdout/Telegram report.

Push: `origin/main` verified after commit/push by the engineer before final report.
