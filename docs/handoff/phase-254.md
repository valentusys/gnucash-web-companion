# Phase 254 — Dogfood command wrapper with explicit step modes

Date: 2026-05-21

Status: COMPLETE — local-only copied-book dogfood wrapper added and verified with synthetic wrapper runs.

## Summary

Phase 254 added `scripts/write_alpha_copied_book_dogfood.py`, a local-only explicit-step wrapper for future copied-book write-alpha dogfood.

The wrapper supports separate `--dry-run` and `--create-one` modes, requires explicit copied/disposable/original-untouched/outside-git confirmations, requires an extra mutation confirmation for `--create-one`, calls the Phase 235 redacted preflight, creates a pre-step backup before either mode, writes redacted JSON evidence, rejects unsafe paths, and verifies the committed/default `GNUCASH_WRITES_ENABLED=false` posture after each run.

`--create-one` delegates the actual CREATE to a caller-supplied command or the existing local write-alpha create smoke helper. The wrapper itself does not add broad mutation logic, does not add DELETE mode, does not open/parse books, and does not print raw paths.

## Artifacts

- `scripts/write_alpha_copied_book_dogfood.py`
- `apps/api/tests/test_write_alpha_copied_book_dogfood.py`
- `docs/handoff/phase-254.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`
- `README.ru.md`
- `docs/ROADMAP.md`
- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`

## Wrapper behavior

- `--dry-run`: preflight + pre-step backup + redacted evidence + default-disabled proof; no mutation command is executed.
- `--create-one`: preflight + pre-step backup + delegated single CREATE command + redacted evidence + default-disabled proof.
- Confirmation flags are required for copied/disposable target, original untouched, outside-git target, and `--create-one` mutation.
- Targets inside the git working tree are rejected by the preflight path.
- Output and evidence use redacted labels/opaque refs only.
- DELETE is not supported by default.

## Safety posture

- Original books: still forbidden.
- Only-copy books: still forbidden.
- Allowed target: outside-git copied/restorable working book only.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- `APP_ENV=test` write-alpha gate remains intact.
- No real/private/only-copy book, raw path/account/memo/amount/payload evidence, screenshot, CSV, app DB, backup artifact, `.env`, token, key, cert, release, tag, default-write change, or production/security/write-safety claim was added.

## Verification performed

```bash
cd apps/api && pytest tests/test_write_alpha_copied_book_dogfood.py tests/test_write_alpha_preflight_cli.py tests/test_redact_dogfood_evidence.py -q
cd apps/api && pytest -q

# Synthetic local wrapper dogfood: dry-run and create-one with a harmless delegated command,
# redacted evidence validation, cleanup of temporary ignored backups.
GNUCASH_WRITES_ENABLED=true APP_ENV=test python3 scripts/write_alpha_copied_book_dogfood.py --dry-run ...
GNUCASH_WRITES_ENABLED=true APP_ENV=test python3 scripts/write_alpha_copied_book_dogfood.py --create-one ... --confirm-create-one-mutation --create-command true
python3 scripts/redact_dogfood_evidence.py <redacted-dry-run-evidence-json>
python3 scripts/redact_dogfood_evidence.py <redacted-create-one-evidence-json>

# Unsafe-path rejection probe
GNUCASH_WRITES_ENABLED=true APP_ENV=test python3 scripts/write_alpha_copied_book_dogfood.py --dry-run --target <inside-repo-or-missing-target> ...

python3 scripts/check_public_status.py
cd apps/api && pytest tests/test_public_status_guard.py -q
git diff --check
```

Results:

- Wrapper/preflight/redaction tests: PASS (`16 passed`).
- Full backend suite: PASS (`566 passed`, warnings only from existing piecash/SQLAlchemy/FastAPI deprecations).
- Synthetic local wrapper dry-run: PASS with redacted output and `verified-default-disabled` proof.
- Synthetic local wrapper create-one mode: PASS with redacted output, pre-step backup, harmless delegated command, and `verified-default-disabled` proof.
- Redacted evidence validation: PASS for dry-run and create-one evidence.
- Unsafe-path rejection probe: PASS; wrapper exited nonzero before evidence write.
- Public status guard: PASS.
- Public status guard tests: PASS.
- Whitespace check: PASS.

## GitHub issues

No new GitHub issue was required. Existing issue #36 remains the strategic tracker for controlled-write readiness gates.

## Next phase boundary

Phase 255 may review UI warnings and create-only copied-book mode copy. Phase 254 did not add UI changes, DELETE support, real/private-book dogfood, release publication, or write-default changes.
