# Issue #22 reconcile and Issue #36 owner-writebeta final report

Date: 2026-06-04

## Starting state

Baseline was re-verified from a clean `main` working tree at `bcae43e`.

- `git status --short`: clean at start.
- `git log --oneline -10`: latest commit `bcae43e docs: close issue 22 desktop fixture gate`.
- GitHub open issues: #36 only.
- GitHub #22 REST state: closed.
- GitHub #36 REST state: open.
- Open PRs: REST fallback returned `[]`; `gh pr list` had retryable GraphQL TLS/EOF failures.
- Releases: `v0.5.0-public-readonly-beta` remains current; `v0.5.1-public-readonly-beta` and `v0.4.0-owner-writebeta` are absent.

## Package results

1. Package 1: `CLOSE_22_ON_GITHUB_NARROWLY` remains correct.
2. Package 2: #36 is `READY_FOR_PM_OWNER_WRITEBETA_DECISION`, not release-authorized.
3. Package 3: #36 remains open with exact reduced blockers.
4. Package 4: PM decision is `NO_RELEASE_KEEP_MAINTENANCE`.
5. Package 5: release artifacts skipped because no release was authorized.
6. Package 6: full local final gate passed; no release/tag/package/image was published.

## #22 evidence/state reconciliation decision

Decision: `CLOSE_22_ON_GITHUB_NARROWLY`.

GitHub #22 and repository docs now agree that #22 is closed narrowly. The accepted closure evidence is only:

- one isolated GnuCash 5.14 Desktop-generated synthetic SQLite fixture;
- raw fixture outside git;
- redacted safe metadata only;
- fail-closed preflight accepted;
- default-read-only validation passed with `GNUCASH_WRITES_ENABLED=false` and checksum unchanged.

This does not claim broad Desktop-version support, write compatibility, real-book safety, or PostgreSQL/MySQL/MariaDB/XML support.

## #36 PM decision

Decision: `NO_RELEASE_KEEP_MAINTENANCE`.

#36 remains open. The remaining blockers are now exact:

1. PM has not accepted the original #36 remaining-gates scope as closed.
2. Supported-version write compatibility remains unaccepted beyond narrow synthetic/copied evidence.
3. Real/private/original/working/only-copy mutation remains unauthorized.
4. Any future owner-writebeta release would need a separate conservative authorization and full green final gate.

## Release/no-release decision

No release.

Not published:

- `v0.4.0-owner-writebeta`;
- `v0.5.1-public-readonly-beta`;
- any public write beta;
- any stable, production-ready, or security-audited release;
- any package or image.

`v0.5.0-public-readonly-beta` remains the current public read-only beta.

## Files changed

- `README.md`
- `PROJECT_STATUS.md`
- `docs/write-alpha/issue-36-remaining-gates.md`
- `docs/handoff/issue36-package-1-reconcile-22-state.md`
- `docs/handoff/issue36-package-2-post-22-readiness-audit.md`
- `docs/handoff/issue36-package-3-remaining-gates-decision.md`
- `docs/handoff/issue36-package-4-owner-writebeta-pm-decision.md`
- `docs/handoff/issue36-package-5-release-artifacts-or-skip.md`
- `docs/release/v0.4.0-owner-writebeta-pm-decision.md`
- `docs/handoff/issue22-reconcile-and-issue36-owner-writebeta-final-report.md`

## Commits made

Commit is created after this report is written and pushed as the Package 6 safe docs/guard update. The expected commit subject is:

- `docs: reconcile issue 22 and defer owner writebeta`

## Issues updated/closed

- #22: already closed by `bcae43e`; no new closure was needed.
- #36: remains open. A final conservative no-release/status comment is posted after this report is committed and pushed.

## Tests/gates run

Initial full gate found one README wording regression in the markdown readability test; README was corrected and the full gate was rerun.

Final gate passed:

- `cd apps/api && pytest -q`: `761 passed, 38 warnings`.
- `cd apps/web && npm run check`: 0 errors, 0 warnings.
- `cd apps/web && npm run test:auth-routes`: passed.
- `cd apps/web && npm run build`: passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`: passed.
- `python3 scripts/check_public_status.py`: passed.
- `python3 scripts/check_markdown_readability.py`: passed.
- `python3 scripts/check_write_safety_defaults.py`: passed.
- `python3 scripts/check_tracked_hygiene.py`: passed; 1833 tracked paths inspected.
- `git diff --check`: passed.

## CI status / follow-up

CI is checked after the commit is pushed. GitHub API/GraphQL has intermittent TLS/EOF/reset failures in this environment; those are retried and exact final CI state is recorded in the run log and #36 comment.

## Safety/privacy summary

Mutation counts for this run: CREATE 0 / PATCH 0 / DELETE 0.

No new dogfood was run. No original/private/working/only-copy GnuCash book was touched. No GnuCash book, SQLite book, app DB, backup, CSV export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw private evidence was opened, copied, mutated, committed, or posted.

`GNUCASH_WRITES_ENABLED=false` remains default. Enabled write-alpha/writebeta execution remains `APP_ENV=test` gated.

## Remaining exact blockers

1. #36 remains open until PM accepts closure or exact remaining gates are satisfied.
2. Supported-version write compatibility remains narrow and unaccepted beyond synthetic/copied evidence.
3. Real/private/original/working/only-copy mutation remains unauthorized.
4. Public write beta remains unauthorized.
5. Stable, production-ready, security-audited, public-internet-safe, only-copy-safe, and broad GnuCash compatibility claims remain blocked.

## Next recommended prompt

Continue #36 with a PM closure packet only: decide whether the original controlled-write remaining-gates issue can be closed without any release, preserving owner-only copied/restorable scope, no real-book safety claim, and no public write beta. Do not run dogfood unless a new copied/restorable target and exact same-context authorization are provided.
