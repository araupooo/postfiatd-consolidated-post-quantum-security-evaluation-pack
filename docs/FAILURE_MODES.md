# Failure Modes

How this pack can be wrong, and what was done about each mode. Read this before trusting any number in the pack.

## 1. Machine variance (timing)

Rates (ops/s, us) depend on the machine, its load, and CPU frequency scaling. The fresh numbers in this pack were measured on a shared VM (1.5 shared CPUs). They will differ on another machine — the originating packs' numbers differ from this pack's by up to ~15% on the same algorithms (e.g. ML-KEM-768 decaps 28.30 us in the TLS pack vs 32.77 us here; ML-DSA-44 verify 26,163.3/s vs 27,521.9/s here). **Mitigation:** `scripts/check_measurements.py` checks structure (blocks present, controls PASS, lengths exact, arithmetic exact), not absolute rates. Rates are evidence of feasibility and relative cost, not constants. Sizes, counts, and PASS/FAIL results are exact and machine-independent.

## 2. liboqs name registration (FIPS 205 names)

liboqs 0.14.0 does **not** register the FIPS 205 names (`SLH-DSA-SHA2-128s` → `ALGORITHM_NOT_ENABLED`); the parameter sets are registered under SPHINCS+ names. The first run of this pack's harness failed on exactly this. **Mitigation:** `harness/run_benchmarks.sh` maps display names to liboqs names explicitly, and `outputs/negative_fips205_names.log` records the failure as evidence (CLAIMS.md M-30). Any migration code that asks liboqs for a FIPS 205 name will fail at runtime, not at compile time.

## 3. Pinned source line numbers

Line numbers drift between revisions and can be misread from raw-file fetches. **Mitigation:** every cited line was verified with `grep -n` on the local pinned checkout at commit `0085a1ff885d6a446369cf73a4430f75af22be55`, and the verbatim excerpts are vendored in `data/source_excerpts.json` with `scripts/check_excerpts.py --pin` to re-verify them.

## 4. Carried-forward numbers

Numbers carried from the originating packs (testnet window, probes, drills, amendment inventory) were re-checked against their vendored logs, not re-run: the live testnet state has moved on since those windows, so re-running them would measure a different window. **Mitigation:** they are labelled [MEASURED] with the originating log cited in `docs/CLAIMS.md` section B, and the three origin-pack judgements that could not be re-derived are labelled [UNSUPPORTED] (section D) rather than carried as measured.

## 5. The Caddy-gpg false positive

A naive grep for release-signing tooling (`gpg`) over `.github/workflows/` returns 2 matches in `deploy.yml`. Both import the Caddy APT repository public key; neither signs a postfiatd release. A reader who stops at the grep would conclude releases are signed. **Mitigation:** `outputs/negative_search.log` records the matches and explains them; CLAIMS.md M-28 states the result precisely.

## 6. SHA256SUMS circularity

`outputs/reproduce_selfcheck.log` embeds the digest-verification output, so it can never be in its own digest set. **Mitigation:** `SHA256SUMS` excludes itself and `outputs/reproduce_selfcheck.log`; the self-check log is verified by byte-identical regeneration (three consecutive runs produced identical logs — see the verification record in `PACK-READY.md`'s parent review, or re-run `bash reproduce.sh` twice and `diff` the log).

## 7. Measurement logs vs vendored evidence

`reproduce.sh` re-runs measurements into a scratch directory, never into `outputs/`. A run that overwrote the vendored logs would silently change the evidence the docs cite. **Mitigation:** `harness/run_benchmarks.sh` writes only to `$MEASUREMENT_OUTDIR`; `reproduce.sh` sets it to scratch.

## 8. CI environment differences

CI builds liboqs from a fresh clone on `ubuntu-latest`; the local run reuses `~/liboqs/build`. A stale local build could mask a build failure. **Mitigation:** `harness/run_benchmarks.sh` verifies the liboqs HEAD against the pinned commit before building or reusing anything, and the CI workflow (`/.github/workflows/ci.yml`) clones tag 0.14.0 fresh. CI-equivalence was also proven locally by running reproduce with the pinned checkout moved aside.

## 9. Sign-rate iteration caps

`bench_sig` caps signing at 25 iterations and `hybrid_bench` at 50: the reported sign rates are lower bounds, and the sign-side numbers (e.g. SLH-DSA-128s 2.798/s) are the least precise figures in the pack. **Mitigation:** the caps are stated in the logs and in `docs/CLAIMS.md`; no conclusion in this pack depends on a sign rate to better than an order of magnitude.

## 10. What this pack does not cover

- No secp256k1 verify baseline was measured (OpenSSL `speed` has no secp256k1 mode; CLAIMS.md does not claim one).
- No constant-time claim is made for ML-KEM decapsulation (the timing check is wall-clock only; CLAIMS.md M-14 says so explicitly).
- The server-side TLS handshake call site is outside the pinned tree (C-G10, INFO).
- The PQ validation format is not specified here (S2-2 must specify it byte-exactly).
