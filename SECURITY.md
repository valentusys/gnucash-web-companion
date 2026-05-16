# Security Policy

## Reporting vulnerabilities

If you discover a security vulnerability in `gnucash-web-companion`, please report it responsibly:

1. **Do not** open a public GitHub issue for the vulnerability.
2. **Email** the maintainers directly at: `[SECURITY_CONTACT_EMAIL]` *(placeholder — replace with a real address before publishing)*.
3. Include a clear description of the vulnerability, steps to reproduce, and any relevant environment details.
4. Allow a reasonable time for the maintainers to respond and address the issue before public disclosure.

We appreciate your help in keeping this project and its users safe.

## ⚠️ Do not expose early versions publicly

`gnucash-web-companion` is in **pre-alpha / early development**. It has not undergone a security audit. **Do not:**

- Expose this application to the public internet.
- Deploy it in a production environment.
- Use it with real financial data without thorough testing and backups.
- Assume it is hardened against common web attacks (CSRF, XSS, injection, etc.).

Treat early versions as **development-only** tools running on trusted, private networks.

## Secrets handling

- **Never commit secrets** (API keys, database credentials, session secrets, etc.) to the repository.
- Use environment variables or a secrets manager. See `.env.example` for the expected configuration variables.
- The `.gitignore` file excludes `.env` — do not override this.
- If you accidentally commit a secret, rotate it immediately and notify the maintainers.

## Financial data sensitivity

This application is designed to read GnuCash books, which contain **highly sensitive personal or business financial data**. Consider:

- **Data at rest:** The GnuCash book and the app metadata database should be stored on encrypted storage where feasible.
- **Data in transit:** Always serve the application over HTTPS (via a reverse proxy or TLS termination).
- **Access control:** Restrict access to the application to authorized users only. Do not rely on obscurity.
- **Backups:** Maintain regular, tested backups of your GnuCash book. This application should never be your only copy of financial data.

## No guarantee of production readiness

This project is provided as-is, without warranty of any kind. It is **not guaranteed to be production-ready** at this stage. Use at your own risk, and always maintain independent backups of your data.
