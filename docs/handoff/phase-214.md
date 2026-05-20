# Phase 214 handoff — synthetic upgrade and app-metadata preservation smoke

Date: 2026-05-21

## Summary

Phase 214 added and ran a synthetic Docker upgrade smoke from the previous published write-alpha tag `v0.2.4-writealpha` to current `main`.

The smoke verified that dummy app metadata remains readable after upgrade, default book access remains available, selected-book recovery remains safe, read-only route families still pass, write-alpha audit-summary remains a read-only app-metadata endpoint, and disabled write probes still return 403 with `GNUCASH_WRITES_ENABLED=false`.

## Files changed

- `scripts/smoke/synthetic-upgrade-smoke.sh`
  - New local-only synthetic upgrade helper.
  - Uses a temporary clone/runtime, committed synthetic fixture copy, dummy credentials, and default-disabled writes.
  - Starts the previous tag, injects dummy legacy metadata, upgrades to current ref, and runs read-only/write-disabled probes.
- `apps/api/tests/test_upgrade_metadata_preservation.py`
  - Regression tests for startup seed idempotence and selected/default app metadata preservation semantics.
- `docs/dogfood/phase-214-synthetic-upgrade-smoke.md`
  - Records smoke command, result, and safety boundaries.
- Public/status docs updated for Phase 214 completion:
  - `PROJECT_STATUS.md`
  - `README.md`
  - `README.ru.md`
  - `CHANGELOG.md`
  - `docs/ROADMAP.md`
  - `scripts/check_public_status.py`
  - `apps/api/tests/test_public_status_guard.py`

## Verification performed

- `cd apps/api && pytest tests/test_upgrade_metadata_preservation.py -q`
- `bash -n scripts/smoke/synthetic-upgrade-smoke.sh`
- `scripts/smoke/synthetic-upgrade-smoke.sh --previous-ref v0.2.4-writealpha --current-ref HEAD --port 18083`

Additional final verification for the committed phase is recorded in the final operator report.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No real/private GnuCash book, app metadata DB, backup, `.env`, screenshot, export, token, key, or certificate was used or committed.
- The smoke uses ignored runtime data in a temporary clone only.
- No write-enabled mode was run.
- No release/tag/package/image was published.
- The phase does not add a migration wizard and does not claim production readiness, security-audited status, broad upgrade guarantee, or real/private-book write safety.

## Follow-up risks/blockers

None blocking Phase 214. This remains narrow synthetic upgrade-path evidence only; real/private deployments still require operator-owned backups and copied/disposable validation before any use.
