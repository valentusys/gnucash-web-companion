# Security Policy

## Reporting vulnerabilities

If you discover a security vulnerability in `gnucash-web-companion`, please report it responsibly:

1. **Do not** open a public GitHub issue for the vulnerability.
2. Use GitHub's private vulnerability reporting / Security Advisory flow if it is enabled for the repository.
3. If private reporting is not available, contact the project owner privately before public disclosure.
4. Include a clear description, steps to reproduce, affected commit/version, and relevant environment details.
5. Allow a reasonable time for maintainers to respond and address the issue before public disclosure.

## Supported versions

This project is currently **pre-alpha**. There are no supported production releases yet.

Security fixes will target the `main` branch until versioned support policy is defined.

## Do not expose early versions publicly

`gnucash-web-companion` is in **pre-alpha / MVP in progress**. It has not undergone a security audit. Do not:

- Expose this application directly to the public internet.
- Deploy it in a production environment.
- Use it with real financial data without thorough testing and backups.
- Assume it is hardened against common web attacks.

Treat early versions as development-only or trusted-private-network tools.

## Secrets handling

- Never commit secrets, API keys, database credentials, JWT secrets, private keys, or real `.env` files.
- Use environment variables or a secrets manager.
- `.gitignore` excludes `.env`, common key/cert files, `secrets/`, and `credentials/`.
- If you accidentally commit a secret, rotate it immediately and notify maintainers.

## Financial data sensitivity

This application reads GnuCash books, which may contain highly sensitive personal or business financial data.

Recommended precautions:

- Test with a non-sensitive fixture or copy of your book first.
- Store GnuCash books and app metadata databases on encrypted storage where feasible.
- Serve the application over HTTPS behind a trusted reverse proxy if used beyond localhost.
- Restrict access to authorized users only.
- Maintain regular, tested backups of your GnuCash book.
- Do not commit real `.gnucash`, `.sqlite`, backup, or export files.

## Read-only boundary

The MVP is read-only-first, but that is not a guarantee that your operational setup is safe. Review [docs/GNUCASH_SAFETY.md](docs/GNUCASH_SAFETY.md) before using the app with real data.

## No production guarantee

This project is provided as-is, without warranty of any kind. It is **not guaranteed to be production-ready** at this stage. Use at your own risk.
