# Phase 2 Handoff: Project Skeleton

## Status

Phase 2 created a runnable monorepo skeleton with SvelteKit, FastAPI, Docker Compose, and a Caddy reverse proxy.

No business features were implemented. No auth, account, transaction, piecash, app metadata schema, or GnuCash data-access code was added.

## Created / updated files

### Backend (`apps/api/`)

- `app/main.py` — FastAPI application with CORS middleware and `/health` endpoint.
- `app/config.py` — Pydantic Settings module reading `APP_ENV`, `APP_DATABASE_URL`, `GNUCASH_DEFAULT_BOOK_PATH`, `JWT_SECRET`, `CORS_ORIGINS`.
- `app/__init__.py` — package marker.
- `tests/test_health.py` — pytest for the health endpoint.
- `tests/__init__.py` — package marker.
- `pyproject.toml` — Python project metadata and dependencies.
- `requirements.txt` — dependencies for local/dev Docker installs.
- `Dockerfile` — Python 3.12 slim image running uvicorn on port 8000.

### Frontend (`apps/web/`)

- `package.json` — SvelteKit + TypeScript + Tailwind CSS v4 tooling.
- `svelte.config.js` — Node adapter configuration.
- `tsconfig.json` — strict TypeScript config extending SvelteKit generated config.
- `vite.config.ts` — Vite with SvelteKit and Tailwind plugins.
- `src/app.html` — base HTML shell.
- `src/app.css` — Tailwind import.
- `src/app.d.ts` — SvelteKit types.
- `src/routes/+layout.svelte` — imports global CSS.
- `src/routes/+page.svelte` — main page displaying “GnuCash Web Companion” and “Frontend is running”.
- `src/lib/api/index.ts` — minimal API client helper.
- `src/lib/components/.gitkeep` — placeholder for future components.
- `src/lib/styles/.gitkeep` — placeholder for future style modules.
- `Dockerfile` — multi-stage build serving SvelteKit via Node on port 3000.

### Docker & Proxy

- `docker-compose.yml` — three services: `api`, `web`, `proxy`.
- `docker/Caddyfile.docker` — Caddy config routing `/api/*` to `api:8000` with path stripping, and everything else to `web:3000`.
- `docker/Caddyfile` — local host-network variant for optional manual Caddy runs.

### Configuration

- `.env.example` now includes:
  - `APP_ENV=development`
  - `APP_DATABASE_URL=sqlite:////data/app/app.db`
  - `GNUCASH_DEFAULT_BOOK_PATH=/data/books/main.gnucash.sqlite`
  - `JWT_SECRET=change-me`
  - `PUBLIC_APP_NAME=GnuCash Web Companion`
  - `API_INTERNAL_URL=http://api:8000`
  - `CORS_ORIGINS=["*"]`

### Docs and CI

- `README.md` — Phase 2 marked complete and quickstart updated with real Docker commands.
- `docs/DEVELOPMENT.md` — Docker/local development setup, environment variables, health check info, CI checks.
- `.github/workflows/ci.yml` — now runs frontend `npm run check`/`npm run build`, backend `pytest`, and compose validation where Docker exists.

## Architecture decisions

- **Caddy over nginx:** simpler reverse proxy config and easy future HTTPS support.
- **Caddy `handle_path /api/*`:** external `/api/health` maps to backend `/health` without requiring backend `/api` prefix.
- **SvelteKit node adapter:** Docker image serves the frontend as a Node process on port 3000.
- **Tailwind CSS v4:** integrated via the Vite plugin and `@import "tailwindcss"`.
- **FastAPI settings module:** config reads required environment variables now but does not use them for business features yet.
- **No piecash connection:** deferred to Phase 3.
- **No app metadata DB schema:** deferred until explicitly planned.

## Acceptance criteria status

- `docker compose up --build` launches: configured, but not executed in this environment because Docker is not installed on the runner.
- `/` through proxy: configured as `http://localhost:8080/`; frontend was locally built and served directly on port 3000 for verification.
- `/api/health` through proxy: configured as `http://localhost:8080/api/health`; backend was locally run and verified directly at `http://127.0.0.1:8000/health` returning `{ "status": "ok", "service": "api" }`.
- README updated: yes.
- DEVELOPMENT updated: yes.
- `docs/handoff/phase-2.md` created: yes.

## Verification performed

- `npm install` in `apps/web/`.
- `npm run check` in `apps/web/` — passed.
- `npm run build` in `apps/web/` — passed.
- `node build` in `apps/web/` — served page locally.
- `curl http://127.0.0.1:3000/` — confirmed page contains “GnuCash Web Companion” and “Frontend is running”.
- Python virtualenv install in `apps/api/`.
- `pytest -q` in `apps/api/` — passed.
- `uvicorn app.main:app --host 127.0.0.1 --port 8000` — served API locally.
- `curl http://127.0.0.1:8000/health` — returned expected health JSON.
- YAML parsing for `docker-compose.yml` and GitHub workflow files — passed.

## What still needs Docker-side validation

Run this on a machine with Docker Engine/Compose available:

```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8080/
curl http://localhost:8080/api/health
```

Expected API response:

```json
{"status":"ok","service":"api"}
```

## Recommended next phase

Phase 3 should stay read-only and safety-focused:

1. Validate piecash can open the configured GnuCash book path read-only.
2. Add fixture/sample-book strategy without committing real financial data.
3. Define exact amount representation for API responses.
4. Add read-only book/account endpoint contracts.
5. Add tests proving read operations do not mutate fixture books.
