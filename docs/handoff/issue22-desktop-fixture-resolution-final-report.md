# Issue #22 Desktop fixture resolution final report

Date: 2026-06-04

## Decision

CLOSE_22_NARROW_DESKTOP_SYNTHETIC_SQLITE_EVIDENCE_ONLY

## What was completed

- Audited issue #22, compatibility docs, fixture workflow docs, validator scripts, public status guard,
  and prior handoff/status docs.
- Installed isolated GUI automation prerequisites after explicit operator approval.
- Ran GnuCash 5.14 Desktop in an isolated Xvfb session with isolated home/config/cache paths.
- Created a disposable synthetic SQLite GnuCash book outside git.
- Collected redacted compatibility metadata only.
- Ran the fail-closed Desktop fixture preflight on redacted candidate metadata.
- Ran default-read-only service validation with `GNUCASH_WRITES_ENABLED=false` and verified the book
  checksum was unchanged.
- Updated public compatibility/status guard wording to allow #22 closure only as narrow synthetic
  Desktop fixture evidence, while still blocking broad Desktop/backend support claims.

## Fixture source / generation method

Raw fixture path was outside git under `/tmp` and was not committed.

Observed generation environment:

- `gnucash-cli --version`: GnuCash 5.14 / Build ID 5.14+(2025-12-20)
- `gnucash`: GnuCash Desktop launched in isolated Xvfb
- GUI automation: `Xvfb`, `xvfb-run`, `xdotool`
- Fixture origin marker: `desktop-generated-synthetic`
- Fixture scope: synthetic/disposable
- Backend: SQLite
- Raw book/app DB/screenshots/logs: outside git only, not committed

## Redacted metadata summary

The collector output recorded only redacted/safe metadata:

- backend: SQLite
- fixture origin: desktop-generated-synthetic
- Desktop version evidence: GnuCash 5.14
- `versions` markers: `Gnucash = 3000000`, `Gnucash-Resave = 19920`
- selected safe table counts only
- no row data, private paths, account names, transaction descriptions, memos, amounts, app DBs,
  backups, CSV exports, screenshots, secrets, keys, tokens, or certificates

## Validators run

Local validation run on 2026-06-04:

- `python3 apps/api/scripts/collect_gnucash_compatibility_metadata.py <outside-git-fixture>
  --gnucash-version "GnuCash 5.14" --fixture-origin desktop-generated-synthetic --output <tmp-json>`
  — passed
- `python3 scripts/preflight_desktop_fixture_candidate.py <redacted-candidate-json>` — passed:
  accepted true, backend SQLite, default-read-only validation passed
- default-read-only service smoke with `GNUCASH_WRITES_ENABLED=false` — passed:
  `check_connection=true`, `account_count=63`, `transaction_count=0`, summary/report paths opened,
  checksum unchanged (`4682a6360687dfe565d8b6a4e438812aefbcb5d0c9d007aa1c963f09c3f42982` before
  and after)

## Safety/privacy summary

- No original/private/working/only-copy GnuCash book was touched.
- No owner/private book was used as input or fixture evidence.
- No GnuCash book, SQLite DB, app DB, backup, CSV export, screenshot, `.env`, token, key, cert,
  private path, account name, transaction description, memo, amount, or raw evidence was committed.
- No copied-book dogfood was performed.
- No real working-book mutation was performed.
- `GNUCASH_WRITES_ENABLED=false` default remains preserved.
- `APP_ENV=test` and fail-closed write gates remain preserved.
- No release, tag, package, or image was published.

## Issue update links

- #22: https://github.com/valentusys/gnucash-web-companion/issues/22
- #36 remains open: https://github.com/valentusys/gnucash-web-companion/issues/36

## Release impact on #36 / v0.4 owner-writebeta

- #22 closure is narrow read-only synthetic Desktop SQLite evidence only.
- PostgreSQL/MySQL/MariaDB GnuCash backends remain unclaimed.
- Broad GnuCash Desktop version support is not claimed.
- Supported-version write compatibility remains pending for #36.
- The W3 copied-book write dogfood acceptance remains narrow evidence for #36 only.
- v0.4.0-owner-writebeta remains not prepared and not published.
