# Troubleshooting

This guide is for self-hosted pre-alpha deployments of `gnucash-web-companion`.
It focuses on safe diagnostics only: do not paste secrets, `.env` contents, real
GnuCash books, app databases, backups, real screenshots, or real exports into
public issues.

GnuCash Desktop remains the authoritative editor. The web app does not provide a
setup wizard, config-writing UI, book upload flow, or book-management UI for
first-run recovery.

## First safety checks

Before debugging a deployment, confirm:

```bash
grep '^GNUCASH_WRITES_ENABLED=' .env
```

Expected read-only default:

```text
GNUCASH_WRITES_ENABLED=false
```

Controlled writes are experimental post-MVP only. Do not enable write mode while
troubleshooting a real or only copy of a GnuCash book.

## Health endpoint

The API health endpoint is available through the reverse proxy at:

```text
http://localhost:8080/api/health
```

The backend direct endpoint is:

```text
http://localhost:8000/health
```

The endpoint returns a non-sensitive payload. It intentionally does not expose
full filesystem paths, credentials, JWT secrets, admin passwords, or connection
strings.

Example healthy shape:

```json
{
  "status": "ok",
  "service": "api",
  "checks": {
    "app_database": {
      "backend": "sqlite",
      "database_name": "app.db",
      "configured": true,
      "reachable": true,
      "message": "App metadata database is reachable."
    },
    "auth_configuration": {
      "jwt_secret_configured": true,
      "admin_credentials_configured": true,
      "admin_password_hash_configured": true,
      "plaintext_admin_password_configured": false,
      "message": "Login bootstrap configuration is present.",
      "issues": [],
      "safe_next_actions": ["Sign in with the configured local admin account."]
    },
    "default_book": {
      "configured": true,
      "exists": true,
      "readable": true,
      "filename": "main.gnucash.sqlite",
      "parent_exists": true,
      "message": "Default GnuCash book file is present."
    },
    "writes_enabled": false
  }
}
```

`status: degraded` means the API process is running but at least one required
runtime check needs attention. Common first-run causes are a missing/unreadable
default book file, placeholder JWT secret, missing admin bootstrap credential, or
an unreachable app metadata DB.

## Missing or unreadable default book

If the health endpoint shows:

```text
Default GnuCash book file is missing or not mounted. Check GNUCASH_DEFAULT_BOOK_PATH and the books volume.
```

Check these items locally without sharing the real path publicly:

1. `GNUCASH_DEFAULT_BOOK_PATH` points to the intended file inside the container,
   usually under `/data/books/`.
2. The Docker Compose volume mounts your local `data/books/` directory into the
   API container.
3. The file is a copied/test GnuCash SQL book, not your only real book.
4. The filename in the health response matches the file you expected.
5. The parent directory exists (`parent_exists: true`). If it is false, the
   books volume is probably not mounted where the app expects it.

Safe local checks:

```bash
docker compose ps
docker compose exec api sh -lc 'ls -l /data/books && test -f "$GNUCASH_DEFAULT_BOOK_PATH"'
```

Do not paste the resulting real filenames publicly if they reveal personal data.
Use a generic description or rename the copied test file first.

If the health endpoint says the file exists but is not readable, keep the same
book path and fix host/container ownership or read permissions. The health
payload intentionally returns only the filename and generic permission guidance,
not the full host path.

## Placeholder JWT secret or missing admin bootstrap credential

If `/login` reports an operator-fixable configuration problem, check
`checks.auth_configuration` in `/health`.

For a missing or placeholder JWT secret:

1. Set `JWT_SECRET` to a long random value in the local `.env` or deployment
   environment.
2. Do not use placeholder values from `.env.example`.
3. Restart the service after changing the value.

For a missing first-admin bootstrap credential:

1. Prefer `APP_ADMIN_PASSWORD_HASH` for durable deployments.
2. `APP_ADMIN_PASSWORD` is accepted as a local bootstrap convenience and is
   hashed before storage.
3. Restart after setting the credential. For disposable local testing only,
   recreate the ignored app metadata DB if the first-run seed already ran with
   incomplete settings.

The health endpoint and startup logs report boolean/config-key diagnostics only.
They must not include JWT secret values, admin passwords, password hashes, or
full `.env` contents.

## App metadata DB not reachable

If `checks.app_database.reachable` is `false`:

1. Confirm the app data volume exists and is writable by the API container.
2. Confirm `APP_DATABASE_URL` is set to the intended app metadata DB, not a
   GnuCash book.
3. Restart the API after fixing the volume or environment.

Safe local checks:

```bash
docker compose exec api sh -lc 'test -d /data/app && test -w /data/app'
docker compose logs api --tail=100
```

The health endpoint exposes only the database backend and database filename for
SQLite. It must not expose connection strings or credentials.

## Startup diagnostics logs

On startup, the API logs one structured diagnostics event named
`startup_diagnostics`. It includes:

- app environment;
- overall health status;
- app DB reachability;
- default book configured/existence/readability status;
- default book filename only, not the full path;
- whether write mode is enabled.

It must not include JWT secrets, admin passwords, `.env` values, full book paths,
full database URLs, or credentials.

Useful command:

```bash
docker compose logs api --tail=200 | grep startup_diagnostics
```

If you share logs in an issue, review them manually first and remove any local
hostnames, usernames, paths, or filenames you consider private.

## Authentication or UI problems

1. Confirm the API process is healthy or only degraded because of a known missing
   copied book.
2. Confirm `JWT_SECRET` is set to a long random value and is not the placeholder
   from `.env.example`.
3. Confirm one admin bootstrap credential is configured:
   `APP_ADMIN_PASSWORD_HASH` is preferred; `APP_ADMIN_PASSWORD` is development
   convenience only.
4. Confirm browser auth uses httpOnly cookies; do not store tokens in
   localStorage/sessionStorage.

## What to include in bug reports

Include:

- project version or commit SHA;
- whether Docker or local development mode is used;
- sanitized `/api/health` payload;
- sanitized `startup_diagnostics` log line;
- which screen/API call failed;
- whether the book is a synthetic/test copy.

Do not include:

- `.env` contents;
- JWT secrets, passwords, tokens, keys, or certificates;
- real GnuCash books, app DBs, backups, screenshots, or exports;
- real financial account names or transaction descriptions;
- full private filesystem paths if they reveal personal information.

## What this diagnostics work does not guarantee

These checks are operational smoke diagnostics for a pre-alpha app. They are not
a production monitoring system, security audit, backup system, or guarantee that
a GnuCash book is semantically compatible with every feature.
