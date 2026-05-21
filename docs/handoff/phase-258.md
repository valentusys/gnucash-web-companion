# Phase 258 — End-to-end synthetic copied-book package rehearsal

Date: 2026-05-21

Status: COMPLETE — maintainer copied-book dogfood package rehearsed on synthetic/disposable copied fixture evidence only.

## Summary

Phase 258 ran the copied-book package rehearsal before any owner copied-book attempt:

- Wrapper dry-run passed with redacted preflight, pre-step backup, no mutation, and default-disabled reset proof.
- Docker/Caddy was started in explicit local write-alpha test mode with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` against an ignored synthetic runtime copy.
- Wrapper create-one passed through the delegated create smoke helper: validation probes behaved as expected, exactly one CREATE succeeded, the created transaction was read back, backup/audit counts increased, and lock evidence was inactive.
- Compatibility harness opened the mutated synthetic copy read-only with piecash; host `gnucash-cli` was unavailable and therefore recorded as blocked rather than claimed as compatibility evidence.
- A separate temporary Debian container GnuCash CLI probe ran `gnucash-cli --report show --name "Balance Sheet" <redacted-book>` successfully against the synthetic copy; this is narrow tooling evidence only, not broad compatibility evidence.
- Restore verification restored a copied working book from the pre-mutation backup, matched checksum prefixes, and passed piecash read-back.
- Runtime was reset to `GNUCASH_WRITES_ENABLED=false`, and read-only API smoke through Caddy verified validate/create/PATCH/DELETE all return disabled-write 403.

## Artifacts

- `docs/dogfood/phase-258-synthetic-copied-book-package.md`
- `docs/handoff/phase-258.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- No real/private/original/only-copy book was used.
- No app DB, GnuCash book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, API payload, cookie, or private financial data artifact was committed.
- No release/tag was published.
- No production, security-audited, public-internet, broad Desktop/version compatibility, production disaster-recovery, or real/private/only-copy write-safety claim was added.

## Verification performed

```bash
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/write_alpha_copied_book_dogfood.py --dry-run ...
APP_ENV=test GNUCASH_WRITES_ENABLED=true GNUCASH_DEFAULT_BOOK_PATH=/data/books/<redacted-synthetic-copy> JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose up -d --build
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/write_alpha_copied_book_dogfood.py --create-one ...
python3 scripts/write_alpha_compatibility_check.py <redacted-mutated-copy> --output <redacted-evidence-json>
docker run --rm ... debian:bookworm-slim ... gnucash-cli --report show --name "Balance Sheet" <redacted-book>
python3 scripts/write_alpha_restore_verify.py --target <redacted-copy> --backup <redacted-pre-mutation-backup> --output <redacted-evidence-json> ...
APP_ENV=test GNUCASH_WRITES_ENABLED=false GNUCASH_DEFAULT_BOOK_PATH=/data/books/<redacted-synthetic-copy> JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 docker compose up -d
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
python3 scripts/check_public_status.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
python3 - <<'PY'
# sensitive tracked-file hygiene scan
PY
git diff --check
```

Results:

- Dry-run wrapper: PASS.
- Create-one wrapper and read-back smoke: PASS.
- Compatibility harness: piecash PASS; host Desktop/CLI tooling BLOCKED because `gnucash-cli` was not on host PATH.
- Temporary Debian container GnuCash CLI report probe: PASS with bounded output.
- Restore verification: PASS for checksum match and piecash read-back; optional API command inside the restore harness was not used, and web/API read-back was verified separately after reset.
- Reset default-disabled API smoke through Caddy: PASS; validate/create/PATCH/DELETE returned 403.
- Browser dogfood: BLOCKED/NON-BLOCKING in this environment because the helper timed out on transaction-row navigation after earlier route checks; no Phase 258 browser evidence is claimed.
- Public status guard, Docker Compose config, sensitive tracked-file hygiene scan, and git whitespace check: PASS.

## GitHub issues

No new GitHub issue was required. Phase 258 evidence is relevant to existing write-alpha readiness tracking (#36), but it still does not authorize owner copied-book or real/private-book writes.

## Next phase boundary

Phase 259 may run the owner copied-book decision gate. It should decide whether to ask the owner for dry-run only, create-one after dry-run, or not ready, using Phase 258 evidence plus the known host Desktop/CLI blocked condition. Phase 258 did not execute owner dogfood, publish a release, or claim real/private/only-copy write safety.
