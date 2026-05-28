# Roadmap

Status after Phase 480: Completed through Phase 480 with final NO_RELEASE. Current public releases remain `v0.1.7-readonly` and `v0.2.8-writealpha`; the current write-alpha release baseline remains Phase 261. `GNUCASH_WRITES_ENABLED=false` remains the default.

## v0.4.0-owner-writebeta

Goal: owner-safe write beta under an integrated, recoverable, owner-controlled workflow.

Current state: deferred. Non-mutating preflight, redacted manifest and UI warning prototype were added, but PM blocked copied-book mutation for this run and real working-book mutation remains blocked.

Exit criteria: see `docs/strategy/v0.4-owner-writebeta-exit-criteria.md`.

## v0.5.0-public-readonly-beta

Goal: public-facing read-only beta for careful external testers.

Current state: deferred. Public install/security/feedback docs were drafted, but an actual fresh-clone read-only smoke and full release gate are still required.

Exit criteria: see `docs/strategy/v0.5-public-readonly-beta-exit-criteria.md`.

## Explicitly not now

- stable/production release;
- security-audited or public-internet safety claim;
- public write beta;
- only-copy or original-book write safety claim;
- Phase 481+ planning without a concrete owner bug, blocker or milestone.
