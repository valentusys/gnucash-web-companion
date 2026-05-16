# Security Model

> Status: placeholder / pre-alpha. This is a policy direction, not a completed security audit.

## Threat model summary

The app handles sensitive financial data. The main threats are:

- Unauthorized access to the web UI/API.
- Accidental exposure to the public internet.
- Leakage of GnuCash book files or metadata DB files.
- Credential/secret leakage through commits, logs, or environment dumps.
- Future write-mode data corruption or unauthorized mutation.

## Early deployment guidance

Do not expose early versions publicly. Run only on trusted private networks or behind a hardened reverse proxy with authentication and HTTPS.

## Secrets

- Never commit `.env` or real credentials.
- Use environment variables or a secrets manager.
- Rotate immediately if a secret is committed accidentally.

## Data separation

- GnuCash book: authoritative accounting data.
- App metadata DB: preferences/cache/saved filters only.
- These must be separate files/databases.

## MVP security posture

MVP is read-only, but still sensitive because read access exposes financial data.

Required before production claims:

- Authentication model documented and implemented.
- HTTPS/reverse proxy guide.
- Dependency scanning.
- CSRF/XSS review.
- No secrets in logs.
- Backup/restore guidance.

No production-readiness guarantee is made at this stage.
