# Phase 296 handoff — Evidence matrix and posture reconciliation

Status: COMPLETE — copied-book write-alpha posture reconciled after Phase 295 audit.

## Result

Updated the write-alpha evidence matrix and copied-book posture to distinguish:

- synthetic/disposable CREATE/PATCH route evidence;
- maintainer copied-test-book/package rehearsal evidence;
- owner copied-book dry-run evidence;
- owner copied-book CREATE-one evidence;
- synthetic/disposable PATCH-one rehearsal evidence;
- superseded/absent original owner PATCH-one evidence;
- Phase 294/295 owner copied-book CREATE-to-PATCH fresh-chain evidence;
- owner DELETE blocked/not run.

## Verification

- `python3 scripts/check_public_status.py` — passed.
- `git diff --check` — passed.
- Public docs/status guard expectations updated to Phase 296.
- No private/raw evidence, paths, account names, memos, amounts, screenshots, exports, DBs, backups, or `.hermes/` artifacts were staged.

## GitHub issue

Issue #36 was updated with a conservative comment summarizing the accepted Phase 294/295 evidence and the remaining DELETE/original-book blockers.

## Safety posture

`GNUCASH_WRITES_ENABLED=false` remains default. Enabled write-alpha remains `APP_ENV=test` gated. DELETE remains blocked/not run. PATCH remains metadata/memo-only. Original/private/only-copy writes remain forbidden and unsupported.

## Next phase

Phase 297: decide whether a `v0.2.9-writealpha` release is useful or whether no-release is safer.
