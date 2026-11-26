# Memo 03 — Peer-Transport TLS

**Surface:** TLS on the peer port: authentication, certificates, versions, ciphers, and the hybrid KEM migration.
**Pinned revision:** `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
**Verdict:** anonymous by code, measured, and fully designed — but nothing can be switched on today. Score 1/5 (`docs/SCORECARD.md`).

## What this memo adds over the originating pack

The TLS migration pack measured the hybrid and specified the wire format. This memo ranks the findings by severity *and* exploitability, corrects one overstatement the originating pack could be read as making (the hybrid handshake does not authenticate peers), and names the interaction that makes this surface dangerous in combination rather than alone.

## Findings on this surface (consolidated)

| ID | Sev | Exploit | Finding |
|----|-----|---------|---------|
| C-G01 | HIGH | Medium | Peer TLS is anonymous; peer identity is not established by TLS |
| C-G02 | HIGH | Low | Ephemeral self-signed RSA-2048 peer certificate, no pinning |
| C-G03 | MEDIUM | Low | No TLS version floor/ceiling; cipher list does not cover TLS 1.3 |
| C-G04 | MEDIUM | Low | Operator `ssl_ciphers` does not apply to the peer port |
| C-G05 | MEDIUM | Low | Outbound HTTPS client pins TLS 1.2 |
| C-G06 | MEDIUM | Low | No ML-KEM support in the TLS stack |
| C-G07 | LOW | Low | Ephemeral certificate valid 2 years |
| C-G08 | LOW | Low | X25519 EVP keygen/derive overhead on hot paths |
| C-G09 | LOW | Low | ML-KEM-1024 key distribution size |
| C-G10 | INFO | Low | Server-side TLS handshake call site is outside the pinned tree |

Register ranks: C-G01 6, C-G02 9, C-G03 29, C-G04 30, C-G05 31, C-G06 32, C-G07 51, C-G08 52, C-G09 53, C-G10 60. Full text, sources, and fixes: `docs/REMEDIATION.md`.

## Measured facts (re-verified fresh in this pack)

- **Anonymous by code, both ends.** `ConnectAttempt.cpp:175` sets `verify_none` on the outgoing handshake; `make_SSLContext.cpp:391` sets `verify_none` in the shared context (`data/source_excerpts.json` E-01, E-02). Peer authentication comes from the manifest/signature layer above TLS — not from TLS.
- **Certificate:** ephemeral self-signed RSA-2048 (`make_SSLContext.cpp:66`, E-03), regenerated at every server start, valid 2 years. It carries no identity and is never verified.
- **Versions and ciphers:** only SSLv2/SSLv3/TLS 1.0/TLS 1.1 are disabled (`make_SSLContext.cpp:352-357`, E-05); no min/max version is set. The default cipher list is `TLSv1.2:!CBC:!DSS:!PSK:!eNULL:!aNULL` (`:104`, E-04) and does not govern TLS 1.3 ciphersuites.
- **No PQ code in the TLS files:** `outputs/negative_search.log` — zero ML-KEM/ML-DSA matches in `make_SSLContext.cpp` or `ConnectAttempt.cpp`. OpenSSL 3.0.13 as used here has no ML-KEM support.

## Fresh measurements (this pack)

Re-run 2026-11-26, liboqs 0.14.0, single thread (`outputs/hybrid_bench.log`, `outputs/benchmark-kem.log`):

| | Client (us) | Server (us) | Total (us) | Wire (B, excl. header) |
|---|---:|---:|---:|---:|
| X25519 + ML-KEM-512 | 79.51 | 90.66 | 170.17 | 32 + 800 + 768 |
| X25519 + ML-KEM-768 | 89.18 | 93.95 | 183.13 | 32 + 1,184 + 1,088 |
| X25519 + ML-KEM-1024 | 98.05 | 108.32 | 206.37 | 32 + 1,568 + 1,568 |

Arithmetic: 79.51 + 90.66 = 170.17; 89.18 + 93.95 = 183.13; 98.05 + 108.32 = 206.37. X25519 baseline: keygen 70.63 us, derive 65.01 us. ML-KEM-768 encaps 26.96 us, decaps 32.77 us. Implicit rejection 108/108. Controls: shared secrets agree both directions; all-zero X25519 rejected by OpenSSL (rc=-1); tampered ciphertext yields a non-matching secret.

**Recommended default: ML-KEM-768** (wire 1,123 B with the 3-byte header). ML-KEM-512 saves 320 B for a lower security level; ML-KEM-1024 costs 480 B more for a level the peer handshake does not need.

## The H-1 wire format (carried, byte-exact)

The hybrid key-exchange wire format, fixed in full (originating pack; re-verified against the fresh wire-byte results):

| Bytes | Content |
|---|---|
| 0 | version `0x01` |
| 1 | kem_id: `0x00` = ML-KEM-512, `0x01` = ML-KEM-768, `0x02` = ML-KEM-1024 |
| 2 | mode `0x00` (hybrid X25519 + ML-KEM; all other values reserved, must reject) |
| 3–34 | X25519 public key (32 B) |
| 35… | ML-KEM ciphertext (768 / 1,088 / 1,568 B by kem_id) |

Total wire: 803 / 1,123 / 1,603 B. Every byte is fixed; there are no unspecified bytes in this format. The ML-KEM public key is the peer's long-term KEM key, distributed out of band (same channel as the validator manifest); the ciphertext is per-handshake.

## A correction to the originating pack's framing

The hybrid handshake protects **session confidentiality** against a future quantum adversary. It does **not** authenticate the peer: the handshake is still anonymous at the TLS layer, and peer identity still lives entirely in the manifest/signature layer. Any description of the S1 hybrid handshake as "securing peer identity" would be wrong. The fix for C-G01 is not the hybrid handshake — the fix is to stop relying on TLS for identity at all, keep identity in the manifest layer, and make sure that layer is itself signed (see Memo 04 and interaction X-1).

## Cross-surface interactions

- **X-1 (with release signing):** anonymous TLS + unsigned releases is the highest-compounding interaction in the pack. A network MITM terminates TLS and serves a tampered binary; nothing checks it. Either fix breaks the chain; release signing (S0-1) is cheaper.
- **X-3 (with validator manifests):** the validation signature is the only peer authentication. TLS contributes nothing, so the S1 handshake must be evaluated on confidentiality alone.
- **X-5 (with ML-KEM absence):** recorded peer traffic is harvestable now and decryptable later. The S1 hybrid handshake is the only stage that closes the harvest window for new traffic; it does nothing for traffic already recorded.
- **With amendment governance:** the outbound HTTPS client (C-G05) fetches the validator site and the exclusion list — the data governance decisions depend on. It pins TLS 1.2 while the peer port has no version floor at all: the one TLS client that verifies anything is the one with the narrowest version policy.

## The single most valuable fix on this surface

**The S1 hybrid KEM peer handshake (S1-4), behind a testnet flag.** It is the only fix that closes the harvest-now window for peer traffic, and it is fully specified and measured — there is no design work left, only implementation. The cheaper S0 fixes (version floor, cipher list, S0-4) should ship first because they cost nothing, but they change no cryptography.
