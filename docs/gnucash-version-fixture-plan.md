# GnuCash Version Fixture Plan

Status: Phase 136 compatibility fixture planning document. This is a plan only; it does not add fixture binaries, run GnuCash Desktop, test real user books, or broaden compatibility guarantees.

`gnucash-web-companion` remains read-only by default for the MVP. GnuCash Desktop remains the authoritative editor. Any compatibility fixtures must be synthetic/disposable and must never contain real financial data.

## Goals

- Define a safe, reproducible path for validating read-only behavior against GnuCash books produced by real GnuCash Desktop versions.
- Track the source version, operating system, SQL backend, schema markers, and fixture data model for each fixture.
- Make future acceptance tests explicit before committing or generating more fixture artifacts.
- Keep compatibility claims conservative until fixtures and tests exist.

## Non-goals

- No production compatibility guarantee.
- No validation of real user books.
- No XML-book support in this SQL-book MVP plan.
- No PostgreSQL/MySQL/MariaDB fixture commitment until separate infrastructure and safety review exists.
- No controlled-write scope expansion. Controlled writes remain experimental post-MVP and disabled by default with `GNUCASH_WRITES_ENABLED=false`.
- No large binary fixture commits unless explicitly approved.

## Target GnuCash versions

Start with versions that are realistic for self-hosted/Linux users and easy to reproduce in CI or documented local generation:

| Priority | GnuCash version family | Fixture source | Why |
|---:|---|---|---|
| 1 | Current stable packaged on Debian/Ubuntu LTS | Debian/Ubuntu package or container | Likely self-host target for this project. |
| 2 | Current upstream stable Flatpak | Flatpak runtime on Linux | Common cross-distro install path with newer GnuCash versions. |
| 3 | Previous stable major/minor still commonly used | Distro package archive or documented manual VM/container | Detect schema drift from older but plausible user books. |
| 4 | macOS/Windows desktop-generated SQLite books | Manual generation only, if contributor can verify provenance | Useful user coverage, but not required for automated Linux CI in v1. |

The first implementation phase should pick one reproducible Linux path only. Additional version families should be added incrementally after safety review.

## Current fixture/evidence inventory

As of Phase 136, every compatibility evidence row in `docs/gnucash-compatibility.md` is synthetic/disposable only:

| Evidence source | Status | Desktop version tested? | Notes |
|---|---|---|---|
| `apps/api/tests/fixtures/test-book.gnucash.sqlite` | committed synthetic SQLite test fixture | No | Automated tests pin `Gnucash = 3000000` and `Gnucash-Resave = 19920`; fixture is not a broad Desktop-version claim. |
| `apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite` | committed synthetic SQLite test fixture | No | Covers read-only multi-currency limitation behavior; same documented schema markers. |
| `apps/api/scripts/create_compatibility_fixture_v1.py` | generated synthetic/disposable SQLite fixture path | No | Generated through `piecash`; binary output remains local/ignored. |
| Redacted metadata collector | tested safe metadata procedure | No by itself | Operator-supplied `--gnucash-version` values document a copied/disposable fixture only; they do not independently prove support for that Desktop release. |
| Desktop-tooling probes from Phases 111, 127, 154, 163, and 197 | safe blocker evidence | No | Host `gnucash`/`gnucash-cli` were unavailable in earlier phases. Phase 154 adds missing-command reasons plus optional non-mutating package-candidate hints. Phase 163/197 prove GnuCash 4.13 tooling can be installed inside a disposable Debian 12 container, but no safe noninteractive SQLite fixture creation command was found, so no Desktop-generated fixture was produced. Phase 197 narrows the next step to an isolated disposable GUI/manual-safe creation path plus redacted metadata/read-only validation. Phase 204 adds matrix classification tests so metadata alone stays blocked/manual until read-only validation passes. |

Therefore the current tested GnuCash Desktop version list is empty: no real GnuCash Desktop release has been validated by the automated suite. Future rows must remain narrow until a synthetic book is generated/saved by the named Desktop version and read-only tests pass against that fixture.

## Current #22 maintainer checklist and blocker

The latest autonomous multiqueue probe keeps the issue in a blocked-but-actionable state:

1. `gnucash-cli --version` is available and reports GnuCash 5.14.
2. `gnucash --version` is present but cannot initialize the graphical interface in this headless
   session because `$DISPLAY` is unavailable.
3. `desktop_generated_fixture_possible_now=false`; command/version output is not a
   Desktop-generated fixture.
4. No book was opened and no user directory was searched.
5. The next acceptable maintainer action is an isolated disposable GUI/manual-safe session that
   creates a synthetic SQLite fixture from the data model below, then runs the redacted metadata
   collector and read-only validation.

#22 was closed only after narrow Desktop-generated synthetic SQLite fixture evidence passed
fail-closed preflight plus default-read-only validation. Do not turn package/tooling availability,
operator-supplied version strings, metadata-only rows, or the single synthetic fixture into broad
compatibility claims.

## OS and source of fixtures

Each fixture entry must record:

- GnuCash Desktop version (`gnucash --version` output where available).
- OS/distribution and release, for example Debian 12, Ubuntu 24.04 LTS, Flatpak runtime version, macOS version, or Windows version.
- Install source: distro package, Flatpak, upstream bundle, or manual contributor environment.
- SQL backend: SQLite first. PostgreSQL/MySQL/MariaDB stay untested until later explicit phases.
- piecash version used by the backend test runner.
- Fixture generation command or manual steps.
- SQLite `versions` table markers.
- SHA-256 of any generated fixture file, if the file is committed or published as an external artifact.

## Fixture data model

Fixture data must be synthetic and boring by design. It should exercise core read-only behavior without resembling a real household, business, or user ledger.

Required accounts:

- Assets: Checking, Savings, Cash.
- Liabilities: Credit Card.
- Income: Salary, Interest.
- Expenses: Groceries, Utilities, Travel.
- Equity: Opening Balances.

Required transactions:

- Opening balances for at least two asset accounts.
- Simple income transaction.
- Simple expense transaction.
- Split transaction with at least three splits.
- Transfer between asset accounts.
- Credit-card expense and payment.
- Multi-currency transaction only in a separate fixture or explicitly labeled fixture variant.

Data rules:

- Use fake names such as `Fixture Grocery`, `Fixture Employer`, and `Fixture Utility`.
- Use round or intentionally simple amounts.
- Use non-real dates in a compact fixed range, for example January 2024.
- Do not include real account numbers, addresses, descriptions, memos, file paths, customer/vendor names, or screenshots.
- Money expectations in tests must use strings/Decimal-compatible values, never floats.

## Safe fixture creation process

Preferred future path:

1. Generate a book in a disposable environment using the target GnuCash Desktop version.
2. Use only synthetic fixture data from this document.
3. Save as SQLite, not XML, for the current MVP compatibility path.
4. Inspect the SQLite `versions` table and basic table list.
5. Run a local read-only smoke against the copied/generated fixture.
6. Confirm `GNUCASH_WRITES_ENABLED=false` for all read-only validation.
7. If committing the fixture is proposed, check size, license/provenance, data contents, and repository impact first.
8. Prefer a generator script or documented manual generation over committing binary files when practical.

Example safe inspection commands for a disposable SQLite fixture:

```bash
sqlite3 fixture.gnucash.sqlite 'select table_name, table_version from versions order by table_name;'
sqlite3 fixture.gnucash.sqlite 'select count(*) from accounts;'
sqlite3 fixture.gnucash.sqlite 'select count(*) from transactions;'
```

Do not print or publish real descriptions, account names, transaction memos, private paths, or balances from user books.

## Phase 92+ copied/test-book metadata procedure

Phase 92 improves the test-copy procedure without committing a new binary fixture. Use this when a contributor has a generated disposable fixture or a copied book outside git and wants to provide compatibility evidence safely.

1. Work only on a copied/disposable SQLite book. Do not point the collector at the only/original book.
2. Record the exact GnuCash Desktop version that created or last saved the copy, if known:

   ```bash
   gnucash --version
   ```

3. Run the metadata collector from the repository root:

   ```bash
   python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
     /tmp/gwc-desktop-fixture/desktop-synthetic-fixture.gnucash.sqlite \
     --gnucash-version "GnuCash 5.10" \
     --fixture-origin desktop-generated-synthetic \
     --output /tmp/compatibility-metadata.json
   ```

4. Review `/tmp/compatibility-metadata.json` before sharing. It should contain only the redacted path (`"<redacted>"`), backend, declared GnuCash Desktop version, `versions` markers, and selected table counts. It must not contain account names, transaction descriptions, amounts, memos, split rows, private paths, screenshots, `.env`, app DB data, backups, or secrets.
5. If this metadata is used to update `docs/gnucash-compatibility.md`, describe the row narrowly. A metadata row is evidence for that copied/test environment only; it is not proof of all GnuCash versions, all SQL backends, XML books, or production readiness.

Phase 102 updates this metadata procedure so the JSON also records safe local runtime provenance: collector/generator version, operating system string, Python version, SQLite library version, and piecash package version. These fields help reproduce generated/disposable fixture evidence and are allowed to share after review because they do not include private paths or book row data.

Phase 111 adds a separate Desktop-tooling probe for environments where the maintainer wants to know whether a real Desktop-generated fixture can be produced locally:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py --output /tmp/gnucash-tooling-probe.json
```

This probe records only whether `gnucash` and `gnucash-cli` are available, redacts executable paths, and stores bounded `--version` output if a command exists. It does not open books, search home directories, or collect row data. If the probe reports `desktop_tooling_available=false`, do not add a Desktop-version matrix row; use the generated/disposable fixture path until a disposable environment with GnuCash Desktop/CLI is available.

Phase 127 repeats this check and keeps the same rule: if both `gnucash --version` and `gnucash-cli --version` are unavailable, document the blocker in GitHub #22/docs and do not fabricate Desktop-generated evidence.

Phase 154 updates the probe to version `phase-154` and adds an optional non-mutating package metadata check:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py \
  --include-install-hints \
  --output /tmp/gnucash-tooling-probe.json
```

The optional hints are allowed only because they query known package names with `apt-cache policy`; they do not install packages, open books, search user directories, or serialize private paths. Package availability is not Desktop-generated fixture evidence by itself. A future Desktop row still requires a disposable environment, an actually created synthetic SQLite book, redacted metadata collection, and read-only service validation.

Phase 163 adds a disposable-container tooling probe for environments where host package installation is not acceptable:

```bash
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py \
  --output /tmp/phase-163-gnucash-container-probe.json
```

This helper runs a temporary `debian:12-slim` Docker container, installs GnuCash packages only inside that container, and records bounded command/version/help/package metadata. It does not mount host books, open or generate a book, search private directories, install host packages, or write a fixture into the repository. Phase 163 evidence shows Debian 12 can install GnuCash 4.13 (`gnucash` and `gnucash-cli` available), but `gnucash-cli --help` exposes report/quote commands rather than a safe noninteractive create/save-as SQLite fixture command. Therefore Desktop-generated fixture evidence remains blocked until a disposable GUI/manual path or confirmed noninteractive creation path exists.

Phase 136 keeps that boundary explicit: all current compatibility evidence is synthetic-only, and the Desktop-tested version list is empty until a future disposable Desktop environment produces a synthetic SQLite book and tests cover it. The manual procedure for that future work is:

1. Use a disposable VM/container or other non-private environment with GnuCash Desktop/CLI installed.
2. Confirm the tool version:

   ```bash
   gnucash --version || gnucash-cli --version
   ```

3. Create a new synthetic SQLite book from scratch using only the fixture model above.
4. Save it outside the repository, for example `/tmp/gnucash-desktop-fixture.gnucash.sqlite`.
5. Run the redacted metadata collector:

   ```bash
   python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
     /tmp/gnucash-desktop-fixture.gnucash.sqlite \
     --gnucash-version "GnuCash X.Y" \
     --fixture-origin desktop-generated-synthetic \
     --output /tmp/gnucash-desktop-fixture-metadata.json
   ```

6. Review the JSON before sharing. It must contain only redacted path, backend, declared Desktop version, `versions` markers, selected table counts, and safe runtime context.
7. Do not commit the generated book unless a later explicit phase approves a new binary fixture after size/provenance/private-data review.

Phase 92 local procedure evidence:

- `gnucash --version`: unavailable in this container (`gnucash: command not found`).
- `piecash`: 1.2.1.
- Generated disposable source: `apps/api/scripts/create_compatibility_fixture_v1.py` into a temporary directory outside git.
- Collector result: redacted path, `Gnucash = 3000000`, `Gnucash-Resave = 19920`, safe table counts only.
- Regression coverage: `apps/api/tests/test_gnucash_compatibility_metadata.py` proves the collector does not serialize private path, account name, or transaction description values from a copied SQLite book.

Phase 102 local procedure evidence:

- `gnucash --version`: unavailable in this container (`gnucash: command not found`).
- `piecash`: 1.2.1.
- `python`: 3.11.15.
- `sqlite`: 3.50.4.
- Generated disposable source: `apps/api/scripts/create_compatibility_fixture_v1.py` into a temporary directory outside git.
- Collector result: redacted path, `Gnucash = 3000000`, `Gnucash-Resave = 19920`, selected safe table counts (`accounts`, `books`, `commodities`, `splits`, `transactions`), and safe runtime context only.
- Regression coverage: `apps/api/tests/test_gnucash_compatibility_metadata.py` and `apps/api/tests/test_compatibility_fixture_v1.py` assert safe runtime provenance is present while private path, account name, and transaction description values are not serialized by the copied-book collector.

Phase 111 local procedure evidence:

- `apps/api/scripts/probe_gnucash_desktop_tooling.py --output /tmp/phase-111-gnucash-tooling-probe.json` reported `desktop_tooling_available=false`.
- `gnucash`: not found.
- `gnucash-cli`: not found.
- No GnuCash book was opened, no user private directories were searched, and no Desktop-generated fixture was produced.
- Regression coverage: `apps/api/tests/test_gnucash_compatibility_metadata.py` asserts the probe redacts executable paths, handles unavailable commands, and records only safe availability/version metadata.

Phase 127 local procedure evidence:

- `gnucash --version`: unavailable in this container (`gnucash: command not found`).
- `gnucash-cli --version`: unavailable in this container (`gnucash-cli: command not found`).
- `apps/api/scripts/probe_gnucash_desktop_tooling.py --output /tmp/phase-127-gnucash-tooling-probe.json` reported `desktop_tooling_available=false`.
- No GnuCash book was opened, no user private directories were searched, no real/private book was used, and no Desktop-generated fixture was produced.
- Regression coverage: `apps/api/tests/test_compatibility_fixture_v1.py` asserts missing Desktop tooling is represented as a safe blocker, not Desktop-generated evidence, and does not serialize private paths.

Phase 154 local procedure evidence:

- `apps/api/scripts/probe_gnucash_desktop_tooling.py --include-install-hints --output /tmp/phase-154-gnucash-tooling-probe.json` reported `desktop_tooling_available=false` and `desktop_generated_fixture_possible_now=false`.
- `gnucash`: not found on `PATH`.
- `gnucash-cli`: not found on `PATH`.
- `apt-cache policy gnucash`: candidate `1:5.14-1build1`, installed `(none)`; this is package metadata only, not fixture evidence.
- No package was installed, no GnuCash book was opened, no user private directories were searched, no real/private book was used, and no Desktop-generated fixture was produced.
- Evidence summary: `docs/gnucash-desktop-tooling-phase-154.md`.
- Regression coverage: `apps/api/tests/test_gnucash_compatibility_metadata.py` asserts phase-154 probe metadata, missing-command reasons, optional non-mutating install hints, and private-path omission; `apps/api/tests/test_compatibility_fixture_v1.py` continues to assert missing Desktop tooling is a safe blocker.

Phase 163 disposable-container evidence:

- `apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output /home/val/.hermes/logs/gnucash-web-companion/phase-163/disposable-container-probe.json` completed with return code `0`.
- Container image: `debian:12-slim`.
- Container package candidates: `gnucash = 1:4.13-1`, `gnucash-common = 1:4.13-1`.
- Container commands: `gnucash` and `gnucash-cli` available inside the disposable container only.
- `gnucash-cli --version`: `GnuCash 4.13`.
- `gnucash-cli --help`: report generation and price quote commands only; no safe noninteractive create/save-as SQLite fixture command was identified.
- No host package was installed, no book was opened or generated, no user private directories were searched, no real/private book was used, and no Desktop-generated fixture was produced.
- Evidence summary: `docs/gnucash-desktop-tooling-phase-163.md`.
- Regression coverage: `apps/api/tests/test_gnucash_desktop_container_probe.py` asserts the disposable-container probe records tooling availability and package candidates without claiming Desktop-generated fixture evidence or serializing private paths.

Phase 197 blocker refresh evidence:

- `apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output /tmp/phase-197-container-probe.json --timeout-seconds 900` completed with return code `0`.
- Container image: `debian:12-slim`.
- Container commands: `gnucash` and `gnucash-cli` available inside the disposable container only.
- `gnucash-cli --version`: `GnuCash 4.13`.
- `gnucash-cli --help`: no safe noninteractive create/save-as SQLite fixture command was identified.
- Exact next requirement: isolated disposable GUI/manual-safe GnuCash Desktop session that creates/saves a synthetic SQLite fixture outside git, followed by `collect_gnucash_compatibility_metadata.py --fixture-origin desktop-generated-synthetic` and read-only API validation with `GNUCASH_WRITES_ENABLED=false`.
- No host package was installed, no book was opened or generated, no user private directories were searched, no real/private book was used, and no Desktop-generated fixture was produced.
- Evidence summary: `docs/gnucash-desktop-tooling-phase-197.md`.
- Regression coverage: `apps/api/tests/test_gnucash_compatibility_metadata.py` asserts the phase-197 collector records provenance/redaction metadata while excluding private paths, account names/descriptions, transaction descriptions, split memos, split amounts, and other row values.

## Storage and generation policy

Allowed without extra approval:

- Documentation describing how to generate a fixture.
- Small scripts that generate synthetic fixture data.
- Small scripts that collect redacted compatibility metadata from copied/disposable SQLite books.
- Tests that operate on generated or already committed synthetic fixture copies.

Needs explicit approval before commit:

- New binary SQLite fixture files.
- Large fixture artifacts.
- Fixtures generated outside a documented disposable environment.
- External artifact publishing.

Never allowed:

- Real user GnuCash files.
- `.env`, app DBs, backups, secrets, keys, tokens, certificates, or real screenshots/exports.
- Fixture files copied from a personal or business book and scrubbed after the fact.

## Acceptance tests for future implementation

A future implementation phase should add tests that prove each accepted fixture can be opened and read without mutation:

- Fixture file exists or generator produces it deterministically.
- Fixture provenance metadata is documented.
- `versions` table markers are captured and asserted or snapshotted.
- Account tree endpoint returns expected root/top-level accounts.
- Transaction list endpoint returns expected transaction count and stable fields.
- Transaction detail endpoint handles the split transaction.
- Reports summary endpoint returns basic read-only aggregates.
- CSV export endpoint works and preserves read-only semantics.
- Disabled write endpoints still return 403 when `GNUCASH_WRITES_ENABLED=false`.
- The fixture file checksum is unchanged after read-only tests.

For manual fixtures, at minimum the handoff must include the generation steps, version metadata, and a reason automated generation was not practical.

## Relationship to existing compatibility docs

The current compatibility matrix remains intentionally narrow and is documented in `docs/gnucash-compatibility.md`. Compatibility claims must stay limited to the already committed/generated synthetic fixtures, redacted metadata/probe procedures, and their recorded schema markers until a future explicit phase adds a Desktop-generated synthetic fixture with provenance and tests. A declared GnuCash Desktop version string in metadata is not enough by itself to claim that the release is supported.

## GitHub tracking

This plan advances GitHub issue #22 by defining the target versions, fixture data model, safe generation/storage policy, and future acceptance tests. The issue should stay open until at least one real-version disposable fixture or reproducible generation path is implemented and tested.
