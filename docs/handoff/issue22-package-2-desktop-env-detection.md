# Issue #22 package 2 Desktop environment detection

Status: `DESKTOP_FIXTURE_ENV_MISSING_GUI_OR_XVFB`.

Detection timestamp: 2026-06-04T01:48:01Z.

This package checked only command/tooling availability. It did not open, search, copy, or mutate any GnuCash book and did not scan private directories.

## Checked commands

Observed on this host:

- `gnucash`: present on `PATH`, but `gnucash --version` failed because no graphical display was available.
- `gnucash-cli`: present on `PATH`; `gnucash-cli --version` returned `GnuCash 5.14` / `Build ID: 5.14+(2025-12-20)`.
- `xvfb-run`: missing on `PATH`.
- `Xvfb`: missing on `PATH`.
- `xdotool`: missing on `PATH`.
- `dbus-run-session`: present on `PATH`.
- `DISPLAY`: unset.
- `WAYLAND_DISPLAY`: unset.
- `docker`: present on `PATH`, but this package did not run a new fixture-generation container.

The repository-safe probe `python apps/api/scripts/probe_gnucash_desktop_tooling.py --include-install-hints` reported tooling availability for `gnucash-cli`, but also reported `desktop_generated_fixture_possible_now=false`.

Private raw detection log is outside git at:

`/home/val/.hermes/background-runs/gnucash-issue22-desktop-fixture-20260604-114237/desktop-env-detection.log`

Do not commit that raw log.

## Help/creation path review

`gnucash-cli --help` exposes report and price-quote oriented commands. The bounded help output did not expose a safe noninteractive command to create a new GnuCash SQLite book from scratch or save a new synthetic book as SQLite without a GUI session.

`gnucash --help` could not run cleanly in this headless session because the GUI could not initialize.

## Classification

Classification: `DESKTOP_FIXTURE_ENV_MISSING_GUI_OR_XVFB`.

Reasoning:

1. GnuCash CLI/Desktop binaries exist, so this is not `DESKTOP_FIXTURE_ENV_MISSING_GNUCASH`.
2. No display server is configured and no Xvfb/xvfb-run/xdotool automation tooling is available.
3. No safe noninteractive create/save SQLite fixture command was found.
4. Creating the fixture would require either host GUI/Xvfb tooling that is absent now or a separate isolated disposable Desktop/GUI environment.
5. Since generating a Desktop fixture by pretending CLI/version output is fixture evidence would overclaim #22, Package 3B is required.

## Safety notes

- No owner/private/working/only-copy book was opened, copied, searched, or mutated.
- No GnuCash book, SQLite DB, app DB, backup, CSV export, screenshot, private path, account name, memo, amount, `.env`, token, key, or cert was created or committed.
- `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` posture was unchanged.
