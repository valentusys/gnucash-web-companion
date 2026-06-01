# Issue #43 work package 1 — baseline and blocker confirmation

- goal: Confirm live repo, GitHub issue, release posture, and exact blocker before code changes.
- scope: inspected issue #43, release list, existing issue #43 docs, helper code, AuditLog model.
- non-goals: no mutation, no release, no broad roadmap.
- acceptance criteria: blocker reconfirmed as local evidence-helper audit payload field-name handling; current model field is `AuditLog.payload_json`; latest release remains `v0.5.0-public-readonly-beta`; issue #43 remains open.
- safety checks: git status showed only pre-existing untracked `.hermes/`; no private artifacts staged; default write-disabled posture checked in source.
- verification: `gh issue view 43`, `gh release list --limit 20`, code review of `apps/api/app/models/__init__.py` and helper/tests.
- artifacts: this file; `docs/audits/issue-43-blocker-reconfirmation.md`.
- verdict: CONTINUE.
