# GitHub Release Automation Notes

Status: automated for `v0.0.1-prealpha`.

`gh` is installed in the user environment (`~/.local/bin/gh`) and authenticated for the repository owner account. The GitHub pre-release for tag `v0.0.1-prealpha` was created with GitHub CLI.

Release URL:

```text
https://github.com/valentusys/gnucash-web-companion/releases/tag/v0.0.1-prealpha
```

## Recreate or update with gh

```bash
gh auth status
gh release view v0.0.1-prealpha
# If needed later:
gh release edit v0.0.1-prealpha --notes-file docs/release/v0.0.1-prealpha-notes.md --prerelease
```

## Safety reminder

Do not claim production readiness or audited security. Keep the read-only/default-disabled write boundary explicit.
