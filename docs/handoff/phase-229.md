# Phase 229 handoff — Public status and release-doc drift guard refresh

Date: 2026-05-21
Status: COMPLETE — public status/release-support docs and drift guard refreshed; no release or tag published.

## Summary

Phase 229 stayed within the Cycle 3 Phase 8 contract. It synchronized the public status layer after Phases 222–228 and expanded guard expectations so docs cannot drift before the later release-gate phase.

No product behavior, write route, release tag, GitHub release, package, image, write default, or `APP_ENV=test` gate changed.

## Files changed

- `README.md` and `README.ru.md` — current public status moved to Phase 229 while keeping `v0.1.7-readonly` as current read-only and `v0.2.4-writealpha` as current write-alpha.
- `CHANGELOG.md`, `docs/ROADMAP.md`, and `PROJECT_STATUS.md` — release posture synchronized: Phase 229 complete, `v0.2.5-writealpha` remains unpublished, no tag/release created, blocker closure remains synthetic/disposable only.
- `docs/release/v0.2.5-writealpha-notes.md`, `docs/release/v0.2.5-writealpha-checklist.md`, `docs/release/v0.2.5-writealpha-final-gate.md`, `docs/release/v0.2.5-writealpha-no-release-verdict.md`, and `docs/release/v0.2.5-writealpha-blocker-closure.md` — release-support addenda clarify current public write-alpha stays `v0.2.4-writealpha` until a later authorized release phase.
- `scripts/check_public_status.py` — current phase expectation updated to Phase 229 and guard coverage expanded to `v0.2.5-writealpha` no-release/support docs while still reading only tracked public docs/config.
- `apps/api/tests/test_public_status_guard.py` — backend guard tests updated for Phase 229 and stale Phase 228 current-baseline rejection.
- `docs/handoff/phase-229.md` — this handoff.

## Verification performed

- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest tests/test_public_status_guard.py -q` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check && npm run test:auth-routes && npm run build` — passed.
- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- `APP_ENV=test` was not weakened.
- Status guard reads only declared tracked public docs/config files; it does not read `.env`, runtime books, app DBs, backups, private paths, screenshots, exports, tokens, or secrets.
- No write-enabled smoke was run.
- No real/private/only-copy book, committed runtime book, app DB, backup artifact, `.env`, screenshot/export, token, key, cert, raw path, account name, memo, amount, production/security claim, public-internet-safety claim, or real/private-book write-safety claim was added.

## Risks / blockers

No Phase 229 blocker remains. `v0.2.5-writealpha` remains unpublished; a later release-candidate dogfood and release-gate phase must still run before any tag or GitHub release.

## Next

Do not start the next roadmap phase from this session.
