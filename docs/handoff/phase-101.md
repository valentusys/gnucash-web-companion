# Phase 101 — Copied personal-book dogfood rerun gate

## Status

Complete as a blocked gate. Phase 101 implemented `docs/handoff/phase-101-pm-brief.md` by checking the copied personal-book dogfood prerequisite for GitHub #38 and recording an honest blocked result.

Verdict: `BLOCKED — safe copied book path not provided`.

No `v0.1.1-readonly` tag was created. No GitHub release was created or edited. No package or release artifact was published. Publication remains reserved for a later separate explicit authorization from Val.

## Implementation summary

Created:

- `docs/dogfood/phase-101-personal-copied-book-results.md`
  - records the Phase 101 blocked verdict;
  - records that no explicit safe copied GnuCash SQL book path was available;
  - records non-mutating release-boundary/tooling checks;
  - records why the local copied-book dogfood smoke was not run;
  - preserves redaction and no-private-data rules.

Updated:

- `PROJECT_STATUS.md` — baseline advanced through Phase 101, with GitHub #38 still open/blocked and Phase 102 recommended as the next practical non-publishing compatibility evidence phase.
- `docs/handoff/phase-101.md` — this handoff.

`CHANGELOG.md` was not updated because this phase produced a blocked dogfood gate/status artifact only and did not add user-facing behavior, tooling, or release output.

## Verification summary

| Check | Result |
| --- | --- |
| `git status --short` before work | PASS — clean output. |
| `git rev-parse --abbrev-ref HEAD` | PASS — `main`. |
| `git rev-parse --short HEAD` / `git rev-parse HEAD` | PASS — `80ccc96` / `80ccc9623761445cdb90f40789772a0c4a279fc3` before Phase 101 changes. |
| `git tag --list 'v0.1.1-readonly'` | PASS — no tag output. |
| `gh auth status` | PASS — authenticated as `valentusys`; token output was masked by `gh`. |
| `gh release view v0.1.1-readonly || true` | PASS — `release not found`. |
| `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` | PASS — no output. |
| `python3 scripts/smoke/read-only-api-smoke.py --help` | PASS. |
| `python3 -m py_compile scripts/smoke/read-only-api-smoke.py` | PASS. |
| Safe copied-book path gate | BLOCKED — no explicit `GNUCASH_DOGFOOD_BOOK_PATH`, copy-confirmation flag, inline controller path, or existing redacted handoff path was provided. |

Backend/frontend full suites were not rerun because Phase 101 changed only dogfood/status/handoff documentation and did not change backend product code, frontend application code, Docker Compose config, auth implementation, money handling, or write-mode implementation. Docker Compose config validation and smoke-script help/compile checks were run.

## Dogfood execution summary

The personal copied-book dogfood run was skipped by design because no safe copied GnuCash SQL book path was explicitly provided.

The engineer did not search private directories, guess book locations, open a GnuCash book, copy a book into the repository, generate screenshots, or export CSV data.

## Safety statement

- MVP remains read-only by default.
- `GNUCASH_WRITES_ENABLED=false` remains the required posture for any future dogfood run.
- Controlled writes remain post-MVP/experimental and disabled by default.
- GnuCash Desktop remains the authoritative editor.
- No tag, GitHub release, package, or release artifact was published.
- No backend/frontend/write-mode product behavior was changed.
- No real/private financial data, personal GnuCash books, app DBs, backups, `.env`, screenshots, private CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, or amounts were committed.
- Phase 101 does not claim production readiness, audited security, broad GnuCash compatibility, hosted SaaS readiness, family-wallet positioning, collaborative accounting, or personal-book dogfood success.

## GitHub / backlog note

- GitHub #38 remains open/blocked until Val provides an explicit safe copied/disposable GnuCash SQL book path outside git and confirms it is not the live authoritative book.
- GitHub #39 remains closed; no CSV export regression was investigated or found in this documentation-only gate.
- GitHub #22 remains open for broader compatibility evidence.
- No GitHub release was published.
- No new GitHub issue was created.

## Changed files

- `docs/dogfood/phase-101-personal-copied-book-results.md`
- `docs/handoff/phase-101.md`
- `PROJECT_STATUS.md`

## Risks / follow-up

- #38 remains a real evidence gap. Do not claim copied personal-book dogfood passed until a safe copied/disposable book is explicitly provided and a read-only local smoke passes.
- Publication is still not authorized. A future publish phase must re-check branch, HEAD, clean tree, tag/release absence, recent GitHub Actions state, and release notes before creating any tag/release.
- Compatibility evidence remains narrow; avoid broad GnuCash version/backend claims.

## Next recommended phase

If Val provides a safe copied/disposable GnuCash SQL book path outside the repository, rerun #38 as a local-only read-only dogfood phase with `GNUCASH_WRITES_ENABLED=false` and redacted evidence.

If continuing without such a path and without publication authorization, proceed to Phase 102: compatibility fixture/version matrix v3 for GitHub #22 using only safe disposable/generated or explicitly provided copied test books.

## Commit / push

Implementation commit and push are performed after this handoff is written. Final commit hash and push status are reported in the Phase 101 Telegram/stdout report after verification.
