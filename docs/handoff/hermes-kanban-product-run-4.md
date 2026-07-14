# Hermes Kanban product-development run 4

Status: **PRODUCT #55 CLOSEOUT ACCEPTED; DOCS/STATUS COMMIT AWAITS OPERATOR
FF/PUSH/EXACT-HEAD CI**

This handoff records the fourth product-development run on the dedicated Hermes Kanban board. It
covers [issue #55](https://github.com/valentusys/gnucash-web-companion/issues/55): advanced
read-only account exploration with hierarchy, native-commodity balances, bounded activity, and
transaction/report drilldowns.

## Scope and publication boundary

- Documentation/status closeout only; this file does not claim a release.
- Current public read-only beta remains `v0.5.0-public-readonly-beta`.
- `v0.5.1-public-readonly-beta` and `v0.4.0-owner-writebeta` remain unpublished.
- GnuCash Desktop remains authoritative. `GNUCASH_WRITES_ENABLED=false` remains the default.
- Issue #55 is read-only: no GnuCash writes, no FX conversion, and no direct frontend access to a
  GnuCash file/database.

## Baseline, board, and integration

- Baseline before run 4: `0d9381544118a64795827b24d787d1a8e7d998c0`.
- Accepted/integrated product head before this docs commit:
  `3dfd60604d78e329284979442b959aea4b6763a2`.
- Accepted product tree: `db72bc9ab91db4d27e2a8b2719c58ba9fdda5751`.
- Integration method: fast-forward-only main integration of accepted product source.
- `main`, `origin/main`, and this worktree HEAD were equal at
  `3dfd60604d78e329284979442b959aea4b6763a2` before this docs/status commit.
- Hermes board: `gnucash-web-companion-product-dev`.
- Board DB: `/home/val/.hermes/kanban/boards/gnucash-web-companion-product-dev/kanban.db`.
- Repo-local supervisor SHA-256:
  `8d9e0aec155bbe6248b09512077b0b3197c4386d4c8c7a890dc3a56e6055e766`.

## Task graph and acceptance

| Task | Final factual outcome |
|---|---|
| `t_58589927` | Contract task for #55 scope and frozen API. |
| `t_162480d5` | Accepted backend account explorer/overview/activity source. |
| `t_f05a3e42` | Accepted SSR account explorer/detail frontend source. |
| `t_fe3d520c` | Accepted performance/benchmark coverage. |
| `t_88eef6f9` | Rejected browser gate predecessor; not acceptance evidence. |
| `t_77189d1d` | Accepted redaction replacement for activity diagnostics. |
| `t_319b9585` | QA1 ACCEPT. |
| `t_8e1e691a` | QA2 FINAL ACCEPT. |

Rejected predecessors are recorded only as rejection history; task `status=done` alone is not treated
as acceptance.

Issue #54 factual closeout source patch was integrated once: stable patch
`2a2296aa92ff3e0dc17d53aa71c7cc3f46ef005a`. QA-local
`fd98bd369cbaaaec4149f14f0ce03f3c3a792b58` was not integrated.

## Integrated stable patch IDs

Exact stable patch IDs integrated for run 4, in order:

1. `2a2296aa92ff3e0dc17d53aa71c7cc3f46ef005a`
2. `326b1804e5ddf38fc2776afcc2d14844e95bca18`
3. `bb836f321f4f2bd1a641b93d74f9d8f23ecfaf1b`
4. `b2db78bf5a738817ae07407d72e3f2112c18b89f`
5. `39308d7f3ddfd0d4508ed7853573753e8f61cf75`
6. `08f11c87a8648f9244034f99c28ef6043bfd75c6`
7. `a75ff1dd4cc8afa17a17b19dcb06160caa57b805`
8. `9abf7cc2d43dd805a52e141746cf2089e473cd88`
9. `833a0c45188dfa4351e02a6907a23fd2799dd6be`
10. `ac77e4cd4c48dd5c237f470d6f55fb0430f9a224`

## User-visible read-only functionality

The accepted #55 product head adds:

- hierarchical account explorer;
- bounded account overview and activity sections;
- native commodity exact amounts without float or FX conversion;
- deterministic repair/partial semantics for bounded account sections;
- SSR navigation for account explorer/detail paths;
- transaction and report drilldowns;
- EN/RU desktop and mobile browser coverage.

Frozen account endpoints:

```text
GET /books/{book_id}/accounts/explorer
GET /books/{book_id}/accounts/{account_id}/overview
GET /books/{book_id}/accounts/{account_id}/activity
```

Legacy account endpoints and `AccountDTO.balance` are preserved. No float/FX path and no write path
were added.

## QA2 evidence

QA2 final acceptance evidence on the product head recorded:

- full API: `1229 passed`;
- focused backend/API account matrix: `80 passed`;
- frontend `check`, `build`, static checks, and all browser gates passed;
- account gate counters: account explorer `4`, overview `6`, activity `5`, transaction explorer `1`;
- HTML private sentinel: `false`;
- API forbidden `0`, browser forbidden `0`, runtime exceptions `0`, console errors `0`;
- mobile width/scroll: `320/320`.

Exact product CI after product integration:

- GitHub Actions run
  [29297230998](https://github.com/valentusys/gnucash-web-companion/actions/runs/29297230998)
  concluded `success` for head `3dfd60604d78e329284979442b959aea4b6763a2`.
- Jobs succeeded: Backend tests, Frontend checks, Foundation checks, and Docker Compose validation.

## Generated-only local benchmark medians

These medians are local, generated/disposable, synthetic-only evidence. They are not production
performance claims. Counters: `synthetic=true`, `contains_real_data=false`, `read_only=true`,
`write_routes=false`.

| Dataset | Case | Median |
|---:|---|---:|
| 1k | unfiltered tree | `80.98 ms` |
| 1k | text tree | `62.78 ms` |
| 1k | flat search | `63.90 ms` |
| 1k | type filter | `62.60 ms` |
| 1k | root overview | `60.88 ms` |
| 1k | recursive native buckets | `62.85 ms` |
| 1k | direct activity | `32.66 ms` |
| 1k | transaction drilldown | `61.98 ms` |
| 10k | filtered tree | `619.89 ms` |
| 10k | root overview | `616.38 ms` |
| 10k | direct activity | `81.58 ms` |
| 10k | drilldown | `257.93 ms` |

The 10k unfiltered tree request returned the expected bounded `result_too_large` response.

## Issue closeout facts

- Issue URL: <https://github.com/valentusys/gnucash-web-companion/issues/55>.
- Issue #55 is closed as completed at `2026-07-14T01:08:15Z`.
- Final acceptance comment:
  [#issuecomment-4964411655](https://github.com/valentusys/gnucash-web-companion/issues/55#issuecomment-4964411655),
  created `2026-07-14T01:08:13Z`.

## Safety counters

- Owner/private/original/working/Syncthing/only-copy books opened/copied/mutated: `0`.
- Product acceptance CREATE/PATCH/DELETE/batch: `0`.
- GitHub release/tag/package/container publication: `0`.
- Write-default flips: `0`.
- Committed private/runtime artifacts: `0`.
- FX conversion added: `0`.

## Remaining operator gate for this docs commit

This docs/status commit itself still requires FF-only integration/push and its own exact-head CI
before final operational closeout. This file intentionally does not invent the future docs commit
SHA, CI run, time, issue/task, or result.
