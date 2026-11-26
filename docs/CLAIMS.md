# Claim Index

Every substantive claim in this pack, with its evidence. Labels:

- **[MEASURED]** — re-run fresh in this pack's own harness (liboqs 0.14.0, single thread), or re-verified against an originating pack's vendored log, which is cited by file and line.
- **[SIMULATED]** — the output of a model or simulation, not a measurement.
- **[UNSUPPORTED]** — a claim carried from an originating pack that this pack could not re-verify; it is recorded, not endorsed.

Findings (judgements) live in `docs/REMEDIATION.md` and `docs/RISK_REGISTER.md`, never here. Pinned postfiatd revision throughout: `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10). Machine: single thread; see `outputs/environment.txt`.

## A. Fresh measurements (this pack, re-run 2026-11-26)

### A1. Post-quantum signatures — `outputs/benchmark-pq.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-01 | [MEASURED] ML-DSA-44: verify 27,521.903/s, sign 9,165.012/s (32-byte message, 5 s budgets) | `benchmark-pq.log` (`--- ML-DSA-44 ---`, `verify_ops_per_sec: 27521.903`, `sign_ops_per_sec: 9165.012`) |
| M-02 | [MEASURED] ML-DSA-65: verify 16,319.199/s, sign 5,146.369/s | `benchmark-pq.log` (`--- ML-DSA-65 ---`) |
| M-03 | [MEASURED] ML-DSA-87: verify 11,197.188/s, sign 6,199.975/s | `benchmark-pq.log` (`--- ML-DSA-87 ---`) |
| M-04 | [MEASURED] SLH-DSA-SHA2-128s: verify 2,680.271/s, sign 2.798/s | `benchmark-pq.log` (`--- SLH-DSA-SHA2-128s ---`) |
| M-05 | [MEASURED] SLH-DSA-SHA2-128f: verify 897.479/s, sign 75.210/s | `benchmark-pq.log` (`--- SLH-DSA-SHA2-128f ---`) |
| M-06 | [MEASURED] On a 2,048-byte release-manifest payload: ML-DSA-44 verify 19,831.164/s; SLH-DSA-SHA2-128f verify 962.127/s | `benchmark-pq.log` (`--- ML-DSA-44 (2048-byte payload) ---`, `--- SLH-DSA-SHA2-128f (2048-byte payload) ---`) |
| M-07 | [MEASURED] Signature sizes: ML-DSA-44 2,420 B; ML-DSA-65 3,309 B; ML-DSA-87 4,627 B; SLH-DSA-128s 7,856 B; SLH-DSA-128f 17,088 B. Ratios vs Ed25519 64 B: 37.8x, 51.7x, 72.3x, 122.8x, 267.0x (arithmetic: 2420/64 = 37.8125; 3309/64 = 51.7031; 4627/64 = 72.2969; 7856/64 = 122.75; 17088/64 = 267.0) | `benchmark-pq.log` (`length_signature` per block); FIPS 204 Table 2; FIPS 205 |
| M-08 | [MEASURED] Public-key sizes: ML-DSA-44 1,312 B; ML-DSA-65 1,952 B; ML-DSA-87 2,592 B; SLH-DSA-128s/f 32 B | `benchmark-pq.log` (`length_public_key` per block); liboqs `sig_ml_dsa.h` (ML-DSA-44 signature 2,420 B) |
| M-09 | [MEASURED] Every algorithm's controls passed: a valid signature verifies, a tampered signature is rejected | `benchmark-pq.log` (`control_valid_signature_verifies: PASS`, `control_tampered_signature_rejected: PASS` per block) |

### A2. ML-KEM — `outputs/benchmark-kem.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-10 | [MEASURED] ML-KEM-512: keygen 16.21 us, encaps 17.21 us, decaps 21.45 us (n=500) | `benchmark-kem.log` (`RESULT ML-KEM-512 keygen_us=16.21 encaps_us=17.21 decaps_us=21.45 n=500`) |
| M-11 | [MEASURED] ML-KEM-768: keygen 27.16 us, encaps 26.96 us, decaps 32.77 us (n=500) | `benchmark-kem.log` (`RESULT ML-KEM-768 keygen_us=27.16 encaps_us=26.96 decaps_us=32.77 n=500`) |
| M-12 | [MEASURED] ML-KEM-1024: keygen 40.74 us, encaps 38.74 us, decaps 46.47 us (n=500) | `benchmark-kem.log` (`RESULT ML-KEM-1024 keygen_us=40.74 encaps_us=38.74 decaps_us=46.47 n=500`) |
| M-13 | [MEASURED] Implicit rejection: 108/108 invalid ciphertexts (36 per parameter set: bit-flips + random) decapsulated to a pseudorandom shared secret different from the reference | `benchmark-kem.log` (`RESULT implicit_rejection_total 108/108`) |
| M-14 | [MEASURED] ML-KEM-768 decaps timing: valid 34.323 us vs invalid 33.388 us (n=1000) — no timing signal at wall-clock resolution; this is not a constant-time proof | `benchmark-kem.log` (`RESULT ML-KEM-768 decaps_timing valid_us=34.323 invalid_us=33.388 n=1000`) |
| M-15 | [MEASURED] ML-KEM-768 key reuse: 100/100 roundtrips, 100/100 distinct ciphertexts; wrong-key decapsulation returns rc=0 with a non-matching secret; replay decapsulation is deterministic | `benchmark-kem.log` (`RESULT ML-KEM-768 key_reuse roundtrips=100/100 distinct_ciphertexts=100/100`, `wrong_key_decaps rc=0 matches_ref=0`, `replay_decaps deterministic=1`) |
| M-16 | [MEASURED] ML-KEM sizes (liboqs, verified against headers): 512 pk 800 / sk 1,632 / ct 768 / ss 32; 768 pk 1,184 / sk 2,400 / ct 1,088 / ss 32; 1024 pk 1,568 / sk 3,168 / ct 1,568 / ss 32 | `benchmark-kem.log` (`liboqs pk=... sk=... ct=... ss=32` per block); liboqs `kem_ml_kem.h:22-25` (768: pk 1184, sk 2400, ct 1088, ss 32) |

### A3. Hybrid handshake (X25519 + ML-KEM) — `outputs/hybrid_bench.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-17 | [MEASURED] X25519 baseline (OpenSSL EVP): keygen 70.63 us, derive 65.01 us (n=200); ECDH 18,123.5 ops/s | `hybrid_bench.log` (`RESULT X25519 keygen_us=70.63`, `RESULT X25519 derive_us=65.01`); `benchmark-classical.log` (`253 bits ecdh (X25519) 18123.5`) |
| M-18 | [MEASURED] Hybrid handshake totals: ML-KEM-512 170.17 us (client 79.51 + server 90.66); ML-KEM-768 183.13 us (89.18 + 93.95); ML-KEM-1024 206.37 us (98.05 + 108.32). Arithmetic check: 79.51 + 90.66 = 170.17; 89.18 + 93.95 = 183.13; 98.05 + 108.32 = 206.37 | `hybrid_bench.log` (`RESULT ML-KEM-512 hybrid client_us=79.51 server_us=90.66 total_us=170.17`, `RESULT ML-KEM-768 hybrid client_us=89.18 server_us=93.95 total_us=183.13`, `RESULT ML-KEM-1024 hybrid client_us=98.05 server_us=108.32 total_us=206.37`) |
| M-19 | [MEASURED] Hybrid wire bytes (excluding the 3-byte H-1 header): X25519 pubkey 32 B + ML-KEM pk 800/1,184/1,568 B + ML-KEM ct 768/1,088/1,568 B; totals with header 803/1,123/1,603 B | `hybrid_bench.log` (`RESULT ML-KEM-512 wire_bytes x25519_pub=32 mlkem_pk=800 mlkem_ct=768`, and the 768/1024 equivalents) |
| M-20 | [MEASURED] Hybrid controls: client/server shared secrets agree in both directions; an all-zero X25519 shared secret is rejected by OpenSSL (rc=-1); a tampered ciphertext decapsulates to a non-matching secret (rc=0, matches_ref=0) | `hybrid_bench.log` (`[PASS] hybrid client/server shared secrets agree`, `RESULT hybrid all_zero_x25519 rc=-1 rejected_by_openssl`, `RESULT hybrid tampered_ct rc=0 matches_ref=0`) |

### A4. Hybrid dual signature (release envelope) — `outputs/hybrid_dual_sig_bench.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-21 | [MEASURED] Ed25519 + ML-DSA-44 dual signature: combined 2,484 B (64 + 2,420); verify 5,051.858/s; sign 5,137.986/s (50-iteration cap: a lower bound) | `hybrid_dual_sig_bench.log` (`hybrid_signature_len: 2484`, `hybrid_verify_ops_per_sec: 5051.858`, `hybrid_sign_ops_per_sec: 5137.986`) |
| M-22 | [MEASURED] Ed25519 + SLH-DSA-SHA2-128f dual signature: verify 843.260/s | `hybrid_dual_sig_bench.log` (`hybrid_verify_ops_per_sec: 843.260`) |
| M-23 | [MEASURED] Dual-signature controls C-1..C-5 all PASS: valid hybrid verifies; tampered classical half rejected; tampered PQ half rejected; stripped PQ half rejected by exact-length check (got 64, want 2484); stripped classical half rejected (got 2420, want 2484) | `hybrid_dual_sig_bench.log` (`control C-1: PASS` … `control C-5: PASS`) |
| M-24 | [MEASURED] PFQS v1 envelope total: 8-byte header + 64 B Ed25519 + 2,420 B ML-DSA-44 = 2,492 B. Arithmetic: 8 + 64 + 2420 = 2492. Header bytes are fully fixed in `docs/memos/04-release-signing.md` (magic `PFQS`, version 0x01, mode 0x00, flags 0x00, reserved 0x00). | `hybrid_dual_sig_bench.log` (`hybrid_signature_len: 2484`); `docs/memos/04-release-signing.md` |

### A5. Classical baseline — `outputs/benchmark-classical.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-25 | [MEASURED] Ed25519 (OpenSSL 3.0.13, 2 s run): sign 19,035.5/s, verify 7,071.0/s | `benchmark-classical.log` (`253 bits EdDSA (Ed25519) 19035.5 7071.0`) |
| M-26 | [MEASURED] ML-DSA-44 verifies faster than the classical baseline on this machine: 27,521.903/s vs Ed25519 7,071.0/s (3.9x) | M-01 + M-25 (arithmetic: 27521.903 / 7071.0 = 3.89) |

### A6. Negative searches — `outputs/negative_search.log`, `outputs/negative_fips205_names.log`

| ID | Claim | Evidence |
|----|-------|----------|
| M-27 | [MEASURED] No post-quantum algorithm code exists in the pinned tree: case-insensitive grep for ML-DSA, ML-KEM, SLH-DSA, Kyber, Dilithium, SPHINCS over `src/` and `include/` returns zero matches | `outputs/negative_search.log` (`[step] result: zero matches above`) |
| M-28 | [MEASURED] No release-signing step exists in any workflow file: grep for cosign/sigstore/attest/gpg/sha256sum/checksum/slsa returns exactly 2 matches, both in `deploy.yml`, both importing the Caddy APT repository public key — neither signs a postfiatd release | `outputs/negative_search.log` (`[step] result: 2 matches above, both in deploy.yml …`) |
| M-29 | [MEASURED] No ML-KEM/ML-DSA code exists in the peer TLS files (`make_SSLContext.cpp`, `ConnectAttempt.cpp`) | `outputs/negative_search.log` (`[step] result: zero matches above`) |
| M-30 | [MEASURED] liboqs 0.14.0 does not register the FIPS 205 names: `bench_sig "SLH-DSA-SHA2-128s"` exits 1 with `result: ALGORITHM_NOT_ENABLED`; the same parameter sets are registered under their SPHINCS+ names | `outputs/negative_fips205_names.log` |

### A7. Pinned-source facts — `data/source_excerpts.json`

| ID | Claim | Evidence |
|----|-------|----------|
| M-31 | [MEASURED] Outgoing peer TLS sets `verify_none` (`ConnectAttempt.cpp:175`); the shared peer TLS context sets `verify_none` (`make_SSLContext.cpp:391`) | `data/source_excerpts.json` E-01, E-02 (verbatim excerpts; re-verified with `grep -n` on the pinned checkout) |
| M-32 | [MEASURED] Ephemeral self-signed RSA certificate, 2,048 bits (`make_SSLContext.cpp:66`); default cipher list `TLSv1.2:!CBC:!DSS:!PSK:!eNULL:!aNULL` (`:104`); only SSLv2/SSLv3/TLS 1.0/TLS 1.1 disabled, no min/max version (`:352-357`) | `data/source_excerpts.json` E-03, E-04, E-05 |
| M-33 | [MEASURED] Peer handshake rejects any node public key that is not secp256k1 (`Handshake.cpp:294`) | `data/source_excerpts.json` E-06 |
| M-34 | [MEASURED] Quorum comment `pi + pj < .33*ni` (`ValidatorList.cpp:1927-1928`); pre-fix majority 204/256 (`SystemParameters.h:83`), post-fix 67/100 (`:85`), majority hold 2 weeks (`:88`) | `data/source_excerpts.json` E-07, E-08 |
| M-35 | [MEASURED] Per-amendment vote counts (`count`/`validations`/`threshold`) are emitted only when `isAdmin` is true (`AmendmentTable.cpp:1019-1028`) | `data/source_excerpts.json` E-09 |

## B. Carried-forward measurements (originating packs; logs re-checked, not re-run)

| ID | Claim | Evidence |
|----|-------|----------|
| M-36 | [MEASURED] Live testnet window 2026-11-24 17:06:22Z → 2026-11-25 17:18:03Z: 28,800 ledgers (seqs 8332480→8361280), close-time mean 3.0243 s, 122 RPC requests, zero 429s; burn 98,436 drops | Originating pack T11 `outputs/measure_window.log` (re-checked: figures match the T11 claim index) |
| M-37 | [MEASURED] Agent-surface probes: P-01 GET / → 200; P-03 GET /api → 200 SPA-fallback; P-04 GET /api/tasks → 200 unauthenticated JSON read; P-05/P-06 POST /api/tasks → 405 | Originating pack T11 `outputs/agent_surface_probe.log:1-6` (re-checked verbatim) |
| M-38 | [MEASURED] Validator list seq 31: 25 validators, quorum 17 (67%) vs 20 (80% upstream), overlap 21/25 vs 23/25 | Originating pack T11 `outputs/validator_topology.log` (re-checked) |
| M-39 | [MEASURED] Partition-recovery drills D-01..D-04: 4/4 PASS; minimum survivable partition 17 (68%) at 67% quorum; max crash loss 8 at 67%; detection ≥ 1 flag period (~768 s) | Originating pack T12 `outputs/recovery_drills.log` (re-checked) |
| M-40 | [MEASURED] Amendment inventory (2026-11-25 19:27 UTC, validated ledger 8363822): 101 amendments, 64 enabled / 37 disabled, 0 changes vs the previous window | Originating pack T13 `outputs/feature_inventory.log`, `data/features_current.json` (re-checked) |
| M-41 | [MEASURED] Amendment arithmetic: post-fix threshold 67/100 strict `>` needs 17 of 25 votes (68.00%); pre-fix needed 19 (76.00%); majority hold 2 weeks = 1,209,600 s = 403,200 ledgers at 3.0000 s = 1,575.0 flag intervals | Originating pack T13 `outputs/governance_audit.log`, `outputs/lifecycle_simulation.log`; arithmetic re-checked: 1209600/3 = 403200; 1209600/768 = 1575.0 |
| M-42 | [MEASURED] Both PostFiat-specific amendments are disabled: `PF_ValidatorVoteTracking` and `PF_AccountExclusion` | Originating pack T13 inventory (re-checked); code exists at `src/xrpld/app/misc/ValidatorVoteTracker.cpp:162` |

## C. Simulated

| ID | Claim | Evidence |
|----|-------|----------|
| S-01 | [SIMULATED] Amendment activation timing: fastest 14 days (S-a); majority lost/regained → day 23 (S-c); 24 h expiry dip → day 20 (S-f); 16/25 votes, 9 vetoes, or the pre-fix rule at 17 votes → never (S-b, S-e, S-g) | Originating pack T13 `outputs/lifecycle_simulation.log` (model, not a live observation) |
| S-02 | [SIMULATED] Negative-UNL behaviour: max listed 7; quorum after full listing 15; disable < 128, re-enable > 204, vote > 230 | Originating pack T12 simulation (model, not a live observation) |
| S-03 | [SIMULATED] T13 R-06 9-veto scenario: 9 vetoes permanently block activation | Originating pack T13 simulation (labelled [SIMULATED] there too) |
| S-04 | [SIMULATED] T9 burst model: ML-DSA-44 sustains validation bursts at the measured verify rate; SLH-DSA-128f is the burst bottleneck | Originating pack T9 `outputs/burst-model.csv`, `outputs/burst-model.log` (model) |

## D. Unsupported

| ID | Claim | Evidence |
|----|-------|----------|
| U-01 | [UNSUPPORTED] "One verification entry point: easy to extend, single point of failure" (T9 F-05) — the originating pack's architectural reading of the verification path; this pack did not re-derive the call graph from the pinned tree, so it is carried as an origin-pack judgement, not as a re-verified claim | Originating pack T9 `FINDINGS.md` F-05; no fresh evidence in this pack |
| U-02 | [UNSUPPORTED] The T11 judgement that authorization is enforced at routing rather than at the API layer (T11 R-02) — the probe results (M-37) are measured, but the layer at which authorization lives was not re-derived from the server's code in this pack (the server code is not in the pinned tree) | Originating pack T11 `docs/REMEDIATION.md` R-02; probe log only |
| U-03 | [UNSUPPORTED] The T12 judgement that UNL uniformity cannot be treated as verified (T12 R-02) beyond the measured overlap figures (M-38) — the overlap numbers are measured; the uniformity judgement is carried, not re-derived | Originating pack T12 `docs/REMEDIATION.md` R-02 |

No claim in this pack is stated without a label. If a row above cannot be traced to its cited log, it is wrong — report it against the log, not against this index.
