# Phase 189 — Fresh-clone install smoke v2 with published/current tags

Date: 2026-05-20
Status: PASS — current public read-only release, current public write-alpha release, and current main all passed fresh-clone Docker smoke with synthetic data only
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 8 only)

## Goal

Verify install/upgrade confidence for current published releases and current `main` without reading private data.

## Scope completed

Fresh-clone Docker smoke was run against:

| Target | Ref tested | Commit | Port | Result |
| --- | --- | --- | --- | --- |
| current public read-only release | `v0.1.7-readonly` | `d248b5a355ed2b57913d0c408e643b5f6cfcfe5b` | `18087` | PASS |
| current public write-alpha release | `v0.2.1-writealpha` | `8c316b9f5c8028b519b603da0ba3cb37542bc4c0` | `18092` | PASS |
| current `main` | `HEAD` | `04751c3fe472fd7751746df525383214c3eb907c` | `18089` | PASS |

Each run used `scripts/smoke/fresh-clone-docker-smoke.sh` from the current working tree as the wrapper/controller. The checked-out target code ran from a temporary clone. The wrapper also ran the DELETE disabled-write probe for tagged checkouts whose bundled smoke helper may predate current DELETE coverage.

## Runtime setup

Common setup for all three runs:

- clone source: `/home/val/gnucash-web-companion`;
- temporary clone parent: `/tmp`;
- runtime fixture source inside each clone: `apps/api/tests/fixtures/test-book.gnucash.sqlite`;
- runtime fixture filename: `main.gnucash.sqlite`;
- runtime fixture SHA-256: `c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f`;
- dummy local-only admin/JWT secrets written only to the temporary clone-local ignored `.env`;
- runtime and rendered config: `GNUCASH_WRITES_ENABLED=false`;
- no public internet exposure; Caddy bound to `127.0.0.1` ports only;
- temporary clones were removed by helper teardown.

## Exact commands and log files

```bash
scripts/smoke/fresh-clone-docker-smoke.sh \
  --repo /home/val/gnucash-web-companion \
  --ref v0.1.7-readonly \
  --port 18087
```

Log: `/home/val/.hermes/logs/gnucash-web-companion/phase-189/v0.1.7-readonly-fresh-clone-smoke.log`

```bash
scripts/smoke/fresh-clone-docker-smoke.sh \
  --repo /home/val/gnucash-web-companion \
  --ref v0.2.1-writealpha \
  --port 18092
```

Log: `/home/val/.hermes/logs/gnucash-web-companion/phase-189/v0.2.1-writealpha-fresh-clone-smoke.log`

```bash
scripts/smoke/fresh-clone-docker-smoke.sh \
  --repo /home/val/gnucash-web-companion \
  --ref HEAD \
  --port 18089
```

Log: `/home/val/.hermes/logs/gnucash-web-companion/phase-189/main-fresh-clone-smoke.log`

## Evidence summary

All three runs passed the same acceptance path:

- Docker Compose config validation passed with dummy local-only secrets.
- Rendered config kept `GNUCASH_WRITES_ENABLED: "false"`.
- Docker Compose/Caddy started from the temporary clone.
- `/api/health` returned `status=ok` and `writes_enabled=false`.
- API smoke passed:
  - health;
  - login;
  - `/auth/me`;
  - `/books` and default book detail;
  - accounts;
  - transactions;
  - transaction detail;
  - CSV export;
  - reports summary;
  - disabled validate/create/PATCH/DELETE write probes returning HTTP 403.
- Browser dogfood passed at the default mobile viewport:
  - login page;
  - protected redirect;
  - authenticated login with auth cookie not readable from `document.cookie`;
  - dashboard;
  - accounts;
  - books;
  - scheduled;
  - account detail;
  - transaction filters;
  - transaction detail;
  - CSV export route;
  - hidden write UI;
  - no horizontal overflow on covered mobile paths;
  - no browser screenshots/downloads/CSV files written.
- Helper no-artifact scan passed: no new raw screenshot/export/backup artifacts were created in the temporary clone.
- Post-run host scan found no remaining `/tmp/gwc-fresh-clone-smoke.*` directories and no running Docker containers, volumes, or networks with `gwc_fresh_clone` names.

Representative pass markers:

```text
ok: health status=ok writes_enabled=false
PASS: read-only API smoke checks completed
ok: delete endpoint is write-disabled
PASS: read-only browser dogfood completed
ok: no new raw screenshot/export/backup artifacts found
[fresh-clone-smoke] fresh-clone smoke PASS head=d248b5a base_url=http://127.0.0.1:18087 fixture_sha=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
[fresh-clone-smoke] fresh-clone smoke PASS head=8c316b9 base_url=http://127.0.0.1:18092 fixture_sha=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
[fresh-clone-smoke] fresh-clone smoke PASS head=04751c3 base_url=http://127.0.0.1:18089 fixture_sha=c8f22b449c49a425d88f4dcf5ed3aed6d7a4356865c66d3e384c741e74ac1c2f
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remained the default and runtime posture for all runs.
- No explicit write-enabled smoke was run in this phase.
- Only the committed synthetic fixture was used.
- Generated `.env`, runtime app DB, runtime book copy, Caddy/Docker state, browser downloads, and any temporary artifacts stayed inside temporary clones or Docker runtime and were removed by teardown.
- No real/private book, app DB, backup, `.env`, token, key, cert, screenshot, raw CSV export, private path, account name, memo, amount, or private financial data was committed.
- No release, tag, package, Docker image, or public deployment was published.

## Acceptance result

PASS. Fresh clone starts and passes health/login/books/accounts/transactions/reports/CSV/browser flows for the current public read-only release, the current public write-alpha release, and current `main`; disabled write probes return 403; and teardown/no-artifact checks passed.

## Limitations

- This is local synthetic/disposable Docker smoke evidence only.
- It is not a production deployment hardening claim, security audit, public-internet safety claim, broad GnuCash compatibility claim, or real/private-book write-safety claim.
- The write-alpha release was tested only with the default read-only posture; no write-enabled path was exercised in this phase.
