# Memo 04 — Release Signing

**Surface:** signing of GitHub releases and Docker images, the hybrid release envelope, key rotation, and rollback protection.
**Pinned revision:** `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
**Verdict:** the worst surface in the pack — unsigned releases, unsigned images, no keys, no rotation, no rollback protection. Score 0/5 (`docs/SCORECARD.md`).

## What this memo adds over the originating pack

The release-signing pack measured the schemes and proposed a hybrid envelope but left the version/mode byte unspecified — an open gap its own verifier flagged. This memo **closes that gap**: the PFQS v1 envelope below fixes every byte. It also ranks the findings by severity *and* exploitability, and names the cross-surface interactions that make unsigned releases a governance risk, not only a supply-chain risk.

## Findings on this surface (consolidated)

| ID | Sev | Exploit | Finding |
|----|-----|---------|---------|
| C-F01 | HIGH | High | GitHub releases are published unsigned |
| C-F02 | HIGH | High | Docker images pushed unsigned, under mutable `-latest` tags; signing explicitly deferred |
| C-F03 | MEDIUM | Medium | No rollback protection for releases |
| C-F04 | MEDIUM | Medium | Downgrade risk during the hybrid transition |
| C-F05 | MEDIUM | Low | SLH-DSA-128s signing too slow for high-frequency use; signatures very large |
| C-F06 | LOW | Low | ML-DSA security rests on lattice assumptions |
| C-F07 | LOW | Low | secp256k1 ECDSA DER malleability — already mitigated in-tree |
| C-F08 | INFO | Low | Ed25519 verification enforces canonicality, strips the 0xED prefix |
| C-F09 | MEDIUM | Medium | No published key-rotation procedure for release keys |
| C-F10 | LOW | Low | Release pipeline trust anchor is a GitHub Actions token; signing alone does not fix a compromised pipeline |

Register ranks: C-F01 2, C-F02 3, C-F03 13, C-F04 14, C-F09 15, C-F05 28, C-F06 48, C-F07 49, C-F10 50, C-F08 59. Full text, sources, and fixes: `docs/REMEDIATION.md`.

## Measured facts (re-verified fresh in this pack)

- **No release-signing step exists in any workflow file.** `outputs/negative_search.log`: grep for cosign/sigstore/attest/gpg/sha256sum/checksum/slsa over `.github/workflows/` returns exactly 2 matches, both in `deploy.yml`, both importing the Caddy APT repository public key (`gpg --dearmor` into a keyring). Neither signs a postfiatd release.
- **No release-signing code exists in the pinned tree.** `outputs/negative_search.log`: zero ML-DSA/ML-KEM/SLH-DSA matches in `src/` or `include/`.
- **Images:** mutable `-latest` tags, no signing step (`build.yml:71-90`, originating pack); image signing (Cosign), container scanning, and SBOM explicitly deferred to "Phase 2 or mainnet" (`docs/dynamic-unl/reviews/FeedbackAnalysis_Codex54.md:335,341`, originating pack).

## Fresh measurements (this pack)

Re-run 2026-11-26, liboqs 0.14.0, single thread, 2,048-byte manifest payload (`outputs/hybrid_dual_sig_bench.log`, `outputs/benchmark-pq.log`):

| Envelope | Combined sig (B) | Verify/s | Sign/s |
|---|---:|---:|---:|
| Ed25519 + ML-DSA-44 | 2,484 (64 + 2,420) | 5,051.858 | 5,137.986 (50-iteration cap: lower bound) |
| Ed25519 + SLH-DSA-128f | 17,152 (64 + 17,088) | 843.260 | 73.813 (cap: lower bound) |

Controls C-1..C-5 all PASS: valid hybrid verifies; tampered classical half rejected; tampered PQ half rejected; stripped PQ half rejected by exact-length check (got 64, want 2484); stripped classical half rejected (got 2420, want 2484).

## The PFQS v1 envelope (new in this pack — closes the T14 open gap)

The originating pack's H-1 design left the version/mode byte unspecified. PFQS v1 fixes every byte. Any deviation rejects.

| Bytes | Content |
|---|---|
| 0–3 | magic `PFQS` (`0x50 0x46 0x51 0x53`) |
| 4 | version `0x01` |
| 5 | mode `0x00` = Ed25519 + ML-DSA-44. All other values reserved; a verifier MUST reject them. |
| 6 | flags `0x00`. All bits reserved; a verifier MUST reject any non-zero value. |
| 7 | reserved `0x00`. A verifier MUST reject any non-zero value. |
| 8–71 | Ed25519 signature (64 B) over the release manifest |
| 72–2491 | ML-DSA-44 signature (2,420 B) over the same manifest |

**Total: 2,492 B.** Arithmetic: 8 + 64 + 2420 = 2492. Verification is AND: both halves must verify, and the total length must be exactly 2,492 B. A stripped half is rejected by the length check before any cryptography runs (controls C-4/C-5).

What PFQS v1 deliberately does **not** contain (open decisions D-01, D-03): no timestamp or sequence field (rollback protection is a separate S1-3 manifest field, not part of the envelope); no key identifier (key distribution and rotation are S1-2, open decision D-01); no ML-DSA-65/87 mode (reserved values; D-04 covers the SLH-DSA question). These are labelled open, not silently unspecified.

## Severity + exploitability ranking (why this surface scores 0/5)

C-F01 and C-F02 are the only two findings in the pack rated HIGH severity **and** High exploitability (ranks 2 and 3, behind only the unauthenticated API read). The reasoning: the attack needs no quantum computer, no network position, and no exploit — it needs only the ability to publish or replace a release, which is exactly the ability a compromised workflow token or maintainer account already grants. And the operator has *nothing* to check the result against: no signature, no attestation, no checksum. The documented upgrade path (`docker compose pull`) will pull whatever is published.

C-F09 (rank 15) is the trap inside the fix: signing releases without a published rotation procedure creates keys that cannot be rotated when they leak. S1-2 must ship with S1-1, not after it. C-F10 (rank 50) is the honest limit: signing attests to the release, not to the pipeline. A compromised pipeline can sign a malicious release correctly. Pipeline hardening (least-privilege tokens, branch protection, required reviews) is part of S1, not an afterthought.

## Cross-surface interactions

- **X-1 (with peer TLS):** anonymous TLS + unsigned releases. A MITM serves a tampered binary over a TLS session nobody authenticates, and the operator cannot detect it. Release signing is the cheaper half of this pair — fix it first.
- **X-2 (with amendment governance):** unsigned releases + unobservable amendment votes. A malicious release that changes voting behaviour cannot be detected by operators (no vote visibility) and cannot be rejected by signature (none exists). A supply-chain compromise becomes a governance compromise with no alarm.
- **With protocol signatures (Memo 01):** the same ML-DSA-44 signs releases and (later) validations. Ship the envelope on releases first (S1): it needs no consensus change, exercises the key handling, and proves the hybrid shape before validations depend on it.
- **With validator manifests (Memo 02):** the release key-rotation procedure (S1-2) is the template for validator key rotation, which also does not exist.

## The single most valuable fix in the pack

**S0-1: publish an Ed25519 signature and a SHA-256 checksum file with every release, plus a verifier script in the repo.** It closes the highest-exploitability finding at near-zero cost and no protocol change, and it is the prerequisite for every later hybrid stage: without signed releases, a signed hybrid envelope has nothing trustworthy to attach to. S1-1 (PFQS v1) follows in the same quarter; S1-2 (rotation) must ship with it.
