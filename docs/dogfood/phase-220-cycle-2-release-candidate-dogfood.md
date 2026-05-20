# Phase 220 — Cycle-2 release-candidate dogfood

Date: 2026-05-21
Status: NO-RELEASE BLOCKER — default-read-only dogfood passed; bounded write-alpha drill exposed backup-count evidence drift after DELETE.
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md` (Cycle 2, Phase 9 only)

## Scope

This phase collected a fresh local release-candidate evidence pack after Phases 212–219:

- default Docker/Caddy run with the committed synthetic fixture copied into ignored runtime storage and `GNUCASH_WRITES_ENABLED=false`;
- read-only API smoke for health, login/auth, books, accounts, transactions, transaction detail, CSV export, reports, scheduled metadata, write-alpha audit summary, and disabled validate/create/PATCH/DELETE probes;
- browser dogfood at mobile `320x720` and desktop `1280x900` for hidden write UI, auth-cookie no-readability, CSV fetch, and no-overflow/no-artifact checks;
- separate explicit local write-alpha drill with `APP_ENV=test` and `GNUCASH_WRITES_ENABLED=true` only on synthetic/disposable ignored runtime copies;
- reset back to default false and cleanup of smoke runtime artifacts.

No real/private or only-copy book was used. No screenshot, raw CSV, runtime book, backup, app DB, `.env`, token, cookie, account name, memo, amount, or raw private path is committed here.

## Default-read-only evidence

Rendered Compose before smoke:

```text
GNUCASH_WRITES_ENABLED: "false" for API and web
```

API smoke result:

```text
PASS: health, login/auth, books/default book, accounts, transactions, transaction detail, CSV export, reports summary, scheduled transaction metadata, write-alpha audit summary, and validate/create/PATCH/DELETE disabled-write probes returning 403.
```

Browser dogfood result:

```text
PASS: mobile 320x720 and desktop 1280x900. Login/protected redirect passed; auth cookie was not readable from document.cookie; dashboard/accounts/books/scheduled/account-detail/transactions/transaction-detail routes loaded; write UI stayed hidden; CSV fetch passed; no horizontal overflow or screenshot/download/CSV artifacts were produced.
```

## Bounded write-alpha drill evidence

Write-alpha was started only with explicit local `APP_ENV=test` plus `GNUCASH_WRITES_ENABLED=true` and dummy local-only credentials. The source was the committed synthetic fixture copied to a temporary disposable source, then to ignored runtime storage. The preflight summary was redacted and passed:

```text
status=ready; source=external copied/disposable; runtime=ignored data/books; backups=ignored data/backups; dry_run=true
```

Route-family results:

```text
CREATE: PASS. Expected validation probes failed safely, exactly one balanced create succeeded, backup/audit evidence increased once, and lock evidence was stale-released/not active.
PATCH: PASS. Missing-transaction PATCH failed safely without backup, exactly one metadata/split-memo PATCH succeeded, runtime/API read-back matched synthetic markers only, amount fingerprint stayed unchanged, backup/audit evidence passed, and lock evidence was stale-released/not active.
DELETE: BLOCKED. The DELETE route returned success, API/runtime absence checks passed, the backup evidence contained the deleted transaction with matching bounded split fingerprint, and the audit table recorded one successful DELETE. The helper then failed because backup file count did not increase by exactly one after DELETE.
```

Immediate redacted inspection after the DELETE failure:

```text
backup_file_count=2
audit successes with backup: create=1, patch=1, delete=1
patch failed-safe audit without backup=1
lock status=stale_released, active=false
```

Interpretation: three successful write route families produced three successful backup-bearing audit entries, but only two backup files were present after the DELETE run. This is treated as a release blocker because it may indicate backup filename/count collision or overwrite under fast consecutive route-family smokes. No second DELETE rerun was performed after the successful routed DELETE; the runtime was reset and cleaned instead.

## Default-false reset and cleanup

After the write-alpha drill, the stack was stopped, ignored runtime artifacts were cleaned with the stopped-runtime cleanup helper, a fresh default-read-only synthetic fixture was started, and rendered Compose again showed:

```text
GNUCASH_WRITES_ENABLED: "false" for API and web
```

The reset read-only API smoke passed again, including validate/create/PATCH/DELETE returning 403.

Final cleanup removed smoke runtime book/backups/locks and generated smoke app DB. A pre-existing ignored local app DB was restored as local untracked state; it is not staged or committed.

## Verification summary

Passed:

- `JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> ORIGIN=http://localhost:8080 GNUCASH_WRITES_ENABLED=false docker compose config --quiet`
- rendered Compose false before and after write-alpha drill
- `python3 -m py_compile` for read-only and write-alpha smoke helpers
- default-read-only API smoke before write-alpha drill
- mobile browser dogfood
- desktop browser dogfood
- write-alpha preflight dry-run
- write-alpha create smoke
- write-alpha PATCH smoke
- default-read-only API smoke after reset
- stopped-runtime cleanup of ignored smoke artifacts

Blocked:

- write-alpha DELETE+restore smoke failed after successful DELETE because backup file count did not increase by exactly one.

## Release impact

No release should be published from this evidence pack until the DELETE backup-count anomaly is investigated and a fresh bounded write-alpha drill passes. The default-read-only release-candidate path is green, but the cycle includes write-alpha path changes/evidence requirements, so this phase records an explicit no-release blocker for Phase 221.
