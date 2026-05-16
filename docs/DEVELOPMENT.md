# Development

> Status: placeholder. Detailed setup will be added when Phase 2 creates the SvelteKit/FastAPI skeleton.

## Repository layout

- `apps/web/` — planned SvelteKit frontend.
- `apps/api/` — planned FastAPI backend.
- `docs/` — product, architecture, security, and handoff docs.
- `docker/` — planned Docker/dev infrastructure.
- `data/` — local development data directory; real data files must not be committed.

## Expected local setup

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
# edit .env for your local paths
```

App startup commands will be added after the project skeleton exists.

## Development principles

- Respect the read-only MVP boundary.
- Keep app metadata separate from GnuCash books.
- Use tests for any data-access logic.
- Do not commit secrets or real financial data.
- Prefer small focused PRs.

## Future checks

CI is currently a non-breaking skeleton. Later it should run:

- frontend lint and typecheck
- backend tests
- formatting checks
- security/dependency checks
