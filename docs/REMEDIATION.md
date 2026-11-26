# Remediation — consolidated findings and recommended actions

Severity is judged by the harm if the weakness is used; exploitability by how easily an attacker can trigger it. Both are judged against the pinned tree and the live testnet evidence cited. **Counts: 60 findings — 9 HIGH, 23 MEDIUM, 21 LOW, 7 INFO.**

Findings are not claims: measured claims live in `docs/CLAIMS.md`; these are the judgements drawn from them. Each finding names the roadmap stage that closes it; the full roadmap is `docs/ROADMAP.md`.

## Priority order

1. **S0-1 release signing (C-F01)** — the single most valuable fix: Ed25519 signature + SHA-256 checksum on every release.
2. **S0-3 authenticate /api/tasks (C-C01)** — a one-line authorization check on a public endpoint.
3. **S0-2 pin images by digest (C-F02)** — stop directing operators to mutable `-latest` tags.
4. **S1 hybrid releases and hybrid peer handshake (C-F04, C-G06, C-B01)** — the first post-quantum cryptography shipped.
5. **S2 governance observability (C-E01, C-E02) and dual-signed validations (C-A06)**.

## network-agent-surface

### C-C01 — HIGH: Unauthenticated /api/tasks read: GET returns 200 with task JSON to any caller

- **Rank:** 1 of 60 · **Exploitability:** High · **Origin:** T11 R-01
- **Source:** T11 outputs/agent_surface_probe.log:4 (P-04 GET /api/tasks -> 200 UNAUTHENTICATED-JSON-READ)
- **Citation:** live testnet endpoint, window 2026-11-24/25 (see T11 pack)
- **Fix:** Require authentication on /api/tasks (S0-3). This is the second most valuable fix in the pack.

### C-C02 — MEDIUM: Authorization enforced at routing, not at the API layer

- **Rank:** 12 of 60 · **Exploitability:** Medium · **Origin:** T11 R-02
- **Source:** T11 pack evidence (P-05/P-06 POST -> 405, not 401/403)
- **Citation:** live testnet endpoint (see T11 pack)
- **Fix:** Enforce authorization at the API layer (S0-3); do not rely on routing to hide endpoints.

### C-C03 — MEDIUM: Track the 67% -> 80% quorum revert as a mainnet gate (live VL seq 31, quorum 17 of 25 = 67%)

- **Rank:** 22 of 60 · **Exploitability:** Low · **Origin:** T11 R-03
- **Source:** T11 outputs/validator_topology.log
- **Citation:** postfiatd 0085a1ff; live testnet VL
- **Fix:** Decide the 67% vs 80% quorum explicitly and record it (S4-1); do not go to mainnet on an undecided quorum.

### C-C04 — LOW: Publish /robots.txt (or return a real 404)

- **Rank:** 39 of 60 · **Exploitability:** Low · **Origin:** T11 R-04
- **Source:** T11 outputs/agent_surface_probe.log
- **Citation:** live testnet endpoint (see T11 pack)
- **Fix:** Publish /robots.txt (S0-6).

### C-C05 — LOW: Stop serving the app shell for unknown /api/* paths

- **Rank:** 40 of 60 · **Exploitability:** Low · **Origin:** T11 R-05
- **Source:** T11 outputs/agent_surface_probe.log:3 (P-03 GET /api -> 200 SPA-FALLBACK)
- **Citation:** live testnet endpoint (see T11 pack)
- **Fix:** Return a real 404 for unknown /api/* paths (S0-6).

### C-C06 — LOW: Document and signal API rate limits (122 RPC requests, zero 429s in the measured window)

- **Rank:** 41 of 60 · **Exploitability:** Low · **Origin:** T11 R-06
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet RPC (see T11 pack)
- **Fix:** Document and signal API rate limits (S0-6).

### C-C07 — LOW: Monitor close-time segment means, not per-ledger diffs (mean close time 3.0243 s)

- **Rank:** 42 of 60 · **Exploitability:** Low · **Origin:** T11 R-07
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet ledgers 8332480-8361280 (see T11 pack)
- **Fix:** Monitor close-time segment means, not per-ledger diffs.

### C-C08 — INFO: Testnet traffic is near idle; fee/burn figures are not stress figures (burn 98,436 drops over the window)

- **Rank:** 55 of 60 · **Exploitability:** Low · **Origin:** T11 R-08
- **Source:** T11 outputs/measure_window.log
- **Citation:** live testnet (see T11 pack)
- **Fix:** No action: testnet idleness is a fact about the measurement window, not a defect.

## release-signing

### C-F01 — HIGH: GitHub releases are published unsigned: no signature, attestation, or checksum with any release

- **Rank:** 2 of 60 · **Exploitability:** High · **Origin:** T14 R-01
- **Source:** .github/workflows/testnet-build.yml:44-71 (gh release create, notes only); negative grep for cosign/sigstore/attest/gpg/sha256sum over all ten workflow files
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** Publish an Ed25519 signature and SHA-256 checksum with every release, plus a verifier script (S0-1). This is the single most valuable fix in the pack.

### C-F02 — HIGH: Docker images pushed unsigned, under mutable -latest tags; image signing explicitly deferred to 'Phase 2 or mainnet'

- **Rank:** 3 of 60 · **Exploitability:** High · **Origin:** T14 R-02
- **Source:** .github/workflows/build.yml:71-90; docs/dynamic-unl/reviews/FeedbackAnalysis_Codex54.md:335,341
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** Pin images by digest; stop directing operators to -latest tags (S0-2). Revisit the explicit deferral of image signing with a date or release version, not 'Phase 2 or mainnet'.

### C-F03 — MEDIUM: No rollback protection for releases (no signed version record, no sequence enforcement)

- **Rank:** 13 of 60 · **Exploitability:** Medium · **Origin:** T14 R-03
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** Add a signed manifest sequence number and enforce monotonic sequence on upgrade (S1-3).

### C-F04 — MEDIUM: Downgrade risk during the hybrid transition (a stripped PQ half must be rejected by length check)

- **Rank:** 14 of 60 · **Exploitability:** Medium · **Origin:** T14 R-04
- **Source:** outputs/hybrid_dual_sig_bench.log (controls C-4/C-5: stripped halves rejected)
- **Citation:** this pack, fresh re-run
- **Fix:** Ship the PFQS v1 hybrid envelope with an exact-length check (S1-1); a stripped half must be rejected, as controls C-4/C-5 demonstrate.

### C-F09 — MEDIUM: No published key-rotation procedure exists for release keys

- **Rank:** 15 of 60 · **Exploitability:** Medium · **Origin:** T14 R-09
- **Source:** T14 pack evidence (negative search)
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** Publish the key-rotation procedure (S1-2) and exercise it once on a test release.

### C-F05 — MEDIUM: SLH-DSA-128s signing is too slow for any high-frequency use (2.8/s) and SLH-DSA signatures are very large (17,088 B for 128f)

- **Rank:** 28 of 60 · **Exploitability:** Low · **Origin:** T14 R-05
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205; liboqs 0.14.0
- **Fix:** Do not use SLH-DSA-128s for high-frequency signing; use ML-DSA-44 as the PQ half and evaluate SLH-DSA-128f only for archival releases (S3-2).

### C-F06 — LOW: ML-DSA security rests on lattice assumptions; a lattice break would break the PQ half (the Ed25519 half survives: AND-verification)

- **Rank:** 48 of 60 · **Exploitability:** Low · **Origin:** T14 R-06
- **Source:** outputs/hybrid_dual_sig_bench.log (hybrid_verify_ops_per_sec 5051.858)
- **Citation:** FIPS 204; NIST PQC
- **Fix:** Keep AND-verification: the Ed25519 half survives a lattice break, and the ML-DSA-44 half survives a classical break. Do not ship a PQ-only signature.

### C-F07 — LOW: secp256k1 ECDSA DER signatures are malleable unless canonicality is enforced: already mitigated in-tree

- **Rank:** 49 of 60 · **Exploitability:** Low · **Origin:** T14 R-07
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** No action: canonicality is already enforced in-tree.

### C-F10 — LOW: The release pipeline's trust anchor is a GitHub Actions token; signing alone does not fix a compromised pipeline

- **Rank:** 50 of 60 · **Exploitability:** Low · **Origin:** T14 R-10
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** Harden the release pipeline itself (least-privilege tokens, branch protection, required reviews); signing attests to the release, not to the pipeline.

### C-F08 — INFO: Ed25519 verification enforces canonicality and strips the 0xED key prefix

- **Rank:** 59 of 60 · **Exploitability:** Low · **Origin:** T14 R-08
- **Source:** T14 pack evidence
- **Citation:** postfiatd 0085a1ff (see T14 pack)
- **Fix:** No action: recorded fact.

## protocol-signatures

### C-A01 — HIGH: No post-quantum signature support in the pinned revision

- **Rank:** 4 of 60 · **Exploitability:** Medium · **Origin:** T9 F-01
- **Source:** negative search over the pinned tree (no ML-DSA/SLH-DSA code)
- **Citation:** FIPS 204; FIPS 205; this pack outputs/benchmark-pq.log
- **Fix:** Follow the staged roadmap: PFQS v1 hybrid release envelope (S1), ML-DSA validation signatures testnet-gated (S2), full migration before mainnet (S4).

### C-A02 — HIGH: Signature-size blowup dominates the migration cost (ML-DSA-44 2,420 B = 37.8x Ed25519 64 B)

- **Rank:** 7 of 60 · **Exploitability:** Low · **Origin:** T9 F-02
- **Source:** outputs/benchmark-pq.log (length_signature 2420 vs 64)
- **Citation:** FIPS 204 Table 2; liboqs sig_ml_dsa.h:11
- **Fix:** Accept the size cost where signatures are rare (releases, validations); do not put ML-DSA-87 or SLH-DSA on any high-frequency path. Prefer ML-DSA-44 (2,420 B) as the default PQ half.

### C-A05 — MEDIUM: One verification entry point: easy to extend, single point of failure

- **Rank:** 10 of 60 · **Exploitability:** Medium · **Origin:** T9 F-05
- **Source:** pinned tree signature verification path
- **Citation:** postfiatd 0085a1ff (see T9 pack)
- **Fix:** When the PQ entry point is added, keep a single dispatch but add per-algorithm test vectors and a fuzz target; the single point of failure is acceptable only with that coverage. (Origin-pack judgement; see CLAIMS.md U-01.)

### C-A06 — MEDIUM: Validator validation signatures are secp256k1-only

- **Rank:** 11 of 60 · **Exploitability:** Medium · **Origin:** T9 F-06
- **Source:** src/xrpld/overlay/detail/Handshake.cpp:294
- **Citation:** data/source_excerpts.json E-06
- **Fix:** Dual-sign validations during transition (S2-2); secp256k1 retained until the network migrates. The handshake check (Handshake.cpp:294) is the gate that must be widened, not removed.

### C-A03 — MEDIUM: SLH-DSA verification is the burst bottleneck (128f 897.5/s; 128s sign 2.8/s)

- **Rank:** 16 of 60 · **Exploitability:** Low · **Origin:** T9 F-03
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205; liboqs 0.14.0
- **Fix:** Do not use SLH-DSA on burst paths. Reserve SLH-DSA-128f for long-lived archival signatures (S3-2 decision).

### C-A04 — MEDIUM: ML-DSA verification is faster than the classical baseline here (ML-DSA-44 27,521.9/s vs Ed25519 7,071.0/s)

- **Rank:** 17 of 60 · **Exploitability:** Low · **Origin:** T9 F-04
- **Source:** outputs/benchmark-pq.log; outputs/benchmark-classical.log
- **Citation:** liboqs 0.14.0; OpenSSL 3.0.13
- **Fix:** No action: ML-DSA-44 verify is faster than Ed25519 verify on this machine; the migration is not blocked on verify cost.

### C-A07 — LOW: SLH-DSA 'f' is faster to sign but slower to verify than 's'

- **Rank:** 33 of 60 · **Exploitability:** Low · **Origin:** T9 F-07
- **Source:** outputs/benchmark-pq.log
- **Citation:** FIPS 205
- **Fix:** Prefer 's' variants where verify rate matters; 'f' only where sign rate matters and signatures are rare.

### C-A08 — LOW: No secp256k1 baseline was measured (OpenSSL speed has no secp256k1; P-256 used as stand-in)

- **Rank:** 34 of 60 · **Exploitability:** Low · **Origin:** T9 F-08
- **Source:** outputs/benchmark-classical.log
- **Citation:** OpenSSL 3.0.13
- **Fix:** Measure secp256k1 verify directly (e.g. via the in-tree secp256k1 library) before sizing any validation path on it.

## ml-kem-key-exchange

### C-B01 — HIGH: postfiatd has no ML-KEM code at all

- **Rank:** 5 of 60 · **Exploitability:** Medium · **Origin:** T10 F-01
- **Source:** negative search over the pinned tree
- **Citation:** FIPS 203; this pack outputs/benchmark-kem.log
- **Fix:** Implement the S1 hybrid KEM peer handshake; add ML-KEM to the TLS stack in S3. Until then the exposure is harvest-now (see X-5).

### C-B06 — HIGH: X-Wing (draft-11) has no all-zero X25519 check; the combiner itself does not reject a zero shared secret

- **Rank:** 8 of 60 · **Exploitability:** Low · **Origin:** T10 F-06
- **Source:** outputs/hybrid_bench.log (all_zero_x25519 rc=-1 rejected_by_openssl: the rejection comes from OpenSSL, not from the combiner)
- **Citation:** draft-irtf-cfrg-xwing-kem-11; RFC 10024
- **Fix:** Enforce the all-zero X25519 check in the combiner itself (S3-1), not only in OpenSSL: reject a zero shared secret before combining.

### C-B02 — MEDIUM: Implicit rejection is silent: no error is ever returned for an invalid ciphertext

- **Rank:** 18 of 60 · **Exploitability:** Low · **Origin:** T10 F-02
- **Source:** outputs/benchmark-kem.log (implicit_rejection_total 108/108)
- **Citation:** FIPS 203 section 7.3
- **Fix:** Return an explicit, distinguishable error for invalid ciphertexts at the application layer (S3-3); do not rely on the pseudorandom output alone to signal rejection.

### C-B05 — MEDIUM: Key reuse is safe for correctness, unsafe to assume for replay protection

- **Rank:** 19 of 60 · **Exploitability:** Low · **Origin:** T10 F-05
- **Source:** outputs/benchmark-kem.log (key_reuse roundtrips 100/100)
- **Citation:** FIPS 203 section 7.2
- **Fix:** Do not reuse a KEM keypair across sessions that need replay protection; bind each handshake to a fresh ephemeral keypair and a transcript hash.

### C-B07 — MEDIUM: X-Wing is still a draft; the TLS hybrid combiner is already an RFC

- **Rank:** 20 of 60 · **Exploitability:** Low · **Origin:** T10 F-07
- **Source:** T10 pack evidence
- **Citation:** RFC 10024
- **Fix:** Prefer the RFC combiner (RFC 10024) over the X-Wing draft where both are available; track the draft's standardisation.

### C-B10 — MEDIUM: The FIPS 203 section 7.3 length check must live in the application

- **Rank:** 21 of 60 · **Exploitability:** Low · **Origin:** T10 F-10
- **Source:** FIPS 203 section 7.3 (no in-tree caller exists)
- **Citation:** FIPS 203 section 7.3
- **Fix:** Apply the FIPS 203 section 7.3 length check in the application (S3-3) wherever ML-KEM ciphertexts are accepted.

### C-B03 — LOW: Rejected outputs are distinct per invalid ciphertext (pseudorandom shared secret, as specified)

- **Rank:** 35 of 60 · **Exploitability:** Low · **Origin:** T10 F-03
- **Source:** outputs/benchmark-kem.log
- **Citation:** FIPS 203 section 7.3
- **Fix:** No action: distinct pseudorandom outputs per invalid ciphertext are the specified behaviour (FIPS 203 section 7.3).

### C-B04 — LOW: No timing signal at wall-clock resolution; not a constant-time proof

- **Rank:** 36 of 60 · **Exploitability:** Low · **Origin:** T10 F-04
- **Source:** outputs/benchmark-kem.log (valid 34.323 us vs invalid 33.388 us, n=1000, re-measured in T10)
- **Citation:** FIPS 203
- **Fix:** No action at wall-clock resolution; a constant-time claim requires a dedicated timing analysis, not a benchmark.

### C-B08 — LOW: liboqs 0.14.0 does not ship X-Wing or expose ML-KEM.KeyGen_internal

- **Rank:** 37 of 60 · **Exploitability:** Low · **Origin:** T10 F-08
- **Source:** liboqs 0.14.0 headers (kem.h; no X-Wing registration)
- **Citation:** liboqs 0.14.0
- **Fix:** No action in this pack: use the liboqs ML-KEM API as shipped; do not vendor a draft X-Wing implementation.

### C-B11 — LOW: ML-KEM alone lacks the binding properties X-Wing provides

- **Rank:** 38 of 60 · **Exploitability:** Low · **Origin:** T10 F-11
- **Source:** T10 pack analysis
- **Citation:** draft-irtf-cfrg-xwing-kem-11
- **Fix:** Use a combiner (X-Wing or the RFC hybrid) rather than raw ML-KEM wherever binding between the classical and PQ halves matters.

### C-B09 — INFO: Sizes and speeds confirmed (ML-KEM-768 pk 1,184 B, ct 1,088 B, ss 32 B)

- **Rank:** 54 of 60 · **Exploitability:** Low · **Origin:** T10 F-09
- **Source:** outputs/benchmark-kem.log; liboqs kem_ml_kem.h:22-25
- **Citation:** FIPS 203 Table 2; liboqs 0.14.0
- **Fix:** No action: sizes and speeds are confirmed and cited in CLAIMS.md M-16.

## peer-transport-tls

### C-G01 — HIGH: Peer TLS is anonymous: peer identity is not established by TLS (verify_none on both ends)

- **Rank:** 6 of 60 · **Exploitability:** Medium · **Origin:** T15 R-01
- **Source:** src/xrpld/overlay/detail/ConnectAttempt.cpp:175; src/libxrpl/basics/make_SSLContext.cpp:391
- **Citation:** data/source_excerpts.json E-01, E-02
- **Fix:** Do not rely on TLS for peer identity: keep identity in the manifest/signature layer, and protect session confidentiality with the S1 hybrid KEM handshake. TLS anonymity is acceptable only while the manifest layer is the trust anchor and is itself signed (see X-1, X-3).

### C-G02 — HIGH: Ephemeral self-signed RSA-2048 peer certificate, no pinning; the certificate carries no identity and is never verified

- **Rank:** 9 of 60 · **Exploitability:** Low · **Origin:** T15 R-02
- **Source:** src/libxrpl/basics/make_SSLContext.cpp:66
- **Citation:** data/source_excerpts.json E-03
- **Fix:** Keep the certificate ephemeral and anonymous; never add verification of peer certificates without a pinning or PKI design.

### C-G03 — MEDIUM: No TLS version floor/ceiling; cipher list does not cover TLS 1.3

- **Rank:** 29 of 60 · **Exploitability:** Low · **Origin:** T15 R-03
- **Source:** src/libxrpl/basics/make_SSLContext.cpp:104,352-357
- **Citation:** data/source_excerpts.json E-04, E-05
- **Fix:** Set an explicit TLS version floor and TLS 1.3 ciphersuite list (S0-4).

### C-G04 — MEDIUM: Operator ssl_ciphers does not apply to the peer port (peer listener always uses make_SSLContext(""))

- **Rank:** 30 of 60 · **Exploitability:** Low · **Origin:** T15 R-04
- **Source:** T15 pack evidence (OverlayImpl.cpp:1550; ServerHandler.cpp:1090,1092)
- **Citation:** postfiatd 0085a1ff (see T15 pack)
- **Fix:** Pass the operator ssl_ciphers list to the peer listener, or document that the peer port intentionally uses the default list (S0-4).

### C-G05 — MEDIUM: Outbound HTTPS client pins TLS 1.2 (validator-site and exclusion-list fetches)

- **Rank:** 31 of 60 · **Exploitability:** Low · **Origin:** T15 R-05
- **Source:** T15 pack evidence (WorkSSL.cpp:41)
- **Citation:** postfiatd 0085a1ff (see T15 pack)
- **Fix:** Allow TLS 1.3 in the outbound HTTPS client (S2-3).

### C-G06 — MEDIUM: No ML-KEM support in the TLS stack (OpenSSL 3.0.13 as used here has none)

- **Rank:** 32 of 60 · **Exploitability:** Low · **Origin:** T15 R-06
- **Source:** negative search; outputs/benchmark-kem.log
- **Citation:** FIPS 203; OpenSSL 3.0.13
- **Fix:** Add ML-KEM to the TLS stack via a provider (S3-1); until then the S1 hybrid handshake is the transport protection.

### C-G07 — LOW: Ephemeral certificate valid 2 years

- **Rank:** 51 of 60 · **Exploitability:** Low · **Origin:** T15 R-07
- **Source:** T15 pack evidence
- **Citation:** postfiatd 0085a1ff (see T15 pack)
- **Fix:** No action: a 2-year validity on an ephemeral, unverified certificate is not itself a defect; revisit if the certificate ever carries identity.

### C-G08 — LOW: X25519 EVP keygen/derive overhead on hot paths (keygen 70.63 us, derive 65.01 us, n=200)

- **Rank:** 52 of 60 · **Exploitability:** Low · **Origin:** T15 R-08
- **Source:** outputs/hybrid_bench.log
- **Citation:** this pack, fresh re-run
- **Fix:** No action: X25519 keygen/derive at ~70/65 us is acceptable on the peer handshake path; re-measure if the handshake rate grows.

### C-G09 — LOW: ML-KEM-1024 key distribution size (pk 1,568 B, ct 1,568 B; hybrid wire 1,603 B)

- **Rank:** 53 of 60 · **Exploitability:** Low · **Origin:** T15 R-09
- **Source:** outputs/hybrid_bench.log
- **Citation:** FIPS 203 Table 2; liboqs 0.14.0
- **Fix:** Prefer ML-KEM-768 (wire 1,123 B) as the default hybrid; reserve ML-KEM-1024 (1,603 B) for deployments that need its level.

### C-G10 — INFO: Server-side TLS handshake call site is outside the pinned tree

- **Rank:** 60 of 60 · **Exploitability:** Low · **Origin:** T15 R-10
- **Source:** T15 pack evidence (negative search)
- **Citation:** postfiatd 0085a1ff (see T15 pack)
- **Fix:** No action: recorded fact; the server-side call site is outside the pinned tree.

## overlay-partition-recovery

### C-D01 — MEDIUM: Quorum comment's fork-safety claim is wrong: the pi+pj < .33*ni bound holds only at zero Byzantine faults; under the comment's own fault model Theorem 8 certifies nothing at 67% (required overlap 28.5 > 25)

- **Rank:** 23 of 60 · **Exploitability:** Low · **Origin:** T12 R-01
- **Source:** src/xrpld/app/misc/detail/ValidatorList.cpp:1927-1928
- **Citation:** data/source_excerpts.json E-07
- **Fix:** Correct the comment in ValidatorList.cpp (S0-5): state that pi+pj < .33*ni holds only at zero Byzantine faults.

### C-D02 — MEDIUM: Do not treat UNL uniformity as verified (25 validators, overlap 21/25 at 67% vs 23/25 upstream)

- **Rank:** 24 of 60 · **Exploitability:** Low · **Origin:** T12 R-02
- **Source:** T12 pack evidence; T11 validator_topology.log
- **Citation:** live testnet VL seq 31 (see T11/T12 packs)
- **Fix:** Verify UNL uniformity independently before relying on it; do not assume it from the overlap figure. (See CLAIMS.md U-03.)

### C-D03 — MEDIUM: A sub-quorum side cannot self-rescue via the negative UNL (max listed 7; quorum after full listing 15)

- **Rank:** 25 of 60 · **Exploitability:** Low · **Origin:** T12 R-03
- **Source:** T12 pack evidence (negative-UNL simulation)
- **Citation:** postfiatd 0085a1ff (see T12 pack)
- **Fix:** Document that a sub-quorum side cannot self-rescue via the negative UNL; plan recovery around rejoining the majority side.

### C-D04 — LOW: Do not use converged/diverged flags as a partition detector

- **Rank:** 43 of 60 · **Exploitability:** Low · **Origin:** T12 R-04
- **Source:** T12 pack evidence
- **Citation:** postfiatd 0085a1ff (see T12 pack)
- **Fix:** Do not use converged/diverged flags as a partition detector; use ledger-sequence divergence and quorum accounting.

### C-D05 — LOW: Plan ledger catch-up capacity for long partitions (drills D-01..D-04 4/4 PASS; detection >= 1 flag period ~768 s)

- **Rank:** 44 of 60 · **Exploitability:** Low · **Origin:** T12 R-05
- **Source:** T12 outputs/recovery_drills.log
- **Citation:** postfiatd 0085a1ff (see T12 pack)
- **Fix:** Plan ledger catch-up capacity for long partitions (fetch window, bandwidth, and time to rejoin).

### C-D06 — INFO: Reconnection pacing is adequate for healing

- **Rank:** 56 of 60 · **Exploitability:** Low · **Origin:** T12 R-06
- **Source:** T12 pack evidence
- **Citation:** postfiatd 0085a1ff (see T12 pack)
- **Fix:** No action: reconnection pacing is adequate.

## amendment-governance

### C-E01 — MEDIUM: Per-amendment vote counts are not publicly observable (count/validations/threshold emitted only for admin callers)

- **Rank:** 26 of 60 · **Exploitability:** Low · **Origin:** T13 R-01
- **Source:** src/xrpld/app/misc/detail/AmendmentTable.cpp:1019-1028
- **Citation:** data/source_excerpts.json E-09
- **Fix:** Make per-amendment vote counts publicly readable (S2-1).

### C-E02 — MEDIUM: The vote-tracking amendment is itself disabled (PF_ValidatorVoteTracking; both PostFiat-specific amendments disabled)

- **Rank:** 27 of 60 · **Exploitability:** Low · **Origin:** T13 R-02
- **Source:** src/xrpld/app/misc/ValidatorVoteTracker.cpp:162; live inventory 101 amendments, 64 enabled / 37 disabled
- **Citation:** postfiatd 0085a1ff; live testnet feature RPC 2026-11-25 (see T13 pack)
- **Fix:** Enable PF_ValidatorVoteTracking or publish its output (S2-1); a vote that cannot be observed cannot be audited.

### C-E03 — LOW: A lost majority restarts the full 2-week clock (majority hold 1,209,600 s = 403,200 ledgers)

- **Rank:** 45 of 60 · **Exploitability:** Low · **Origin:** T13 R-03
- **Source:** include/xrpl/protocol/SystemParameters.h:88
- **Citation:** data/source_excerpts.json E-08
- **Fix:** No action: the 2-week restart on a lost majority is the specified behaviour; operators should know it before voting.

### C-E04 — LOW: 24 h vote expiry can cost a majority (activation S-f: day 20 instead of day 14)

- **Rank:** 46 of 60 · **Exploitability:** Low · **Origin:** T13 R-04
- **Source:** T13 pack lifecycle simulation
- **Citation:** postfiatd 0085a1ff (see T13 pack)
- **Fix:** Monitor vote expiry (24 h) during any amendment campaign; re-vote before expiry where a majority is close.

### C-E06 — LOW: 9 vetoes permanently block activation (simulated scenario S-e)

- **Rank:** 47 of 60 · **Exploitability:** Low · **Origin:** T13 R-06
- **Source:** T13 pack lifecycle simulation (labelled [SIMULATED])
- **Citation:** postfiatd 0085a1ff (see T13 pack)
- **Fix:** No action: 9 vetoes blocking activation is the specified behaviour; the risk is governance deadlock, mitigated by S2-1 observability.

### C-E05 — INFO: The effective required fraction exceeds 67%: post-fix 67/100 strict '>' needs 17 of 25 votes (68.00%); pre-fix needed 19 (76.00%)

- **Rank:** 57 of 60 · **Exploitability:** Low · **Origin:** T13 R-05
- **Source:** include/xrpl/protocol/SystemParameters.h:83,85
- **Citation:** data/source_excerpts.json E-08
- **Fix:** No action: the 68% effective fraction is a fact of the post-fix arithmetic; record it in operator docs.

### C-E07 — INFO: PF_AccountExclusion is disabled

- **Rank:** 58 of 60 · **Exploitability:** Low · **Origin:** T13 R-07
- **Source:** live inventory 101 amendments (see T13 pack)
- **Citation:** live testnet feature RPC 2026-11-25
- **Fix:** No action: PF_AccountExclusion being disabled is a recorded state, not a defect.
