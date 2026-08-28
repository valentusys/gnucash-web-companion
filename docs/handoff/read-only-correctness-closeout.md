# Read-only correctness closeout — issue #61

Status: accepted product head and C2 copied-book gate are complete. This C3 handoff is a docs-only
closeout on top of the accepted product head; its own commit and CI are recorded in the final GitHub
issue and Kanban handoff because a document cannot contain its own future Git commit or CI run ID.

This is pre-alpha, test-copy-first software. This document is not a release, production-readiness
claim, security audit, hosted-SaaS claim, or broad GnuCash compatibility claim.
`GNUCASH_WRITES_ENABLED=false`, selected-currency-only/no-FX reporting, and `NO_RELEASE` remain
unchanged.

## Authority and accepted product head

- Authoritative plan:
  `.hermes/plans/2026-08-23_104451-readonly-correctness-autonomous-roadmap.md`.
- Verified plan SHA-256:
  `040bca87998f4505d045e00abf00f0aea0d1aa6731b95839b19f06c5846abe29`.
- Launch baseline: `500e052cbd90f9c5cd035d3993bb2def9df43347`, tree
  `31246ea28f54fa6d2f8c5b60678848a04369f269`.
- Accepted product head: `43313767f28ff83893a592ee8fd39f9668a6c303`, tree
  `c793f72a099f57ba3d68aa240d790091b2d738cb`.
- Exact-product-head GitHub Actions:
  [33139548729](https://github.com/valentusys/gnucash-web-companion/actions/runs/33139548729),
  completed `success` for Foundation, Frontend, Backend, and Docker Compose.
- C3 fetched origin and verified `HEAD == main == origin/main` at the accepted product head before the
  docs-only closeout; divergence was `0/0`, baseline ancestry passed, and the worktree was clean.
- No merge commit or history rewrite was required. Every accepted product patch is in the single
  first-parent history from the launch baseline to the accepted product head.

## Card reconciliation

The launch graph contained 18 cards. Two recovery/provenance cards were added during A7/A8, so C3
reconciled 20 total records. `ACCEPT` below means the final independent verdict, not merely a worker
self-report.

| Block | Card | Final disposition | Reconciled head/tree |
|---|---|---|---|
| A0 | `t_b8270565` | ACCEPT baseline/contract | `500e052c...` / `31246ea2...` |
| A1 | `t_c228810d` | ACCEPT generated fixture/preflight fixes | `c19d728f...` / `b860841f...` |
| A2 | `t_414983cb` | ACCEPT liabilities/net-worth contract | `fa33a512...` / `a128ab61...` |
| A3 | `t_24070ec4` | ACCEPT historical/as-of summaries | `7b1cb314...` / `153155fb...` |
| A4 | `t_fd0f0e09` | ACCEPT cumulative financial QA; no patch | `7b1cb314...` / `153155fb...` |
| A5 | `t_0e1e54e4` | ACCEPT hierarchy correction | `ce54fff8...` / `7a9d0680...` |
| A6 | `t_28ee6aa6` | ACCEPT bounded account options | `2b0f8d64...` / `916f4453...` |
| A7 | `t_45144e1b` | ARCHIVED, NOT ACCEPT; salvage provenance only | source `e83d6a62...`, tree `81d5cb1d...` |
| A7R | `t_275d57f0` | ACCEPT recovered A7 implementation | `6182dd20...` / `d6ce9e72...` |
| A8 correction | `t_d3a27709` | ARCHIVED after capability loop; candidate accepted by independent A8 re-gate | `68a55797...` / `db264080...` |
| A8 | `t_1faf91f1` | ACCEPT cumulative core-compatibility re-gate | `68a55797...` / `db264080...` |
| B1 | `t_bf4c0f28` | ACCEPT bounded primary reads | `7b7dde9a...` / `b3e4728e...` |
| B2 | `t_20724922` | ACCEPT compact account explorer | `379f33ca...` / `04fc063c...` |
| B3 | `t_2d30a48a` | ACCEPT decision-oriented dashboard | `8a96c231...` / `b4645ee1...` |
| B4 | `t_93b36fbf` | ACCEPT compact comparison reports, round 2 | `1aef0346...` / `101e5a96...` |
| B5 | `t_5552a8f8` | ACCEPT scheduled next-occurrence backend | `0acf7e67...` / `e34137b1...` |
| B6 | `t_27e49a58` | ACCEPT scheduled forecast/mobile UI | `e1f30105...` / `faeba95d...` |
| C1 | `t_62025eb9` | ACCEPT dependencies, Docker contexts, browser harness | `43313767...` / `c793f72a...` |
| C2 | `t_708c7a77` | ACCEPT final QA and fresh copied-book dogfood; no patch | `43313767...` / `c793f72a...` |
| C3 | `t_e1670e20` | docs-only exact-head closeout | product base `43313767...` / `c793f72a...` |

The archived A7 source was never merged directly. Recovery cherry-picked its patch to canonical commit
`1ac3aa7715c7bf20af9a15b491e8dcbd139beff2`; source and canonical commits share tree
`81d5cb1d7709d9f90ef1244b456c3728e8a5c9e3` and stable patch ID
`0c192d5bdef12fca890033a50c8bf4b910a0d709`. Recovery commit
`6182dd20463c9d712cb6297a4feb95b989e94238` completed the contract and was independently accepted.
The archived A8 correction card did not reach its own terminal ACCEPT because repeated scoped-Docker
cleanup attempts hit the old headless approval loop. The correction candidate was nevertheless
cleaned, integrated, and independently re-gated by A8 at the exact unchanged head before acceptance.

## Commit, tree, and stable patch ledger

The complete product history from launch baseline to accepted head was recomputed with `git log` and
`git patch-id --stable`:

| Owning block | Commit | Tree | Stable patch ID |
|---|---|---|---|
| A1 | `bd2cc3ec346768e95eebff4bddce7d3c9eea957f` | `fb4df88dc42fe377eac2e860f9f077e3701000de` | `90bff71038da5959a7d64ca44ef64f07e3b18fa8` |
| A1 | `2060ecadb96f54f0372395c544f66a0404d618e3` | `768fecb6df52e6325c91a3e90a2bc1041a94c73c` | `45e3d9aff28c670e9d0334188d721d7da6f21b00` |
| A1 | `5edd1b3e5315b41cdd8f2117bf1ec3957945c338` | `746755cdfc9545b5fc6577f15386994c4b595ef0` | `83636f4ddeb5a4cebf9f2a0f59922604a8f43aee` |
| A1 | `c19d728f68f3b6b3022ee427f3b50cbfe54b4abd` | `b860841fb164d67f01617d89b7b432036b4e25bc` | `ed22c211eea628faa392c55c4481d1f8011b6c84` |
| A2 | `fa33a512e841de022b03601df009555b5a4cb9c2` | `a128ab61f0836214d21ac9ed528f77022c8945dd` | `7250c7d5a3b8cba8caea5ff1cea3699de24d1100` |
| A3 | `7b1cb3140bf11a9ae3a51a2b97e0ccc7a72163aa` | `153155fb7dac353ec7a6f9fc9486d6020148cb07` | `99bc46816a59303306ced63a28125b007729199c` |
| A5 | `ce54fff85ccc11549ce517e9ac09f94ca42ab178` | `7a9d0680e03b1d5a7434ec54713157a693c3f5a5` | `7107d36bf52b67437588ca39aa0afc61a542c997` |
| A6 | `75fc3a3a2684970d1b46152e7e9d69ab71fc2034` | `d0ac377e584343fa731c1aeffa667a9f84816094` | `6bad1db27310229fc34590e055b5f341c5a90e8b` |
| A6 | `2b0f8d643f153a9c1ef83752e814262796894ea3` | `916f4453cd030ae847655c32304cb8b9d4c69a47` | `685c6dcc53ab7f1f7bc425c74c85dcb81bbd2baf` |
| A7R | `1ac3aa7715c7bf20af9a15b491e8dcbd139beff2` | `81d5cb1d7709d9f90ef1244b456c3728e8a5c9e3` | `0c192d5bdef12fca890033a50c8bf4b910a0d709` |
| A7R | `6182dd20463c9d712cb6297a4feb95b989e94238` | `d6ce9e7258d10a76564c86c04ac38693f6010c21` | `f8ed00322142c323131d96b13b0ec84cbaff56ec` |
| A8 correction | `68a5579782ce00d3b0109ceab26830d36820d19b` | `db264080af3abd8956ea2c3d7bdd89544bbffcff` | `c176676def64955b56c43c960981d2b63713bab7` |
| B1 | `7b7dde9a5d04c4613a81c59b30a03d6fbc80984d` | `b3e4728ef8a08d7943fc57fcbe98096f2fd4a13a` | `40bbcf1b9804664dc375acdaa45514edfaee7e8e` |
| B2 | `379f33ca0e362284ce85c1c40f744580dc048920` | `04fc063c83b921eee01cfae9bec4f363e9c9a40f` | `00eea10462758132b3bc2f9c729a68a347864c5d` |
| B3 | `8a96c231ba124e70d885d6ff84eb9b4fee41cf32` | `b4645ee14d77ff9c23d8bdd13ddff12f05b058d4` | `c3dbc7c1f65fb5d9c5dc17a747608e8e833b62f2` |
| B4 | `f43a40d5eeec89270b495ff7755fc1c581f6a9a1` | `fae9eaf89daaf21e11f3b0fc30b161f4c39acb06` | `e0e108b451deac502f9af5900831fbf04c965030` |
| B4 | `1aef034638e7a96cd3d26da93aaab5605bc464f6` | `101e5a9696e61ef03fb95f68281b604eddd5ffc1` | `632fe8c49f312a93cfc0b3e7a6190eff5d317daf` |
| B5 | `0acf7e673dfed31c830f8128f4520a790cf055f1` | `e34137b1a8101652178b296e9c5257fcba97a424` | `a03f8bd21bb8d6082b3e1cbbe2926820303158d6` |
| B6 | `e1f30105e136ed969762e7fca512a65d0eff62a5` | `faeba95d9e02a5845560ea74d00b6e2075120a3b` | `f18eed016babb3c17108473ca6ea1bf9133f0a07` |
| C1 | `43313767f28ff83893a592ee8fd39f9668a6c303` | `c793f72a099f57ba3d68aa240d790091b2d738cb` | `6dd5738e007ccca45a50a8f2ab3246693d180311` |

QA-only cards A0/A4/A8/C2 and C3 before its docs-only commit add no product patch.

## Final product-head verification

C3 reran the complete accepted matrix against product head `43313767...`:

- Repository-native root guards passed: public status, write-safety defaults, Markdown readability,
  tracked hygiene (`2068` paths), `git diff --check`, and Compose validation with dummy credentials.
- Backend, from the canonical `apps/api` working directory: `1556 passed`, `142 warnings`,
  `719.87s`. An initial invocation from repository root also collected seven separate smoke-protocol
  tests and failed only a cwd-relative synthetic-fixture existence assertion; rerunning the canonical
  command from `apps/api` passed the full accepted suite.
- Browser-harness protocol/build contracts: `7/7` passed.
- Frontend: `npm run check` reported zero errors/warnings; production build passed; all 11 static
  contract scripts and all 12 browser aliases passed. Final Transactions evidence reported
  `legacy_accounts=0`, `api_forbidden=0`, `browser_forbidden=0`, and 1280/390/320 viewport coverage.
- Fresh-clone Docker/Caddy smoke passed at exact product head using only the committed synthetic
  fixture. API, web, and proxy became healthy; write mode stayed false; health/login/me/books/
  accounts/transactions/detail/CSV/reports/scheduled/audit passed; validate/CREATE/PATCH/DELETE all
  remained forbidden; Chrome 151 mobile `320x720` and desktop `1280x900` browser flows passed with no
  horizontal overflow, screenshots, downloads, or raw CSV artifacts.
- Synthetic fixture SHA-256 remained
  `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`.
- Docker cleanup passed: zero project containers/networks remained and ports 18080–18082 were closed.
  The temporary clone, runtime, images, and local dependency symlink were removed.

Historical C2 independently passed the same accepted product head with a fresh outside-Git copied
book. Source/copy hashes matched before and after; SQLite quick check passed; copied books were
mounted read-only; writes were false; desktop/mobile required routes passed; forbidden requests and
successful mutations were zero; raw/private artifacts were removed; Docker was stopped; and port
18080 was closed. Only redacted structured Kanban metadata remains.

## Safety, issue, and operational closeout

- Owner/private/original/working/Syncthing book access/list/hash/copy/mutation in C3: `0`.
- Private CREATE/PATCH/DELETE/batch/source-delete: `0`.
- Product source changes in C3: `0`; docs-only closeout files only.
- Tracked raw books, app DBs, backups, screenshots, exports, `.env`, credentials, or private paths:
  `0`.
- Releases, tags, package/image publication, deployment, or public-readiness claim: `0`.
- Issues #45–#50 were observed OPEN with their pre-closeout update timestamps and were not changed.
- Issue #61 was observed OPEN before C3 mutation. Its final comment/closure is gated on successful CI
  for the exact docs-only closeout commit.
- Hermes cron jobs: `0`.
- No source-worker or `scripts/autonomy/supervisor.py` process remained; the C3 worker was the only
  active board worker at final pre-completion inspection.
- The original 18 roadmap cards plus both recovery/provenance cards had no ready/review/blocked/running
  task except C3 itself before completion.

## Bounded remaining risks

- Existing piecash/SQLAlchemy deprecation/cache warnings remain; they are not new C3 failures.
- ESLint 9 has no repository `eslint.config.*`, so the accepted CI/local matrix intentionally skips
  `npm run lint`; type checking, static contracts, browser tests, build, and audit remain green.
- Remove the `cookie` dependency override when the upstream SvelteKit-compatible range is patched.
- The read-only browser smoke can honestly skip transaction detail when its filtered synthetic page
  exposes no row; API transaction-detail and required Transactions/preview coverage pass.
- This milestone does not add FX, external rates, broad compatibility, release publication,
  production readiness, or security-audit claims.
