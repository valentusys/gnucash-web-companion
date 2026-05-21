# Phase 253 — Maintainer copied-book dogfood packet

Date: 2026-05-21

Status: COMPLETE — maintainer-safe copied-book dogfood packet added; no mutation performed.

## Summary

Phase 253 created `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`, a complete owner/maintainer procedure for future copied-book dogfood.

The packet defaults to dry-run first, forbids original and only-copy books, requires outside-git copied/restorable targets plus independent backup, keeps evidence redacted, requires restore verification after any mutation, prohibits DELETE unless separately authorized against a write-alpha-created test transaction, and ends with cleanup plus reset proof that `GNUCASH_WRITES_ENABLED=false` remains the default.

No dogfood run, CREATE, PATCH, DELETE, real/private-book access, release, tag, default-write change, `APP_ENV=test` gate weakening, or real/private/only-copy write-safety claim was added.

## Artifacts

- `docs/write-alpha/maintainer-copied-book-dogfood-packet.md`
- `docs/handoff/phase-253.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `README.md`
- `README.ru.md`
- `docs/ROADMAP.md`
- `scripts/check_public_status.py`
- `apps/api/tests/test_public_status_guard.py`

## Packet coverage

The packet includes:

- preflight;
- independent backup;
- dry-run first;
- optional one CREATE only;
- optional PATCH later only after review;
- DELETE prohibited unless separately authorized for a write-alpha-created test transaction;
- evidence redaction requirements;
- restore verification;
- stop conditions;
- cleanup;
- reset to default false.

## Safety posture

- Original book: explicitly forbidden.
- Only-copy book: explicitly forbidden.
- Allowed target: outside-git copied/restorable working book only.
- Default action: dry-run first.
- Write-alpha remains experimental, pre-alpha, local-only, disabled by default, and gated by `APP_ENV=test` when explicitly enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- No private paths, account names, memos, amounts, screenshots, CSV rows, app DBs, backups, tokens, keys, certs, raw payloads, or book files were added.

## Verification performed

```bash
python3 scripts/check_public_status.py
cd apps/api && pytest tests/test_public_status_guard.py -q
git diff --check
grep -R "GNUCASH_WRITES_ENABLED" -n .env.example docker-compose.yml apps || true
grep -R "APP_ENV=test" -n README.md docs apps || true
grep -R "localStorage\|sessionStorage" -n apps/web/src || true
```

Results:

- Public status guard: PASS.
- Public status guard tests: PASS.
- Whitespace check: PASS.
- Safety greps: committed defaults still show `GNUCASH_WRITES_ENABLED=false`; Docker Compose defaults still render write mode as false; `APP_ENV=test` guard wording remains present; browser storage grep shows theme-only `localStorage` usage in `apps/web/src`.
- Sensitive tracked-file hygiene scan: PASS.

## GitHub issues

No new GitHub issue was required. Existing issue #36 remains the strategic tracker for remaining controlled-write readiness gates.

## Next phase boundary

Phase 254 may add a local-only dogfood command wrapper with explicit `--dry-run` and `--create-one` modes. Phase 253 did not implement wrapper code and did not perform copied-book dogfood.
