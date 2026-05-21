# Phase 259 — Owner copied-book decision gate

Date: 2026-05-21

Status: COMPLETE — owner copied-book decision gate completed with a dry-run-only recommendation.

## Summary

Phase 259 reviewed the Phase 258 synthetic copied-book package rehearsal, maintainer packet completeness, write-alpha ownership guards, restore harness, compatibility harness, and current known blockers.

Verdict:

- Ready to ask the owner for copied-book dry-run only.
- Not ready to ask for CREATE-one as the first owner action.
- CREATE-one can be considered only after owner dry-run evidence is reviewed and confirms preflight, independent backup, redaction, local-only runtime, restore plan, and reset to `GNUCASH_WRITES_ENABLED=false`.

## Artifacts

- `docs/audits/phase-259-owner-copied-book-decision.md`
- `docs/handoff/phase-259.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## Safety posture

- `GNUCASH_WRITES_ENABLED=false` remains the committed/default posture.
- The backend `APP_ENV=test` write-alpha gate was not changed or weakened.
- No owner/private/original/only-copy book was used or requested.
- No app DB, GnuCash book, backup, CSV, screenshot, `.env`, token, key, cert, raw path, account name, memo, amount, API payload, cookie, or private financial data artifact was committed.
- No release/tag was published.
- No production, security-audited, public-internet, broad Desktop/version compatibility, production disaster-recovery, or real/private/only-copy write-safety claim was added.

## Findings

- Phase 258 is strong enough to support a local owner dry-run ask: synthetic wrapper dry-run passed, synthetic create-one rehearsal passed, restore proof passed, disabled write probes returned 403 after reset, and committed evidence is redacted.
- Phase 258 is not enough to ask the owner for immediate mutation: no owner dry-run evidence exists yet, no owner local backup/restore/redaction proof exists yet, host `gnucash-cli` remained blocked for the compatibility harness, and browser evidence was not claimed.
- The dogfood packet is complete for dry-run and conservative for later CREATE-one: original/only-copy books are forbidden, outside-git copied/restorable targets and independent backup are required, DELETE is prohibited unless separately authorized, and reset to default false is required.
- Ownership guards remain suitable for copied-book dogfood: PATCH/DELETE require app metadata write-alpha ownership and do not authorize editing/deleting historical/manual transactions.
- Restore and compatibility harnesses remain bounded, redacted, local-only checks and do not prove production recovery or broad GnuCash Desktop compatibility.

## Verification performed

```bash
git status --short
git log --oneline -8 --decorate --no-color
gh issue list --state open --limit 50 || true
# safety greps for GNUCASH_WRITES_ENABLED, gnucash_writes_enabled, APP_ENV=test, localStorage/sessionStorage
python3 scripts/check_public_status.py
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
```

Results:

- Git status before edits: tracked tree clean; untracked repo-local `.hermes/` present and excluded.
- GitHub issue list attempt failed with a transient API connection reset; no issue mutation was attempted.
- Public status guard: PASS.
- Docker Compose config: PASS.
- Rendered Docker Compose default: `GNUCASH_WRITES_ENABLED=false` for API and web.
- Git whitespace check: PASS.

## GitHub issues

No new GitHub issue was created. The Phase 259 decision remains relevant to the existing controlled-write readiness umbrella (#36). The transient GitHub API issue prevented live issue listing during this phase, but no current finding requires a new issue.

## Next phase boundary

Phase 260 may decide whether the copied-book dogfood package merits a `v0.2.8-writealpha` release candidate or a no-release verdict. Phase 259 did not execute owner dogfood, ask for private data, authorize CREATE-one as the immediate owner action, publish a release, or claim real/private/only-copy write safety.
