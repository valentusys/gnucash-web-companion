# overnight-v2-worker-05

Target issue: #36
Package name: Backup/restore readiness guard expansion

## Summary

Added a restore safety boundary doc and expanded the write-safety guard to require restore-to-copy, not-destructive-restore, not-real-book-safety-evidence, independent-backup, redacted-evidence-only, default-disabled, and test-gated markers.

## Files changed

- `docs/write-alpha/restore-safety-boundary.md`
- `scripts/check_write_safety_defaults.py`
- `apps/api/tests/test_write_safety_defaults_guard.py`
- `docs/handoff/overnight-v2-worker-05.md`

## Tests run and results

- `cd apps/api && pytest -q tests/test_write_safety_defaults_guard.py`: passed.
- `python3 scripts/check_write_safety_defaults.py`: passed.

## Safety summary

Non-mutating only. Mutation counts: CREATE 0 / PATCH 0 / DELETE 0. No private/runtime/book artifacts touched. Restore docs explicitly distinguish restore-to-copy from destructive restore and real-book safety evidence.

## Issue update

#36 should stay open; restore boundary is clearer, but it is not closure evidence by itself.

## Commit SHA

e0ea339bbf882168103f2bafe7926a13dcae7333

## Remaining blockers

Future copied/restorable authorization packet, supported-version compatibility, and PM closure acceptance remain pending.

## Recommendation

Run #36 owner-writebeta operating checklist hardening next.
