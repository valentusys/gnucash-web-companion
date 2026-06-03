# Daytime write worker 4 — #36-W1-F Audit summary privacy

## Worker ID

daytime-write-worker-4

## Target issue

#36 — controlled-write v0.2 readiness gates

## Package

#36-W1-F — Audit summary privacy

## Scope completed

- Strengthened `_safe_shape()` in `apps/api/app/owner_writebeta_state_machine.py` to
  replace user-provided dict keys with opaque `field_N` placeholders. Previously,
  `_safe_shape` preserved original key names (e.g., `secret_account`, `description`,
  `amount`) in the shape output, which could leak private semantic information through
  key names even though values were replaced with type names. Now both keys and values
  are fully redacted.

- Added `_sanitized_failed_reason()` and `_SAFE_FAILED_REASONS` allowlist to
  `OwnerWritebetaSession`. The `redacted_summary()` method now only emits
  known-safe `failed_reason` strings; any unrecognized reason (including paths,
  credentials, or other sensitive text that might transit through error paths) is
  replaced with the generic message
  `"owner-writebeta session failed; see opaque audit refs only."`.

- Added `_bounded_opaque_ref()` validation for backup/audit/restore/operation
  refs. Path-like, URL-like, whitespace-bearing, or evidence-like refs are now
  rejected before they can enter `redacted_summary()`.

- Added regression test `test_owner_writebeta_redacted_summary_sanitizes_safe_shape_keys_and_values`
  to `tests/test_owner_writebeta_state_machine.py` proving that neither user-provided
  dict keys nor values from `payload_shape` leak into the shape output.

- Added regression test `test_owner_writebeta_route_status_and_preview_redact_private_payload_values`
  to `tests/test_owner_writebeta_state_machine.py` proving:
  - `/status` redacted_summary exposes only opaque refs/bounded counters
  - `/preview` redacted_summary never contains payload keys or values
  - `/confirm` rejects path-like backup refs and otherwise exposes only `owb-conf-*` token refs
  - `failed_reason` containing raw paths/credentials/secrets is sanitized in `/status`

## Safety notes

- No GnuCash books, app DBs, backups, `.env`, tokens, screenshots, or private
  artifacts were touched.
- `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` gates remain unchanged and
  were not weakened.
- No public write beta or release action.
- All opaque references in tests are synthetic (e.g., `rr-`, `bkp-`, `audit-`,
  prefixed strings — no real paths or evidence).
- Changes are minimal and fail-closed: the `_safe_shape` replacement and
  `_sanitized_failed_reason` allowlist shrink the information surface.

## Tests run and results

From `apps/api`:

| Test file | Result |
|-----------|--------|
| `tests/test_owner_writebeta_state_machine.py` | 16 passed (+2 new) |
| `tests/test_owner_writebeta_routes.py` | 10 passed |
| `tests/test_write_alpha_audit_summary.py` | 7 passed |
| `tests/test_write_safety_defaults_guard.py` | 11 passed |
| `tests/test_write_alpha_readiness.py` | 10 passed |

```
pytest -q tests/test_owner_writebeta_state_machine.py \
          tests/test_owner_writebeta_routes.py \
          tests/test_write_alpha_audit_summary.py \
          tests/test_write_safety_defaults_guard.py \
          tests/test_write_alpha_readiness.py
54 passed, 22 warnings in 20.66s
```

From repository root:

```
git diff --check
# no output (clean)
```

## Files changed

| File | Change |
|------|--------|
| `apps/api/app/owner_writebeta_state_machine.py` | `_safe_shape()` now replaces dict keys with `field_N`; added `_bounded_opaque_ref()` for evidence refs; added `_SAFE_FAILED_REASONS` allowlist and `_sanitized_failed_reason()` method; `redacted_summary()` uses sanitized reason |
| `apps/api/tests/test_owner_writebeta_state_machine.py` | 2 new tests: `test_owner_writebeta_redacted_summary_sanitizes_safe_shape_keys_and_values`, `test_owner_writebeta_route_status_and_preview_redact_private_payload_values` |
| `docs/handoff/daytime-write-worker-4.md` | This handoff document |

## Issue draft (do not post)

Issue #36 comment draft:

> daytime-write-worker-4 (#36-W1-F): Strengthened audit summary privacy for owner-writebeta/write-mode sessions. _safe_shape() now replaces user-provided dict keys with opaque field_N placeholders (previously keys like secret_account, description, amount leaked through). Added _bounded_opaque_ref() so path-like/URL-like/whitespace-bearing backup/audit/restore/operation refs are rejected before they can enter redacted_summary. Added _sanitized_failed_reason() with an allowlist so only known-safe failed_reason strings appear in redacted_summary; unrecognized reason text (paths, credentials, secrets) is replaced with a generic message. Regression tests prove: (1) payload_shape keys/values never leak into shape output; (2) /status, /preview, /confirm responses contain only opaque refs and bounded counters; (3) a crafted failed_reason with postgres:// URL and file paths is sanitized. APP_ENV=test and GNUCASH_WRITES_ENABLED=false unchanged. No book mutation. #36 stays open.

## Blockers

None. All 54 targeted tests pass. git diff --check is clean.

## Follow-up

Supervisor should review, run broader gates as practical, commit/push if safe,
then continue with the next #36 W1/W2 package.
