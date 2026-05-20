# GnuCash Compatibility Matrix

Status: pre-alpha compatibility notes for read-only MVP validation. Compatibility evidence is based on synthetic/disposable fixtures only unless a row explicitly says otherwise.

`gnucash-web-companion` accesses GnuCash SQL books through `piecash` behind the FastAPI service layer. GnuCash Desktop remains the authoritative editor, and users should test with a disposable copy before pointing the app at any real book.

## Current compatibility matrix

This matrix is intentionally narrow. It separates automated synthetic fixture evidence from blocked/manual fixture work and from unclaimed backends. Rows below do not prove compatibility with every GnuCash Desktop release, SQL backend, operating system, or real user book.

Phase 204 regression guard: `apps/api/app/compatibility_matrix.py` and `apps/api/tests/test_compatibility_matrix.py` ingest redacted collector metadata and classify it as tested synthetic evidence, blocked/manual fixture work, or unclaimed backend. Tests fail if docs or changelog wording implies broad compatibility such as all-version, all-backend, production-ready, or real-book guarantees.

## Tested synthetic/disposable fixture evidence

These rows are the only rows currently treated as tested. They are synthetic/disposable SQLite evidence only.

| Source / fixture | Book format | Fixture provenance | GnuCash Desktop version evidence | GnuCash SQL `versions` marker | Coverage | Status |
|---|---:|---|---|---:|---|---|
| `apps/api/tests/fixtures/test-book.gnucash.sqlite` | SQLite | committed synthetic fixture used only for tests | not Desktop-version evidence; fixture is synthetic and the currently documented source is the repository test fixture | `Gnucash = 3000000`, `Gnucash-Resave = 19920` | read-only accounts, transactions, reports, CSV export; controlled-write tests only against disposable copies | Tested in CI/backend suite |
| `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite` | SQLite | committed synthetic fixture used only for tests | not Desktop-version evidence; fixture is synthetic and the currently documented source is the repository test fixture | `Gnucash = 3000000`, `Gnucash-Resave = 19920` | read-only multi-currency limitation behavior | Tested in CI/backend suite |
| `apps/api/scripts/create_compatibility_fixture_v1.py` generated fixture | SQLite | generated synthetic/disposable fixture; binary fixture is not committed | not Desktop-generated; generated through `piecash` | captured at test/runtime by metadata helper; expected compatibility-path markers match `Gnucash = 3000000`, `Gnucash-Resave = 19920` | generated account tree, transaction list, split transaction detail, reports basic, checksum no-mutation check | Tested by `tests/test_compatibility_fixture_v1.py`; generated locally, binary fixture not committed |
| Phase 92 local compatibility metadata procedure against a generated disposable fixture | SQLite | generated disposable fixture plus redacted metadata collector | no Desktop executable was installed in this environment; any `--gnucash-version` value is operator-supplied metadata, not independently verified compatibility | safe JSON collector recorded `Gnucash = 3000000`, `Gnucash-Resave = 19920`, plus table counts only | copied/test-book metadata collection procedure, no row data, no private path, no mutation | Tested by `tests/test_gnucash_compatibility_metadata.py`; procedure evidence only, not a desktop-version compatibility claim |
| Phase 102 generated/disposable compatibility provenance refresh | SQLite | generated disposable fixture plus redacted runtime provenance | `gnucash --version` unavailable; this remains generated/piecash evidence rather than a real GnuCash Desktop version row | safe JSON collector recorded `Gnucash = 3000000`, `Gnucash-Resave = 19920`, selected safe table counts, and safe runtime context (`collector_version`, OS, Python, SQLite, piecash versions) | generated fixture metadata and copied/test-book metadata include reproducible local runtime provenance without row data or private paths | Tested by `tests/test_gnucash_compatibility_metadata.py` and `tests/test_compatibility_fixture_v1.py` |
| Phase 176 write-alpha mutated disposable copy opened by GnuCash CLI tooling | SQLite | committed synthetic fixture copied to a temporary external path, mutated exactly once through write-alpha create in `APP_ENV=test`, then deleted after redacted checks | GnuCash CLI 4.13 inside a temporary `debian:12-slim` container accepted the mutated disposable SQLite book via `gnucash-cli --report show --name "Balance Sheet"`; this is CLI tooling evidence only, not a Desktop-generated fixture or broad GUI compatibility claim | existing synthetic fixture markers before mutation remained the provenance baseline; no new committed fixture/schema marker was added | one disposable write-alpha create mutation, GnuCash CLI open/report-metadata check, and read-only API re-open smoke with writes disabled by default | Evidence documented in `docs/dogfood/phase-176-write-alpha-desktop-verification.md`; no raw book/app DB/backup/screenshot/export committed |

## Blocked/manual fixture work

These rows are evidence of safe procedures or blockers. They are not tested Desktop-version support rows.

| Source / procedure | Book format | Fixture provenance | Desktop/version evidence boundary | Schema marker boundary | Coverage | Status |
|---|---:|---|---|---:|---|---|
| Phase 111 Desktop-tooling availability probe | no Desktop-generated SQLite fixture produced | safe availability probe only | local probe result was `desktop_tooling_available=false`; no GnuCash Desktop version was tested | no new Desktop-generated schema marker; existing generated fixture markers remain `Gnucash = 3000000`, `Gnucash-Resave = 19920` | safe probe records whether `gnucash` / `gnucash-cli` are available and records bounded `--version` output only when present; no book is opened and no private directories are searched | Tested by `tests/test_gnucash_compatibility_metadata.py`; reproducibility/evidence hygiene only |
| Phase 127 Desktop compatibility evidence refresh | no Desktop-generated SQLite fixture produced | safe missing-tooling blocker refresh | `gnucash --version` and `gnucash-cli --version` were unavailable; no GnuCash Desktop version was tested | no new Desktop-generated schema marker; existing generated fixture markers remain `Gnucash = 3000000`, `Gnucash-Resave = 19920` | re-ran `gnucash --version`, `gnucash-cli --version`, and the safe tooling probe; both commands were unavailable, so no synthetic Desktop-generated book could be created in this environment | Blocker documented for GitHub #22; missing Desktop tooling is treated as a safe blocker, not Desktop evidence |
| Phase 154 Desktop tooling blocker refresh | no Desktop-generated SQLite fixture produced | improved safe missing-tooling blocker with non-mutating install hints | `gnucash` and `gnucash-cli` are not installed on `PATH`; Ubuntu package metadata shows a `gnucash` candidate but no Desktop-generated fixture was created or tested | no new Desktop-generated schema marker; existing generated fixture markers remain `Gnucash = 3000000`, `Gnucash-Resave = 19920` | phase-154 probe records missing command reasons, `desktop_generated_fixture_possible_now=false`, and optional bounded `apt-cache policy` candidate metadata without installing packages, opening books, or searching private directories | Blocker documented in `docs/gnucash-desktop-tooling-phase-154.md`; tested by metadata/probe tests |
| Phase 163 disposable Desktop container probe | no Desktop-generated SQLite fixture produced | disposable Debian 12 container tooling probe only | `gnucash`/`gnucash-cli` install inside `debian:12-slim` as GnuCash 4.13, but no safe noninteractive SQLite fixture creation command was identified; no Desktop-generated book was created or tested | no new Desktop-generated schema marker; existing generated fixture markers remain `Gnucash = 3000000`, `Gnucash-Resave = 19920` | phase-163 probe records container package candidates, command availability, bounded version/help output, and an explicit fixture-generation blocker without installing host packages, opening books, or searching private directories | Blocker documented in `docs/gnucash-desktop-tooling-phase-163.md`; tested by `tests/test_gnucash_desktop_container_probe.py` |
| Phase 197 disposable Desktop fixture blocker refresh | no Desktop-generated SQLite fixture produced | disposable Debian 12 container tooling probe plus collector hardening | `gnucash`/`gnucash-cli` install inside `debian:12-slim` as GnuCash 4.13, but no safe noninteractive SQLite fixture creation command was identified; a disposable GUI/manual-safe step is still required | no new Desktop-generated schema marker; existing generated fixture markers remain `Gnucash = 3000000`, `Gnucash-Resave = 19920` | phase-197 evidence narrows the blocker to an isolated GUI/manual Desktop creation step and adds collector provenance/redaction tests for future Desktop-generated synthetic fixtures | Blocker documented in `docs/gnucash-desktop-tooling-phase-197.md`; tested by metadata and container-probe tests |
| Phase 203 disposable Desktop fixture capture path | no Desktop-generated SQLite fixture produced | deterministic manually supplied synthetic Desktop candidate gate | no new Desktop version was tested; candidates require an explicit operator-supplied Desktop version string before metadata collection | no new Desktop-generated schema marker; accepted future candidates will record schema markers only after passing path/name/provenance checks | helper accepts/rejects desktop-generated synthetic candidates safely, rejects backup/app/secrets/non-disposable classes, and records bounded redacted candidate metadata only | Capture path documented in `docs/gnucash-desktop-fixture-capture.md`; tested by `tests/test_gnucash_compatibility_metadata.py` |
| Future accepted Desktop-generated synthetic metadata | SQLite only | manually supplied synthetic/disposable Desktop candidate after Phase 203 checks | metadata captured; read-only validation still required; operator-supplied version strings are not independent Desktop evidence | schema markers may be listed only after safe metadata collection and review | metadata ingestion is classified as blocked/manual until default-read-only validation passes | Guarded by `tests/test_compatibility_matrix.py` |

## Unclaimed backends and formats

These entries are intentionally outside the tested matrix until a later explicit phase adds safe fixtures, read-only validation, and docs/tests.

| Backend / format | Current matrix status | Required before a tested row |
|---|---|---|
| PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed | No automated compatibility evidence and no support statement in this matrix | Separate synthetic backend fixtures, isolated infrastructure, redacted metadata, read-only validation, and explicit roadmap scope |
| XML books remain outside the SQL-book MVP | Not part of the current service-layer input model | Separate product scope and tests before documenting any XML behavior |
| Real/private user books | Not evidence for committed docs/tests and never committed | Use copied/disposable review only; do not publish private paths, row data, exports, screenshots, backups, or app DBs |

## GnuCash Desktop versions tested

No real GnuCash Desktop version has been tested by this repository's automated compatibility suite yet. Current compatibility evidence is synthetic only:

- committed synthetic SQLite fixtures with `Gnucash = 3000000` and `Gnucash-Resave = 19920` schema markers;
- generated `piecash` synthetic/disposable SQLite fixture coverage;
- redacted metadata collection/probe tests that avoid private paths and row data;
- repeated local checks where `gnucash` and `gnucash-cli` were unavailable, so no Desktop-generated fixture could be produced.
- Phase 154's refreshed blocker confirms `gnucash` and `gnucash-cli` are still unavailable on `PATH`; non-mutating package metadata found an Ubuntu candidate, but no package was installed and no Desktop-generated fixture was created in this shared environment.
- Phase 163's disposable container probe confirms Debian 12 can install GnuCash 4.13 tooling in isolation, but `gnucash-cli --help` did not expose a safe noninteractive create/save-as SQLite fixture path, so no Desktop-generated fixture was created or tested.
- Phase 176 confirms the disposable write-alpha-mutated synthetic SQLite copy can be opened by GnuCash CLI 4.13 in a temporary Debian 12 container for bounded report metadata. This narrows the write-alpha dogfood evidence for that copy only; it is not a Desktop-generated fixture, GUI-session proof, or broad GnuCash Desktop version support claim.
- Phase 197 re-ran the disposable container path and narrowed the remaining Desktop-generated fixture blocker: Debian 12 can install GnuCash/GnuCash CLI 4.13, but no safe noninteractive SQLite creation command is exposed, so the next step must be an isolated disposable GUI/manual-safe Desktop creation followed by redacted metadata collection and read-only validation.
- Phase 203 adds a deterministic capture gate for a future manually supplied Desktop-generated synthetic SQLite fixture. The collector now rejects unsafe candidate names/path classes before reading metadata, records only redacted candidate acceptance metadata on success, and still does not claim any Desktop-version row because no fixture was generated or supplied.

Operator-supplied metadata strings such as `--gnucash-version "GnuCash 5.10"` are documentation inputs for a copied/disposable fixture. They are not proof that this project has independently tested that Desktop release until a synthetic book generated/saved by that Desktop version is created, documented, and covered by tests.

## Not yet formally tested

The project does not yet have committed fixture books generated by real GnuCash Desktop versions. Until those exist, compatibility must be described conservatively:

- SQLite books with the schema markers above are exercised by automated tests.
- PostgreSQL/MySQL/MariaDB GnuCash backends are not formally tested by this project yet.
- XML books are not in scope for the current SQL-book MVP.
- Scheduled/recurring transaction awareness is available as conservative read-only metadata only; richer schedule calculations/editing remain out of scope.
- Controlled writes remain post-MVP/experimental and disabled by default.

## User guidance

1. Check your GnuCash Desktop version and backend before testing.
2. Make a copy of the book; do not use your only file.
3. Keep `GNUCASH_WRITES_ENABLED=false` for MVP/read-only testing.
4. Start with read-only screens: dashboard, accounts, transactions, reports, CSV export.
5. If the app fails to open a book, keep the original untouched and report the GnuCash version, backend, and sanitized schema/version details.

## How to inspect a SQL book version safely

Use a copied SQLite book only:

```bash
sqlite3 copied-book.gnucash.sqlite 'select table_name, table_version from versions order by table_name;'
```

Do not paste real account names, descriptions, balances, transaction data, or private file paths into public issues.

## Safe compatibility metadata collection for copied SQLite books

Phase 92 adds a small metadata collector so a maintainer or contributor can record evidence from a copied/disposable GnuCash SQLite book without publishing private row data:

```bash
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite \
  --gnucash-version "GnuCash 5.10" \
  --fixture-origin desktop-generated-synthetic \
  --output /tmp/compatibility-metadata.json
```

The JSON intentionally records only:

- redacted book path (`"<redacted>"`);
- declared fixture origin, including whether the input is claimed as `desktop-generated-synthetic`;
- declared GnuCash Desktop version, if supplied by the operator;
- backend (`SQLite`);
- `versions` table markers;
- safe table counts for selected tables;
- safe runtime provenance: collector version, operating system string, Python version, SQLite library version, and piecash package version.

It intentionally does not record account names, transaction descriptions, amounts, memos, split rows, private file paths, app database data, backups, `.env`, secrets, keys, tokens, screenshots, or CSV rows. Review the JSON before pasting it into GitHub issues or docs.

Before claiming Desktop-generated evidence, Phase 111 adds a safe tooling probe:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py \
  --include-install-hints \
  --output /tmp/gnucash-tooling-probe.json
```

The probe checks `gnucash` and `gnucash-cli` command availability and bounded `--version` output. With `--include-install-hints`, it also performs non-mutating `apt-cache policy` checks for known GnuCash packages when `apt-cache` exists. It does not install packages, open a book, scan private directories, or record executable paths. In this environment both commands were unavailable, so no Desktop-generated fixture or Desktop-version compatibility row is claimed.

## Future compatibility work

- Phase 45 added a fixture planning document: [docs/gnucash-version-fixture-plan.md](gnucash-version-fixture-plan.md).
- Phase 46 added the first generated disposable fixture path: [docs/gnucash-compatibility-fixture-v1.md](gnucash-compatibility-fixture-v1.md).
- Phase 102 refreshed the generated/disposable path with safe runtime provenance because no local GnuCash Desktop binary was available (`gnucash: command not found`).
- Phase 111 added a tested Desktop-tooling availability probe. The local result was `desktop_tooling_available=false`, so future Desktop-generated evidence still requires installing/providing GnuCash Desktop/CLI in a disposable environment and generating a synthetic SQLite book.
- Phase 127 re-ran the Desktop-tooling evidence check for GitHub #22. `gnucash --version` and `gnucash-cli --version` were still unavailable in this execution environment, so the compatibility matrix records a blocker rather than a Desktop-generated fixture claim. The new regression test in `tests/test_compatibility_fixture_v1.py` pins this behavior: missing Desktop tooling must be reported as a safe blocker and must not serialize private paths or pretend that Desktop evidence exists.
- Phase 154 refreshed the blocker again with an improved phase-154 probe, optional non-mutating package-candidate hints, and `docs/gnucash-desktop-tooling-phase-154.md`. The result remains blocked for Desktop-generated fixture evidence: `gnucash` and `gnucash-cli` are absent on `PATH`, package metadata alone is not compatibility evidence, and future work must use a disposable Desktop/CLI environment plus a synthetic SQLite fixture and read-only tests.
- Phase 163 moved the probe into a disposable Debian 12 container. The container could install GnuCash 4.13, but no safe noninteractive SQLite fixture creation command was found, so the project still records a blocker rather than a Desktop-generated fixture claim.
- Phase 197 narrowed the blocker to an exact next requirement: run GnuCash Desktop in an isolated disposable GUI/manual-safe environment, create/save a synthetic SQLite fixture there, then run the redacted phase-197 metadata collector with `--fixture-origin desktop-generated-synthetic` and read-only API validation with `GNUCASH_WRITES_ENABLED=false`.
- Phase 203 hardened that future fixture capture path: the collector now deterministically rejects manually supplied Desktop synthetic candidates with unsafe names/path classes and records only bounded redacted candidate metadata for accepted inputs. See [docs/gnucash-desktop-fixture-capture.md](gnucash-desktop-fixture-capture.md).
- Phase 204 adds automated matrix-regression coverage for that metadata path: collector JSON is classified as tested synthetic fixture evidence, blocked/manual fixture work, or unclaimed backend. Desktop-generated metadata remains blocked/manual until explicit default-read-only validation passes, and PostgreSQL/MySQL/MariaDB/XML remain unclaimed.

- Add fixture books generated by current supported GnuCash Desktop releases.
- Record GnuCash Desktop version, SQL backend, OS, piecash version, and schema markers for each fixture.
- Add read-only integration tests for each fixture.
- Add a compatibility CI job only after the fixture set is non-sensitive and reproducible.
