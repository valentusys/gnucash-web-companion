# Write-alpha compatibility check harness

Phase 256 adds `scripts/write_alpha_compatibility_check.py`, a local-only, best-effort check that can run after a copied/disposable write-alpha mutation.

## Purpose

The harness answers only this narrow question:

> Can this already-mutated synthetic/disposable or maintainer-copied test book be opened read-only with piecash, and can already-available GnuCash CLI tooling read it through a non-mutating report command?

It does not prove broad GnuCash Desktop compatibility. One successful run is not evidence for all GnuCash versions, backends, platforms, real/private books, production use, or only-copy safety.

## Safety boundary

Use only:

- synthetic/disposable fixture copies; or
- maintainer-created copied/restorable test books outside git, after preflight and backup.

Do not use:

- the original/source book;
- the only existing copy;
- real/private books inside this repository;
- committed app DBs, backups, screenshots, CSV exports, tokens, keys, certs, or raw evidence with financial data.

The harness opens the target read-only with piecash. If `gnucash-cli` is already available on `PATH`, it also runs a bounded non-mutating report command. It does not install GnuCash Desktop or any heavy tool.

## Command

```bash
python3 scripts/write_alpha_compatibility_check.py \
  /outside/git/copied-disposable-book.gnucash.sqlite \
  --output /outside/git/redacted-phase-256-compatibility.json
```

The committed docs intentionally show placeholder paths only. Do not commit operator evidence that contains raw paths.

## Result semantics

- `pass` — piecash read passed and already-available `gnucash-cli` report command exited successfully.
- `blocked` — piecash read passed, but `gnucash-cli` was unavailable on `PATH`; Desktop/CLI compatibility evidence remains blocked.
- `fail` — piecash read failed, or `gnucash-cli` was available but the non-mutating report command failed or timed out.

## Redaction contract

The JSON evidence records only bounded metadata:

- result/status values;
- object counts;
- whether Desktop tooling was available;
- redacted command shape;
- explicit `broad_compatibility_claimed=false`.

It excludes:

- raw filesystem paths;
- account names;
- transaction descriptions;
- split memos;
- amounts;
- Desktop/CLI stdout/stderr.

## Maintainer packet placement

For copied-book dogfood, run this only after the create-only mutation step and before restore verification:

1. preflight;
2. independent backup;
3. dry-run first;
4. at most one CREATE test transaction when explicitly continuing;
5. compatibility harness;
6. restore verification;
7. cleanup and reset to `GNUCASH_WRITES_ENABLED=false`.
