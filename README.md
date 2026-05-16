# gnucash-web-companion

> **Status: pre-alpha / MVP in progress** — this repository is suitable for review and experimentation, but it is not feature-complete, audited, or production-ready.

A modern, self-hosted web companion for existing [GnuCash](https://www.gnucash.org/) books. It is designed to browse accounts, transactions, dashboards, and basic reports in a browser while keeping GnuCash Desktop as the authoritative editor.

## What it is

- A **read-only-first** web application for existing GnuCash SQL books, accessed through [piecash](https://github.com/sdementen/piecash).
- A **self-hosted** app you run on your own infrastructure.
- A **companion**, not a replacement: GnuCash Desktop remains the source of truth for editing.
- **Single-book by default**, with internal service boundaries that keep later multi-book support possible.

## What it is not

- It is **not** a GnuCash replacement.
- It is **not** a hosted personal-finance SaaS.
- It is **not** true collaborative multi-user accounting.
- It does **not** write to your GnuCash book by default.
- It does **not** provide any production-readiness or security guarantee yet.

## Current status

- Phase 0–14 are complete.
- MVP v0.1 remains **read-only by default**.
- Controlled-write code, if present in the repository, is experimental post-MVP work and disabled by default.
- First public pre-alpha release candidate: `v0.0.1-prealpha`.

## MVP scope: read-only first

The first public milestone is intentionally conservative:

- Connect to one configured GnuCash SQL book.
- Open the book in read-only mode.
- Show account hierarchy and balances.
- Browse account detail and transaction detail.
- Search/filter transactions with pagination.
- Show basic dashboard reports: net worth, income/expense, cash flow, top expense categories.
- Store application metadata in a separate app database, not inside the GnuCash book.
- Provide Docker/self-host deployment scaffolding.

Explicitly out of scope for the MVP:

- Transaction/account creation or editing enabled by default.
- Direct GnuCash schema modification.
- Invoice, bill, customer, or vendor editing.
- True collaborative multi-user editing.
- Family shared-wallet baseline.
- Multi-book management UI as a core baseline.
- Hosted SaaS operation.
- Fake currency conversion.

## Safety warning

GnuCash books contain sensitive accounting data. This project is read-only-first, but early software can still have bugs and operational risks.

Use it safely:

- **Use a test copy of your book first.** Do not point pre-alpha builds at your only copy.
- Maintain regular, tested backups of all GnuCash files.
- Do not commit `.gnucash`, `.sqlite`, backups, `.env`, or secrets to the repository.
- Do not expose early builds directly to the public internet.
- Review [docs/GNUCASH_SAFETY.md](docs/GNUCASH_SAFETY.md) before testing with real data.

## Experimental write code

This repository may contain experimental post-MVP controlled-write code. It is disabled by default with:

```text
GNUCASH_WRITES_ENABLED=false
```

Controlled writes are not part of MVP v0.1. Do not enable write mode against your only copy of a GnuCash book. See [docs/v0.2-controlled-writes.md](docs/v0.2-controlled-writes.md) for the design and safety requirements.

## Quick start

> This is a pre-alpha quick start. It assumes Docker Engine and Docker Compose are installed. Docker runtime has not been certified for production use.

```bash
git clone https://github.com/valentusys/gnucash-web-companion.git
cd gnucash-web-companion
cp .env.example .env
# Edit .env: set a real JWT_SECRET, admin bootstrap password/hash, and GNUCASH_DEFAULT_BOOK_PATH.
# The placeholder JWT_SECRET in .env.example is intentionally rejected by the API.
# Keep GNUCASH_WRITES_ENABLED=false for the read-only MVP.
# Put only a test copy of your GnuCash SQL book under data/books/.
docker compose up --build
```

Default local URLs:

- Web UI: <http://localhost:8080>
- API health via proxy: <http://localhost:8080/api/health>

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for local development setup.

## Architecture

- **Frontend:** SvelteKit in `apps/web/`
- **Backend:** FastAPI in `apps/api/`
- **GnuCash access:** piecash opened read-only behind a service layer
- **App metadata DB:** separate SQLite database (`app.db`) for users, book registry, access metadata, and audit logs
- **Deployment:** Docker Compose with Caddy reverse proxy

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Release readiness

The first public pre-alpha tag is planned as:

```text
v0.0.1-prealpha
```

Release checklist and notes:

- [docs/release/v0.0.1-prealpha-checklist.md](docs/release/v0.0.1-prealpha-checklist.md)
- [docs/release/v0.0.1-prealpha-notes.md](docs/release/v0.0.1-prealpha-notes.md)

Do not publish npm or PyPI packages unless explicitly requested.

## Repository description and topics

Suggested GitHub repository description:

> Modern self-hosted read-only web companion for GnuCash books, built with SvelteKit, FastAPI, and piecash.

Suggested topics:

- `gnucash`
- `personal-finance`
- `accounting`
- `self-hosted`
- `sveltekit`
- `fastapi`
- `open-source`
- `finance`
- `sqlite`

## Screenshots

Screenshots are not included yet. The README intentionally does not promise a polished UI until the MVP has completed integration testing.

## Contributing

Contributions are welcome, especially documentation, tests, safety review, and read-only UX improvements. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## Funding

This project is not yet funded. See [.github/FUNDING.yml](.github/FUNDING.yml) for current funding metadata/placeholders.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see [LICENSE](LICENSE).

### Why AGPL-3.0?

`gnucash-web-companion` is a self-hosted web application. AGPL-3.0 keeps modifications shared over a network open, aligns well with GnuCash's GPL-3.0 license family, and preserves the project as free/open software.

This licensing summary is not legal advice.
