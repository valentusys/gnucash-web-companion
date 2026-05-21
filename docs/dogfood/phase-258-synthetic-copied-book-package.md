# Phase 258 — Synthetic copied-book package rehearsal

Date: 2026-05-21

Status: COMPLETE — synthetic copied-book package rehearsed end-to-end with redacted evidence.

## Scope

This rehearsal used only synthetic/disposable copies derived from the committed test fixture. No real/private/original/only-copy book was used.

Covered steps:

1. copied-book wrapper dry-run;
2. copied-book wrapper create-one against a local Docker/Caddy write-alpha test runtime;
3. created transaction read-back through the create smoke helper;
4. compatibility harness read-back;
5. temporary Debian/GnuCash CLI report probe;
6. restore verification from pre-mutation backup;
7. reset runtime to `GNUCASH_WRITES_ENABLED=false`;
8. disabled write probes for validate/create/PATCH/DELETE through Caddy;
9. redacted evidence review.

## Redacted evidence summary

| Step | Result | Evidence |
| --- | --- | --- |
| Dry-run wrapper | PASS | preflight ready; pre-step backup created; no mutation command executed; default-disabled posture verified |
| Create-one wrapper | PASS | preflight ready; pre-step backup created; delegated create smoke passed; default-disabled posture verified |
| Read-back | PASS | create smoke verified health/books/accounts, validation failures, exactly one CREATE, transaction read-back, backup increase, audit increase, and inactive lock evidence |
| Compatibility harness | PARTIAL/PASS_WITH_BLOCKED_HOST_CLI | piecash read-back passed on the mutated synthetic copy; host `gnucash-cli` was unavailable and recorded as blocked, not as compatibility evidence |
| Temporary GnuCash CLI probe | PASS | disposable Debian container installed GnuCash, ran `gnucash-cli --report show --name "Balance Sheet" <redacted-book>`, and produced bounded report output |
| Restore verification | PASS | restored copied working book from pre-mutation backup; backup/restored checksum prefixes matched; piecash read-back passed |
| Reset to default false | PASS | runtime restarted with `GNUCASH_WRITES_ENABLED=false`; Compose/default checks stayed false |
| Disabled write probes | PASS | read-only API smoke through Caddy verified validate/create/PATCH/DELETE return 403 while writes are disabled |
| Browser smoke | BLOCKED/NON-BLOCKING | read-only API/Caddy smoke passed; browser helper timed out on transaction-row navigation in this environment, after login and earlier route checks, so no browser evidence is claimed for Phase 258 |

## Counts and statuses

- Wrapper dry-run backup count: 1.
- Wrapper create-one backup count: 1.
- Routed write-alpha CREATE count: 1.
- App metadata write-alpha ownership markers after create: 1.
- Runtime app backup files after create: 1.
- Lock evidence during create smoke: inactive; one stale lock file remained after runtime stop/restart and was not committed.
- Restore proof: verified offline with checksum match and piecash read-back.
- Disabled probes: validate/create/PATCH/DELETE all returned write-disabled 403 after reset.

## Redaction and safety review

Committed evidence contains only statuses, counts, checksum prefixes, opaque refs, and placeholder command labels. It does not include raw book paths, account names, transaction descriptions, memos, amounts, cookies, tokens, app DB contents, backup filenames, screenshots, CSV exports, or private financial data.

Safety posture remains unchanged:

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- The run used synthetic/disposable fixture copies only.
- No release/tag was published.
- No production, security-audited, public-internet, broad Desktop/version compatibility, production disaster-recovery, or real/private/only-copy write-safety claim is made.

## Verification commands

```bash
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/write_alpha_copied_book_dogfood.py --dry-run ...
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose up -d --build
APP_ENV=test GNUCASH_WRITES_ENABLED=true JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/write_alpha_copied_book_dogfood.py --create-one ...
python3 scripts/write_alpha_compatibility_check.py <redacted-mutated-copy> --output <redacted-evidence-json>
docker run --rm ... debian:bookworm-slim ... gnucash-cli --report show --name "Balance Sheet" <redacted-book>
python3 scripts/write_alpha_restore_verify.py --target <redacted-copy> --backup <redacted-pre-mutation-backup> --output <redacted-evidence-json> ...
APP_ENV=test GNUCASH_WRITES_ENABLED=false JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose up -d
SMOKE_API_BASE_URL=http://localhost:8080/api SMOKE_ADMIN_PASSWORD=<dummy-local-password> python3 scripts/smoke/read-only-api-smoke.py
python3 scripts/check_public_status.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
git diff --check
```

## Result

Phase 258 package rehearsal is complete for synthetic/disposable evidence. The package is suitable for the next analyst decision gate to decide whether owner copied-book dogfood should be requested. The host Desktop/CLI harness remains explicitly blocked when host `gnucash-cli` is unavailable, but a separate temporary Debian container GnuCash CLI probe passed against the synthetic copy; this is narrow tooling evidence only and not broad compatibility evidence.
