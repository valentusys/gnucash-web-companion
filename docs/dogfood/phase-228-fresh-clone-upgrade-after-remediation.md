# Phase 228 — fresh-clone and synthetic upgrade smoke after remediation

Date: 2026-05-21
Status: PASS — current `HEAD` fresh-clone Docker smoke and `v0.2.4-writealpha` → current `HEAD` synthetic upgrade smoke passed with default-disabled writes.
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-3/roadmap-cycle-3.md` (Cycle 3, Phase 7 only)

## Scope

This phase verified the clean-checkout and synthetic upgrade paths after the write-alpha backup/audit remediation and before any release gate.

The run used only temporary clones, the committed synthetic fixture copied into ignored runtime storage, dummy local-only credentials, Docker Compose/Caddy, and `GNUCASH_WRITES_ENABLED=false`.

No write-enabled smoke, release tag, migration feature work, real/private book, app DB, backup, `.env`, screenshot, export, token, key, cert, raw private path, account name, memo, amount, or private financial data was committed.

## Commands run

Fresh clone from current `HEAD`:

```text
scripts/smoke/fresh-clone-docker-smoke.sh --repo /home/val/gnucash-web-companion --ref HEAD --port 18084
```

Synthetic upgrade from the current public write-alpha tag runtime state to current `HEAD`:

```text
scripts/smoke/synthetic-upgrade-smoke.sh --repo /home/val/gnucash-web-companion --previous-ref v0.2.4-writealpha --current-ref HEAD --port 18085
```

Full local logs were written outside git:

```text
/home/val/.hermes/logs/gnucash-web-companion/phase-228/fresh-clone-current-head.log
/home/val/.hermes/logs/gnucash-web-companion/phase-228/synthetic-upgrade-v024-to-head.log
```

## Evidence summary

### Fresh-clone smoke

- Checkout under test: `059b40f`.
- Runtime data: committed synthetic fixture copied into the temporary clone as ignored `data/books/main.gnucash.sqlite`.
- Docker Compose config validation passed with `GNUCASH_WRITES_ENABLED=false` rendered.
- `/api/health` reported writes disabled.
- Read-only API smoke passed:
  - health
  - login/auth
  - books/default book
  - accounts
  - transactions
  - transaction detail
  - CSV export endpoint
  - reports summary
  - scheduled transactions endpoint
  - write-alpha audit summary endpoint
  - validate/create/PATCH/DELETE disabled-write probes returning HTTP 403
- Browser dogfood passed at `320x720` and `1280x900`:
  - login and protected-route redirect
  - dashboard/accounts/books/scheduled/account detail/transaction filters/transaction detail
  - hidden write UI
  - auth cookie not readable from `document.cookie`
  - no horizontal overflow at both widths
  - CSV fetch through the browser without saved downloads
- No raw screenshot/export/backup artifacts were created in the temporary clone.
- Helper teardown removed the temporary clone and Docker runtime.

### Synthetic upgrade smoke

- Previous runtime state: `v0.2.4-writealpha` checkout `05f9080`.
- Current checkout under test after upgrade: `059b40f`.
- Runtime data preserved only inside the temporary clone's ignored `data/` paths.
- Dummy app metadata DB remained readable after switching the checkout to current `HEAD` and rebuilding/restarting Docker Compose.
- Default book and selected-book recovery remained available and path-safe.
- Upgraded read-only routes passed for accounts, transactions, reports, scheduled metadata, and write-alpha audit summary.
- Disabled validate/create/PATCH/DELETE probes returned HTTP 403 after upgrade.
- Docker Compose rendering kept `GNUCASH_WRITES_ENABLED=false`.
- Helper teardown removed the temporary clone and Docker runtime.

## Cleanup / no-artifact result

Post-run checks found no leftover `gwc_fresh_clone` or `gwc_synthetic_upgrade` Docker containers/volumes/networks. The only untracked repository path after the smoke runs was `.hermes/`, which contains local logs and is intentionally excluded from commits.

## Safety notes

- `GNUCASH_WRITES_ENABLED=false` remained in force throughout both smokes.
- Dummy local-only secrets were used and are not recorded here.
- No write-enabled mode was started.
- No real/private/only-copy book or copied personal book was used.
- Evidence records bounded synthetic fixture/status/hash information only.
- This is fresh-clone and synthetic upgrade smoke evidence only. It is not production readiness, a security audit, broad migration compatibility, or real/private-book write-safety evidence.
