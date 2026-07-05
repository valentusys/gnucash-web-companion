# Issue #48 deterministic synthetic browser smoke harness

Date: 2026-07-05
Issue: [#48 Owner web transaction-entry UI for CREATE + optional PATCH app-created metadata](https://github.com/valentusys/gnucash-web-companion/issues/48)
Verdict: **SYNTHETIC_BROWSER_SMOKE_PREVIEW_ONLY_NO_MUTATION**

## Scope

This slice adds a deterministic browser smoke harness for `/transactions/new`. It exercises the real SvelteKit route in
headless Chromium through a synthetic local API stub while `GNUCASH_WRITES_ENABLED=false` and `APP_ENV=test` are set.

The smoke is synthetic and redacted. It does not use a private, original, working, or only-copy GnuCash book. It does not
CREATE, PATCH, DELETE, or batch any transaction.

## Harness approach

The project did not already have Playwright or an e2e test stack. Instead of adding a large new dependency, the harness
uses Node's built-in WebSocket client to drive local Chromium through the Chrome DevTools Protocol:

- starts a synthetic in-process API stub;
- starts the existing Vite/SvelteKit dev server against that stub;
- sets a synthetic auth cookie;
- opens `/transactions/new` in a mobile-sized headless Chromium viewport;
- observes browser network requests and synthetic API calls;
- cleans up the Chromium profile, dev server, and stub after the run.

Command:

```bash
cd apps/web
npm run test:transaction-entry-preview-browser
```

## Covered preview-only states

The smoke verifies:

- the preview-only/no-write warning is visible;
- source and destination selectors are visible;
- synthetic account filtering works and search text is not submitted;
- the form submits only through the `/transactions/new` preview action;
- the server action calls only the backend `create-preview` route;
- normalized preview output is visible;
- the approval packet is visible;
- the approval packet states future CREATE requires fresh same-context owner approval and exact `CREATE count = 1`;
- the Future Create control remains disabled and inert;
- the approval template rendered in the browser is placeholder-only and omits preview values;
- the preview-reviewed checkbox can be checked locally;
- changing a field after preview shows the stale-preview warning and resets/disables the local review checkbox;
- the stale preview cannot support a future owner-approved CREATE;
- Clear preview / start over returns the page to the no-preview state;
- no browser-observed or synthetic API CREATE, PATCH, DELETE, or batch request is made.

## Guard relationship

`npm run test:transaction-entry-preview` remains the source/static guard for the route contract. It still fails if:

- `/transactions/new` gains an active create/write action;
- Future Create is enabled;
- `create-preview` stops being the only transaction-entry submission target;
- approval packet, stale-preview warning, no-write copy, or placeholder-only copy safety disappears.

The new browser smoke complements that guard by validating the rendered route and user flow against a synthetic stub.

## Safety summary

- CREATE: 0
- PATCH: 0
- DELETE: 0
- batch: 0
- no private-book dogfood
- no release, tag, package, image, or public write beta
- no production, stable, or security-audited claim
- no private paths, account names, descriptions, memos, amounts, GUIDs, screenshots, tokens, keys, certs, or `.env`
  values are included in this report

Future CREATE still requires fresh same-context owner approval, exact CREATE count, enabled write gates, and the existing
backup/read-back/audit/reset/probe requirements. DELETE, batch, historical/manual mutation, and balance-affecting PATCH
remain forbidden.
