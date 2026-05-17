# Local Secure Deployment Guide

> **Pre-alpha warning:** This guide is for safe local or private-network testing of `gnucash-web-companion`. It is not a production hardening certification, security audit, or guarantee. Start with a copied/disposable GnuCash SQL book and keep GnuCash Desktop as the authoritative editor.

## Scope

This guide covers conservative self-hosted deployments for the read-only MVP:

- local-only deployment on one machine;
- LAN or VPN-only deployment for trusted devices;
- reverse proxy and HTTPS notes;
- `.env` secrets and bootstrap credentials;
- Docker volume/data locations;
- GnuCash book and app metadata separation;
- keeping controlled writes disabled.

It does not cover public internet hosting, SaaS operation, high availability, or production compliance.

## Deployment modes

### Local-only: safest starting point

Use this mode first while testing the app and your copied book.

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Put a copied/disposable GnuCash SQL book under `data/books/`.
4. Keep the proxy bound to localhost if you do not need LAN access.

Example local-only override:

```yaml
# docker-compose.localhost.yml
services:
  proxy:
    ports:
      - "127.0.0.1:8080:80"
```

Run:

```bash
docker compose -f docker-compose.yml -f docker-compose.localhost.yml up --build
```

Open:

```text
http://localhost:8080
```

### LAN/VPN-only: private-network testing

Use this only on a trusted LAN or behind a VPN such as WireGuard/Tailscale.

- Do not publish the container port directly to the public internet.
- Restrict access with host firewall rules, router rules, or VPN ACLs.
- Prefer HTTPS even on a LAN if credentials or real copied data may cross the network.
- Assume every CSV export, screenshot, browser cache, and log from this deployment may contain sensitive financial data.

If you expose `8080` on a LAN, verify that it is reachable only from the intended private subnet or VPN.

## Minimal setup

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
mkdir -p data/books data/app data/backups data/locks
```

Copy a test book:

```bash
cp /path/to/copied-test-book.gnucash.sqlite data/books/main.gnucash.sqlite
```

Do not copy your only authoritative GnuCash file. Do not commit files under `data/books/`, `data/app/`, `data/backups/`, or `.env`.

## Required `.env` settings

Edit `.env` before starting:

```dotenv
APP_ENV=development
APP_DATABASE_URL=sqlite:////data/app/app.db
GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite
JWT_SECRET=<long-random-secret>
APP_ADMIN_USERNAME=admin
APP_ADMIN_PASSWORD=<temporary-bootstrap-password>
APP_ADMIN_PASSWORD_HASH=
GNUCASH_WRITES_ENABLED=false
ORIGIN=http://localhost:8080
```

Generate a secret:

```bash
openssl rand -hex 32
```

For non-local deployments, prefer `APP_ADMIN_PASSWORD_HASH` instead of keeping a plaintext bootstrap password in `.env` after the initial setup path is mature enough for your environment. Treat `.env` as a secret file either way.

Important:

- `JWT_SECRET=change-me-use-a-long-random-secret` is a placeholder and is intentionally unsafe.
- Keep `GNUCASH_WRITES_ENABLED=false` for the read-only MVP.
- `CORS_ORIGINS=["*"]` is a development-friendly default; narrow it before any shared LAN/VPN deployment if browser origins are known.
- Set `ORIGIN` to the exact external URL used by browsers, especially when using HTTPS behind a reverse proxy.

## Data locations and volumes

The default Docker Compose file mounts the repository `./data` directory into containers as `/data`.

| Host path | Container path | Purpose | Safety note |
| --- | --- | --- | --- |
| `./data/app/` | `/data/app/` | App metadata SQLite DB, including users/book access metadata | Back up separately; never commit. |
| `./data/books/` | `/data/books/` | Copied GnuCash SQL books | Use copied/disposable books first; never commit. |
| `./data/backups/` | `/data/backups/` | Backup files used by experimental controlled-write paths | Keep even with writes disabled if testing write mode later; never commit. |
| `./data/locks/` | `/data/locks/` | Per-book lock files for controlled-write code | Operational runtime state; never commit. |

The app metadata DB is not the GnuCash book. Keep them separate and back them up separately.

## Start and verify

Validate configuration without printing secrets:

```bash
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

Start:

```bash
docker compose up --build
```

Basic checks:

```bash
curl -fsS http://localhost:8080/api/health
```

Then open:

```text
http://localhost:8080
```

Use `scripts/smoke/read-only-api-smoke.py` after the deployment is running:

```bash
SMOKE_ADMIN_PASSWORD='<local-admin-password>' scripts/smoke/read-only-api-smoke.py
```

The smoke script checks health, login, `/auth/me`, book discovery, accounts, transactions, reports summary, and that controlled-write endpoints return 403 while writes are disabled.

## Keeping writes disabled

The safe default is:

```dotenv
GNUCASH_WRITES_ENABLED=false
```

Verify Docker Compose resolves the same value:

```bash
docker compose config | grep 'GNUCASH_WRITES_ENABLED=false'
```

Expected behavior with writes disabled:

- the authenticated app displays read-only safety wording;
- the normal write UI is hidden or blocked;
- direct write API requests return a read-only 403 response;
- GnuCash Desktop remains the authoritative editor.

Do not enable write mode for this local deployment guide. Controlled writes are experimental post-MVP work and are not part of the read-only MVP.

## Reverse proxy and HTTPS notes

The repository includes a Caddy-based Docker proxy for local use. For a LAN/VPN deployment behind another reverse proxy:

- terminate HTTPS at the outer proxy;
- forward requests to the app proxy or directly to the web/API services only on a private Docker/host network;
- set `ORIGIN=https://your-private-host.example`;
- restrict access to VPN/LAN users;
- avoid logging request bodies, cookies, CSV responses, account names, transaction descriptions, balances, or `.env` values;
- set HSTS only after you are sure the private HTTPS hostname is stable.

Auth cookies are `httpOnly`, `sameSite=lax`, and marked `secure` only when the browser origin is HTTPS. See `docs/security/auth-cookie-deployment.md` for the detailed cookie model.

## Why not expose directly to the public internet

Do not expose this pre-alpha app directly to the public internet because:

- it has not been security-audited or penetration-tested;
- it has no production-grade rate limiting, intrusion detection, or WAF story;
- GnuCash books and CSV exports contain sensitive financial data;
- misconfigured `.env`, proxy, or volume mounts could expose secrets/data;
- controlled-write code exists in the repository but must remain disabled by default.

If remote access is needed, use a VPN first.

## Backup guidance for this phase

Before testing with any copied real data:

- keep an untouched original GnuCash book outside this repository;
- keep an external backup not mounted into the containers;
- back up `data/app/app.db` if you care about local users/book registry state;
- back up copied books under `data/books/` if you have made local test changes outside this app;
- periodically run a restore dry-run outside the app.

This is basic operational guidance, not a production backup system. A fuller backup/recovery runbook is intentionally left for a later phase.

## Shutdown and cleanup

Stop containers:

```bash
docker compose down
```

Optional cleanup for a disposable test deployment:

```bash
rm -f data/app/app.db
rm -f data/books/main.gnucash.sqlite
rm -rf data/backups/* data/locks/*
```

Do not delete your original GnuCash book or external backups.

## Pre-flight checklist

- [ ] Running on localhost, LAN, or VPN only.
- [ ] HTTPS used for any non-localhost browser access.
- [ ] `.env` exists locally and is not committed.
- [ ] `JWT_SECRET` is long and random.
- [ ] Admin bootstrap credential is treated as secret.
- [ ] `GNUCASH_WRITES_ENABLED=false` is set and verified through `docker compose config`.
- [ ] `data/books/` contains only a copied/disposable book for first tests.
- [ ] `data/app/`, `data/books/`, `data/backups/`, and `.env` remain untracked by git.
- [ ] Public reports/issues do not include real account names, balances, screenshots, CSV rows, book files, `.env`, or logs containing secrets.
