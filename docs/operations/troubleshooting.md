# Troubleshooting

This guide is for self-hosted pre-alpha deployments of `gnucash-web-companion`.
It focuses on safe diagnostics only: do not paste secrets, `.env` contents, real
GnuCash books, app databases, backups, real screenshots, or real exports into
public issues.

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
runtime check needs attention. The most common cause is a missing or unmounted
default book file.

## Missing default book

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
