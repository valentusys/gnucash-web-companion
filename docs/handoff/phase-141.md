# Phase 141 — v0.1.4-readonly release artifact preparation

Date: 2026-05-19
Status: DONE

## Goal

Prepare conservative release artifacts for a possible `v0.1.4-readonly` maintenance pre-release without publishing a tag/release/package and without changing the read-only/default-write-disabled posture.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-140.md`;
  - release-governance notes from the project skill.
- Checked starting git state first:
  - branch: `main`;
  - starting HEAD: `7699ce399ebce3aa5b48ef293960fa759badca95`;
  - `origin/main` matched the starting HEAD;
  - pre-existing untracked `.hermes/` local agent data was not touched or committed.
- Created `docs/release/v0.1.4-readonly-notes.md`.
- Created `docs/release/v0.1.4-readonly-checklist.md`.
- Created `docs/release/v0.1.4-readonly-final-gate.md`.
- Updated `CHANGELOG.md` with a `[0.1.4-readonly]` candidate section and separated the existing `v0.2.0-writealpha` published history from the read-only candidate.
- Updated `README.md` so current status/release readiness links include the prepared unpublished `v0.1.4-readonly` artifacts while keeping `v0.1.3-readonly` as the current public read-only release until publication.
- Updated `PROJECT_STATUS.md` through Phase 141.

## Verdict

`Ready for later authorized publish phase — unpublished`.

The Phase 140 documentation-drift blocker is resolved for the prepared candidate artifacts. This phase does not publish. A later publish phase must re-check clean `main`, `HEAD == origin/main`, tag/release absence, GitHub Actions success, local checks, `GNUCASH_WRITES_ENABLED=false`, and sensitive-data hygiene before creating any tag or GitHub release.

## Verification

- `cd apps/api && pytest tests/test_health.py tests/test_auth.py -q` — passed: `17 passed, 1 warning in 4.94s`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed with no output.
- `git tag --list 'v0.1.4-readonly'` — passed: no local tag output.
- `gh release view v0.1.4-readonly --json tagName,url,isPrerelease,isDraft 2>&1 || true` — passed: `release not found`.
- `git diff --check` — passed.
- Sensitive tracked-file scan — passed after refining the scan to avoid treating source route names such as `export` as artifacts:
  - no unexpected tracked `.env`, app DB, runtime DB, private book, backup artifact, secret/token/cert/key, CSV export artifact, or private media artifact paths;
  - allowed existing placeholders/fixtures: `.env.example`, `data/app/.gitkeep`, `apps/api/tests/fixtures/test-book.gnucash.sqlite`, and `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite`.

## Non-goals / safety boundaries

- No product code changed.
- No tests were added because this was documentation/release-artifact preparation only; no behavior or UX implementation changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No release, tag, package, uploaded artifact, or publication was performed.
- No real/private GnuCash book, app DB, backup, `.env`, token, key, cert, screenshot, export, private path, or real/private financial data was added or committed.
- Docs remain honest: pre-alpha, test copies first, no production guarantee, no security-audit claim, no real/private-book write-safety claim.

## Expected artifacts

- `docs/release/v0.1.4-readonly-notes.md`
- `docs/release/v0.1.4-readonly-checklist.md`
- `docs/release/v0.1.4-readonly-final-gate.md`
- Updated `CHANGELOG.md`
- Updated `README.md`
- Updated `PROJECT_STATUS.md`
- `docs/handoff/phase-141.md`

## GitHub / release state

- No release/publication gate was executed beyond preparation and local release-state checks.
- No tag or GitHub release was created.
- Phase 141 was committed as one documentation/release/status commit and pushed to `origin/main`.
