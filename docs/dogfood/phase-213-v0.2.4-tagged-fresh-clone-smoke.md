# Phase 213 — v0.2.4 tagged fresh-clone smoke

Date: 2026-05-21
Status: PASS — published `v0.2.4-writealpha` tag and current `main` passed fresh-clone Docker/Caddy smoke with default-disabled writes.
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-2/roadmap-cycle-2.md` (Cycle 2, Phase 2 only)

## Scope

This phase independently checked the published `v0.2.4-writealpha` tag from a fresh clone/tag path using only the committed synthetic fixture, dummy local-only secrets, Docker Compose/Caddy, API read-only smoke, and browser dogfood at mobile and desktop widths.

No write-enabled run was performed. No real/private/copied personal book, app DB, backup, `.env`, screenshot, export, token, key, cert, or runtime artifact is committed.

## Helper hardening

`scripts/smoke/fresh-clone-docker-smoke.sh` now runs browser dogfood twice for each fresh clone:

- mobile viewport: `320x720`
- desktop viewport: `1280x900`

`scripts/smoke/read-only-browser-dogfood.py` now classifies viewports as mobile below `768px` and desktop at wider widths for the CDP device metrics override.

This is smoke-helper hardening only; product runtime behavior, write routes, write defaults, and release state were not changed.

## Commands run

Tagged release smoke:

```text
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref v0.2.4-writealpha --port 18081
```

Current main comparison smoke:

```text
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18082
```

Full local logs were written outside git:

```text
/home/val/.hermes/logs/gnucash-web-companion/phase-213/v0.2.4-tagged-fresh-clone-smoke.log
/home/val/.hermes/logs/gnucash-web-companion/phase-213/current-main-fresh-clone-smoke.log
```

## Evidence summary

### `v0.2.4-writealpha` tag

- Fresh clone checkout: `8b6412b`.
- Runtime data: committed synthetic fixture copied to ignored `data/books/main.gnucash.sqlite` inside the temporary clone.
- Docker Compose config validation passed with writes disabled.
- `/api/health` reported `writes_enabled=false`.
- Read-only API smoke passed:
  - health
  - login/auth
  - books/default book
  - accounts
  - transactions
  - transaction detail
  - CSV export headers
  - reports summary
  - scheduled metadata
  - write-alpha audit summary read-only endpoint
  - validate/create/PATCH/DELETE disabled-write probes
- Disabled write probes returned HTTP 403 for validate/create/PATCH/DELETE.
- Extra wrapper DELETE probe passed for tagged-checkout compatibility.
- Browser dogfood passed at `320x720` and `1280x900`:
  - login and protected-route redirect
  - dashboard/accounts/books/scheduled/account detail/transaction filters/transaction detail
  - hidden write UI
  - no horizontal overflow at both widths
  - CSV fetch through the browser without writing downloads
  - `document.cookie` did not expose the auth cookie
- No raw screenshot/export/backup artifacts were found in the temporary clone.
- Temporary clone and Docker runtime were removed by helper teardown.

### Current `main` comparison

- Fresh clone checkout: `fedc892`.
- Same synthetic fixture, dummy-secret, write-disabled Docker/Caddy path passed.
- Read-only API smoke passed, including validate/create/PATCH/DELETE disabled-write probes.
- Browser dogfood passed at `320x720` and `1280x900` with hidden write UI, auth cookie not readable from `document.cookie`, no-overflow checks, CSV fetch, and no artifacts.
- Temporary clone and Docker runtime were removed by helper teardown.

## Safety notes

- `GNUCASH_WRITES_ENABLED=false` was used throughout and confirmed by rendered Docker config plus `/api/health`.
- Only dummy local-only secrets were used; exact dummy values are intentionally not recorded here.
- No write-enabled mode was started.
- No real/private/only-copy book or copied personal book was used.
- Evidence records only bounded synthetic fixture filename/checksum, tag/head short hashes, status results, and no-artifact outcomes.
- Local logs under `.hermes/` are untracked and not committed.

## Result

PASS. The published `v0.2.4-writealpha` tag independently starts from a fresh clone through Docker Compose/Caddy and passes the documented read-only API/browser smoke path with default-disabled writes and synthetic/disposable data only.
