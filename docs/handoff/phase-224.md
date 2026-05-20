# Phase 224 handoff — Write-alpha DELETE restore proof v2

Date: 2026-05-21
Status: COMPLETE — bounded synthetic/disposable DELETE restore proof rerun passed after backup evidence hardening.

## Summary

Phase 224 stayed within the Cycle 3 Phase 3 contract. It reran only the DELETE write-alpha dogfood path on one fresh ignored synthetic/disposable runtime copy, then proved that the single backup artifact from that DELETE could restore the deleted transaction and be read back through SQLite and the API.

The routed DELETE executed exactly once. The successful write was not repeated after the host-side helper reported root-owned backup unreadability for host restore; the restore proof was completed inside the API container against the same single backup artifact.

## Files changed

- `docs/dogfood/phase-224-delete-restore-v2.md` — redacted DELETE restore proof evidence.
- `docs/handoff/phase-224.md` — this handoff.
- `CHANGELOG.md` and `PROJECT_STATUS.md` — phase status synchronized.

No product code or smoke helper code was changed in this phase.

## Verification performed

Dogfood / smoke evidence:

- Stopped-runtime cleanup dry-run and cleanup before setup — passed.
- Write-alpha copied-book preflight against an external disposable copy and ignored runtime/backup targets — passed.
- `APP_ENV=test` + `GNUCASH_WRITES_ENABLED=true` Docker/Caddy runtime — started healthy.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/write-alpha-delete-restore-smoke.py` — passed for exactly one DELETE, post-delete API/runtime absence, one backup increment, one successful audit increment, backup transaction evidence, and stale-released/non-active lock evidence.
- Container-side restore/read-back proof on the same single backup — passed: single backup readable, delete audit count exactly one, restore checksum matched backup, SQLite/API read-back found the restored deleted transaction.
- Default false reset Docker/Caddy runtime — started healthy.
- `SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py` — passed, including disabled validate/create/PATCH/DELETE probes returning 403.
- Stopped-runtime cleanup dry-run and cleanup after smoke — passed with `--via-compose` for root-owned backup/lock cleanup; final dry-run reported zero runtime artifacts.

Standard checks:

- `cd apps/api && pytest -q`
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build`
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet`
- `git diff --check`

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` gate was not weakened.
- The only routed mutation was one local synthetic/disposable DELETE; no create/PATCH route was rerun.
- No release/tag/package/image/deployment was published.
- No real/private/only-copy book was used.
- No runtime book, backup, app DB, lock artifact, `.env`, screenshot, export, token, cookie, cert, key, raw private path, account name, memo, amount, backup filename, or private financial data was staged or committed.

## Risks / blockers

Phase 224 closes the narrow Phase 3 DELETE restore proof requirement for a synthetic/disposable local copy. It does not claim production write safety, security audit coverage, broad GnuCash compatibility, or real/private/only-copy book safety. Later roadmap phases still need the combined create/PATCH/DELETE matrix, default read-only regression, fresh-clone/upgrade smokes, and final release gate before any publication decision.

## Next

Do not start the next roadmap phase from this session. The next safe phase is Cycle 3 Phase 4/225 only if explicitly launched in a fresh Hermes session.
