# Phase 214 synthetic upgrade smoke

Date: 2026-05-21

## Scope

Phase 214 verified a safe synthetic local upgrade path from the previous published write-alpha tag/runtime state to current `main`.

This evidence uses only ignored synthetic runtime copies and dummy local-only credentials. It does not inspect or commit a real/private `data/app/app.db`, GnuCash book, backup, `.env`, screenshot, export, token, key, or certificate.

## Command

```bash
scripts/smoke/synthetic-upgrade-smoke.sh --previous-ref v0.2.4-writealpha --current-ref HEAD --port 18083
```

## Result

PASS.

The smoke script:

1. Created a temporary clone at `v0.2.4-writealpha`.
2. Copied the committed synthetic fixture into ignored runtime storage as `main.gnucash.sqlite`.
3. Started Docker Compose with dummy local-only credentials and `GNUCASH_WRITES_ENABLED=false`.
4. Injected dummy legacy app metadata into the app metadata DB inside the temporary runtime only.
5. Verified login and read-only API access on the previous tag.
6. Swapped the temporary checkout to current `HEAD` and rebuilt/restarted the local stack.
7. Verified the dummy app metadata DB stayed readable after upgrade.
8. Verified default/selected book metadata, accounts, transactions, reports, scheduled metadata, and write-alpha audit-summary read-only route.
9. Verified selected-book recovery is safe when an unavailable selected-book cookie is present.
10. Verified disabled write probes for validate/create/PATCH/DELETE return HTTP 403.
11. Confirmed Docker Compose rendering keeps `GNUCASH_WRITES_ENABLED=false`.
12. Tore down the temporary stack and removed the temporary clone.

## Safety notes

- Runtime data lived only in the smoke helper temporary clone under ignored `data/` paths.
- Credentials used by the smoke were dummy local-only values.
- The GnuCash fixture was the committed synthetic fixture copy only.
- No write-enabled run was performed.
- No release, tag, package, Docker image, or publication artifact was created.
- The result is upgrade-path smoke evidence only; it is not production readiness, security audit, broad migration guarantee, or real/private-book safety evidence.
