# Phase 100 — Non-publishing synthetic install/upgrade smoke

## Status

Complete. Phase 100 implemented `docs/handoff/phase-100-pm-brief.md` as a non-publishing synthetic/disposable local Docker smoke on current `main`.

Final smoke verdict: PASS.

No `v0.1.1-readonly` tag was created. No GitHub release was created or edited. No package or release artifact was published. Publication remains reserved for a later separate explicit authorization from Val.

## Implementation summary

Created:

- `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md`
  - records branch/HEAD under test;
  - records tag/release absence;
  - records synthetic fixture source and ignored runtime copy;
  - records Docker Compose config validation;
  - records local Docker API smoke coverage for health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, and disabled write probes;
  - records the honest upgrade limitation;
  - records safety boundaries and backlog state.

Updated:

- `scripts/smoke/read-only-api-smoke.py`
  - added real `--help`/CLI options while preserving environment-variable defaults;
  - added transaction-detail and CSV-export checks to the smoke path;
  - made CSV export header lookup case-insensitive.
- `PROJECT_STATUS.md` — baseline advanced through Phase 100 and next planned phase recommended as non-publishing Phase 101 copied personal-book dogfood only if Val provides a safe copied SQL book path; otherwise choose another practical non-publishing read-only phase or explicitly authorize publication separately.
- `CHANGELOG.md` — narrow Unreleased entry for Phase 100 smoke evidence and smoke-tooling improvement.
- `docs/handoff/phase-100.md` — this handoff.

## Verification summary

| Check | Result |
| --- | --- |
| `git status --short` before work | PASS — clean output. |
| `git rev-parse --abbrev-ref HEAD` | PASS — `main`. |
| `git rev-parse --short HEAD` / `git rev-parse HEAD` | PASS — `10d9233` / `10d923316b8454a173d41ea7ee33127ce3cb6b05` before Phase 100 changes. |
| `git tag --list 'v0.1.1-readonly'` | PASS — no tag output. |
| `gh auth status` | PASS — authenticated as `valentusys`; token output was masked by `gh`. |
| `gh release view v0.1.1-readonly || true` | PASS — `release not found`. |
| `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` | PASS — no output. |
| `python3 scripts/smoke/read-only-api-smoke.py --help` | Initially exposed tooling drift before the fix; PASS after adding argparse help. |
| `python3 -m py_compile scripts/smoke/read-only-api-smoke.py` | PASS. |
| Local Docker build/start | PASS — `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy GNUCASH_WRITES_ENABLED=false docker compose up --build` built and started API/web/proxy. |
| `SMOKE_ADMIN_PASSWORD=dummy scripts/smoke/read-only-api-smoke.py` | PASS — health, login/auth, book discovery, accounts, transactions, transaction detail, CSV export, report summary, and disabled validate/create/patch write probes passed. |
| `git diff --check` | PASS. |

Product backend/frontend full suites were not rerun because Phase 100 changed smoke tooling and documentation/status artifacts, not backend service/router code, frontend application code, Docker Compose config, auth implementation, money handling, or write-mode implementation. The phase did run Docker Compose config validation and an actual local Docker/API smoke with synthetic data.

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` was used for the local Docker smoke and remains the required default posture.
- Controlled writes remain post-MVP/experimental and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- No tag, GitHub release, package, or release artifact was published.
- No backend/frontend/write-mode product behavior was changed.
- No real/private financial data, personal GnuCash books, app DBs, backups, `.env`, screenshots, private CSV exports, secrets, tokens, certs, keys, or private paths were committed.
- Phase 100 does not claim production readiness, audited security, broad GnuCash compatibility, hosted SaaS readiness, family-wallet positioning, collaborative accounting, or personal-book dogfood success.

## GitHub / backlog note

- GitHub #39 remains closed; no CSV export regression was found in the synthetic Phase 100 smoke.
- GitHub #38 remains open/blocked until a safe copied personal GnuCash SQL book is available outside git; Phase 100 synthetic evidence does not close or satisfy it.
- GitHub #22 remains open for broader compatibility evidence; Phase 100 does not add broad compatibility claims.
- No GitHub release was published.
- No new GitHub issue was created.

## Changed files

- `scripts/smoke/read-only-api-smoke.py`
- `docs/dogfood/phase-100-synthetic-install-upgrade-smoke.md`
- `docs/handoff/phase-100.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## Risks / follow-up

- Publication is still not authorized. A future publish phase must re-check branch, HEAD, clean working tree, tag/release absence, recent GitHub Actions state, and release notes before creating any tag/release.
- #38 remains a real evidence gap for copied personal-book dogfood; do not claim it passed in release notes or announcements.
- A true upgrade from `v0.1.1-readonly` could not be tested because that tag/release does not exist and was not authorized for publication.
- Compatibility remains narrow; avoid broad GnuCash version/backend claims.

## Next recommended phase

If Val explicitly authorizes publication in a separate request: re-check branch, HEAD, clean tree, tag/release absence, recent GitHub Actions state, and release notes, then run a dedicated publish phase for `v0.1.1-readonly`.

If continuing without publication authorization: Phase 101 should run copied personal-book dogfood only if Val provides a safe copied GnuCash SQL book path outside git. If no safe copied book is available, choose another practical non-publishing read-only maintenance/dogfood task rather than claiming #38 success.

## Commit / push

Implementation commit and push are performed after this handoff is written. Final commit hash and push status are reported in the Phase 100 Telegram/stdout report after verification.
