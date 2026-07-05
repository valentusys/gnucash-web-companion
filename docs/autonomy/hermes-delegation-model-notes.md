# Hermes delegation model notes

Date: 2026-07-05
Scope: Hermes subagent/delegation configuration for future long-run work in this repository.

This note is operational documentation only. It does not change product code, GnuCash data, write-mode behavior, or release posture.

## Incident

During an autonomous #48 run, `delegate_task` subagents were routed to:

```yaml
delegation:
  provider: openrouter
  model: openrouter/owl-alpha
```

The model endpoint failed with 404s and transient connection errors, including:

```text
HTTP 404: No endpoints found for openrouter/owl-alpha.
```

The main parent agent was already using the working Codex model, but the explicit `delegation.*` override took precedence for child agents. That made every subagent fail before doing useful work.

## Model source rules

Hermes delegation resolves subagent model settings as follows:

1. If `delegation.provider` / `delegation.model` are configured, subagents use that override.
2. If those keys are empty/omitted, subagents inherit the parent model/provider/credentials.
3. `delegate_task` does not accept a per-call model override; the model is controlled by config or parent inheritance.
4. Config changes in a running Hermes TUI session may not affect already-loaded runtime config until a fresh session/restart. Verify with a canary before long fan-out.

## Current recommended setting

For this workspace, subagents should use the same known-working Codex model family as the parent:

```yaml
delegation:
  provider: openai-codex
  model: gpt-5.5
```

Alternative if the operator wants true parent inheritance after changing models often:

```yaml
delegation:
  provider: ""
  model: ""
```

Either option is safer than pinning subagents to `openrouter/owl-alpha`.

Keep these safety controls unless there is a specific reason to change them:

```yaml
delegation:
  max_concurrent_children: 3
  max_spawn_depth: 1
  subagent_auto_approve: false
```

## Canary before long-run delegation

Before starting a multi-hour task that depends on subagents, run a one-child read-only canary from the repository root:

```text
Use delegate_task once. Child task: run only `git status --short --branch`, summarize one sentence, and do not write files.
```

Expected safe result:

```text
## main...origin/main
```

A successful canary proves the child can make model calls and run a read-only terminal command. It does not approve product writes or any GnuCash mutation.

## Fallback when canary fails

If the canary reports provider/model errors, `404`, `401`, `429`, or never returns a child summary:

1. Do not launch parallel subagents for the long run.
2. Switch to sequential main-agent workflow, or use a durable background `terminal(..., notify_on_complete=true)` command if appropriate.
3. Fix delegation config to either inherit the parent or use a known-working provider/model.
4. Restart/start a fresh Hermes session if the old TUI session cached stale delegation config.
5. Re-run the canary before using multi-subagent fan-out.

## Privacy and safety constraints

- Do not put secrets, API keys, OAuth tokens, `.env` values, private book paths, account names, amounts, GUIDs, or screenshots in this document.
- Do not commit `~/.hermes/config.yaml`, `~/.hermes/.env`, auth files, tokens, or runtime logs.
- Delegation config changes are user-level Hermes config, not repository state.
- A delegation canary is read-only and does not approve CREATE, PATCH, DELETE, batch operations, or any GnuCash book mutation.
