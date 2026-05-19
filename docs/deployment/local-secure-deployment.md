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

### JWT secret setup and rotation

`JWT_SECRET` signs login sessions. It is not stored in the GnuCash book, but anyone who knows it could mint valid app tokens until the secret is changed. Generate it locally and store it only in your private `.env` or secret manager:

```bash
openssl rand -hex 32
```

Recommended practice:

- use at least 32 random bytes, for example the 64-character hex output above;
- do not use names, hostnames, book names, passwords, or copied examples as the secret;
- do not paste the real value into issues, logs, screenshots, handoff docs, shell history shared with others, or committed files;
- keep a private offline copy only if you need deterministic restart/recovery of existing sessions;
- rotate the secret after any suspected `.env` exposure, after sharing a test environment, or before moving from localhost-only testing to LAN/VPN testing.

Rotation procedure:

1. Stop the deployment: `docker compose down`.
2. Replace `JWT_SECRET` in `.env` with a new `openssl rand -hex 32` value.
3. Start the deployment again: `docker compose up -d --build`.
4. Log in again from each browser. Existing auth cookies should be treated as invalid after rotation.
5. If exposure was suspected, also rotate the admin bootstrap password/hash and review reverse-proxy/container logs for leaked request or environment data.

There is currently no multi-key graceful JWT rotation or centralized session revocation workflow. Rotation is intentionally simple and conservative for the pre-alpha self-hosted deployment model.

For non-local deployments, prefer `APP_ADMIN_PASSWORD_HASH` instead of keeping a plaintext bootstrap password in `.env` after the initial setup path is mature enough for your environment. Treat `.env` as a secret file either way.

Important:

- `JWT_SECRET=change-me-use-a-long-random-secret` is a placeholder and is intentionally unsafe.
- Keep `GNUCASH_WRITES_ENABLED=false` for the read-only MVP.
- `CORS_ORIGINS=["*"]` is a development-friendly default; narrow it before any shared LAN/VPN deployment if browser origins are known. The API health/startup diagnostics warn when this wildcard is used outside development-like `APP_ENV` values.
- Set `ORIGIN` to the exact external URL used by browsers, especially when using HTTPS behind a reverse proxy.

## CORS origin narrowing for LAN/VPN

CORS is not a public-internet security boundary, but wildcard browser origins are still too loose for shared LAN/VPN testing. Before a LAN/VPN deployment, set `CORS_ORIGINS` to the exact browser origins that should call the API through the web/proxy URL.

Recommended values by deployment mode:

- localhost-only: `CORS_ORIGINS=["http://localhost:8080"]` or the exact loopback host/port you actually open in the browser;
- trusted LAN HTTP: include only the private DNS name and/or static private IP that users type in the browser, for example `http://gnucash.lan:8080` and `http://192.168.1.50:8080`;
- VPN/private HTTPS: prefer one private HTTPS hostname and list only that origin, for example `https://gnucash.vpn.example`;
- avoid `CORS_ORIGINS=["*"]` outside single-machine development.

Examples:

```dotenv
# Local-only browser access
APP_ENV=development
ORIGIN=http://localhost:8080
CORS_ORIGINS=["http://localhost:8080"]

# LAN HTTP testing on a trusted subnet only
APP_ENV=lan
ORIGIN=http://gnucash.lan:8080
CORS_ORIGINS=["http://gnucash.lan:8080","http://192.168.1.50:8080"]

# VPN or private HTTPS reverse-proxy hostname
APP_ENV=vpn
ORIGIN=https://gnucash.vpn.example
CORS_ORIGINS=["https://gnucash.vpn.example"]
```

Notes:

- Include the scheme (`http://` or `https://`) and port exactly as the browser sees them.
- Do not include secrets, JWTs, passwords, book paths, account names, transaction descriptions, amounts, or CSV data in origin values or logs.
- Even with narrowed CORS, keep this pre-alpha app off the direct public internet; use localhost, a trusted LAN, or a VPN, and prefer HTTPS when credentials or copied financial data cross the network.
- If `/api/health` reports a CORS warning for a non-development-like `APP_ENV`, narrow `CORS_ORIGINS` before using the deployment from shared devices.

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
docker compose config | grep -E 'GNUCASH_WRITES_ENABLED: "?false"?'
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

This is basic operational guidance, not a production backup system. See `docs/operations/backup-and-recovery.md` for the fuller manual backup and recovery runbook.

### App metadata DB backup

`data/app/app.db` stores app metadata such as the local admin user, registered books, access metadata, and session/audit placeholders. It is separate from the GnuCash book under `data/books/`; backing up one does not back up the other.

Conservative backup approach for self-hosted testing:

1. Stop containers before copying the SQLite file to avoid a partial live copy:
   ```bash
   docker compose down
   ```
2. Copy the app metadata DB to private storage outside the repository working tree:
   ```bash
   mkdir -p /private/backup/location/gnucash-web-companion/app
   cp data/app/app.db /private/backup/location/gnucash-web-companion/app/app-$(date +%Y%m%d-%H%M%S).db
   ```
3. Restrict permissions on the backup directory because metadata can reveal usernames, book registry state, and operational history:
   ```bash
   chmod 700 /private/backup/location/gnucash-web-companion/app
   ```
4. Start containers again:
   ```bash
   docker compose up -d
   ```
5. Periodically test restore into a disposable checkout or VM, never over your only working copy first.

Do not commit `data/app/app.db` or app metadata backups. Do not include real usernames, private book names, paths, or logs from the DB in public issues or handoff docs.

If you need a consistent backup without stopping containers, use SQLite online backup tooling from a controlled maintenance shell and verify the restore result before relying on it; this guide keeps the default procedure stop-copy-start because it is easier to reason about for pre-alpha self-hosting.

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

## Pre-deployment checklist for self-hosting

- [ ] Deployment URL is localhost, a trusted LAN hostname/IP, or a VPN-only hostname; no direct public-internet exposure is planned.
- [ ] Host firewall, router rules, or VPN ACLs restrict access to the intended devices/subnets.
- [ ] HTTPS is used for any non-localhost browser access, or the remaining LAN HTTP risk is explicitly accepted for short-lived testing only.
- [ ] `.env` exists only locally, is not committed, and does not contain copied example secrets.
- [ ] `JWT_SECRET` is freshly generated with `openssl rand -hex 32` or equivalent random tooling.
- [ ] Admin bootstrap credential or `APP_ADMIN_PASSWORD_HASH` is unique for this deployment and treated as secret.
- [ ] `ORIGIN` exactly matches the browser URL, including scheme and port.
- [ ] `CORS_ORIGINS` is narrowed to exact localhost/LAN/VPN origins; wildcard CORS is used only for single-machine development.
- [ ] `GNUCASH_WRITES_ENABLED=false` is set in `.env` and verified through `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` plus a `docker compose config` review.
- [ ] `data/books/` contains only a copied/disposable GnuCash SQL book for first tests; the authoritative original remains outside this repository.
- [ ] `data/app/app.db` backup/restore expectations are understood; any backup target is private and outside git.
- [ ] `data/app/`, `data/books/`, `data/backups/`, `data/locks/`, `.env`, secrets, keys, screenshots, CSV exports, and logs with private data remain untracked by git.
- [ ] Reverse-proxy logs are configured not to capture cookies, request bodies, CSV responses, account names, transaction descriptions, balances, or `.env` values.
- [ ] The read-only smoke script passes after startup, including disabled-write probes returning 403.
- [ ] Public reports/issues/handoffs contain only synthetic or redacted evidence and do not include real account names, balances, screenshots, CSV rows, book files, `.env`, private paths, secrets, or logs containing secrets.
- [ ] Everyone using the deployment understands this is pre-alpha/private testing with test copies first and no production guarantee.
