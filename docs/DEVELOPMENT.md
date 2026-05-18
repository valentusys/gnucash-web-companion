# Development

> Detailed setup for the project development environment.

## Repository layout

```text
apps/
  web/          SvelteKit frontend (served by Node in production)
  api/          FastAPI backend (uvicorn)
data/           Local development data directory
docker/         Docker and proxy configuration
docs/           Product, architecture, security, and handoff docs
```

## Quick start (Docker)

Prerequisites: Docker Engine and Docker Compose.

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
docker compose up --build
```

The application will be available at:

- **Frontend:** <http://localhost:8080>
- **API health:** <http://localhost:8080/api/health>

## Local development (without Docker)

### Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

## Environment variables

See `.env.example` for the full list of configuration options.

| Variable                    | Description                                   |
|-----------------------------|-----------------------------------------------|
| `APP_ENV`                   | Application environment (development/prod)    |
| `APP_DATABASE_URL`          | SQLAlchemy-compatible app metadata DB URL     |
| `GNUCASH_DEFAULT_BOOK_PATH` | Path to the GnuCash SQLite book file          |
| `JWT_SECRET`                | Secret key for JWT signing                    |
| `JWT_TOKEN_EXPIRE_MINUTES`  | Access token lifetime in minutes             |
| `APP_ADMIN_USERNAME`        | Bootstrap admin username                     |
| `APP_ADMIN_PASSWORD`        | Plaintext bootstrap password; dev only       |
| `APP_ADMIN_PASSWORD_HASH`   | Preferred bootstrap bcrypt password hash     |
| `PUBLIC_APP_NAME`           | Public display name for the app               |
| `API_INTERNAL_URL`          | Internal URL the proxy uses to reach the API  |
| `CORS_ORIGINS`              | JSON list of allowed CORS origins             |

## Health check

The API exposes a non-sensitive health endpoint:

```text
GET /api/health
```

The response includes `status`, `service`, and safe checks for app metadata DB
reachability, CORS deployment posture, default book presence, and whether experimental writes are enabled.
It intentionally avoids full filesystem paths, credentials, JWT secrets, admin
passwords, and database connection strings. See
[docs/operations/troubleshooting.md](operations/troubleshooting.md) for example
payloads and troubleshooting steps.

If `CORS_ORIGINS` contains `*` while `APP_ENV` is not development-like, health
and startup diagnostics include a non-secret warning. Keep `CORS_ORIGINS=["*"]`
for local development only; for shared LAN/VPN testing, use exact origins such
as `CORS_ORIGINS=["http://gnucash.lan:8080"]` or
`CORS_ORIGINS=["https://gnucash.vpn.example"]`.

## Development principles

- Respect the read-only MVP boundary.
- Keep app metadata separate from GnuCash books.
- Use tests for any data-access logic.
- Do not commit secrets or real financial data.
- Prefer small focused PRs.

## CI checks

CI now runs foundation checks plus real skeleton checks when app manifests exist:

- frontend install, `npm run check`, and `npm run build`
- backend dependency install and `pytest`
- Docker Compose file validation

Future phases should add lint/format enforcement and security/dependency checks.
