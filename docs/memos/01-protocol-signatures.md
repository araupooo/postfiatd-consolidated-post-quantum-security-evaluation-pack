# Memo 01 — Protocol Signatures

**Surface:** post-quantum signature schemes for protocol messages (validations, manifests, transactions).
**Pinned revision:** `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
**Verdict:** measurement-complete, migration-not-started. Score 2/5 (`docs/SCORECARD.md`).

## What this memo adds over the originating pack

The originating pack (lattice benchmarks) measured the schemes. This memo ranks the findings by severity *and* exploitability, names the cross-surface interactions that change the priority, and says which single fix buys the most.

## Findings on this surface (consolidated)

| ID | Sev | Exploit | Finding |
|----|-----|---------|---------|
| C-A01 | HIGH | Medium | No post-quantum signature support in the pinned revision |
| C-A02 | HIGH | Low | Signature-size blowup dominates the migration cost (ML-DSA-44 2,420 B = 37.8x Ed25519) |
| C-A03 | MEDIUM | Low | SLH-DSA verification is the burst bottleneck (128f 897.5/s; 128s sign 2.8/s) |
| C-A04 | MEDIUM | Low | ML-DSA verification is faster than the classical baseline here (27,521.9/s vs 7,071.0/s) |
| C-A05 | MEDIUM | Medium | One verification entry point: easy to extend, single point of failure |
| C-A06 | MEDIUM | Medium | Validator validation signatures are secp256k1-only |
| C-A07 | LOW | Low | SLH-DSA 'f' is faster to sign but slower to verify than 's' |
| C-A08 | LOW | Low | No secp256k1 baseline was measured |

Full text, sources, and fixes: `docs/REMEDIATION.md` (C-A01..C-A08). Register ranks: C-A01 4, C-A02 7, C-A05 10, C-A06 11, C-A03 16, C-A04 17, C-A07 33, C-A08 34.

## Fresh measurements (this pack)

Re-run 2026-11-26, liboqs 0.14.0, single thread, 5 s budgets (`outputs/benchmark-pq.log`):

| Scheme | Verify/s | Sign/s | Sig (B) | PK (B) | vs Ed25519 (64 B) |
|--------|--------:|--------:|--------:|--------:|-------------------:|
| Ed25519 (current) | 7,071.0 | 19,035.5 | 64 | 32 | 1.0x |
| ML-DSA-44 | 27,521.903 | 9,165.012 | 2,420 | 1,312 | 37.8x |
| ML-DSA-65 | 16,319.199 | 5,146.369 | 3,309 | 1,952 | 51.7x |
| ML-DSA-87 | 11,197.188 | 6,199.975 | 4,627 | 2,592 | 72.3x |
| SLH-DSA-SHA2-128s | 2,680.271 | 2.798 | 7,856 | 32 | 122.8x |
| SLH-DSA-SHA2-128f | 897.479 | 75.210 | 17,088 | 32 | 267.0x |

On a 2,048-byte release-manifest payload: ML-DSA-44 verify 19,831.164/s; SLH-DSA-128f verify 962.127/s. Every algorithm's controls passed (valid verifies, tampered rejects). Sizes verified against FIPS 204 Table 2 / FIPS 205 and liboqs headers (`sig_ml_dsa.h:11` — ML-DSA-44 signature 2,420 B).

Two facts decide the migration shape:

1. **Verify cost is not the blocker.** ML-DSA-44 verifies 3.9x faster than Ed25519 on this machine (27,521.903 / 7,071.0 = 3.89). The cost is size, not speed.
2. **SLH-DSA-128s cannot sign at any frequency that matters** (2.798/s). It is a long-lived-signature candidate only, never a validation-signature candidate.

A third fact is a tooling trap, measured fresh in this pack: liboqs 0.14.0 does **not** register the FIPS 205 names — `bench_sig "SLH-DSA-SHA2-128s"` exits 1 with `result: ALGORITHM_NOT_ENABLED` (`outputs/negative_fips205_names.log`). The same parameter sets are registered under their SPHINCS+ names. Any migration code that asks liboqs for `SLH-DSA-SHA2-128s` by name will fail at runtime, not at compile time.

## Cross-surface interactions

- **With validator manifests (Memo 02):** C-A06 is the same exposure as C-A01, narrowed to the one signature that authenticates peers. The protocol-signature migration and the validation-signature migration are one workstream, not two: the day ML-DSA validations ship, the protocol has a PQ signature; until then it has none anywhere.
- **With peer TLS (Memo 03):** the validation signature is the *only* peer-authentication layer, because peer TLS is anonymous (C-G01). A quantum break of secp256k1 therefore collapses peer authentication with no defence in depth (interaction X-3). This is why C-A06 ranks above its severity alone would suggest: it is the last line, not one of several.
- **With release signing (Memo 04):** the same ML-DSA-44 that signs validations signs releases in the PFQS v1 envelope. One scheme, one key-management story, two surfaces — but the release envelope ships first (S1) because it needs no consensus change.
- **With amendment governance (Memo 05):** a PQ signature migration is itself a protocol change that will need an amendment to activate. The governance surface that must approve the migration is the surface with the weakest observability (C-E01, C-E02). The migration's own approval path is unobservable.

## The single most valuable fix on this surface

**Dual-sign validations on testnet (S2-2), using ML-DSA-44 as the PQ half.** It is not the cheapest fix in the pack — release signing (S0-1) is cheaper and ranks first overall — but on *this* surface it is the fix that converts measurement into protection: it proves the validation format, exercises the key handling, and gives the network a PQ-authenticated peer layer to fall back on. Until it ships, every number in the table above is a plan, not a protection.

## Open decisions touching this surface

- D-04: SLH-DSA adoption for archival releases is deferred to S3-2. ML-DSA-44 is the only PQ half in PFQS v1.
- The PQ validation format itself (field layout, dual-signature encoding inside a validation) is not specified in this pack; S2-2 must specify it with every byte fixed, as PFQS v1 does for releases.
