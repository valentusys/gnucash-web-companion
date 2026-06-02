# Handoff: daytime-write-worker-1

**Package:** #36-W1-C Restore-readiness gate
**Date:** 2026-06-02
**Branch:** main (no commit/push; supervisor will inspect)
**Baseline:** ecb30a9

## Goal

Implement and harden non-mutating restore-readiness checks before owner-writebeta
mutation arming. Tests must prove mutation cannot arm without restore-readiness
evidence when required.

## What was done

### State machine changes (`apps/api/app/owner_writebeta_state_machine.py`)

1. **Added `restore_readiness_ref` field** to `OwnerWritebetaSession` — an opaque
   reference string (max 80 chars) representing evidence that a restore path was
   verified before mutation is allowed to arm.

2. **Added restore-readiness gate in `transition()`** — the CONFIRMATION -> MUTATING
   transition now requires three refs: `operation_ref`, `backup_ref`, AND
   `restore_readiness_ref`. If any is missing, the transition raises
   `OwnerWritebetaTransitionError` with message "mutation requires opaque
   operation_ref, backup_ref, and restore_readiness_ref".

3. **Updated `transition()` ref application** — incoming refs are now collected into
   a tentative dict before state-specific checks run, so that `restore_readiness_ref`
   passed directly to `transition(MUTATING, restore_readiness_ref="...")` is visible
   to the guard. The tentative dict is then applied to the session after all checks
   pass.

4. **Updated `arm_confirmed_preview()`** — accepts optional `restore_readiness_ref`
   parameter, which is passed through to `transition(CONFIRMATION, ...)`. This allows
   the restore-readiness evidence to be recorded at confirmation time.

5. **Updated `redacted_summary()`** — now includes `restore_readiness_ref` in the
   output.

### Router changes (`apps/api/app/routers/owner_writebeta.py`)

6. **Added `restore_readiness_ref` to `OwnerWritebetaConfirmRequestDTO`** — optional
   field with `min_length=1, max_length=80` validation.

7. **Updated confirm endpoint** — passes `restore_readiness_ref` from the request
   through to `arm_confirmed_preview()`.

### Test changes

**`apps/api/tests/test_owner_writebeta_state_machine.py`** — 5 new tests added,
8 existing tests updated to supply `restore_readiness_ref` where they transition
to MUTATING:

- `test_owner_writebeta_mutation_requires_restore_readiness_ref` — proves mutation
  fails closed when restore_readiness_ref is missing (RED -> GREEN)
- `test_owner_writebeta_mutation_succeeds_with_restore_readiness_ref` — proves
  mutation succeeds when restore_readiness_ref is provided at transition time
- `test_owner_writebeta_arm_confirmed_preview_stores_restore_readiness_ref` — proves
  `arm_confirmed_preview()` stores the ref and mutation can proceed afterward
- `test_owner_writebeta_restore_readiness_ref_is_opaque_and_truncated` — proves
  long refs are truncated to 80 chars (opaque, no path leaks)
- `test_owner_writebeta_happy_path_with_restore_readiness_gate` — full lifecycle
  test proving the gate works end-to-end through RESET_REQUIRED

**`apps/api/tests/test_owner_writebeta_routes.py`** — 3 new tests added, 1 existing
test updated:

- `test_owner_writebeta_confirm_stores_restore_readiness_ref_when_provided` — router
  passes ref through to state machine
- `test_owner_writebeta_confirm_accepts_missing_restore_readiness_ref` — confirm
  endpoint works without it (gate is at mutation time, not confirm time)
- `test_owner_writebeta_confirm_rejects_invalid_restore_readiness_ref` — Pydantic
  validation rejects refs > 80 chars (422)
- Updated `test_owner_writebeta_preview_and_confirmation_use_opaque_refs` — now
  supplies `restore_readiness_ref` to confirm

## Test results

```
tests/test_owner_writebeta_state_machine.py — 12 passed (7 existing + 5 new)
tests/test_owner_writebeta_routes.py        — 6 passed (3 existing + 3 new)
Broader regression suite                    — 186 passed, 0 failed
```

## Safety summary

- No GnuCash books were touched or mutated.
- No private artifacts created.
- `GNUCASH_WRITES_ENABLED=false` remains default; APP_ENV=test gate unchanged.
- No public write beta exposure; no release.
- Restore-readiness ref is opaque — contains no paths, amounts, or private data.
- The ref is validated to max 80 chars at both the Pydantic DTO level and the state
  machine level.
- All existing tests continue to pass (186 tests, 0 regressions).

## Files changed

| File | Change |
|------|--------|
| `apps/api/app/owner_writebeta_state_machine.py` | Added restore_readiness_ref field, gate check, tentative ref pattern |
| `apps/api/app/routers/owner_writebeta.py` | Added restore_readiness_ref to confirm DTO and endpoint |
| `apps/api/tests/test_owner_writebeta_state_machine.py` | 5 new tests, 8 existing updated |
| `apps/api/tests/test_owner_writebeta_routes.py` | 3 new tests, 1 existing updated |

## Commands

```bash
cd apps/api
python -m pytest tests/test_owner_writebeta_state_machine.py tests/test_owner_writebeta_routes.py -v
python -m pytest -q  # full suite
```

## Blockers

None. gh auth has transient TLS issues (pre-existing), so GitHub issue updates
were not attempted. All work was done locally.

## Design notes

The restore-readiness ref is intentionally **optional at confirm time** but
**required at mutation time**. This two-phase design allows the confirm endpoint
to arm a session without restore-readiness evidence (e.g., in testing), but the
state machine will block the transition from CONFIRMATION to MUTATING if the ref
is missing. In production, the ref would be required at confirm time by
application-level validation or frontend enforcement; the state machine gate is
the safety net.

Refs are always opaque strings — the state machine never inspects their content,
only their presence. This follows the same pattern as `backup_ref`, `audit_ref`,
and `operation_ref`.
