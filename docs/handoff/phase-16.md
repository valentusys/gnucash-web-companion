# Phase 16 Handoff — Project Lead Subagent Profile

## Status

Complete pending commit/push.

## Summary

Analyzed the shared ChatGPT task context. It described Phase 15 public pre-alpha release readiness, the read-only MVP boundary, write-gating, release checklist, GitHub backlog, and the next recommended work.

Based on that, created a durable Project Lead / Руководитель проекта profile for future Hermes sessions and subagent use.

## Created

- `docs/agents/project-lead.md`
- Hermes skill: `gnucash-web-companion-project-lead`

## Updated

- `AGENTS.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-16.md`

## Project Lead responsibility

The Project Lead should:

- plan phases
- prepare phase briefs
- manage backlog/release guidance
- review product positioning
- check safety boundaries
- prevent scope drift
- keep MVP v0.1 read-only by default
- keep controlled writes experimental/post-MVP

The Project Lead should not:

- act as the normal coding implementer
- spawn further subagents
- enable writes by default
- weaken safety/release language
- add collaborative accounting or family-wallet positioning

## Safety status

- MVP read-only boundary preserved: yes
- `GNUCASH_WRITES_ENABLED=false` preserved: yes
- no production-readiness claim added: yes
- no real financial data added: yes
- no secrets added: yes

## Verification

Relevant checks for this docs/skill-only phase:

- `git diff --check`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`

## GitHub automation

As of Phase 15/16:

- `git` works
- `gh` is not installed
- no `GITHUB_TOKEN` is available in the environment
- GitHub issue/label/milestone automation remains blocked unless `gh` or API auth is configured

## Next recommended phase

Phase 17 — use the Project Lead profile to produce a concrete Phase 16/17 execution brief for synthetic GnuCash fixture and real read-only integration validation.

Alternative if continuing implementation directly:

Phase 16 — Synthetic GnuCash fixture and real read-only integration validation.
