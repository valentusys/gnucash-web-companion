# Competitive Review: GnuCash Web Companion

Reviewed on: 2026-05-16

## Executive summary

The existing ecosystem confirms that there is demand for browser/mobile access to GnuCash data, but no reviewed project is the right baseline for `gnucash-web-companion`.

Most projects fall into one of four buckets:

- **Mobile write companion**: `joshuabach/gnucash-web` is the closest conceptual neighbor, but it is intentionally simple, Flask/Bootstrap-based, and write-capable from the start.
- **Rich client-side dashboard/editor**: `QuirkyTurtle94/GnuDash` has the strongest modern UI patterns, but it is Next.js/browser-WASM oriented and has a much broader editing/export engine than our desired safety-first MVP.
- **REST API wrapper**: `loftx/gnucash-rest` has useful resource shapes and JSON API vocabulary, but it depends on GnuCash Python bindings and exposes many write endpoints.
- **Low-code/static/prototype approaches**: `gnucash-2-web`, `gnucash-browser`, and `GnuCashew` are useful references but not reusable foundations for a modern FastAPI/SvelteKit product.

The main product lesson: **start read-only**. GnuCash data files encode accounting invariants, decimal/rational precision, book-level locking expectations, and backend-specific behavior. A web companion should first earn trust by safely browsing, searching, filtering, and reporting over existing books before writing anything back.

## Comparison matrix

| Project | What it does | Stack | GnuCash data access | Writes? | Auth | Mobile | Deployment | Activity signal | Fit as foundation |
|---|---|---|---|---|---|---|---|---|---|
| `joshuabach/gnucash-web` | Self-hosted mobile-friendly companion for browsing accounts and adding/editing simple transactions | Python, Flask, piecash, Bootstrap, WSGI/Gunicorn, Docker | Opens one GnuCash database via piecash; supports sqlite3, PostgreSQL, MySQL/MariaDB | Yes: add/edit/delete two-split transactions; price DB CLI | `None` or DB credential pass-through stored in encrypted session cookie | Explicitly mobile-friendly | PyPI, WSGI, Docker, docker-compose | Active-ish but author states it is personal/beta and simplicity-first; 165 stars, 35 open issues, last push 2024-05-16 | Strong lessons, not a foundation |
| `QuirkyTurtle94/GnuDash` | Modern personal finance dashboard and browser-based editor for GnuCash data | Next.js 16, TypeScript, React 19, Tailwind, shadcn/ui, Recharts/ECharts, SQLite WASM, OPFS, optional Node/Postgres | Browser imports `.gnucash` SQLite/XML/gzip into SQLite WASM/OPFS; optional Postgres backend/schema | Yes for SQLite/client engine; XML read-only; export modified `.gnucash` | Static local mode has no server auth; optional self-hosted server mode | Strong modern responsive dashboard patterns | Static CDN/export; standalone Node.js; Docker compose; Cloudflare/Vercel/Netlify/Coolify docs | Very active; 74 stars, last push 2026-05-01, issues around numeric precision/docs/import/reporting | Best UI inspiration, but architecture differs |
| `loftx/gnucash-rest` | REST API for extracting and manipulating GnuCash data | Python, Flask, WSGI, native GnuCash Python bindings | Uses `gnucash` Python bindings and connection string to GnuCash DB | Yes: transactions, bills, invoices, entries, customers, vendors; GET/POST/DELETE/PAY | No clear built-in app auth in README; WSGI/server expected to handle environment | API only | WSGI/Apache example; separate Docker test repo exists | Some maintenance; 62 stars, last push 2025-03-24, 2 open issues | Useful API vocabulary, not product foundation |
| `lorimark/gnucashew-dev` / GnuCashew | Web-based accounting system compatible with GnuCash data files | C++, Wt web toolkit, custom app, Docker sibling repo | Attempts direct compatibility with GnuCash data files; explicitly not using GnuCash code | Appears intended to write; public demo persists edits | Demo access; auth model not central in README | Web UI, mobile not emphasized | Demo site and `gnucashew-docker` sibling repo | Active; 6 stars, last push 2026-04-20 | Interesting ambition, but different stack/product |
| `jam-py-v5/gnucash-2-web` | Low-code Jam.py web interface over a GnuCash database | Jam.py, Python 3.8+, generated/low-code app, JavaScript repo | Direct DB access; Jam.py supports DB formats except XML; schema informed by piecash docs | Potentially yes; README warns Jam.py can modify database structure | Jam.py platform conventions; not product-defined | Web access, mobile not central | Run `server.py`; PythonAnywhere/self-host/Raspberry Pi possible | New/WIP; 8 stars, last push 2026-02-13 | Useful cautionary reference, not reusable |
| `phjardas/gnucash-browser` | Static read-only website generated from a GnuCash book | Gatsby/JavaScript/Node | Build-time reads configured GnuCash file and generates static site | No; read-only static output | Static hosting only; auth delegated to web server if any | Browser UI, no explicit mobile focus | `npm run build`, deploy `public/` to any web server | Stale/small; 1 star, last push 2022-12-03 | Validates read-only browsing, but too static |

## Project reviews

### 1. `joshuabach/gnucash-web`

Repository: <https://github.com/joshuabach/gnucash-web>

#### What it does

`gnucash-web` is a simple self-hosted GnuCash web interface. Its primary stated use case is adding simple two-split transactions on the go, for example recording a cash expense from a phone. It also supports browsing the account hierarchy, viewing transaction history and balances, recycling common transactions, and updating commodity prices via CLI.

#### Stack

- Python
- Flask
- piecash
- Bootstrap
- WSGI/Gunicorn
- Docker/docker-compose
- PyPI package

#### GnuCash data model

It opens a single pre-existing GnuCash database through piecash. Supported database backends are sqlite3, PostgreSQL, MySQL, and MariaDB. It does not create a full book/account hierarchy itself; the README expects the user to create/populate the book with the official GnuCash desktop app or piecash first.

#### Write operations

Yes. It can add, edit, and delete two-split transactions. It also has a CLI for price updates. This is useful but raises the safety bar immediately.

#### Auth, mobile, deployment

- Auth: supports `None` and `passthrough`. Pass-through prompts for database credentials and stores them encrypted in a browser session cookie.
- Mobile: explicitly optimized for mobile ease of use.
- Deployment: PyPI, WSGI configuration, Docker image/package, docker-compose examples including SQLite and PostgreSQL.

#### What to borrow

- The **companion, not replacement** framing.
- Single-book operational simplicity.
- Explicit warning that the desktop app remains the canonical tool for creating/managing the book.
- Mobile-first transaction/account navigation ideas.
- Docker/self-host deployment examples.
- Clear configuration via environment variables.

#### What to avoid

- Starting the MVP with writes enabled.
- Treating two-split transaction editing as “simple enough” without a broader safety model.
- Pass-through DB credentials in browser cookies as the main long-term auth story.
- Tight coupling between product scope and one maintainer’s personal workflow.

#### Activity and risks

The repo is not archived and still has community attention, but the README explicitly says the project is beta/personal and that the maintainer does not expect much development unless it fits his workflow. Open issues include Docker/runtime friction and deployment/subpath concerns. That suggests a real-world self-hosting pain surface.

Important safety lessons:

- If writes exist, every deployment mistake becomes data-corruption risk.
- Database exposure warnings matter; exposing DB ports for remote desktop access is dangerous.
- “Simple transaction entry” is still accounting write logic.
- The app should make backup/locking/read-only mode explicit, not implicit.

### 2. `QuirkyTurtle94/GnuDash`

Repository: <https://github.com/QuirkyTurtle94/GnuDash>

#### What it does

`GnuDash` is a modern dashboard for GnuCash users. It lets users upload a `.gnucash` SQLite or XML file, explore dashboards and reports, manage accounts/transactions in browser, and export modified files. It also has an optional self-hosted Postgres backend for cross-device access.

#### Stack

- Next.js 16 App Router
- TypeScript
- React 19
- Tailwind CSS
- shadcn/ui / Base UI
- Recharts and ECharts for visualization
- SQLite WASM in a Web Worker
- OPFS for browser persistence
- optional Node.js standalone server and Postgres backend
- Vitest and Playwright

#### GnuCash data model

The default static mode reads a user-selected `.gnucash` file in the browser using the File API. It detects SQLite/XML/gzip variants, loads SQLite into SQLite WASM, and persists a local copy in OPFS. XML is read-only. SQLite mode includes a write engine with GnuCash-compatible export.

Optional server mode can mirror a book into a dedicated Postgres schema. It can also point at an existing GnuCash desktop Postgres DB in read-only mode.

#### Write operations

Yes. GnuDash supports transaction editing, account management, investment transactions, price/budget/lot operations, and export. It emphasizes rational arithmetic and double-entry invariants. However, its own open issue #62 (“Exact numeric reporting vs 'good enough' floats”) shows precision remains an important risk even in a modern implementation.

#### Auth, mobile, deployment

- Auth: local static mode has no server and therefore no server auth; data never leaves browser. Server mode requires normal self-hosting controls but README does not position auth as the core product primitive.
- Mobile: modern responsive dashboard design, but not specifically a “phone quick entry” product.
- Deployment: static export to any static host; standalone Node.js server; Docker compose; docs for Cloudflare Pages, Vercel, Netlify, Coolify, Synology, reverse proxy/TLS.

#### What to borrow

UI patterns worth borrowing:

- Dashboard-first information architecture.
- Account tree with balances and account type indicators.
- Drill-down from charts into underlying transactions.
- Sankey diagrams for income/expense/cash-flow flows.
- Net-worth, cash-flow, budget, and investment pages as separate mental models.
- GnuCash-style transaction register in a tabbed interface.
- Privacy mode that blurs sensitive numbers.
- Demo/sample mode for onboarding.
- Clear “your data never leaves your device/server” trust messaging.
- Explicit read-only treatment for formats/modes where safe writes are not guaranteed.

#### What to avoid

- Copying the browser-WASM architecture when our target is self-hosted FastAPI + piecash.
- Making write/export engine scope part of MVP.
- Adding Postgres synchronization/cross-device sharing before a server-side book safety model exists.
- Allowing the UI richness to obscure accounting correctness.

#### Activity and risks

GnuDash is very active and visually/product-wise the strongest reference. Its breadth is also the warning: dashboards, editing, export, local OPFS persistence, optional server sync, investments, budgets, and custom reports quickly become a large accounting engine.

Key risks to learn from:

- Exact numeric reporting matters.
- Client/server storage modes multiply product complexity.
- Import/export flows create user expectations that the app is a full GnuCash replacement.

### 3. `loftx/gnucash-rest`

Repository: <https://github.com/loftx/gnucash-rest>

#### What it does

`gnucash-rest` exposes GnuCash data as JSON over a REST-like Flask API. It covers accounts, transactions, splits, customers, vendors, invoices, bills, entries, and payments.

#### Stack

- Python
- Flask
- WSGI
- native GnuCash Python bindings (`gnucash`, `gnucash_business`)
- Apache WSGI example

#### GnuCash data model

It opens a GnuCash session using native GnuCash Python bindings and a connection string such as MySQL. The README recommends recent GnuCash builds with Python bindings and warns some functions depend on GnuCash version/binding availability.

#### Write operations

Yes. It includes write endpoints for creating/editing/deleting transactions, bills, invoices, entries, customers, vendors, and marking bills/invoices paid. It also uses a custom `PAY` request method, which is not a mainstream HTTP method.

#### Auth, mobile, deployment

- Auth: no clear built-in product auth documented; production deployment is expected behind WSGI/Apache controls.
- Mobile: API only.
- Deployment: WSGI app with Apache sample; separate docker test repo exists.

#### What to borrow

API shapes worth borrowing conceptually:

- Resource-oriented endpoints: `/accounts`, `/accounts/{guid}`, `/accounts/{guid}/splits`, `/transactions/{guid}`.
- Stable GnuCash GUIDs as primary identifiers in API paths.
- JSON-first representation for integration/UI consumers.
- Query filters for business resources by state/date (`is_paid`, `is_active`, date ranges).
- Separate account, split, transaction, customer/vendor/invoice/bill resources.

For our MVP, adapt these into a safer read-only FastAPI shape:

- `GET /api/book/summary`
- `GET /api/accounts`
- `GET /api/accounts/{guid}`
- `GET /api/accounts/{guid}/splits`
- `GET /api/transactions/{guid}`
- `GET /api/reports/net-worth`
- `GET /api/reports/cash-flow`
- `GET /api/search?q=...`

#### What to avoid

- Exposing write endpoints before safety model, backups, locking, and tests are mature.
- Custom HTTP verbs like `PAY`; prefer standard POST subresources later, e.g. `POST /invoices/{id}/payments`.
- Binding the project to native GnuCash Python bindings if piecash can satisfy read-only MVP needs more cleanly.
- Publishing a broad API before versioning and compatibility semantics are known.

#### Activity and risks

The project has modest activity and a small issue queue. Important risk: it exposes a lot of mutable accounting/business operations with minimal documented auth/deployment hardening.

### 4. `lorimark/gnucashew-dev` / GnuCashew

Repository: <https://github.com/lorimark/gnucashew-dev>

#### What it does

GnuCashew is a web-based accounting system compatible with GnuCash data files. It explicitly says it is not GnuCash and does not use GnuCash code. It appears to be an attempt to build a web app that can read/write compatible data while adding features such as managed bill pay.

#### Stack

- C++
- Wt web toolkit
- custom codebase
- Docker sibling project (`lorimark/gnucashew-docker`)
- public demo

#### GnuCash data model

The README describes direct compatibility with GnuCash data files and an initial desire to hook into the GnuCash codebase, but then pursuing the problem from the “other side” due to GnuCash code complexity.

#### Write operations

Likely yes. The public demo uses a generic sqlite file and says entries put there will remain. The project ambition is a web accounting system, not a read-only viewer.

#### Auth, mobile, deployment

- Auth: not emphasized in README.
- Mobile: not emphasized.
- Deployment: demo site and Docker sibling repo.

#### What to borrow

- Respect for the complexity of the GnuCash codebase and data model.
- The idea that compatibility is hard enough to be its own product risk.
- Doxygen/source documentation practices may be useful later if we build complex domain modules.

#### What to avoid

- Reimplementing a full accounting system.
- Letting “compatible with GnuCash” become “replacement for GnuCash.”
- Choosing an uncommon stack for this project’s expected contributor/user base.

#### Activity and risks

Active but small. The project is more ambitious than our target and uses a completely different technology stack.

### 5. `jam-py-v5/gnucash-2-web`

Repository: <https://github.com/jam-py-v5/gnucash-2-web>

#### What it does

`gnucash-2-web` is a Jam.py low-code web interface for a GnuCash database. It is inspired by `gnucash-web` and aims to provide quick web access to a GnuCash database.

#### Stack

- Jam.py
- Python >3.8
- generated/low-code web app
- JavaScript repository artifacts

#### GnuCash data model

It points Jam.py at GnuCash database formats except XML. The README refers to piecash schema documentation and manually defined table lookups.

#### Write operations

Potentially yes. The README explicitly warns: “Always back up your database. Jam.py is a database framework and can modify the database structure.” That is a major safety signal.

#### Auth, mobile, deployment

- Auth: left to Jam.py/platform conventions.
- Mobile: generic web app, not central.
- Deployment: run `server.py`; can be hosted on PythonAnywhere/self-hosted/Raspberry Pi.

#### What to borrow

- Fast schema exploration ideas.
- Clear acknowledgement that GnuCash schema relationships are central to UI correctness.
- Lightweight self-hosting mindset.

#### What to avoid

- Low-code direct DB editing against a GnuCash book.
- Any tool that might alter database structure.
- Treating “it runs quickly” as more important than data safety.

#### Activity and risks

New/WIP with small community signal. The biggest risk is direct database mutation/schema drift.

### 6. `phjardas/gnucash-browser`

Repository: <https://github.com/phjardas/gnucash-browser>

#### What it does

`gnucash-browser` generates a static read-only website from a complete GnuCash book.

#### Stack

- JavaScript
- Gatsby
- Node/npm
- static site output

#### GnuCash data model

The path to the GnuCash file is configured in `gatsby-config.js`. The build generates a static site in `public/`.

#### Write operations

No. It is explicitly read-only.

#### Auth, mobile, deployment

- Auth: none in-app; static hosting can be protected externally if needed.
- Mobile: browser output, no explicit mobile UX strategy.
- Deployment: deploy generated `public/` to any web server.

#### What to borrow

- Read-only-by-construction is a powerful safety baseline.
- Static/browsing use case validates that users may want access without writes.
- Generated views can be a useful fallback/export concept later.

#### What to avoid

- Build-time-only UX; our product should be interactive and self-hosted.
- No live refresh/index/search model.
- Stale dependencies/low activity.

#### Activity and risks

Small and stale. Useful mainly as proof that read-only web browsing is a valid niche.

## Why not simply use an existing project?

Because each reviewed project optimizes for a different product:

- `gnucash-web` optimizes for simple mobile transaction entry and starts with writes.
- `GnuDash` optimizes for a rich browser-local dashboard/editor and has a broad accounting engine.
- `gnucash-rest` optimizes for API integration and exposes broad mutable business operations.
- `GnuCashew` optimizes toward a full web accounting system.
- `gnucash-2-web` optimizes for quick low-code database access.
- `gnucash-browser` optimizes for static read-only generation.

`gnucash-web-companion` should optimize for a different combination: **modern self-hosted server app, safety-first read-only MVP, clean API, polished UI, and explicit future path to multi-book support without making collaborative editing the core feature.**

## Differentiation for `gnucash-web-companion`

- SvelteKit + FastAPI instead of Flask templates, Next.js browser-WASM, WSGI-only API, C++ Wt, or low-code Jam.py.
- piecash-centered server-side access instead of native GnuCash Python bindings or direct low-code table editing.
- Separate app metadata DB instead of modifying the GnuCash book for preferences/app state.
- Read-only MVP instead of “quick transaction entry” MVP.
- Single-book default with clean book abstraction for later multi-book support.
- Strong deployment story for private self-hosting from day one.
- UI inspired by GnuDash, but domain safety inspired by the pitfalls visible across write-capable projects.

## Borrow / avoid summary

### Borrow

- From `gnucash-web`: companion framing, mobile awareness, single-book simplicity, Docker/self-host docs.
- From `GnuDash`: dashboard-first UI, drill-down charts, account tree/register patterns, privacy mode, demo mode, report pages.
- From `gnucash-rest`: resource-oriented JSON API, GUID-based identifiers, account/split/transaction resource boundaries, filters.
- From `gnucash-browser`: read-only-by-construction baseline.
- From `gnucash-2-web`: visible schema mapping discipline.
- From `GnuCashew`: humility about GnuCash compatibility complexity.

### Avoid

- Write operations in MVP.
- Direct database schema mutation.
- Browser cookie storage of DB credentials as core auth model.
- Full accounting-system replacement ambitions.
- Collaborative multi-user editing as a core feature.
- API methods/resources that imply writes before safety design exists.
- Mixing app metadata into the GnuCash book.
