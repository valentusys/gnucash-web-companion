# Write-alpha evidence matrix

Status: refreshed in Phase 336 after the Phase 335 audit accepted Cycle 2 copied-book PATCH evidence narrowly.

This matrix separates evidence types so write-alpha status is not overstated. It intentionally excludes private paths, account names, memos, amounts, screenshots, exports, tokens, keys, and raw book artifacts.

| Evidence class | Phase(s) | Mutation type | Scope | Restore proof | Compatibility/read-back | Current status | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Synthetic/disposable route tests | Multiple pre-Phase 281 phases plus Phase 283 targeted tests | CREATE/PATCH route behavior; DELETE remains synthetic-only | Test fixtures only | Test-level only unless separately noted | Backend tests passed where recorded | Accepted for synthetic confidence only | Does not prove owner/private/copied-book safety |
| Maintainer copied-test-book/package rehearsal | Earlier write-alpha release preparation phases | Dry-run/CREATE-style package rehearsal | Non-owner copied test data | Recorded in prior release-prep evidence | Recorded in prior release-prep evidence | Accepted only for release-package rehearsal | Not owner evidence |
| Owner copied-book dry-run | Phase 271 accepted, carried forward | No mutation | Owner-provided copied/restorable-book dry-run evidence, redacted | Not applicable because dry-run only | Evidence reviewed as redacted summary | Accepted as dry-run-only evidence | Does not authorize CREATE/PATCH/DELETE by itself |
| Owner copied-book CREATE-one | Phase 276 accepted | Exactly one CREATE | Owner copied/restorable book, redacted evidence only | Accepted in Phase 276 | Read-back/reset evidence accepted in Phase 276 | Accepted for exactly one CREATE evidence item | Does not prove general write safety or PATCH/DELETE safety |
| Synthetic/disposable PATCH-one rehearsal | Phase 283 | Exactly one metadata/memo-only PATCH | Synthetic/disposable fixture copy | Restore proof passed | Read-back, audit, backup, compatibility checks passed | Accepted for synthetic PATCH confidence | No owner/private/copied-book PATCH evidence |
| Owner copied-book PATCH-one | Phases 286, 292 | None run | Owner packet prepared in Phase 285; Phase 292 blocked before mutation because the Phase 276 target transaction was not verifiable in the current copied working book | Absent | Absent | Superseded by Phase 294 fresh-chain evidence | Cannot support release claims or DELETE progression by itself |
| Owner copied-book CREATE-to-PATCH fresh chain | Phases 294–295 | Exactly one CREATE followed by exactly one metadata/memo-only PATCH | Fresh owner copied/restorable working book outside git; PATCH targeted the same write-alpha-created transaction | Restore verification passed after chain evidence collection | Read-back, audit/lock, backup artifact, piecash, gnucash-cli, reset, disabled probe, and redaction checks passed | Accepted narrowly by the Phase 295 audit for this one bounded chain only | Does not prove production, broad compatibility, DELETE, original/only-copy, or general private-book write safety |
| Owner copied-book CREATE/PATCH current Cycle 1-2 chain | Phases 321-335 | Exactly one CREATE in Cycle 1, then exactly one metadata/memo-only PATCH in Cycle 2 | Owner copied/restorable working book outside git; PATCH targeted the existing write-alpha-created test transaction after ownership/current-book verification | Restore verification passed after CREATE and after PATCH | Read-back, audit/lock, backup, piecash, installed `gnucash-cli`, reset, disabled probes, and redaction checks passed | Accepted narrowly by the Phase 335 audit for this bounded copied-book evidence only | Does not prove production, broad compatibility, DELETE, original/only-copy, historical/manual transaction, or general private-book write safety |
| DELETE | Phase 287 and carried through Phase 340 | None run for owner copied-book dogfood | Synthetic-only remains the maximum allowed status | No owner DELETE restore proof | No owner DELETE read-back/compatibility evidence | Blocked for owner dogfood | Destructive; no owner packet; no execution authorization |

## Conservative interpretation

- Read-only use remains the practical safe path.
- Write-alpha remains disabled by default and APP_ENV=test gated when explicitly enabled.
- Synthetic/disposable write-alpha evidence is useful for development only.
- Owner copied-book evidence currently supports: dry-run accepted, CREATE evidence accepted for bounded copied-book runs, Phase 294/295 fresh-chain evidence accepted for one metadata/memo-only PATCH on its same write-alpha-created transaction, and Phase 321-335 current Cycle 1-2 evidence accepted for exactly one CREATE followed by exactly one metadata/memo-only PATCH on a verified write-alpha-owned copied-book test transaction. DELETE remains blocked/not run.
- Original/only-copy/private production-book writes remain forbidden and unsupported.
