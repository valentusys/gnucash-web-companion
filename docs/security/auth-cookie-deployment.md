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
| `maxAge`    | `JWT_TOKEN_EXPIRE_MINUTES * 60` (30 minutes by default) | Browser deletes the cookie on the same schedule as the JWT expiry; invalid values fall back to 30 minutes. |

The cookie stores a JWT issued by the FastAPI `/auth/login` endpoint. The JWT
is signed with `JWT_SECRET` and expires after `jwt_token_expire_minutes`
(default 30).

The Docker Compose web service receives the same `JWT_TOKEN_EXPIRE_MINUTES`
value as the API so the browser cookie lifetime tracks the signed token
lifetime instead of silently staying at a hard-coded 30 minutes.

## Same-origin state-changing routes

SvelteKit rejects unsafe state-changing app requests (`POST`, `PUT`, `PATCH`,
`DELETE`, and other non-safe methods) when a browser `Origin` header is present
and does not match the current app origin. This is a narrow pre-alpha local/LAN
guard for form actions such as login, logout, locale switching, and hidden
write-alpha routes. It complements `sameSite=lax`; it is not a production CSRF
certification or a substitute for keeping the app off the public internet.

Requests without an `Origin` header are allowed to avoid breaking local probes
and reverse-proxy health checks, but browser form submissions are expected to
send an origin.

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
