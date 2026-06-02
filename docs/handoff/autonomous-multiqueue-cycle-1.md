# Autonomous multiqueue cycle 1 — #22 compatibility blocker refresh

## Queue

- Issue: #22 Add compatibility fixtures from real GnuCash versions
- PM package: refresh the maintainer-facing Desktop-generated fixture checklist and record the current local blocker without opening any GnuCash book.

## Scope

- Re-run the safe Desktop tooling probe.
- Update the compatibility fixture plan with the exact current evidence boundary.
- Keep #22 open unless a tested Desktop-generated synthetic SQLite fixture exists.

## Non-goals

- No user/private/original/only-copy book access.
- No GUI Desktop fixture creation in this headless session.
- No broad GnuCash compatibility claim.
- No release/tag/package publication.

## Evidence

Safe probe command:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py --include-install-hints --output /tmp/gwc-gnucash-tooling-probe.json
```

Observed safe output summary:

- `desktop_tooling_available=true`.
- `gnucash-cli --version` succeeded with `GnuCash 5.14` / `Build ID: 5.14+(2025-12-20)`.
- `gnucash --version` did not produce Desktop fixture evidence because GUI initialization failed in the headless environment: missing `$DISPLAY`.
- `desktop_generated_fixture_possible_now=false`.
- No GnuCash book was opened and no user directories were searched.

## Result

#22 remains open. The next safe step is still an isolated disposable GUI/manual-safe Desktop fixture creation path, followed by redacted metadata collection and read-only validation. The current session can provide command/version evidence, but not a Desktop-generated synthetic SQLite fixture.

## Verification

Pending for this package: documentation diff check and focused markdown/status checks after the doc update.

## Safety

- GnuCash mutations: CREATE 0 / PATCH 0 / DELETE 0.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- No private paths, account names, transaction descriptions, memos, amounts, screenshots, app DBs, backups, or books were committed.
