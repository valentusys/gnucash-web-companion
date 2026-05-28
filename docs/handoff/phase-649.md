# Phase 649 — PM v0.5.x diagnostics release decision

Goal: PM v0.5.x diagnostics release decision.

Scope: Executed within the Phase 631–730 roadmap hard stop, using the repo PM safety posture.

Non-goals: No public write beta, no real/private working-book mutation, no private evidence, no stable/production claim.

Acceptance criteria: PM: include diagnostics in final public read-only patch candidate, not a separate immediate release.

Safety checks:
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No GnuCash book, app DB, backup, CSV export, screenshot, `.env`, secret, private path, account name, description, memo, amount, or raw private evidence is committed.
- Public beta wording remains read-only.

Verification: See `docs/release/phase-725-final-local-verification.md` and phase-specific docs for command evidence.

Expected artifacts: this handoff plus relevant code/docs created in the same run.

Final verdict: CONTINUE
