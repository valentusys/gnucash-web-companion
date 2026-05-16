# Phase 13 Handoff — Agent Project Context

## Status

Phase 13 adds persistent repository-level context for future Hermes and coding-agent sessions.

## Scope

Created:

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-13.md`

## What changed

### AGENTS.md

Added concise but actionable project instructions covering:

- project architecture and stack
- key architecture decisions
- controlled write safety rules
- security and financial-data handling rules
- standard backend/frontend/Docker/GitHub commands
- sequential phase workflow
- coding rules

Important workflow note added:

- One agent executes phases sequentially.
- Do not rely on `delegate_task` for this project workflow unless explicitly requested.

### PROJECT_STATUS.md

Added a durable status summary with:

- completed phases through Phase 12
- Phase 13 current status
- standing constraints
- standard verification commands
- GitHub tooling status

## GitHub tooling check

Commands checked:

```bash
git --version
gh --version
gh auth status
```

Result:

- `git` is installed.
- `gh` is not installed (`command not found`).
- Because `gh` is unavailable, GitHub issue create/update automation is blocked for this phase.
- Push can still proceed through existing git credentials if available.

## Verification

Relevant docs-only checks:

```bash
git status --short
git diff --check
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
```

No backend/frontend code changed in this phase, so full test/build suites are not required for the content itself. Run full suites if later phases modify code.

## Follow-up

Optional future improvement:

- Install and authenticate GitHub CLI (`gh`) if issue automation is required from this machine.
