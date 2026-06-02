# Daytime write worker 3 — #36-W1-E Default-disabled reset enforcement

## Worker ID

daytime-write-worker-3

## Target issue

#36 — controlled-write v0.2 readiness gates

## Package

#36-W1-E — Default-disabled reset enforcement

## Scope completed

- Added regression tests to `tests/test_owner_writebeta_state_machine.py` proving the
  complete writebeta lifecycle resets to default-disabled with all active arms
  (preview_hash, confirmation_token_ref, restore_readiness_ref) cleared.
- Added regression test proving FAILED_HARD_STOP is a fully terminal state: no
  further transitions are allowed from it without constructing a fresh session.
- Strengthened the existing router test `test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed`
  to assert that after reset-disabled: (1) all active-arm session refs are
  cleared in the response summary, (2) the `/status` endpoint also reports the
  default-disabled posture with `writes_disabled_default` in blocked_reasons,
  and (3) all four transaction probes (validate/create/patch/delete) are
  individually named-asserted as 403 with "read-only" in the detail string.

## Safety notes

- No GnuCash books, app DBs, backups, `.env`, tokens, screenshots, or private
  artifacts were touched.
- No implementation changes; only tests were added/extended. This is a
  non-mutating regression package.
- `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` gates remain unchanged.
- No public write beta or release action.
- All opaque references in tests are synthetic (e.g., `rr-`, `bkp-`, `audit-`
  prefixed strings — no real paths or evidence).

## Tests run and results

From `apps/api`:

| Test file | Result |
|-----------|--------|
| `tests/test_owner_writebeta_state_machine.py` | 14 passed |
| `tests/test_owner_writebeta_routes.py` | 10 passed |
| `tests/test_write_safety_defaults_guard.py` | 11 passed |
| `tests/test_write_alpha_readiness.py` | 10 passed |

```text
pytest -q tests/test_owner_writebeta_state_machine.py tests/test_owner_writebeta_routes.py tests/test_write_safety_defaults_guard.py tests/test_write_alpha_readiness.py
45 passed, 1 warning in 9.12s
```

From repository root:

```text
git diff --check
# no output (clean)
```

## Files changed

| File | Change |
|------|--------|
| `apps/api/tests/test_owner_writebeta_state_machine.py` | 2 new tests: `test_owner_writebeta_full_reset_enforcement_after_session_completion`, `test_owner_writebeta_restart_post_hard_stop_requires_new_session` |
| `apps/api/tests/test_owner_writebeta_routes.py` | Strengthened `test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed` with arm-clearance, /status, and named-probe assertions |
| `docs/handoff/daytime-write-worker-3.md` | This handoff document |

## Issue draft (do not post if gh is flaky)

Issue #36 comment draft:

> daytime-write-worker-3 (#36-W1-E): Added regression tests proving controlled-write/writebeta sessions reset to default-disabled after mutation verification and session completion. Tests confirm: (1) RESET_REQUIRED -> COMPLETE -> DISABLED clears all active-arm refs (preview_hash, confirmation_token_ref, restore_readiness_ref); (2) FAILED_HARD_STOP is fully terminal — no transitions possible without a fresh session; (3) after reset-disabled, /status shows writes_disabled_default in blocked_reasons and all four transaction probes (validate/create/patch/delete) return 403. Implementation unchanged; strengthened test-only package. No book mutation. #36 stays open.

## Blockers

None. All tests pass. No implementation changes needed — the code already
satisfies the assertions. Tests strengthen regression coverage for #36-W1-E.

## Follow-up

Supervisor should review, run broader gates as practical, commit/push if safe,
then continue with the next #36 W1/W2 package.
