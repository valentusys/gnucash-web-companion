# Phase 153 — Fresh-clone Docker install smoke

Date: 2026-05-19
Status: passed on generated/disposable data
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 2/10 only)

## Summary

Phase 153 added a reproducible fresh-clone Docker smoke helper and used it to prove that a clean checkout can run the read-only app with dummy local-only secrets and the committed synthetic/disposable fixture.

Result: Docker Compose config, Docker startup, `/api/health`, API smoke, browser dogfood, hidden write UI, disabled write probes, and no-new-artifact checks passed with `GNUCASH_WRITES_ENABLED=false`. No real/private GnuCash book, `.env`, app DB, backup, screenshot, raw CSV export, token, key, cert, or private data was committed.

## Helper

New helper:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh
```

What it does:

1. Clones the repository into a temporary directory.
2. Checks out the requested ref, default `HEAD`.
3. Copies only the committed synthetic fixture to ignored runtime data:
   - source: `apps/api/tests/fixtures/test-book.gnucash.sqlite`
   - runtime filename: `data/books/main.gnucash.sqlite`
4. Writes a temporary clone-local `.env` with dummy local-only values and `GNUCASH_WRITES_ENABLED=false`.
5. Creates an ignored `docker-compose.override.yml` in the temporary clone so the proxy uses host port `18080` by default, avoiding conflicts with a developer's existing port `8080` stack.
6. Runs Docker Compose config validation and startup.
7. Runs the existing read-only API smoke helper.
8. Runs the existing headless browser dogfood helper.
9. Verifies that no new raw screenshot/export/backup artifacts were created in the clone.
10. Tears down Docker and removes the temporary clone unless `--keep-workdir` is provided.

The helper does not print secret values. The dummy `.env`, runtime app DB, runtime GnuCash fixture copy, and Docker override remain untracked and temporary.

## Exact command

Run from `/home/val/gnucash-web-companion`:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh
```

Useful options:

```bash
scripts/smoke/fresh-clone-docker-smoke.sh --repo /path/or/url --ref main --port 18080
scripts/smoke/fresh-clone-docker-smoke.sh --keep-workdir
```

## Runtime setup used for this pass

- Clone source: `/home/val/gnucash-web-companion`
- Ref checked out in the temporary clone: `4edda3b`
- Runtime origin: `http://127.0.0.1:18080`
- Runtime fixture filename: `main.gnucash.sqlite`
- Runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`
- Runtime writes: `GNUCASH_WRITES_ENABLED=false`
- Secrets: dummy local-only values inside the temporary clone-local `.env`; values were not printed.
- Browser: headless Chromium via Chrome DevTools Protocol.

## Evidence

Docker Compose config validation passed and rendered `GNUCASH_WRITES_ENABLED=false`.

Docker Compose startup passed with rebuilt API/web images in the temporary clone.

Health check passed:

```text
ok: health status=ok writes_enabled=false
```

API smoke passed:

```text
read-only API smoke: target=http://127.0.0.1:18080/api
ok: API health
ok: login
ok: /auth/me
ok: default book discovered via /books and verified at /books/1
ok: accounts endpoint
ok: transactions endpoint
ok: transaction detail endpoint
ok: CSV export endpoint
ok: reports summary
ok: validate endpoint is write-disabled
ok: create endpoint is write-disabled
ok: patch endpoint is write-disabled
PASS: read-only API smoke checks completed
```

Browser dogfood passed:

```text
read-only browser dogfood: target=http://127.0.0.1:18080
fixture: filename=main.gnucash.sqlite sha256=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
ok: login_page: loaded
ok: protected_redirect: dashboard redirected to login
ok: login: authenticated; auth cookie not readable from document.cookie
ok: dashboard: /dashboard loaded; write UI hidden
ok: accounts: /accounts loaded; write UI hidden
ok: books: /books loaded; write UI hidden
ok: scheduled: /scheduled loaded; write UI hidden
ok: account_detail: first account detail loaded
ok: transactions_filters: filtered transactions page loaded; export link preserved query
ok: transaction_detail: first transaction detail loaded
ok: csv_export: status=200 total=0 truncated=false
ok: no_artifacts: no screenshots/downloads/CSV files written
PASS: read-only browser dogfood completed
```

No-new-artifact check passed:

```text
ok: no new raw screenshot/export/backup artifacts found
[fresh-clone-smoke] fresh-clone smoke PASS head=4edda3b base_url=http://127.0.0.1:18080 fixture_sha=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
```

## Acceptance criteria result

- Clean checkout command path exists: pass.
- Docker Compose config validates with dummy local-only secrets and writes disabled: pass.
- Docker startup works from the temporary clone with synthetic/disposable data: pass.
- Login, health, books, dashboard, accounts, transactions, CSV export, and scheduled page are covered: pass.
- Write UI hidden and validate/create/patch write probes disabled with `403`: pass.
- No screenshots, raw CSV exports, backups, app DB, `.env`, fixture copy, or private data committed: pass.

## Limitations

- This is a local fresh-clone smoke with synthetic/disposable fixture data only.
- This is not a production deployment hardening claim and not a security audit.
- The app remains pre-alpha and should not be exposed directly to the public internet.
- No package, Docker image, binary, tag, or GitHub release was published in this phase.
- Controlled writes remain post-MVP/experimental and disabled by default.

## Safety

- `GNUCASH_WRITES_ENABLED=false` remained the runtime and rendered Docker default.
- GnuCash Desktop remains the authoritative editor.
- No production write mode was enabled.
- No real/private book or private financial data was used.
- No `.env`, token, key, cert, app DB, backup, screenshot, raw CSV export, copied runtime book, or private path was committed.
