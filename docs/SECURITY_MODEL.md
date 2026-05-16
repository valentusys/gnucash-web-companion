# Security Model

> **Status: pre-alpha.** This document describes the intended security posture. It is not a completed security audit and does not imply production readiness.

## Threat model summary

The app handles sensitive financial data. Primary risks:

- Unauthorized access to the web UI/API.
- Accidental exposure to the public internet.
- Leakage of GnuCash book files, backups, screenshots, logs, or metadata DB files.
- Credential/secret leakage through commits, logs, environment dumps, or CI.
- Future write-mode data corruption or unauthorized mutation.

## Current security posture

Implemented foundations:

- Basic app authentication.
- Password hashing for stored app-user passwords.
- JWT-based API auth.
- Frontend stores the token in an httpOnly cookie, not `localStorage` or `sessionStorage`.
- App metadata is stored separately from the GnuCash book.
- GnuCash access is read-only-first through a service layer.
- `.gitignore` blocks common local secrets, book files, and backups.
- CI checks for accidentally tracked sensitive paths.

Still not guaranteed:

- No formal security audit.
- No production hardening claim.
- No complete CSRF/XSS review claim.
- No public-internet deployment recommendation.

## Early deployment guidance

Do not expose pre-alpha builds directly to the public internet. Run only on trusted private networks or behind a hardened reverse proxy with HTTPS and access restrictions.

## Secrets

- Never commit `.env` or real credentials.
- Generate a strong `JWT_SECRET` before any non-local testing.
- Prefer `APP_ADMIN_PASSWORD_HASH` over plaintext bootstrap passwords.
- Use environment variables or a secrets manager.
- Rotate immediately if a secret is committed accidentally.

## Data separation

- GnuCash book: authoritative accounting data.
- App metadata DB: users, book registry, access metadata, and app state.
- These must remain separate files/databases.
- Do not store app users, access roles, sessions, saved UI state, or audit logs inside the GnuCash book.

## Financial data handling

- Treat `.gnucash`, `.sqlite`, `.sqlite3`, backup, export, and screenshot files as sensitive.
- Use fixture or copied books for testing.
- Do not upload real books to issues, PRs, CI artifacts, or public logs.
- Do not add telemetry.

## Required before production claims

- HTTPS/reverse proxy deployment guide validated on a clean host.
- CSRF review for all cookie-authenticated flows.
- XSS review for all rendered transaction/account text.
- Dependency scanning policy.
- Backup/restore guidance.
- Security review of Docker images and runtime configuration.
- Reproducible test fixture strategy for GnuCash no-mutation checks.

No production-readiness guarantee is made at this stage.
