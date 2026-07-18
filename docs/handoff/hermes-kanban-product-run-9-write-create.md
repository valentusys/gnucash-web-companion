# Hermes Kanban product run 9 — issue #59 controlled CREATE handoff

Status: pre-integration documentation handoff after PM implementation ACCEPT.
This is not final closeout, not a release note, and not an issue-closure claim.

## Verdict source

Parent PM implementation task `t_47be8f49` returned strict ACCEPT for exactly:

- candidate branch: `run/product/recovery4-cumulative-real-browser-20260717T235302Z-7ccf5e3b`
- accepted candidate head: `b1cf990bf3a353726b6c97ce26445074898d50f2`
- accepted candidate tree: `0de2cde2e5a7041ef34d01ffa9e08308fb5cf73b`
- accepted candidate stable patch ID: `81ca3b51f2d19385ab9a56795e9ac86f60605972`
- factual baseline: `280127f92563722d010fb91c7e9af2b6e05a1be0`
- factual baseline tree: `7d5fc3906ed6ccafb2b3d4816254ec4f0990ede2`
- issue: [#59](https://github.com/valentusys/gnucash-web-companion/issues/59)

The documentation branch was required to start at the factual baseline and fast-forward only to the
PM-accepted candidate before adding one bounded docs-only handoff commit.

## Ordered reviewed source map

Stable patch IDs verified for the PM-accepted source chain:

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

## Pending state

This is a pre-integration handoff. The following are still pending and must not be implied here:

- product push to the integration branch/main
- exact-head GitHub Actions on the final integrated/docs head
- issue #59 final comment or closure
- release/tag/container publication
- public beta or public write-beta announcement
- owner/private pilot approval
- production readiness, hosted-financial-security, security-audit, FX/trading/business/investment
  support claims

## Next step

Run clean final QA on the docs-only head, then operator fast-forward integration/push/exact-head CI
and issue #59 closeout can happen if that final QA accepts the branch.
