# Hermes Kanban product run 9 — issue #59 controlled CREATE handoff

Status: final factual closeout after corrected product/docs head
`694d6695c7f74b410d1770f1575c65af6eb94bbb` was integrated and pushed FF-only.
This is not a release note, public write-beta announcement, production claim, or security-audit claim.

## Verdict and closeout source

Parent PM implementation task `t_47be8f49` returned strict ACCEPT for exactly:

- candidate branch: `run/product/recovery4-cumulative-real-browser-20260717T235302Z-7ccf5e3b`
- accepted candidate head: `b1cf990bf3a353726b6c97ce26445074898d50f2`
- accepted candidate tree: `0de2cde2e5a7041ef34d01ffa9e08308fb5cf73b`
- accepted candidate stable patch ID: `81ca3b51f2d19385ab9a56795e9ac86f60605972`
- factual baseline: `280127f92563722d010fb91c7e9af2b6e05a1be0`
- factual baseline tree: `7d5fc3906ed6ccafb2b3d4816254ec4f0990ede2`
- issue: [#59](https://github.com/valentusys/gnucash-web-companion/issues/59)

The first docs-only handoff was then accepted by earlier full product/docs FINAL QA task
`t_fc3b18b6`, run `233`, before the first exact-head CI defect was corrected. Independent
correction FINAL QA task `t_0c9c3f10`, run `236`, returned FINAL ACCEPT for corrected head
`694d6695c7f74b410d1770f1575c65af6eb94bbb`, tree
`4f8246ddd0a5f90d314c9d80a7e819efec6fde77`, parent
`275c6192d85c9cf2d5628729775a455192ea7130`, stable patch ID
`ab62710bf8fa419b276beb64b0cb8331770be979`.

The corrected head was integrated to `main` and pushed by fast-forward only. At the start of this
docs-only factual closeout worktree, `HEAD`, `main`, and `origin/main` all matched the corrected
product/docs head above with a clean status.

## Ordered reviewed source map

Stable patch IDs verified for the PM-accepted source chain, docs handoff, and bounded correction:

1. `8e4cc35c92c1834a7a50b43d562a5db67dac545e`
   -> `f04d5cb10b0a17e81d3810a014cfbb58c87b28ae`
2. `1b7d609db8f8d8f0a8d4df6caf8b9a5e5d1884a3`
   -> `fb881ff75ec058d0563e2b0494d669868567737e`
3. `59908bf49bd06b9d2ab72e2494695cbf87088e2b`
   -> `3abb207dee11f2fbba6417321b77899fd8fdfb99`
4. `433f830520cfc3ddbde72ffe7481a00e2eec7f6a`
   -> `d24adf157fe66b53d45365687d45c4e16da30b19`
5. `d1ad7ec6dee6607adb3041c060bb474b61fad3ca`
   -> `f1a8f241d823db27531b7f169cc7d95814dfd80e`
6. `b1cf990bf3a353726b6c97ce26445074898d50f2`
   -> `81ca3b51f2d19385ab9a56795e9ac86f60605972`
7. `275c6192d85c9cf2d5628729775a455192ea7130`
   -> `236e1d8081147baed1baf4992e4204061f395ddb`
8. `694d6695c7f74b410d1770f1575c65af6eb94bbb`
   -> `ab62710bf8fa419b276beb64b0cb8331770be979`

## First CI defect and correction provenance

The earlier full product/docs FINAL QA accepted the pre-correction docs/product head, but the first
exact-head CI exposed bounded test-guard defects rather than a changed product behavior claim. The
correction commit `694d6695c7f74b410d1770f1575c65af6eb94bbb` changed only:

- `apps/api/tests/test_transaction_create_control_plane.py`
- `apps/web/scripts/test-transaction-entry-preview-browser.mjs`

It made the generated-source `replaced_inode` guard use an atomic replacement with verified device
and inode change, and made the browser mutation guard compare forbidden mutation-request counts so
benign late read traffic does not invalidate the safety check. Independent correction QA
`t_0c9c3f10`, run `236`, accepted this exact bounded correction before integration.

## Corrected product-head CI and issue closeout

- Corrected product/docs head: `694d6695c7f74b410d1770f1575c65af6eb94bbb`.
- Corrected product/docs tree: `4f8246ddd0a5f90d314c9d80a7e819efec6fde77`.
- Integration: fast-forward only, pushed to `main` / `origin/main`.
- Exact corrected product-head GitHub Actions run:
  [29630743491](https://github.com/valentusys/gnucash-web-companion/actions/runs/29630743491),
  attempt `1`, exact head, conclusion `success`.
- Successful jobs: Foundation `88043653405`, Frontend `88043653391`, Backend `88043653414`, Docker
  Compose `88043653393`.
- Issue #59 final acceptance comment:
  [#issuecomment-5009945433](https://github.com/valentusys/gnucash-web-companion/issues/59#issuecomment-5009945433).
- Issue #59 closed as completed at `2026-07-18T04:45:00Z`.

## Product behavior represented by the accepted candidate

Issue #59 implements general transaction CREATE only as post-MVP controlled write mode.
The public/MVP posture remains read-only by default.

Required gates and limits:

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Deployment-level write enablement and separate per-book CREATE enablement are both required.
- Owner/editor book assignment is required; admin role alone is not book-data authorization.
- Only ordinary same-native-currency transactions are supported.
- Amounts are exact Decimal/string values, not floats.
- A CREATE request must have 2–50 splits and exact zero-sum by currency.
- Repeated accounts are allowed when the request still satisfies validation and balancing rules.
- FX, trading, and currency conversion are unsupported and rejected; there is no fake conversion.
- A verified backup, stable per-book lock, close/reopen/read-back, idempotency, ownership, and audit
  controls apply to routed CREATE attempts.
- `BACKUP_FAILED` is terminal and non-retryable for the old token/key; a fresh preview/new key is
  required before another CREATE attempt.
- PATCH and DELETE are not normal available product functions.

## Accepted local evidence copied from `t_47be8f49`

All evidence below is copied from the accepted parent task. It is fixed-seed generated/disposable
only; no owner/private/original/Syncthing books or data were listed, accessed, probed, hashed,
copied, or mutated.

Backend and generated checks:

- Full backend: `1484 passed`, `98` visible warnings.
- Generated fixtures plus control plane: `91 passed`.
- Write-safety/default guards and cleanup checks passed in the accepted source matrix.

Frontend/static/browser checks:

- `npm run check`: passed, 0 errors, 0 warnings.
- `npm run build`: passed.
- `npm run test:transaction-create-product-static`: passed.
- `npm run test:transaction-create-product-browser`: passed.
- Old real disposable browser gate passed on one allowed same-head retry after a request-counter
  startup race.

New ordinary-product real browser matrix:

- Command: `npm run test:transaction-create-real-browser`.
- Result: passed in `127.45s`.
- Fixed fixture seed: `59017`.
- Registered disposable books: `11`.
- Successful CREATEs: `4` — expense, income, 3-split, Unicode.
- Same-GUID duplicate confirms: `4`.
- Typed zero-mutation rejections: `7`.
- Rejection codes: `PREVIEW_PAYLOAD_MISMATCH`, `PREVIEW_STALE`, `CREATE_DEPLOYMENT_DISABLED`,
  `CREATE_BOOK_DISABLED`, `BOOK_WRITE_BUSY`, `BACKUP_FAILED`, `COMMODITY_MISMATCH`.
- Browser requests: `1271`.
- Forbidden mutations: `0`.
- Console events: `0`.
- Generated source hashes/counts stayed unchanged.
- Target mutations: `CREATE=4`, `PATCH=0`, `DELETE=0`.
- Disabled-real-backend negative guard failed as required with `CREATE_DEPLOYMENT_DISABLED`.

Each successful CREATE proved Transactions explorer visibility, Accounts activity exact display delta,
Reports totals, close/reopen/read-back, ownership, idempotency, audit, and one verified backup.

Per-case accepted browser counters:

| Case | GUID | Activity delta | Report total |
| --- | --- | ---: | ---: |
| expense | `b4f0c1a3ac6b4068a6fc53d8913932cb` | `-12.34` | `12.34` |
| income | `5de5e073f202466d81e9bbe6ec98afda` | `2500.00` | `2500.00` |
| three-split | `10152c7058f64ab2af9db01716e2740c` | `-30.00` | `30.00` |
| Unicode | `d8a6fcdc79a4476aa34ff2600085c298` | `-45.67` | `45.67` |

## Owner/private zero vector

The accepted source evidence has owner/private vector exactly zero:

- owner/private/original/Syncthing book list: `0`
- owner/private/original/Syncthing book access/probe/hash/copy: `0`
- owner/private/original/Syncthing CREATE/PATCH/DELETE/batch: `0`
- source deletion: `0`
- forbidden product mutations during real browser matrix: `0`
- private screenshots/exports/raw financial evidence committed: `0`

## Remaining boundaries and docs-only pending state

The corrected #59 product/docs head above is integrated, pushed, CI-green on its exact head, and the
issue is closed as completed. The following are still not implied:

- release/tag/container publication
- public beta or public write-beta announcement
- owner/private pilot approval
- production readiness, hosted-financial-security, security-audit, FX/trading/business/investment
  support claims

This current factual closeout is a newer docs-only commit/head on top of the corrected product/docs
head. Its own exact-head GitHub Actions CI and external docs QA are pending at the time of this edit;
this document does not predict its SHA, CI run, or future success.
