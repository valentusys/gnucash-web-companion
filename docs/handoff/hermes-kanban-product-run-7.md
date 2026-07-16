# Hermes Kanban product-development run 7

Status: **#57 CORRECTION COMPLETE; #58 PRODUCT AND ISSUE CLOSEOUT COMPLETE; FACTUAL DOCS SNAPSHOT**

This handoff records the seventh product-development run on the dedicated Hermes Kanban board. It
covers the independent re-check/correction of [issue #57](https://github.com/valentusys/gnucash-web-companion/issues/57)
and the implementation/closeout of [issue #58](https://github.com/valentusys/gnucash-web-companion/issues/58):
safe app-metadata backup, verify, restore rehearsal, and synthetic public-readonly upgrade rehearsal.

## Scope and publication boundary

- Documentation/status closeout only; this handoff does not publish a release, tag, package, or image.
- Current public read-only beta remains `v0.5.0-public-readonly-beta`.
- GnuCash Desktop remains authoritative. `GNUCASH_WRITES_ENABLED=false` remains the default.
- #58 backs up/restores only the companion app metadata SQLite DB. It does not back up, restore, open,
  create, edit, or delete GnuCash source books.
- Product and QA work used synthetic/disposable/test-copy sources only. No owner/private/original/
  working/Syncthing source or app DB was accessed.
- This is pre-alpha evidence, not a production-readiness, security-audit, broad compatibility, or
  production performance claim.

## Baseline, board, and integration

- Baseline before run 7: `4259ed9a42d9c6c239e4a6bfa0d24ad38a0579c7`.
- Corrected #57 head: `32e94fd4e1383c2a19cd6d59612b37b7fbac5cfd`.
- Corrected #57 tree: `7b94e7f350710ce66d51de93da0b49bc0f5ab845`.
- #57 correction exact-head CI: [29456512536](https://github.com/valentusys/gnucash-web-companion/actions/runs/29456512536), success.
- Accepted and integrated #58 product head: `04240b64c906e8e2feca06a0a0fd0ad97e07e67d`.
- Accepted #58 product tree: `8c67b95c726d723c2b4f5f4d9434e6726e93a130`.
- #58 exact-head CI: [29464859269](https://github.com/valentusys/gnucash-web-companion/actions/runs/29464859269), success.
- Integration method: fast-forward-only integration of exact QA-accepted source.
- Project identifier: `gnucash-web-companion`.
- Hermes board: `gnucash-web-companion-product-dev`.
- Run identifier: `hermes-kanban-product-run-7`.

## Task graph and acceptance

| Task | Final factual outcome |
|---|---|
| `t_cfb9e6f9` | PM rejected original #57 because admin-user ordering did not match normalized-username contract. |
| `t_739d554f` | Independent QA initially accepted original #57; PM/QA disagreement triggered correction flow. |
| `t_01981c5e` | Malformed non-wrapper PM child archived before dispatch. |
| `t_7ae4d353` | #57 normalized-order correction accepted at `32e94fd4e1383c2a19cd6d59612b37b7fbac5cfd`. |
| `t_3aa176ef` | PM reacceptance accepted corrected #57 head. |
| `t_271bd0ef` | QA reacceptance accepted corrected #57 head. |
| `t_5a7079bc` | #58 app-metadata recovery CLI foundation accepted. |
| `t_e9cd0be2` | #58 upgrade rehearsal tooling produced valid patch but full smoke exposed Docker import blocker. |
| `t_317f39c5` | Docker import/source-root blocker fixed and full upgrade smoke passed. |
| `t_e96fac05` | QA1 rejected because backup/restore chmodded existing operator parent directories. |
| `t_12c2711b` | Parent-permission defect fixed at `04240b64c906e8e2feca06a0a0fd0ad97e07e67d`. |
| `t_ba9b5520` | QA1 recheck accepted exact #58 head/tree. |

Rejected predecessors were not standalone acceptance evidence. Their corrections entered the final chain
only after bounded fixes and exact-head re-review.

## Integrated stable patch IDs

Exact stable #58 patch IDs integrated, in order:

1. `a4b0de9d93e56ef7636f0030141ce9bef34a781e` — app-metadata recovery CLI foundation.
2. `931c73b84c0d86617467345bc90a6e89475b6223` — synthetic public-readonly upgrade rehearsal.
3. `937732b1ce0820917e462448ab1330c98d9d5b38` — Docker/container source-root import fix.
4. `1f0aed2522b5710dc852e760201cc66598e7a08f` — non-destructive parent-permission fix.

## User-visible behavior and security boundary

- `scripts/app_metadata_recovery.py` exposes `backup`, `verify`, `restore-rehearsal`, and
  `upgrade-rehearsal`.
- Backup requires explicit stopped/offline runtime acknowledgement. The backup path uses SQLite backup
  API evidence, not a raw live DB copy claim.
- Manifests use a fixed redacted allowlist: timestamp/tool/format/schema version, file size, SHA-256,
  SQLite page count/integrity, table names, allowlisted row counts, schema signature, backup method,
  runtime mode, and verification status.
- Restore rehearsal verifies the bundle first and restores only to a new explicit destination outside the
  repo. There is no in-place restore/default overwrite path.
- Existing operator parent directory modes are preserved. Newly created parents are private, and bundle
  directories plus `app.db`, `manifest.json`, and restored DB files are private on POSIX.
- The synthetic upgrade rehearsal starts from `v0.5.0-public-readonly-beta` / `445b12e` and validates
  users, books, access, disabled users, password/auth metadata, cached health, audit rows, selected-book
  fallback, read-only routes, disabled write probes, and unchanged synthetic fixture hashes.
- No browser/API app-DB backup/restore/download surface was added.
- No GnuCash CREATE/PATCH/DELETE/batch path was enabled.

## QA and local evidence

QA1 recheck tested the exact product head
`04240b64c906e8e2feca06a0a0fd0ad97e07e67d` and tree
`8c67b95c726d723c2b4f5f4d9434e6726e93a130`.

Local post-integration evidence on `main`:

- Focused backend #58/#57/write checks: `190 passed, 21 warnings`.
- Full backend suite: `1379 passed, 97 warnings`.
- Root guards passed: public status, write-safety defaults, tracked hygiene, `git diff --check`, Docker
  Compose config, CLI help, and smoke syntax.
- Frontend CI-equivalent matrix passed. ESLint was skipped because no ESLint config exists, matching CI.
- Integrated Docker upgrade smoke passed:
  `PASS synthetic upgrade smoke previous=445b12e current=04240b6 baseline=v0.5.0-public-readonly-beta writes_enabled=false`.
- Docker smoke preserved app metadata state: users `3`, books `3`, access `5`, audit actions `2`,
  `user_version=58`.
- Synthetic fixture SHA-256 values remained unchanged.

## Exact-head CI result

Exact #58 product-head GitHub Actions run
[29464859269](https://github.com/valentusys/gnucash-web-companion/actions/runs/29464859269)
completed successfully for Backend tests, Frontend checks, Foundation checks, and Docker Compose
validation.

## Issue closeout facts

- #57 was reclosed after correction at `2026-07-15T22:56:21Z` with exact-head CI success.
- #58 final acceptance comment:
  [#issuecomment-4987314572](https://github.com/valentusys/gnucash-web-companion/issues/58#issuecomment-4987314572).
- #58 closed as completed at `2026-07-16T01:54:28Z`.

## Residual warnings and evidence limits

- Existing piecash/SQLAlchemy deprecation, relationship-overlap, and date-type cache warnings remain.
- These warnings were not acceptance blockers for the bounded #58 contract, but the evidence does not
  establish broad security, production readiness, compatibility, or production performance.
