# Issue #22 package 3B manual blocker packet

Status: complete. Package 3A was not run because Package 2 returned `DESKTOP_FIXTURE_ENV_MISSING_GUI_OR_XVFB`.

Decision for this package: keep #22 open with exact external/manual blocker and next steps.

## Why Package 3A was skipped

The current environment has GnuCash 5.14 CLI/Desktop commands installed, but it lacks an active graphical display and lacks `xvfb-run`, `Xvfb`, and `xdotool` on `PATH`. `gnucash-cli --help` did not expose a safe noninteractive command to create/save a new SQLite book from scratch. Therefore Desktop-generated fixture evidence cannot be produced safely here without adding GUI/Xvfb tooling or using a separate isolated manual Desktop environment.

## Manual-safe packet created

Created:

- `docs/compatibility/desktop-synthetic-fixture-runbook.md`

The runbook includes:

- exact prerequisites for an isolated disposable GnuCash Desktop GUI environment;
- forbidden private/source-only/owner data boundaries;
- minimal synthetic account/transaction requirements;
- outside-git raw fixture handling;
- redacted metadata collection command;
- fail-closed preflight command and expected output shape;
- default-read-only validation commands with `GNUCASH_WRITES_ENABLED=false`;
- what may and may not be committed;
- GitHub #22 update templates for success or blocker.

## External blocker wording

#22 remains open because this environment cannot safely create the Desktop-generated synthetic SQLite fixture. Exact missing prerequisite: a working isolated disposable GnuCash Desktop GUI/Xvfb/manual-safe session capable of creating and saving a new synthetic SQLite book. GnuCash CLI availability and version output are not fixture evidence.

## Safety/privacy result

- No GnuCash book was opened, copied, generated, or mutated.
- No owner/private/source-only path was scanned or used.
- No raw DB, app DB, backup, export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw evidence was committed.
- Writes remain disabled by default.
- `APP_ENV=test` write-route gating remains unchanged.
