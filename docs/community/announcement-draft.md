# Announcement Draft — gnucash-web-companion

> Draft only. Do not post without maintainer review.

## Short pitch

`gnucash-web-companion` is a modern self-hosted, read-only-first web companion for existing GnuCash SQL books. It lets you browse accounts, transactions, dashboards, basic reports, and CSV exports from a browser while keeping GnuCash Desktop as the authoritative editor.

## Audience

This may be useful for people who:

- already use GnuCash and want browser/mobile read-only access on their own infrastructure;
- want a conservative self-hosted companion instead of a hosted finance SaaS;
- are comfortable testing pre-alpha software against a disposable copy of a GnuCash book;
- care about keeping app metadata separate from the GnuCash book.

This is not for people who need:

- production-ready accounting software;
- audited security guarantees;
- collaborative multi-user editing;
- banking integrations or CSV/OFX imports;
- safe write-mode access to their only copy of a GnuCash book.

## Current status

- Pre-alpha / MVP in progress.
- Read-only by default.
- First public pre-alpha release exists: `v0.0.1-prealpha`.
- `v0.0.2-prealpha` candidate notes exist, but no tag/release has been published yet.
- Controlled-write code exists only as experimental post-MVP work and remains disabled by default with `GNUCASH_WRITES_ENABLED=false`.

## Safety notes to include in any announcement

- Use a disposable/test copy first.
- Keep regular tested backups.
- Do not expose early builds directly to the public internet.
- Do not enable write mode against your only GnuCash book.
- This is not production-ready and not security-audited.

## Comparison notes

- Compared with `gnucash-web`, this project starts read-only-first and uses FastAPI/SvelteKit rather than Flask/Bootstrap.
- Compared with GnuDash, this project is server-side/self-hosted with piecash behind a backend service layer, not a browser-WASM/import/export app.
- Compared with Fava/Beancount, this project targets existing GnuCash SQL books instead of Beancount text ledgers.

## Suggested announcement text

Hello GnuCash/self-hosted community — I’m building `gnucash-web-companion`, a pre-alpha self-hosted web companion for existing GnuCash SQL books.

The goal is intentionally narrow: read-only browser/mobile access to accounts, transactions, dashboards, basic reports, and CSV export, while GnuCash Desktop remains the authoritative editor.

This is not production-ready, not security-audited, and not a GnuCash replacement. Please test only with a disposable copy first. Controlled write code is experimental post-MVP work and disabled by default.

Repository: https://github.com/valentusys/gnucash-web-companion

Feedback wanted: read-only UX, deployment docs, GnuCash compatibility notes, test fixtures, and safety review.
