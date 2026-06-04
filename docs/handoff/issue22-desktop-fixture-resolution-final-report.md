# Issue #22 Desktop fixture resolution final report

Date: 2026-06-04

## Decision

KEEP_22_OPEN_WITH_EXACT_EXTERNAL_BLOCKER_AND_NEXT_MANUAL_STEPS

## What was attempted

- Audited issue #22, current issue state, compatibility docs, fixture workflow docs, validator scripts, public status guard, and prior handoff/status docs.
- Inspected installed GnuCash Desktop/CLI tooling without opening, copying, scanning, or mutating any GnuCash books.
- Checked whether a safe headless GUI/Xvfb path exists for creating a disposable Desktop-generated synthetic SQLite fixture.
- Checked whether `gnucash-cli` exposes a safe noninteractive create/save SQLite command suitable for fixture generation.
- Created a manual-safe runbook for producing the missing Desktop-generated synthetic fixture in an isolated environment.
- Added fail-closed public-status guard coverage to prevent overclaiming #22 closure or Desktop-generated fixture evidence.
- Updated #22 with the exact blocker and next manual steps.

## Fixture source / generation method

No fixture was generated in this session.

Reason: this host has GnuCash tooling but lacks a safe disposable Desktop GUI/Xvfb automation environment.

Observed environment:

- `gnucash-cli --version`: GnuCash 5.14 / Build ID 5.14+(2025-12-20)
- `gnucash`: installed, but no display is available for safe Desktop initialization
- `DISPLAY`: unset
- `WAYLAND_DISPLAY`: unset
- `xvfb-run`: missing
- `Xvfb`: missing
- `xdotool`: missing
- safe noninteractive SQLite fixture create/save command: not found

Manual fixture generation instructions were added at:

- `docs/compatibility/desktop-synthetic-fixture-runbook.md`

## Validators run

Local validation run on 2026-06-04:

- `python3 scripts/check_public_status.py` — passed
- `python3 scripts/check_markdown_readability.py` — passed, 10 docs checked
- `python3 scripts/check_tracked_hygiene.py` — passed, 1826 tracked paths inspected
- `git diff --check` — passed
- focused guard regression test — passed

No Desktop fixture validator was run against a new fixture because no fixture was safely created.

## Tests run

Package 6 local gate:

- `cd apps/api && pytest -q` — 761 passed, 38 warnings
- `cd apps/web && npm run check` — 0 errors, 0 warnings
- `cd apps/web && npm run test:auth-routes` — passed
- `cd apps/web && npm run build` — passed
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed
- `python3 scripts/check_public_status.py` — passed
- `python3 scripts/check_markdown_readability.py` — passed
- `python3 scripts/check_tracked_hygiene.py` — passed
- `git diff --check` — passed

## Safety/privacy summary

- No original/private/working/only-copy GnuCash book was touched.
- No owner/private book was used as input or fixture evidence.
- No GnuCash book, SQLite DB, app DB, backup, CSV export, screenshot, `.env`, token, key, cert, private path, account name, transaction description, memo, amount, or raw evidence was committed.
- No copied-book dogfood was performed.
- No real working-book mutation was performed.
- `GNUCASH_WRITES_ENABLED=false` default remains preserved.
- `APP_ENV=test` and fail-closed write gates remain preserved.
- No release, tag, package, or image was published.

## Issue update links

- #22 remains open: https://github.com/valentusys/gnucash-web-companion/issues/22
- #22 blocker comment: https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4618312615
- #36 remains open: https://github.com/valentusys/gnucash-web-companion/issues/36

## Commits

Commit to be created after this report is staged:

- `docs: record issue 22 desktop fixture blocker`

The final pushed SHA is recorded in the CLI final response and in git history.

## CI status

Local gates passed before commit.

GitHub state checked before commit:

- Open issues: #22 and #36
- Open PRs: none observed after retries
- Latest release remains `v0.5.0-public-readonly-beta`
- No `v0.5.1-public-readonly-beta` release observed
- No `v0.4.0-owner-writebeta` release observed

CI status after push must be checked against the pushed commit.

## Remaining blockers

#22 remains blocked by missing Desktop-generated synthetic SQLite fixture evidence.

Exact blocker:

- An isolated disposable GnuCash Desktop GUI/Xvfb/manual-safe environment must create and save a minimal synthetic SQLite GnuCash book outside git.
- Only redacted metadata, manifests, validator output, and safety docs may be committed.
- The fixture must use only generic synthetic accounts/data and must pass the preflight/read-only/fail-closed validation described in the runbook.

## Release impact on #36 / v0.4 owner-writebeta

- #36 remains open.
- The W3 copied-book write dogfood acceptance remains narrow evidence for #36 only; it does not close #22.
- v0.4.0-owner-writebeta remains not prepared and not published.
- The remaining #22 Desktop synthetic fixture blocker is still a release-confidence gap for broad compatibility/write-readiness claims.

## Exact next step

Owner/manual isolated Desktop fixture generation remains the blocker. Use `docs/compatibility/desktop-synthetic-fixture-runbook.md`, then update #22 with redacted validation output if the fixture is produced safely.
