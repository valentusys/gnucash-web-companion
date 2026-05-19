# Phase 142 — v0.1.4-readonly release gate and authorized publication

Date: 2026-05-19
Status: DONE

## Goal

Perform the final release gate for `v0.1.4-readonly` and publish only if authorized and safe.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-141.md`.
- Checked starting git state first:
  - branch: `main`;
  - starting HEAD: `eba575e5eb81e345c7a4ccf43d49779691b47e46`;
  - `origin/main` matched the starting HEAD;
  - pre-existing untracked `.hermes/` local agent data was not touched or committed.
- Confirmed release artifacts were present:
  - `docs/release/v0.1.4-readonly-notes.md`;
  - `docs/release/v0.1.4-readonly-checklist.md`;
  - `docs/release/v0.1.4-readonly-final-gate.md`.
- Re-ran the requested final gate checks for backend disabled-write behavior, frontend checks, Docker Compose config, GitHub CI, diff whitespace, write-disabled default, and sensitive tracked-file hygiene.
- Updated release/status docs for publication:
  - `docs/release/v0.1.4-readonly-notes.md`;
  - `docs/release/v0.1.4-readonly-checklist.md`;
  - `docs/release/v0.1.4-readonly-final-gate.md`;
  - `docs/release/v0.1.4-readonly-publication-evidence.md`;
  - `README.md`;
  - `CHANGELOG.md`;
  - `PROJECT_STATUS.md`.
- Published after the Phase 142 commit was pushed and GitHub CI passed:
  - annotated git tag `v0.1.4-readonly`;
  - GitHub pre-release `v0.1.4-readonly`.

## Verdict

`Published as authorized GitHub pre-release`.

The publication gate was safe: clean tracked `main`, `HEAD == origin/main`, tag/release absent before publication, release artifacts present, GitHub CI green, local checks passed, `GNUCASH_WRITES_ENABLED=false` remained default, and no prohibited tracked private-data artifacts were found.

## Verification

- `cd apps/api && pytest tests/test_transaction_writes.py::TestWritesDisabledByDefault -q` — passed: `8 passed, 1 warning`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed with no output.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — passed, API and web render `GNUCASH_WRITES_ENABLED: "false"`.
- `gh run list --limit 5` — passed before publication: latest five `main` runs were `completed success`; after the Phase 142 docs commit was pushed, CI was also checked and passed before tag/release publication.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed after using the project allowlist for intentional fixtures/placeholders/docs images:
  - no unexpected tracked `.env`, app DB, runtime DB, private book, backup artifact, secret/token/cert/key, CSV export artifact, or private media artifact;
  - allowed existing placeholders/fixtures/docs images were not new phase artifacts.
- Publication checks after release:
  - `git tag --list 'v0.1.4-readonly'` — tag exists;
  - `gh release view v0.1.4-readonly --json tagName,url,isPrerelease,isDraft` — release exists, is a pre-release, and is not a draft.

## Published artifacts

- Git tag: `v0.1.4-readonly`.
- GitHub pre-release: <https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.1.4-readonly>.
- Publication evidence: `docs/release/v0.1.4-readonly-publication-evidence.md`.

## Non-goals / safety boundaries

- No product code changed.
- No tests were added because this was a release/documentation/publication gate only; no behavior or UX implementation changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No package, binary artifact, Docker image, uploaded runtime artifact, or production deployment was published.
- No real/private GnuCash book, app DB, backup, `.env`, token, key, cert, screenshot, export, private path, or real/private financial data was added or committed.
- Docs remain honest: pre-alpha, test copies first, no production guarantee, no security-audit claim, no real/private-book write-safety claim.

## Expected artifacts

- `docs/release/v0.1.4-readonly-publication-evidence.md`.
- Updated `docs/release/v0.1.4-readonly-notes.md`.
- Updated `docs/release/v0.1.4-readonly-checklist.md`.
- Updated `docs/release/v0.1.4-readonly-final-gate.md`.
- Updated `README.md`.
- Updated `CHANGELOG.md`.
- Updated `PROJECT_STATUS.md`.
- `docs/handoff/phase-142.md`.
- Git tag and GitHub pre-release `v0.1.4-readonly`.
