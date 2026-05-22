# Write-alpha evidence matrix

Status: refreshed in Phase 293.

This matrix separates evidence types so write-alpha status is not overstated. It intentionally excludes private paths, account names, memos, amounts, screenshots, exports, tokens, keys, and raw book artifacts.

| Evidence class | Phase(s) | Mutation type | Scope | Restore proof | Compatibility/read-back | Current status | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Synthetic/disposable route tests | Multiple pre-Phase 281 phases plus Phase 283 targeted tests | CREATE/PATCH route behavior; DELETE remains synthetic-only | Test fixtures only | Test-level only unless separately noted | Backend tests passed where recorded | Accepted for synthetic confidence only | Does not prove owner/private/copied-book safety |
| Maintainer copied-test-book/package rehearsal | Earlier write-alpha release preparation phases | Dry-run/CREATE-style package rehearsal | Non-owner copied test data | Recorded in prior release-prep evidence | Recorded in prior release-prep evidence | Accepted only for release-package rehearsal | Not owner evidence |
| Owner copied-book dry-run | Phase 271 accepted, carried forward | No mutation | Owner-provided copied/restorable-book dry-run evidence, redacted | Not applicable because dry-run only | Evidence reviewed as redacted summary | Accepted as dry-run-only evidence | Does not authorize CREATE/PATCH/DELETE by itself |
| Owner copied-book CREATE-one | Phase 276 accepted | Exactly one CREATE | Owner copied/restorable book, redacted evidence only | Accepted in Phase 276 | Read-back/reset evidence accepted in Phase 276 | Accepted for exactly one CREATE evidence item | Does not prove general write safety or PATCH/DELETE safety |
| Synthetic/disposable PATCH-one rehearsal | Phase 283 | Exactly one metadata/memo-only PATCH | Synthetic/disposable fixture copy | Restore proof passed | Read-back, audit, backup, compatibility checks passed | Accepted for synthetic PATCH confidence | No owner/private/copied-book PATCH evidence |
| Owner copied-book PATCH-one | Phases 286, 292 | None run | Owner packet prepared in Phase 285; Phase 292 blocked before mutation because the Phase 276 target transaction was not verifiable in the current copied working book | Absent | Absent | Blocked before mutation / not accepted | Cannot support release claims or DELETE progression |
| Owner copied-book CREATE-to-PATCH fresh chain | Phase 293 | None run | Owner selected the fresh-chain direction, but exact same-context confirmation for the new mutation scope is not yet present | Absent | Absent | Blocked before mutation pending exact owner confirmation | Would require exactly one new CREATE followed by exactly one metadata/memo-only PATCH on that new write-alpha-created transaction |
| DELETE | Phase 287 | None run for owner copied-book dogfood | Synthetic-only remains the maximum allowed status | No owner restore proof | No owner read-back/compatibility evidence | Blocked for owner dogfood | Destructive; no owner packet; no execution authorization |

## Conservative interpretation

- Read-only use remains the practical safe path.
- Write-alpha remains disabled by default and APP_ENV=test gated when explicitly enabled.
- Synthetic/disposable write-alpha evidence is useful for development only.
- Owner copied-book evidence currently supports: dry-run accepted, exactly one CREATE accepted, PATCH blocked/not accepted, fresh CREATE-to-PATCH chain blocked pending exact confirmation, DELETE blocked.
- Original/only-copy/private production-book writes remain forbidden and unsupported.
