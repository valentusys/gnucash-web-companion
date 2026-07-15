# Hermes Kanban product-development run 5

Status: **PRODUCT #56 AND ISSUE CLOSEOUT COMPLETE; FACTUAL DOCS SNAPSHOT**

This handoff records the fifth product-development run on the dedicated Hermes Kanban board. It
covers [issue #56](https://github.com/valentusys/gnucash-web-companion/issues/56): onboarding,
health, and safe registration for existing server-side GnuCash SQL SQLite books.

## Scope and publication boundary

- Documentation/status closeout only; this handoff does not publish a release.
- Current public read-only beta remains `v0.5.0-public-readonly-beta`.
- `v0.5.1-public-readonly-beta` and `v0.4.0-owner-writebeta` remain unpublished.
- GnuCash Desktop remains authoritative. `GNUCASH_WRITES_ENABLED=false` remains the default.
- Registration and lifecycle actions change app metadata only. They do not create, edit, copy, move,
  or delete GnuCash source data.
- This is pre-alpha evidence, not a production-readiness, security-audit, or broad compatibility claim.

## Baseline, board, and integration

- Baseline before run 5: `23d35bc821b32c9539d5919c513cde895074a78d`.
- Accepted and integrated product head before this docs task:
  `6928a2ae5f66f2ad16fdffdc26d1e8022ac5d706`.
- Accepted product tree: `9ab4a5239505c112dc1956459b60d643324af0ac`.
- Integration method: fast-forward-only integration of accepted product source.
- `main`, `origin/main`, and this docs worktree started equal at the accepted product head.
- Hermes board: `gnucash-web-companion-product-dev`.
- Run identifier: `hermes-kanban-product-run-5`.
- Prior milestone #55 received independent PM and QA acceptance in this run and remains closed.

## Task graph and acceptance

| Task | Final factual outcome |
|---|---|
| `t_79b502be` | PM ACCEPT for #55 and frozen implementation contract for #56. |
| `t_578c6c6f` | Independent QA ACCEPT for #55; the prior milestone remains closed. |
| `t_1e354401` | Accepted B1 preflight, migration, typed health, and allowed-root foundation. |
| `t_6cfbf771` | B2 timed out twice; its mechanical salvage was not accepted on its own. |
| `t_87de9f20` | Accepted B2R lifecycle recovery and zero-source-probe cached serialization correction. |
| `t_f9d5397d` | Accepted F1 onboarding foundation with bounded follow-up defects recorded. |
| `t_288af092` | Accepted F1 admin/readiness/DTO corrections after review rejection and branch recovery. |
| `t_efc18f05` | B3 exhausted its iteration budget; its mechanical salvage was not accepted on its own. |
| `t_596458f5` | B3R correction was rejected because full schema/piecash probes reopened a mutable path. |
| `t_c2c0776f` | Accepted B4 pinned-descriptor correction for the full read-only probe. |
| `t_c6bd9943` | Accepted F2 health/settings and safe metadata lifecycle UX after a recovered worker crash. |
| `t_a01b6f83` | Accepted F3 static/browser/security/mobile gate and CI wiring. |
| `t_2f9b4f59` | QA1 ACCEPT on exact 11-patch head `5fcf151`, tree `6581d45`. |
| `t_d2b35496` | QA2 FINAL ACCEPT on the same exact head and tree. |
| `t_77b5b546` | Accepted bounded Starlette 422 CI correction candidate. |
| `t_8a0d5039` | QA3 FINAL ACCEPT on final head `6928a2a`, tree `9ab4a52`. |
| `t_aa1547eb` | Factual docs/status closeout; no product-source change or release action. |

Rejected, crashed, timed-out, rewound, and auto-decomposed predecessors are history, not acceptance
evidence. The B2 and B3 salvage patches entered the final chain only through fresh recovery/review and
later exact-head QA. The rejected B3R patch remained only as the corrected predecessor to B4, not as
standalone accepted evidence. The F1 duplicate-run rewind was stopped, its exact reviewed content was
restored cleanly, and redundant auto-decomposer tasks were ignored.

## Integrated stable patch IDs

Exact stable product patch IDs integrated for run 5, in order:

1. `aa75aa6368458c4455bd1213b0e5451a30f16e7d`
2. `44dfe4cf1319745a638f479bbb041968a8ba2926`
3. `2d41282b771c1cfa1498fe27b6a38ca784876fdb`
4. `34177d611001419c6654301d59de6490a4704c36`
5. `428e04670aceb98b480200330b3b079696c57d80`
6. `bfe042183d03dd35c375e102b499642969341629`
7. `ae533a43aabcba5c748b5325393eb1c5162cb0f0`
8. `2173f2935a1372baf238e8fdfea82b9613e6f2f2`
9. `e8824eeaf3a412a1d9b3a3e1b6f529e931360eda`
10. `a200749bc414717a2875ed30525cd726cd2ca721`
11. `59ff41b9d0e6d0e158f5961042bb1a6c895c632a`
12. `8534280575a8a11ae0dd588a7d13ddf53d5370f0`

## User-visible behavior

The accepted #56 product head adds a complete read-only-first book onboarding and metadata lifecycle:

- An authenticated admin with no books gets an Add book flow; a normal user gets a safe message to
  contact an administrator.
- The flow accepts one existing server-side path under configured allowed roots. It has no upload,
  browser file chooser, directory discovery, import, conversion, or source-copy step.
- Content is checked as GnuCash SQL SQLite. XML, compressed XML, remote/database URIs, and unknown
  formats are rejected honestly.
- Registration is explicit: the admin runs a side-effect-free preflight, reviews typed readiness, and
  then confirms with an opaque request/source-bound token.
- Book cards and settings show cached typed health, last check/success timestamps, and capability-gated
  Accounts, Transactions, and Reports links.
- Admins can rename display metadata, change base-currency metadata, set default, recheck health,
  disable, enable after a fresh preflight, and unregister app metadata.
- Disable and unregister never delete or modify the source. Unregister removes only the app registry
  reference and clears enabled/default metadata.
- Normal users see only assigned books, safe statuses, timestamps, capabilities, and links. They do not
  receive raw paths, exception text, token internals, inode/device values, or arbitrary backend messages.

## API and security boundary

Accepted lifecycle routes are:

```text
GET    /books
POST   /books/preflight
POST   /books
GET    /books/{book_id}
GET    /books/{book_id}/health
POST   /books/{book_id}/health/recheck
PATCH  /books/{book_id}
POST   /books/{book_id}/default
POST   /books/{book_id}/disable
POST   /books/{book_id}/enable
DELETE /books/{book_id}
```

Key implementation evidence:

- Lifecycle mutation routes are admin-only; cached list/detail/health remain per-user authorized.
- Registration and enable revalidate the token-bound request and source identity.
- Allowed-root, absolute-path, traversal, symlink, regular-file, SQLite magic/schema, and duplicate
  canonical-target checks fail closed with typed path-safe errors.
- SQLite schema checks and the exactly-one piecash read-only preflight open consume a pinned
  `O_RDONLY|O_NOFOLLOW` descriptor through a verified descriptor path. Parent/leaf race tests observed
  zero outside source/schema/piecash opens.
- List, detail, and cached health use app metadata only: source probes, schema opens, piecash opens, and
  transaction materialization are zero on those paths.
- Registration, health refresh, rename/default/disable/enable, and unregister can write app metadata;
  they do not write the GnuCash source.

## QA and browser evidence

- QA1 at `5fcf151` / tree `6581d45`: full API `1288 passed`, focused `364 passed`, and full
  frontend/static/browser/root/Compose gates passed.
- QA2 on the same exact head/tree: full API `1288 passed`, focused `443 passed`, full frontend/browser/
  root/Compose gates passed, and synthetic 1k/10k lifecycle evidence passed.
- QA3 at `6928a2a` / tree `9ab4a52`: full API `1289 passed`, focused `142 passed`, and the actual CI
  Frontend command sequence passed.
- Books browser evidence: `books=2`, `lifecycle_requests=6`, `readonly_source_opens=12`, forbidden
  GnuCash API requests `0`, forbidden GnuCash browser requests `0`, source copy/modify/delete `0`,
  upload/client-filesystem calls `0`, viewport width `320`, and source hash unchanged.
- EN/RU, keyboard/form labels, selected-book recovery, normal-user direct lifecycle `403` responses,
  fixed error copy, and no raw-path/private-sentinel serialization were covered.

## Synthetic lifecycle performance evidence

The 1k/10k evidence is local generated/disposable evidence only, not a production performance claim.
Structural counters were the acceptance signal:

- list, cached health, unavailable-source cached health, and multi-book cases: zero SQLite preflight
  queries, zero preflight piecash opens, zero read-only service opens, and zero transaction
  materialization;
- preflight and recheck: five bounded SQLite queries and exactly one piecash read-only preflight open;
- first read-only data open after registration: exactly one read-only service open;
- source-book writes, write-alpha mutation routes, and private-book inputs: false/zero;
- health recheck app-metadata statements were labelled as metadata lifecycle writes, not source writes.

## CI incident and exact-head result

- Run [29380357480](https://github.com/valentusys/gnucash-web-companion/actions/runs/29380357480)
  failed deterministically on head `5fcf151` because importing the new books router emitted the
  deprecated Starlette 422 status warning into a browser drill that requires empty success stderr.
- The bounded correction at `6928a2a` replaced deprecated aliases with the supported 422 constant and
  added an import-warning regression without suppressing warnings or weakening assertions.
- Exact-final-head run
  [29382943117](https://github.com/valentusys/gnucash-web-companion/actions/runs/29382943117),
  attempt 2, completed successfully for Frontend checks, Backend tests, Foundation checks, and Docker
  Compose validation. Attempt 1 had one Chromium DevTools `/json/list` startup timeout; the permitted
  single rerun used the unchanged SHA and passed.

## Issue closeout facts

- Issue URL: <https://github.com/valentusys/gnucash-web-companion/issues/56>.
- Issue #56 closed as completed at `2026-07-15T02:13:04Z`.
- Final acceptance comment:
  [#issuecomment-4976179921](https://github.com/valentusys/gnucash-web-companion/issues/56#issuecomment-4976179921),
  created `2026-07-15T02:13:03Z`.

## Exact safety counters

- Owner/private/original/working/Syncthing/only-copy access, copy, or probe: `0`.
- #56 GnuCash source CREATE/PATCH/DELETE/batch requests: `0`.
- Product source copy/modify/delete: `0`.
- Forbidden GnuCash API/browser requests in the #56 browser gate: `0` / `0`.
- Upload/client-filesystem operations: `0`.
- Raw private/runtime artifacts committed by the product run: `0`.
- Write-default flips: `0`; `GNUCASH_WRITES_ENABLED=false` remains default.
- Release/tag/package/container publication by this run: `0`.
- Source hash changed in browser evidence: `false`.

## Documentation commit boundary

This handoff records the already completed product and issue closeout. It intentionally does not claim
this docs task's commit SHA, tree, patch ID, push state, or CI result. Those operational facts are
reported by the operator and the later exact-head GitHub run, avoiding self-reference or invented
future evidence.
