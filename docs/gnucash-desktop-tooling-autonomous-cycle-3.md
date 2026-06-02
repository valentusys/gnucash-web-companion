# GnuCash Desktop tooling probe — autonomous cycle 3

Status: safe tooling availability evidence only. This is not Desktop-generated fixture evidence and not a compatibility guarantee.

## Probe scope

The probe records only:

- whether `gnucash` and `gnucash-cli` are on `PATH`;
- bounded `--version` output;
- whether the version command succeeded;
- redacted executable-path status (`<redacted>` or `not found`).

The probe does not:

- open a GnuCash book;
- create or mutate a fixture;
- search user/private directories;
- record executable paths;
- record account names, memos, descriptions, amounts, private paths, books, exports, screenshots, app DBs, backups, secrets, or tokens.

## Local cycle-3 observation

Command run:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py
```

Observed bounded result:

- `gnucash`: available on `PATH`; `gnucash --version` did not succeed in the headless session because no graphical display was available. No book was opened.
- `gnucash-cli`: available on `PATH`; `gnucash-cli --version` returned `GnuCash 5.14` / `Build ID: 5.14+(2025-12-20)`.
- `desktop_tooling_available=true` because at least one command is available.
- `desktop_generated_fixture_possible_now=false` because command availability/version output alone is not a safe noninteractive fixture-creation path.

## Remaining blocker

A tested Desktop-generated synthetic fixture still requires an isolated disposable GUI/manual-safe GnuCash Desktop session that creates/saves a synthetic SQLite fixture outside git, followed by redacted metadata collection and default-read-only validation.

Do not use this probe result to claim Desktop-version compatibility. It is only command availability/version evidence.
