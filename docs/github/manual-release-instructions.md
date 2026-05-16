# Manual GitHub Release Instructions

`gh` is not installed in the current environment, so the tag can be pushed with git but the GitHub pre-release must be created manually unless GitHub CLI/API auth is configured later.

## Create pre-release in GitHub UI

1. Open the repository on GitHub.
2. Go to Releases.
3. Click "Draft a new release".
4. Select tag `v0.0.1-prealpha`.
5. Title: `v0.0.1-prealpha`.
6. Paste the contents of `docs/release/v0.0.1-prealpha-notes.md`.
7. Check "Set as a pre-release".
8. Publish release.

## Safety reminder

Do not claim production readiness or audited security. Keep the read-only/default-disabled write boundary explicit.
