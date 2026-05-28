# Phase 764 — phase 764 restore failure drill

Goal: execute roadmap Phase 764 exactly within the Phase 731–830 run.

Scope: safe repository, GitHub, documentation, local test, and non-private synthetic evidence only. PM invoked: no using docs/agents/project-lead.md authority.

Non-goals: no Phase 831+, no private/raw book evidence, no public write beta, no production/security-audited claim, no real working-book mutation without exact same-context owner confirmation plus PM authorization.

Acceptance criteria: phase artifact created, safety boundary stated, and outcome reconciled with live GitHub/repo evidence.

Safety checks:
- GNUCASH_WRITES_ENABLED=false remains the default.
- APP_ENV=test write gate is not weakened.
- No .env, app DB, GnuCash book, backup, export, screenshot, account name, memo, description, amount, private path, token, or raw private evidence is committed.

Verification: local checks and GitHub/release state are recorded in Phase 825/827/830 artifacts.

Verdict: Restore/default-reset missing proof hard-stops synthetic session.
