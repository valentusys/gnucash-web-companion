# gnucash-web-companion

> **Status: pre-alpha / MVP in progress** — This project is under active early development. It is not yet feature-complete or production-ready.

A modern, self-hosted web companion for existing [GnuCash](https://www.gnucash.org/) books. Open your book in a browser, browse accounts, search transactions, and view dashboards and reports — without modifying your data.

## What it is

- A **read-first** web application that connects to an existing GnuCash book (via [piecash](https://github.com/sdementen/piecash)) and exposes a clean, modern UI.
- A **self-hosted** service: you deploy it on your own infrastructure. Your financial data never leaves your server.
- A **companion**, not a replacement: GnuCash desktop remains the authoritative editor for your book.

## What it is not

- It is **not** a GnuCash replacement.
- It is **not** a hosted personal-finance SaaS.
- It is **not** a collaborative multi-user accounting editor.
- It does **not** write to your GnuCash book in the MVP (v0.1).

## Current status

| Milestone | Status |
|---|---|
| Phase 0 — Competitive review & product positioning | ✅ Complete |
| Phase 1 — Open-source foundation (this release) | ✅ Complete |
| Phase 2 — Project skeleton (SvelteKit + FastAPI + Docker) | ✅ Complete |
| MVP v0.1 — Read-only browsing, dashboards, reports | ⬜ Planned |

## MVP v0.1 scope (read-only)

The first milestone is **read-only**. Planned features:

- Connect to one configured GnuCash book (SQLite via piecash).
- Open the book in read-only mode.
- Display book metadata and health status.
- Account hierarchy with balances.
- Account detail with splits/transactions.
- Transaction detail pages.
- Search and filter transactions.
- Dashboard: net worth, income vs. expenses, cash flow, top expense categories.
- Privacy mode (blur sensitive numbers).
- Clear indicators that the book is read-only.
- Docker/self-host deployment.

**Explicitly out of scope for v0.1:** writes, transaction creation/editing, multi-book UI, collaborative editing, invoice/bill management, direct GnuCash schema modification.

## ⚠️ Safety warning

GnuCash books contain high-trust accounting data. This project:

- Opens your book **read-only** in MVP.
- Stores app metadata (preferences, saved filters, cache state) in a **separate** database.
- Never modifies the GnuCash schema.

**Nevertheless:** always maintain regular backups of your GnuCash files. Do not point this app at your only copy of a book. See [docs/GNUCASH_SAFETY.md](docs/GNUCASH_SAFETY.md) for details.

## Quick start

> 🚧 This is a pre-alpha project. The Docker-based quick start below assumes you have a [Docker Engine](https://docs.docker.com/engine/) installed.

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
docker compose up --build
```

- Frontend: <http://localhost:8080>
- API health: <http://localhost:8080/api/health>

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed setup instructions.

## Architecture

> Architecture is documented at a foundation level in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Phase 2 adds only the runnable shell; GnuCash data access is deferred to Phase 3.

Planned stack:

- **Frontend:** SvelteKit
- **Backend:** FastAPI (Python)
- **GnuCash access:** piecash
- **App metadata DB:** SQLite (separate from the GnuCash book)
- **Deployment:** Docker / docker-compose

## Roadmap

> 🚧 See [docs/ROADMAP.md](docs/ROADMAP.md) for the full roadmap.

Short-term:

1. Phase 2: Project skeleton, Docker dev environment, sample fixtures.
2. Phase 3: Read-only API endpoints, piecash integration, safety tests.
3. Phase 4: UI shell, dashboard, account browsing, search.
4. v0.1 release: Read-only MVP.

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, branch/PR guidelines, and how to respect the read-only MVP boundary.

## Funding

> 🚧 This project is not yet funded. If you find it valuable, consider supporting development:

- GitHub Sponsors: *not yet configured*
- Open Collective: *not yet configured*
- Ko-fi: *not yet configured*

See [.github/FUNDING.yml](.github/FUNDING.yml) for current funding links.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see [LICENSE](LICENSE) for the full text.

### Why AGPL-3.0?

`gnucash-web-companion` is designed to be self-hosted as a web application. The AGPL-3.0 ensures that:

1. **Modifications shared over the network stay open.** If you host a modified version of this app for others to use (even as a service), you must make your source code available under the same license. This protects the open-source nature of the project in the self-hosted/web-app context.
2. **It aligns with GnuCash itself**, which is licensed under GPL-3.0. AGPL-3.0 is a natural fit for a companion project that extends GnuCash into the web.
3. **It keeps the project free and open** for individuals, communities, and self-hosting enthusiasts.

### Not legal advice

The above is an explanation of the project's licensing rationale, not legal advice. If you have questions about how AGPL-3.0 applies to your specific situation, consult a qualified legal professional.
