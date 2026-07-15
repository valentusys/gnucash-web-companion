# Hermes Kanban product-development run 6

Status: **PRODUCT #57 AND ISSUE CLOSEOUT COMPLETE; FACTUAL DOCS SNAPSHOT**

This handoff records the sixth product-development run on the dedicated Hermes Kanban board. It
covers [issue #57](https://github.com/valentusys/gnucash-web-companion/issues/57): admin-managed local
users, explicit book assignments, and immediate session/access enforcement.

## Scope and publication boundary

- Documentation/status closeout only; this handoff does not publish a release, tag, package, or image.
- Current public read-only beta remains `v0.5.0-public-readonly-beta`.
- GnuCash Desktop remains authoritative. `GNUCASH_WRITES_ENABLED=false` remains the default.
- The accepted feature manages app-metadata users, sessions, assignments, and audit rows. It does not
  create, edit, or delete GnuCash source data.
- Product and QA work used synthetic/disposable/test-copy sources only. No owner/private/original/
  working/Syncthing/only-copy source was accessed.
- This is pre-alpha evidence, not a production-readiness, security-audit, broad compatibility, or
  production performance claim.

## Baseline, board, and integration

- Baseline before run 6: `943898986133cc2282d9016c8c92c3c5ddc08a1d`.
- Accepted and integrated product head before this docs task:
  `145654bae771eac622f3d1fb1d1c87bd90d42e3b`.
- Accepted product tree: `ee39862c609d9b628f6f5836bdd89c598f5dec04`.
- Integration method: fast-forward-only integration of accepted product source.
- `main`, `origin/main`, and this docs worktree started equal at the accepted product head.
- Project identifier: `gnucash-web-companion`.
- Hermes board: `gnucash-web-companion-product-dev`.
- Run identifier: `hermes-kanban-product-run-6`.
- Documentation task: `t_1916e118`.

## Task graph and acceptance

| Task | Final factual outcome |
|---|---|
| `t_89641439` / `t_63289fc2` | PM and QA accepted #56 before the #57 contract/work began. |
| `t_fc5ac7ba` | B1 accepted contribution. |
| `t_b7ea6c23` | F1 accepted contribution. |
| `t_13ddcf35` / `t_3f9bc2ed` | F1B rejected predecessor, then bounded correction. |
| `t_9c0f38ad` / `t_069a464e` | B2 rejected predecessor, then bounded correction. |
| `t_92b8235f` / `t_8caf711e` | B3 rejected predecessor, then bounded correction. |
| `t_bc5bf0dd` / `t_7e7f5172` | F2 rejected predecessor, then bounded correction. |
| `t_8dd9d20d` / `t_0f362518` | R1 rejected predecessor, then bounded correction. |
| `t_3eaaccdf` / `t_d266e955` | G1 cumulative rejection, then accepted correction. |
| `t_9654123e` | PM rejected four bounded contract defects. |
| `t_9337b9b9` | B4 accepted backend correction. |
| `t_af79a801` | F3 accepted frontend pagination correction. |
| `t_af22db3e` | PM ACCEPT after independent correction re-review. |
| `t_293ceb80` | QA1 ACCEPT on the exact 16-patch product tree. |
| `t_1708daa8` | QA2 ACCEPT on the same exact head and tree. |

Rejected predecessors were not standalone acceptance evidence. Their corrections entered the final
chain only after later review and exact-tree testing by PM, QA1, and QA2.

## Integrated stable patch IDs

Exact stable product patch IDs integrated for run 6, in order:

1. `7125d4fbe617e405c78afa937a07be7e9965088e`
2. `8b2ca3b2c33701b9b8384f9eb14f467f1c6b0779`
3. `30c86c243e48a993f7d3c200148cf6c250e98288`
4. `1bdb305f9c0a4789d5870bcddeeda48cf967398a`
5. `bdbe2b036ce2a21d37d1dd6f2734ca2fc0837888`
6. `3ef94996ff0959d13a03d3f11555bb0572cff32c`
7. `1024411237fad6805df42cb82c85bc6a78b1dd9e`
8. `186c2afc6f87f73c9366b97ba472c77b08180aa6`
9. `cedeaee3a105eaf49fd1140cf129e12728ac8073`
10. `37d88eba4395d6a524118d2edfa86e16535f7b30`
11. `6ff9b91014f266e2283409625b86f4de5082d51b`
12. `fb1949a494792e2a81298dc64024ce92dcdedab3`
13. `8302869e6e4fd0732b6a0ef7b68590b34049270d`
14. `b0d716b887a86fa4e1594121aec0b1aa124592fc`
15. `88ac985247f8940d57bcc4f8209857dfef096f1c`
16. `0e727c1bcd5500a59c647d809fce640ab633a4db`

## User-visible behavior and security boundary

- Global admins alone can create and manage local users. A new user starts enabled with zero book
  access unless an admin explicitly grants access; neither the default book nor a newly registered book
  grants implicit access.
- Username and global-admin choice are immutable in this milestone. Display name is the only editable
  profile field. Self-disable and last-enabled-admin protections are backend enforced, including races.
- Disable and password reset increment the authentication version. Existing cookies become invalid on
  the next authenticated request; disabled users cannot log in.
- Password values are exact secrets: leading and trailing spaces survive create, reset, and login and
  are not trimmed, repopulated, logged, echoed, or returned as hashes. Policy requires 12–128 Unicode
  code points, no more than 72 UTF-8 bytes, and at least three of lowercase, uppercase, digit, and
  Unicode punctuation/symbol categories `P*`/`S*`. Spaces, controls, combining marks, and uncased
  letters do not count as symbols. The normalized username and an exact weak-password denylist are
  also rejected.
- Book grants are explicit, admin-only, and limited to active, non-archived books. Live revoke and
  direct inaccessible-book requests deny before opening the GnuCash source.
- Book roles are truthful app-metadata labels: `viewer` is read-only; `editor` and `owner` do not grant
  global admin or enable GnuCash writes.
- The local recovery CLI enables an admin and/or resets a password through stdin or TTY. It uses fixed
  redacted messages, touches app metadata only, and never opens a GnuCash source.
- The server-rendered admin UI handles zero books, revoked selected-book fallback, and separate empty,
  stale-page, and API-error states. Active-book options use bounded metadata-only `limit`/`offset`
  pagination with `total_count` and `has_next`; page context survives grant/update actions.
- User-list items are summary/count-only DTOs: id, username, display name, admin/enabled flags,
  assignment count, and timestamps. Assignments appear only in detail responses; password hashes and
  authentication versions are never serialized.
- The audit contract is closed and redacted. Grant/update uses `book_access_granted` with allowlisted
  results; revoke uses `book_access_revoked`. `book_id` stays in its audit column, while payload keys and
  role/result values are allowlisted and invalid values fail before write.
- No #57 route writes to a GnuCash source. `GNUCASH_WRITES_ENABLED=false` remains independent of user or
  book role.

## QA1 and QA2 evidence

Both independent gates tested the exact product head
`145654bae771eac622f3d1fb1d1c87bd90d42e3b` and tree
`ee39862c609d9b628f6f5836bdd89c598f5dec04`.

- QA1: full backend `1358 passed` with 97 warnings; focused #56/#57 backend `96 passed`; all exact 18
  frontend commands passed; root guards and Compose validation passed.
- QA2: full backend `1358 passed` with 97 warnings; focused #56/#57 backend `96 passed`; the same exact
  18 frontend commands passed; root guards and Compose validation passed.
- Both gates ran this exact frontend sequence under `GNUCASH_WRITES_ENABLED=false`:

1. `npm run check`
2. `npm run test:auth-routes`
3. `npm run test:admin-users`
4. `npm run test:admin-users-auth-hardening`
5. `npm run test:admin-users-browser`
6. `npm run test:transaction-entry-preview`
7. `npm run test:transactions-explorer`
8. `npm run test:reports`
9. `npm run test:money-strings`
10. `npm run test:books-onboarding`
11. `npm run test:accounts-explorer`
12. `npm run test:transaction-entry-create-disposable-browser`
13. `npm run test:accounts-explorer-browser`
14. `npm run test:transactions-explorer-browser`
15. `npm run test:books-onboarding-browser`
16. `node scripts/test-reports-browser.mjs`
17. `node scripts/test-dashboard-browser.mjs`
18. `npm run build`

- Admin-browser counters were: normal-user admin API calls `0`, expired-session admin payload calls `0`,
  product/browser product write calls `0` / `0`, secret sentinel leaks `0`, viewport width `320`, and
  exact page-2 grant DTO `true`.
- Across the read-only browser gates, observed API/browser forbidden counters were `0`; onboarding
  source copy/modify/delete was `0`, and the disposable test-copy source hash was unchanged.

## Synthetic reliability evidence

This evidence used generated local app metadata and synthetic/disposable/test-copy sources only. It is
not a production timing, scale, or compatibility claim.

- The 1-user, 100-user, and 1000-user list probes each used three SQLite queries/statements.
- Their ORM row-load counters were user/book/access `1` / `0` / `0`; the one user load was live auth.
- Large inaccessible-book access returned denial before source use. Preflight, piecash, and GnuCash
  service opens were all `0` for that path.
- GnuCash mutation-capable requests in R1 evidence were `0`. Expected local app-metadata audit/user/
  assignment operations used disposable app databases only.

## Exact-head CI result

Exact-product-head GitHub Actions run
[29448413433](https://github.com/valentusys/gnucash-web-companion/actions/runs/29448413433)
completed successfully for Backend tests, Frontend checks, Foundation checks, and Docker Compose
validation.

## Issue closeout facts

- Issue URL: <https://github.com/valentusys/gnucash-web-companion/issues/57>.
- Issue #57 closed as completed at `2026-07-15T20:39:00Z`.
- Final acceptance comment:
  [#issuecomment-4985069377](https://github.com/valentusys/gnucash-web-companion/issues/57#issuecomment-4985069377).

## Residual warnings and evidence limits

- Existing piecash/SQLAlchemy deprecation, relationship-overlap, and date-type cache warnings remain.
- Frontend dependency installation reported three low-severity npm audit findings.
- These warnings were not acceptance blockers for the bounded #57 contract, but the evidence does not
  establish broad security, production readiness, compatibility, or production performance.

## Exact safety counters

- Owner/private/original/working/Syncthing/only-copy source access or probe: `0`.
- #57 GnuCash source CREATE/PATCH/DELETE/batch requests: `0`.
- R1 mutation-capable GnuCash requests: `0`.
- Admin-browser product/browser product write calls: `0` / `0`.
- Normal-user admin API calls and expired-session admin payload calls: `0` / `0`.
- Secret sentinel leaks: `0`.
- Write-default flips: `0`; `GNUCASH_WRITES_ENABLED=false` remains default.
- Release/tag/package/image publication by this run: `0`.

## Documentation commit boundary

This handoff records the already completed product integration, exact-product-head CI, and issue
closeout. It intentionally does not claim this docs task's commit SHA, tree, stable patch ID, push
state, or CI result. The operator verifies and reports those later, avoiding self-reference or
invented future evidence.
