# Reproduction

## What `bash reproduce.sh` does

1. Runs `harness/run_benchmarks.sh` with `MEASUREMENT_OUTDIR` set to a fresh scratch directory (a `mktemp -d` that is deleted on exit). The vendored measurement logs in `outputs/` are **never** overwritten: they are the recorded evidence from the original run, and overwriting them with a new run's rates would silently change the evidence the docs cite.
2. Verifies every file listed in `SHA256SUMS` with `verify_digests.sh`.
3. Runs `scripts/check_measurements.py` against the scratch logs: every algorithm block present, every control PASS, every measured length equal to the FIPS/liboqs parameter table, implicit rejection 108/108, hybrid arithmetic (client + server = total) exact, wire bytes exact, dual-signature controls C-1..C-5 PASS.
4. Runs `scripts/check_excerpts.py` (without `--pin`: internal consistency of `data/source_excerpts.json`; with `--pin <checkout>`: every excerpt line re-verified against the checkout at the pinned commit).
5. Writes `outputs/reproduce_selfcheck.log` and prints `REPRODUCE OK`.

`outputs/reproduce_selfcheck.log` is deterministic: it contains only PASS/FAIL lines and digest-verification output — no timestamps, no absolute paths, no measured rates — so a fresh run regenerates it byte-identically. It is excluded from `SHA256SUMS` by design (it embeds the digest output and can never match its own recorded hash); verify it by byte-identical regeneration instead.

## Requirements

- A POSIX shell, `cc`, `cmake`, `git`, `python3`, OpenSSL (for the classical baseline).
- liboqs 0.14.0: `harness/run_benchmarks.sh` uses `~/liboqs` when its HEAD is the pinned commit `94b421ebb82405c843dba4e9aa521a56ee5a333d`; otherwise it clones tag 0.14.0 into `.deps/liboqs` (network) and builds from source. CI always builds from a fresh clone.
- Single thread throughout. Runtime: a few minutes (dominated by the 5 s sign/verify budgets per algorithm).

## Manual steps

```sh
# Full reproduction (measurements into scratch, digests, structural checks)
bash reproduce.sh

# Measurements only, into outputs/ (overwrites the vendored logs — do not
# do this on a released pack unless you intend to re-issue it)
sh harness/run_benchmarks.sh

# Digest check only
bash verify_digests.sh

# Structural check of a measurement run in <dir>
MEASUREMENT_OUTDIR=<dir> python3 scripts/check_measurements.py

# Excerpt check (internal consistency)
python3 scripts/check_excerpts.py
# Excerpt check against a pinned checkout
python3 scripts/check_excerpts.py --pin ~/workspace/postfiatd-pin-0085a1f
```

## CI-equivalence proof

The pack was verified CI-equivalent by running `bash reproduce.sh` in a fresh copy of the pack with the pinned postfiatd checkout directory temporarily moved aside (then restored): the run passed with no local-checkout dependency, because no pack script reads the checkout except `scripts/check_excerpts.py --pin`, which is optional. See `docs/FAILURE_MODES.md`.
