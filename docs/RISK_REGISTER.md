# Consolidated Risk Register

Consolidation of the findings of seven prior evaluation packs (protocol-signature benchmarks, ML-KEM assessment, network/agent reference, overlay partition-recovery, amendment lifecycle, release-signing migration, TLS migration readiness) against postfiatd at the pinned revision `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).

**Counts: 60 findings — 9 HIGH, 23 MEDIUM, 21 LOW, 7 INFO.** Every finding is carried from an originating pack; nothing here is new measurement except the exploitability rating, which is this pack's value-add.

## Ranking rule

Rank = severity first, then exploitability (High > Medium > Low), then consolidated ID. Severity judges the harm if the weakness is used; exploitability judges how easily and reliably an attacker can trigger it. Both are judged against the pinned tree and the live testnet evidence cited.

## Cross-surface interactions (new in this pack)

Individual findings understate the risk. Five interactions compound across surfaces:

- **X-1 — Anonymous TLS + unsigned releases (C-G01 + C-F01/C-F02):** a network man-in-the-middle can terminate peer TLS and serve a tampered binary; nothing in the download path checks it, because no signature exists to check. Combined exploitability: **High**. Either fix alone breaks the chain; release signing is the cheaper one.
- **X-2 — Unsigned releases + unobservable amendment votes (C-F01 + C-E01/C-E02):** a malicious release that changes amendment-voting behaviour cannot be detected by operators (no vote visibility) and cannot be rejected by signature check (none exists). A supply-chain compromise becomes a governance compromise with no alarm.
- **X-3 — secp256k1-only validations + anonymous TLS (C-A06 + C-G01):** the validation signature is the *only* peer-authentication layer; TLS contributes nothing. A quantum break of secp256k1 (harvest-now, forge-later) collapses peer authentication entirely, with no defence in depth.
- **X-4 — Quorum comment bound + amendment thresholds (C-D01 + C-E05):** governance and overlay both rest on 67% assumptions whose documented justifications are wrong or incomplete (the comment bound holds only at zero Byzantine faults; the effective required fraction is 68%, not 67%). One faulty assumption class affects two surfaces.
- **X-5 — ML-KEM absent everywhere + harvest-now (C-B01 + C-G06 + C-A01):** recorded peer traffic and validations are exposed to future decryption and forgery with no hybrid protection in place today. The exposure window opens the day a cryptographically relevant quantum computer exists, not the day the migration finishes.

## Ranked findings

| Rank | ID | Surface | Sev | Exploit | Finding | Source |
|---:|---|---|---|---|---|---|
| 1 | C-C01 | network-agent-surface | HIGH | High | Unauthenticated /api/tasks read: GET returns 200 with task JSON to any caller | T11 outputs/agent_surface_probe.log:4 (P-04 GET /api/tasks -> 200 UNAUTHENTICATED-JSON-READ) |
| 2 | C-F01 | release-signing | HIGH | High | GitHub releases are published unsigned: no signature, attestation, or checksum with any release | .github/workflows/testnet-build.yml:44-71 (gh release create, notes only); negative grep for cosign/sigstore/attest/gpg/sha256sum over all ten workflow files |
| 3 | C-F02 | release-signing | HIGH | High | Docker images pushed unsigned, under mutable -latest tags; image signing explicitly deferred to 'Phase 2 or mainnet' | .github/workflows/build.yml:71-90; docs/dynamic-unl/reviews/FeedbackAnalysis_Codex54.md:335,341 |
| 4 | C-A01 | protocol-signatures | HIGH | Medium | No post-quantum signature support in the pinned revision | negative search over the pinned tree (no ML-DSA/SLH-DSA code) |
| 5 | C-B01 | ml-kem-key-exchange | HIGH | Medium | postfiatd has no ML-KEM code at all | negative search over the pinned tree |
| 6 | C-G01 | peer-transport-tls | HIGH | Medium | Peer TLS is anonymous: peer identity is not established by TLS (verify_none on both ends) | src/xrpld/overlay/detail/ConnectAttempt.cpp:175; src/libxrpl/basics/make_SSLContext.cpp:391 |
| 7 | C-A02 | protocol-signatures | HIGH | Low | Signature-size blowup dominates the migration cost (ML-DSA-44 2,420 B = 37.8x Ed25519 64 B) | outputs/benchmark-pq.log (length_signature 2420 vs 64) |
| 8 | C-B06 | ml-kem-key-exchange | HIGH | Low | X-Wing (draft-11) has no all-zero X25519 check; the combiner itself does not reject a zero shared secret | outputs/hybrid_bench.log (all_zero_x25519 rc=-1 rejected_by_openssl: the rejection comes from OpenSSL, not from the combiner) |
| 9 | C-G02 | peer-transport-tls | HIGH | Low | Ephemeral self-signed RSA-2048 peer certificate, no pinning; the certificate carries no identity and is never verified | src/libxrpl/basics/make_SSLContext.cpp:66 |
| 10 | C-A05 | protocol-signatures | MEDIUM | Medium | One verification entry point: easy to extend, single point of failure | pinned tree signature verification path |
| 11 | C-A06 | protocol-signatures | MEDIUM | Medium | Validator validation signatures are secp256k1-only | src/xrpld/overlay/detail/Handshake.cpp:294 |
| 12 | C-C02 | network-agent-surface | MEDIUM | Medium | Authorization enforced at routing, not at the API layer | T11 pack evidence (P-05/P-06 POST -> 405, not 401/403) |
| 13 | C-F03 | release-signing | MEDIUM | Medium | No rollback protection for releases (no signed version record, no sequence enforcement) | T14 pack evidence |
| 14 | C-F04 | release-signing | MEDIUM | Medium | Downgrade risk during the hybrid transition (a stripped PQ half must be rejected by length check) | outputs/hybrid_dual_sig_bench.log (controls C-4/C-5: stripped halves rejected) |
| 15 | C-F09 | release-signing | MEDIUM | Medium | No published key-rotation procedure exists for release keys | T14 pack evidence (negative search) |
| 16 | C-A03 | protocol-signatures | MEDIUM | Low | SLH-DSA verification is the burst bottleneck (128f 897.5/s; 128s sign 2.8/s) | outputs/benchmark-pq.log |
| 17 | C-A04 | protocol-signatures | MEDIUM | Low | ML-DSA verification is faster than the classical baseline here (ML-DSA-44 27,521.9/s vs Ed25519 7,071.0/s) | outputs/benchmark-pq.log; outputs/benchmark-classical.log |
| 18 | C-B02 | ml-kem-key-exchange | MEDIUM | Low | Implicit rejection is silent: no error is ever returned for an invalid ciphertext | outputs/benchmark-kem.log (implicit_rejection_total 108/108) |
| 19 | C-B05 | ml-kem-key-exchange | MEDIUM | Low | Key reuse is safe for correctness, unsafe to assume for replay protection | outputs/benchmark-kem.log (key_reuse roundtrips 100/100) |
| 20 | C-B07 | ml-kem-key-exchange | MEDIUM | Low | X-Wing is still a draft; the TLS hybrid combiner is already an RFC | T10 pack evidence |
| 21 | C-B10 | ml-kem-key-exchange | MEDIUM | Low | The FIPS 203 section 7.3 length check must live in the application | FIPS 203 section 7.3 (no in-tree caller exists) |
| 22 | C-C03 | network-agent-surface | MEDIUM | Low | Track the 67% -> 80% quorum revert as a mainnet gate (live VL seq 31, quorum 17 of 25 = 67%) | T11 outputs/validator_topology.log |
| 23 | C-D01 | overlay-partition-recovery | MEDIUM | Low | Quorum comment's fork-safety claim is wrong: the pi+pj < .33*ni bound holds only at zero Byzantine faults; under the comment's own fault model Theorem 8 certifies nothing at 67% (required overlap 28.5 > 25) | src/xrpld/app/misc/detail/ValidatorList.cpp:1927-1928 |
| 24 | C-D02 | overlay-partition-recovery | MEDIUM | Low | Do not treat UNL uniformity as verified (25 validators, overlap 21/25 at 67% vs 23/25 upstream) | T12 pack evidence; T11 validator_topology.log |
| 25 | C-D03 | overlay-partition-recovery | MEDIUM | Low | A sub-quorum side cannot self-rescue via the negative UNL (max listed 7; quorum after full listing 15) | T12 pack evidence (negative-UNL simulation) |
| 26 | C-E01 | amendment-governance | MEDIUM | Low | Per-amendment vote counts are not publicly observable (count/validations/threshold emitted only for admin callers) | src/xrpld/app/misc/detail/AmendmentTable.cpp:1019-1028 |
| 27 | C-E02 | amendment-governance | MEDIUM | Low | The vote-tracking amendment is itself disabled (PF_ValidatorVoteTracking; both PostFiat-specific amendments disabled) | src/xrpld/app/misc/ValidatorVoteTracker.cpp:162; live inventory 101 amendments, 64 enabled / 37 disabled |
| 28 | C-F05 | release-signing | MEDIUM | Low | SLH-DSA-128s signing is too slow for any high-frequency use (2.8/s) and SLH-DSA signatures are very large (17,088 B for 128f) | outputs/benchmark-pq.log |
| 29 | C-G03 | peer-transport-tls | MEDIUM | Low | No TLS version floor/ceiling; cipher list does not cover TLS 1.3 | src/libxrpl/basics/make_SSLContext.cpp:104,352-357 |
| 30 | C-G04 | peer-transport-tls | MEDIUM | Low | Operator ssl_ciphers does not apply to the peer port (peer listener always uses make_SSLContext("")) | T15 pack evidence (OverlayImpl.cpp:1550; ServerHandler.cpp:1090,1092) |
| 31 | C-G05 | peer-transport-tls | MEDIUM | Low | Outbound HTTPS client pins TLS 1.2 (validator-site and exclusion-list fetches) | T15 pack evidence (WorkSSL.cpp:41) |
| 32 | C-G06 | peer-transport-tls | MEDIUM | Low | No ML-KEM support in the TLS stack (OpenSSL 3.0.13 as used here has none) | negative search; outputs/benchmark-kem.log |
| 33 | C-A07 | protocol-signatures | LOW | Low | SLH-DSA 'f' is faster to sign but slower to verify than 's' | outputs/benchmark-pq.log |
| 34 | C-A08 | protocol-signatures | LOW | Low | No secp256k1 baseline was measured (OpenSSL speed has no secp256k1; P-256 used as stand-in) | outputs/benchmark-classical.log |
| 35 | C-B03 | ml-kem-key-exchange | LOW | Low | Rejected outputs are distinct per invalid ciphertext (pseudorandom shared secret, as specified) | outputs/benchmark-kem.log |
| 36 | C-B04 | ml-kem-key-exchange | LOW | Low | No timing signal at wall-clock resolution; not a constant-time proof | outputs/benchmark-kem.log (valid 34.323 us vs invalid 33.388 us, n=1000, re-measured in T10) |
| 37 | C-B08 | ml-kem-key-exchange | LOW | Low | liboqs 0.14.0 does not ship X-Wing or expose ML-KEM.KeyGen_internal | liboqs 0.14.0 headers (kem.h; no X-Wing registration) |
| 38 | C-B11 | ml-kem-key-exchange | LOW | Low | ML-KEM alone lacks the binding properties X-Wing provides | T10 pack analysis |
| 39 | C-C04 | network-agent-surface | LOW | Low | Publish /robots.txt (or return a real 404) | T11 outputs/agent_surface_probe.log |
| 40 | C-C05 | network-agent-surface | LOW | Low | Stop serving the app shell for unknown /api/* paths | T11 outputs/agent_surface_probe.log:3 (P-03 GET /api -> 200 SPA-FALLBACK) |
| 41 | C-C06 | network-agent-surface | LOW | Low | Document and signal API rate limits (122 RPC requests, zero 429s in the measured window) | T11 outputs/measure_window.log |
| 42 | C-C07 | network-agent-surface | LOW | Low | Monitor close-time segment means, not per-ledger diffs (mean close time 3.0243 s) | T11 outputs/measure_window.log |
| 43 | C-D04 | overlay-partition-recovery | LOW | Low | Do not use converged/diverged flags as a partition detector | T12 pack evidence |
| 44 | C-D05 | overlay-partition-recovery | LOW | Low | Plan ledger catch-up capacity for long partitions (drills D-01..D-04 4/4 PASS; detection >= 1 flag period ~768 s) | T12 outputs/recovery_drills.log |
| 45 | C-E03 | amendment-governance | LOW | Low | A lost majority restarts the full 2-week clock (majority hold 1,209,600 s = 403,200 ledgers) | include/xrpl/protocol/SystemParameters.h:88 |
| 46 | C-E04 | amendment-governance | LOW | Low | 24 h vote expiry can cost a majority (activation S-f: day 20 instead of day 14) | T13 pack lifecycle simulation |
| 47 | C-E06 | amendment-governance | LOW | Low | 9 vetoes permanently block activation (simulated scenario S-e) | T13 pack lifecycle simulation (labelled [SIMULATED]) |
| 48 | C-F06 | release-signing | LOW | Low | ML-DSA security rests on lattice assumptions; a lattice break would break the PQ half (the Ed25519 half survives: AND-verification) | outputs/hybrid_dual_sig_bench.log (hybrid_verify_ops_per_sec 5051.858) |
| 49 | C-F07 | release-signing | LOW | Low | secp256k1 ECDSA DER signatures are malleable unless canonicality is enforced: already mitigated in-tree | T14 pack evidence |
| 50 | C-F10 | release-signing | LOW | Low | The release pipeline's trust anchor is a GitHub Actions token; signing alone does not fix a compromised pipeline | T14 pack evidence |
| 51 | C-G07 | peer-transport-tls | LOW | Low | Ephemeral certificate valid 2 years | T15 pack evidence |
| 52 | C-G08 | peer-transport-tls | LOW | Low | X25519 EVP keygen/derive overhead on hot paths (keygen 70.63 us, derive 65.01 us, n=200) | outputs/hybrid_bench.log |
| 53 | C-G09 | peer-transport-tls | LOW | Low | ML-KEM-1024 key distribution size (pk 1,568 B, ct 1,568 B; hybrid wire 1,603 B) | outputs/hybrid_bench.log |
| 54 | C-B09 | ml-kem-key-exchange | INFO | Low | Sizes and speeds confirmed (ML-KEM-768 pk 1,184 B, ct 1,088 B, ss 32 B) | outputs/benchmark-kem.log; liboqs kem_ml_kem.h:22-25 |
| 55 | C-C08 | network-agent-surface | INFO | Low | Testnet traffic is near idle; fee/burn figures are not stress figures (burn 98,436 drops over the window) | T11 outputs/measure_window.log |
| 56 | C-D06 | overlay-partition-recovery | INFO | Low | Reconnection pacing is adequate for healing | T12 pack evidence |
| 57 | C-E05 | amendment-governance | INFO | Low | The effective required fraction exceeds 67%: post-fix 67/100 strict '>' needs 17 of 25 votes (68.00%); pre-fix needed 19 (76.00%) | include/xrpl/protocol/SystemParameters.h:83,85 |
| 58 | C-E07 | amendment-governance | INFO | Low | PF_AccountExclusion is disabled | live inventory 101 amendments (see T13 pack) |
| 59 | C-F08 | release-signing | INFO | Low | Ed25519 verification enforces canonicality and strips the 0xED key prefix | T14 pack evidence |
| 60 | C-G10 | peer-transport-tls | INFO | Low | Server-side TLS handshake call site is outside the pinned tree | T15 pack evidence (negative search) |

## Finding detail

### C-C01 — Unauthenticated /api/tasks read: GET returns 200 with task JSON to any caller

- **Rank:** 1 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-01
- **Severity:** HIGH · **Exploitability:** High
- **Source:** T11 outputs/agent_surface_probe.log:4 (P-04 GET /api/tasks -> 200 UNAUTHENTICATED-JSON-READ)
- **Citation:** live testnet endpoint, window 2026-11-24/25 (see T11 pack)

### C-F01 — GitHub releases are published unsigned: no signature, attestation, or checksum with any release

- **Rank:** 2 of 60 · **Surface:** release-signing · **Origin:** T14 R-01
- **Severity:** HIGH · **Exploitability:** High
- **Source:** .github/workflows/testnet-build.yml:44-71 (gh release create, notes only); negative grep for cosign/sigstore/attest/gpg/sha256sum over all ten workflow files
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-F02 — Docker images pushed unsigned, under mutable -latest tags; image signing explicitly deferred to 'Phase 2 or mainnet'

- **Rank:** 3 of 60 · **Surface:** release-signing · **Origin:** T14 R-02
- **Severity:** HIGH · **Exploitability:** High
- **Source:** .github/workflows/build.yml:71-90; docs/dynamic-unl/reviews/FeedbackAnalysis_Codex54.md:335,341
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-A01 — No post-quantum signature support in the pinned revision

- **Rank:** 4 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-01
- **Severity:** HIGH · **Exploitability:** Medium
- **Source:** negative search over the pinned tree (no ML-DSA/SLH-DSA code)
- **Citation:** FIPS 204; FIPS 205; this pack outputs/benchmark-pq.log

### C-B01 — postfiatd has no ML-KEM code at all

- **Rank:** 5 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-01
- **Severity:** HIGH · **Exploitability:** Medium
- **Source:** negative search over the pinned tree
- **Citation:** FIPS 203; this pack outputs/benchmark-kem.log

### C-G01 — Peer TLS is anonymous: peer identity is not established by TLS (verify_none on both ends)

- **Rank:** 6 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-01
- **Severity:** HIGH · **Exploitability:** Medium
- **Source:** src/xrpld/overlay/detail/ConnectAttempt.cpp:175; src/libxrpl/basics/make_SSLContext.cpp:391
- **Citation:** data/source_excerpts.json E-01, E-02

### C-A02 — Signature-size blowup dominates the migration cost (ML-DSA-44 2,420 B = 37.8x Ed25519 64 B)

- **Rank:** 7 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-02
- **Severity:** HIGH · **Exploitability:** Low
- **Source:** outputs/benchmark-pq.log (length_signature 2420 vs 64)
- **Citation:** FIPS 204 Table 2; liboqs sig_ml_dsa.h:11

### C-B06 — X-Wing (draft-11) has no all-zero X25519 check; the combiner itself does not reject a zero shared secret

- **Rank:** 8 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-06
- **Severity:** HIGH · **Exploitability:** Low
- **Source:** outputs/hybrid_bench.log (all_zero_x25519 rc=-1 rejected_by_openssl: the rejection comes from OpenSSL, not from the combiner)
- **Citation:** draft-irtf-cfrg-xwing-kem-11; RFC 10024

### C-G02 — Ephemeral self-signed RSA-2048 peer certificate, no pinning; the certificate carries no identity and is never verified

- **Rank:** 9 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-02
- **Severity:** HIGH · **Exploitability:** Low
- **Source:** src/libxrpl/basics/make_SSLContext.cpp:66
- **Citation:** data/source_excerpts.json E-03

### C-A05 — One verification entry point: easy to extend, single point of failure

- **Rank:** 10 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-05
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** pinned tree signature verification path
- **Citation:** postfiatd 0085a1ff (see T9 pack)

### C-A06 — Validator validation signatures are secp256k1-only

- **Rank:** 11 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-06
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** src/xrpld/overlay/detail/Handshake.cpp:294
- **Citation:** data/source_excerpts.json E-06

### C-C02 — Authorization enforced at routing, not at the API layer

- **Rank:** 12 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-02
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** T11 pack evidence (P-05/P-06 POST -> 405, not 401/403)
- **Citation:** live testnet endpoint (see T11 pack)

### C-F03 — No rollback protection for releases (no signed version record, no sequence enforcement)

- **Rank:** 13 of 60 · **Surface:** release-signing · **Origin:** T14 R-03
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-F04 — Downgrade risk during the hybrid transition (a stripped PQ half must be rejected by length check)

- **Rank:** 14 of 60 · **Surface:** release-signing · **Origin:** T14 R-04
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** outputs/hybrid_dual_sig_bench.log (controls C-4/C-5: stripped halves rejected)
- **Citation:** this pack, fresh re-run

### C-F09 — No published key-rotation procedure exists for release keys

- **Rank:** 15 of 60 · **Surface:** release-signing · **Origin:** T14 R-09
- **Severity:** MEDIUM · **Exploitability:** Medium
- **Source:** T14 pack evidence (negative search)
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-A03 — SLH-DSA verification is the burst bottleneck (128f 897.5/s; 128s sign 2.8/s)

- **Rank:** 16 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-03
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205; liboqs 0.14.0

### C-A04 — ML-DSA verification is faster than the classical baseline here (ML-DSA-44 27,521.9/s vs Ed25519 7,071.0/s)

- **Rank:** 17 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-04
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** outputs/benchmark-pq.log; outputs/benchmark-classical.log
- **Citation:** liboqs 0.14.0; OpenSSL 3.0.13

### C-B02 — Implicit rejection is silent: no error is ever returned for an invalid ciphertext

- **Rank:** 18 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-02
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** outputs/benchmark-kem.log (implicit_rejection_total 108/108)
- **Citation:** FIPS 203 section 7.3

### C-B05 — Key reuse is safe for correctness, unsafe to assume for replay protection

- **Rank:** 19 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-05
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** outputs/benchmark-kem.log (key_reuse roundtrips 100/100)
- **Citation:** FIPS 203 section 7.2

### C-B07 — X-Wing is still a draft; the TLS hybrid combiner is already an RFC

- **Rank:** 20 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-07
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T10 pack evidence
- **Citation:** RFC 10024

### C-B10 — The FIPS 203 section 7.3 length check must live in the application

- **Rank:** 21 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-10
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** FIPS 203 section 7.3 (no in-tree caller exists)
- **Citation:** FIPS 203 section 7.3

### C-C03 — Track the 67% -> 80% quorum revert as a mainnet gate (live VL seq 31, quorum 17 of 25 = 67%)

- **Rank:** 22 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-03
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T11 outputs/validator_topology.log
- **Citation:** postfiatd 0085a1ff; live testnet VL

### C-D01 — Quorum comment's fork-safety claim is wrong: the pi+pj < .33*ni bound holds only at zero Byzantine faults; under the comment's own fault model Theorem 8 certifies nothing at 67% (required overlap 28.5 > 25)

- **Rank:** 23 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-01
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** src/xrpld/app/misc/detail/ValidatorList.cpp:1927-1928
- **Citation:** data/source_excerpts.json E-07

### C-D02 — Do not treat UNL uniformity as verified (25 validators, overlap 21/25 at 67% vs 23/25 upstream)

- **Rank:** 24 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-02
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T12 pack evidence; T11 validator_topology.log
- **Citation:** live testnet VL seq 31 (see T11/T12 packs)

### C-D03 — A sub-quorum side cannot self-rescue via the negative UNL (max listed 7; quorum after full listing 15)

- **Rank:** 25 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-03
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T12 pack evidence (negative-UNL simulation)
- **Citation:** postfiatd 0085a1ff (see T12 pack)

### C-E01 — Per-amendment vote counts are not publicly observable (count/validations/threshold emitted only for admin callers)

- **Rank:** 26 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-01
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** src/xrpld/app/misc/detail/AmendmentTable.cpp:1019-1028
- **Citation:** data/source_excerpts.json E-09

### C-E02 — The vote-tracking amendment is itself disabled (PF_ValidatorVoteTracking; both PostFiat-specific amendments disabled)

- **Rank:** 27 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-02
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** src/xrpld/app/misc/ValidatorVoteTracker.cpp:162; live inventory 101 amendments, 64 enabled / 37 disabled
- **Citation:** postfiatd 0085a1ff; live testnet feature RPC 2026-11-25 (see T13 pack)

### C-F05 — SLH-DSA-128s signing is too slow for any high-frequency use (2.8/s) and SLH-DSA signatures are very large (17,088 B for 128f)

- **Rank:** 28 of 60 · **Surface:** release-signing · **Origin:** T14 R-05
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205; liboqs 0.14.0

### C-G03 — No TLS version floor/ceiling; cipher list does not cover TLS 1.3

- **Rank:** 29 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-03
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** src/libxrpl/basics/make_SSLContext.cpp:104,352-357
- **Citation:** data/source_excerpts.json E-04, E-05

### C-G04 — Operator ssl_ciphers does not apply to the peer port (peer listener always uses make_SSLContext(""))

- **Rank:** 30 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-04
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T15 pack evidence (OverlayImpl.cpp:1550; ServerHandler.cpp:1090,1092)
- **Citation:** postfiatd 0085a1ff (see T15 pack)

### C-G05 — Outbound HTTPS client pins TLS 1.2 (validator-site and exclusion-list fetches)

- **Rank:** 31 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-05
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** T15 pack evidence (WorkSSL.cpp:41)
- **Citation:** postfiatd 0085a1ff (see T15 pack)

### C-G06 — No ML-KEM support in the TLS stack (OpenSSL 3.0.13 as used here has none)

- **Rank:** 32 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-06
- **Severity:** MEDIUM · **Exploitability:** Low
- **Source:** negative search; outputs/benchmark-kem.log
- **Citation:** FIPS 203; OpenSSL 3.0.13

### C-A07 — SLH-DSA 'f' is faster to sign but slower to verify than 's'

- **Rank:** 33 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-07
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205

### C-A08 — No secp256k1 baseline was measured (OpenSSL speed has no secp256k1; P-256 used as stand-in)

- **Rank:** 34 of 60 · **Surface:** protocol-signatures · **Origin:** T9 F-08
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/benchmark-classical.log
- **Citation:** OpenSSL 3.0.13

### C-B03 — Rejected outputs are distinct per invalid ciphertext (pseudorandom shared secret, as specified)

- **Rank:** 35 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-03
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/benchmark-kem.log
- **Citation:** FIPS 203 section 7.3

### C-B04 — No timing signal at wall-clock resolution; not a constant-time proof

- **Rank:** 36 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-04
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/benchmark-kem.log (valid 34.323 us vs invalid 33.388 us, n=1000, re-measured in T10)
- **Citation:** FIPS 203

### C-B08 — liboqs 0.14.0 does not ship X-Wing or expose ML-KEM.KeyGen_internal

- **Rank:** 37 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-08
- **Severity:** LOW · **Exploitability:** Low
- **Source:** liboqs 0.14.0 headers (kem.h; no X-Wing registration)
- **Citation:** liboqs 0.14.0

### C-B11 — ML-KEM alone lacks the binding properties X-Wing provides

- **Rank:** 38 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-11
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T10 pack analysis
- **Citation:** draft-irtf-cfrg-xwing-kem-11

### C-C04 — Publish /robots.txt (or return a real 404)

- **Rank:** 39 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-04
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T11 outputs/agent_surface_probe.log
- **Citation:** live testnet endpoint (see T11 pack)

### C-C05 — Stop serving the app shell for unknown /api/* paths

- **Rank:** 40 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-05
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T11 outputs/agent_surface_probe.log:3 (P-03 GET /api -> 200 SPA-FALLBACK)
- **Citation:** live testnet endpoint (see T11 pack)

### C-C06 — Document and signal API rate limits (122 RPC requests, zero 429s in the measured window)

- **Rank:** 41 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-06
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet RPC (see T11 pack)

### C-C07 — Monitor close-time segment means, not per-ledger diffs (mean close time 3.0243 s)

- **Rank:** 42 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-07
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet ledgers 8332480-8361280 (see T11 pack)

### C-D04 — Do not use converged/diverged flags as a partition detector

- **Rank:** 43 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-04
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T12 pack evidence
- **Citation:** postfiatd 0085a1ff (see T12 pack)

### C-D05 — Plan ledger catch-up capacity for long partitions (drills D-01..D-04 4/4 PASS; detection >= 1 flag period ~768 s)

- **Rank:** 44 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-05
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T12 outputs/recovery_drills.log
- **Citation:** postfiatd 0085a1ff (see T12 pack)

### C-E03 — A lost majority restarts the full 2-week clock (majority hold 1,209,600 s = 403,200 ledgers)

- **Rank:** 45 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-03
- **Severity:** LOW · **Exploitability:** Low
- **Source:** include/xrpl/protocol/SystemParameters.h:88
- **Citation:** data/source_excerpts.json E-08

### C-E04 — 24 h vote expiry can cost a majority (activation S-f: day 20 instead of day 14)

- **Rank:** 46 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-04
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T13 pack lifecycle simulation
- **Citation:** postfiatd 0085a1ff (see T13 pack)

### C-E06 — 9 vetoes permanently block activation (simulated scenario S-e)

- **Rank:** 47 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-06
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T13 pack lifecycle simulation (labelled [SIMULATED])
- **Citation:** postfiatd 0085a1ff (see T13 pack)

### C-F06 — ML-DSA security rests on lattice assumptions; a lattice break would break the PQ half (the Ed25519 half survives: AND-verification)

- **Rank:** 48 of 60 · **Surface:** release-signing · **Origin:** T14 R-06
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/hybrid_dual_sig_bench.log (hybrid_verify_ops_per_sec 5051.858)
- **Citation:** FIPS 204; NIST PQC

### C-F07 — secp256k1 ECDSA DER signatures are malleable unless canonicality is enforced: already mitigated in-tree

- **Rank:** 49 of 60 · **Surface:** release-signing · **Origin:** T14 R-07
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-F10 — The release pipeline's trust anchor is a GitHub Actions token; signing alone does not fix a compromised pipeline

- **Rank:** 50 of 60 · **Surface:** release-signing · **Origin:** T14 R-10
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-G07 — Ephemeral certificate valid 2 years

- **Rank:** 51 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-07
- **Severity:** LOW · **Exploitability:** Low
- **Source:** T15 pack evidence
- **Citation:** postfiatd 0085a1ff (see T15 pack)

### C-G08 — X25519 EVP keygen/derive overhead on hot paths (keygen 70.63 us, derive 65.01 us, n=200)

- **Rank:** 52 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-08
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/hybrid_bench.log
- **Citation:** this pack, fresh re-run

### C-G09 — ML-KEM-1024 key distribution size (pk 1,568 B, ct 1,568 B; hybrid wire 1,603 B)

- **Rank:** 53 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-09
- **Severity:** LOW · **Exploitability:** Low
- **Source:** outputs/hybrid_bench.log
- **Citation:** FIPS 203 Table 2; liboqs 0.14.0

### C-B09 — Sizes and speeds confirmed (ML-KEM-768 pk 1,184 B, ct 1,088 B, ss 32 B)

- **Rank:** 54 of 60 · **Surface:** ml-kem-key-exchange · **Origin:** T10 F-09
- **Severity:** INFO · **Exploitability:** Low
- **Source:** outputs/benchmark-kem.log; liboqs kem_ml_kem.h:22-25
- **Citation:** FIPS 203 Table 2; liboqs 0.14.0

### C-C08 — Testnet traffic is near idle; fee/burn figures are not stress figures (burn 98,436 drops over the window)

- **Rank:** 55 of 60 · **Surface:** network-agent-surface · **Origin:** T11 R-08
- **Severity:** INFO · **Exploitability:** Low
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet (see T11 pack)

### C-D06 — Reconnection pacing is adequate for healing

- **Rank:** 56 of 60 · **Surface:** overlay-partition-recovery · **Origin:** T12 R-06
- **Severity:** INFO · **Exploitability:** Low
- **Source:** T12 pack evidence
- **Citation:** postfiatd 0085a1ff (see T12 pack)

### C-E05 — The effective required fraction exceeds 67%: post-fix 67/100 strict '>' needs 17 of 25 votes (68.00%); pre-fix needed 19 (76.00%)

- **Rank:** 57 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-05
- **Severity:** INFO · **Exploitability:** Low
- **Source:** include/xrpl/protocol/SystemParameters.h:83,85
- **Citation:** data/source_excerpts.json E-08

### C-E07 — PF_AccountExclusion is disabled

- **Rank:** 58 of 60 · **Surface:** amendment-governance · **Origin:** T13 R-07
- **Severity:** INFO · **Exploitability:** Low
- **Source:** live inventory 101 amendments (see T13 pack)
- **Citation:** live testnet feature RPC 2026-11-25

### C-F08 — Ed25519 verification enforces canonicality and strips the 0xED key prefix

- **Rank:** 59 of 60 · **Surface:** release-signing · **Origin:** T14 R-08
- **Severity:** INFO · **Exploitability:** Low
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)

### C-G10 — Server-side TLS handshake call site is outside the pinned tree

- **Rank:** 60 of 60 · **Surface:** peer-transport-tls · **Origin:** T15 R-10
- **Severity:** INFO · **Exploitability:** Low
- **Source:** T15 pack evidence (negative search)
- **Citation:** postfiatd 0085a1ff (see T15 pack)
