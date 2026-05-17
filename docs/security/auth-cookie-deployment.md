# Authentication Cookie and Deployment Security

> **Pre-alpha disclaimer:** This document describes the current authentication
> cookie behaviour of a pre-alpha application. It has not been independently
> audited. The security properties described here are best-effort and may change.
> **Do not rely on this application for production security.**

## Cookie attributes

The `access_token` cookie is set by the SvelteKit login handler
(`apps/web/src/routes/login/+page.server.ts`) with the following attributes:

| Attribute   | Value                                   | Purpose                                                |
|-------------|-----------------------------------------|--------------------------------------------------------|
| `httpOnly`  | `true`                                  | Prevents JavaScript access; mitigates XSS token theft. |
| `secure`    | `true` on HTTPS, `false` on HTTP       | On `https:` origins the cookie is only sent over TLS.  |
| `sameSite`  | `lax`                                   | Cookie is not sent on cross-origin POST requests.      |
| `path`      | `/`                                     | Cookie is sent with every request to the application.   |
| `maxAge`    | `1800` (30 minutes, matching JWT expiry)| Browser deletes the cookie after the JWT expires.       |

The cookie stores a JWT issued by the FastAPI `/auth/login` endpoint. The JWT
is signed with `JWT_SECRET` and expires after `jwt_token_expire_minutes`
(default 30).

## Stateless JWT logout model

The backend `/auth/logout` endpoint returns `{"status": "ok"}` but does **not**
maintain a server-side token blacklist. Logout is completed entirely by the
frontend deleting the `access_token` cookie.

Consequences:

- The JWT remains cryptographically valid until it expires (max 30 minutes).
- If an attacker has already captured the token, it can still be used until
  expiry. There is no server-side revocation.
- This is a deliberate trade-off for a self-hosted, single-user MVP.

## Local development behaviour

When running on `http://localhost` (or any non-HTTPS origin), the `secure`
attribute is `false`. This means the cookie is sent over plain HTTP, which is
acceptable for local development but **must not be used in production**.

## Self-hosted deployment warning

If you deploy this application yourself:

1. **Use HTTPS.** The `secure` cookie flag is only set on `https:` origins.
   Without HTTPS the JWT cookie is transmitted in cleartext.
2. **Do not expose directly to the public internet.** This is a pre-alpha
   application with no WAF, rate-limiting, or DDoS protection.
3. **Set a strong `JWT_SECRET`.** The placeholder value in `.env.example` is
   intentionally rejected by the API. Use a random 32+ byte secret.
4. **Keep `GNUCASH_WRITES_ENABLED=false`** unless you explicitly need
   post-MVP write features and have tested backups.
5. **Treat the admin password as sensitive.** The bootstrap admin password is
   stored as a hash in the app metadata DB, but the `.env` file may contain
   the plaintext bootstrap value.

## No production security guarantee

This application is **pre-alpha software**. It has not been audited, penetration
tested, or certified for any security standard. The cookie settings described
here are reasonable defaults for a self-hosted tool, but they do **not** provide
a production security guarantee.

Use at your own risk. Always maintain tested backups of your GnuCash data.
