# Sources

## Primary standards

- NIST FIPS 203, *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (ML-KEM), August 2024. Sections cited: 7.2 (key generation / encapsulation), 7.3 (decapsulation, implicit rejection, length checks).
- NIST FIPS 204, *Module-Lattice-Based Digital Signature Standard* (ML-DSA), August 2024. Table 2 (parameter sets, sizes).
- NIST FIPS 205, *Stateless Hash-Based Digital Signature Standard* (SLH-DSA), August 2024.
- RFC 10024 (hybrid key exchange in TLS 1.3; the TLS hybrid combiner referenced by the ML-KEM assessment).
- draft-irtf-cfrg-xwing-kem-11 (X-Wing hybrid KEM combiner; still a draft at the time of writing).
- OpenSSL 3.0.13 (classical baseline; `openssl speed`).
- liboqs 0.14.0, commit `94b421ebb82405c843dba4e9aa521a56ee5a333d` (open-quantum-safe/liboqs, tag 0.14.0). Headers used for size verification: `sig_ml_dsa.h:11` (ML-DSA-44 signature 2,420 B), `kem_ml_kem.h:22-25` (ML-KEM-768: pk 1,184, sk 2,400, ct 1,088, ss 32).

## Pinned postfiatd revision

- postfiatd, commit `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10, version 1.0.9).
- Verbatim source excerpts with file:line: `data/source_excerpts.json` (E-01..E-09). Every cited line number was verified with `grep -n` on the local pinned checkout, never from a raw-file fetch.
- Live testnet evidence (testnet RPC and endpoints, windows 2026-11-24/25) is carried from the originating packs; see `docs/CLAIMS.md` section B for the exact logs.

## Originating packs (consolidated here)

Seven prior evaluation packs, each a public GitHub repository under the same author account; their vendored logs were re-checked (not re-run) for the carried-forward claims in `docs/CLAIMS.md` section B, and their key measurements were re-run fresh in this pack's own harness (section A).

| Pack | Subject | Findings carried |
|---|---|---|
| Protocol security and lattice benchmarks | ML-DSA/SLH-DSA benchmarks, 8 findings | C-A01..C-A08 |
| ML-KEM implicit-rejection and hybrid-KEM assessment | ML-KEM, implicit rejection, X-Wing/RFC-10024 hybrids, 11 findings | C-B01..C-B11 |
| Second-window network and agent reference | Live testnet window, agent surface probes, 8 findings | C-C01..C-C08 |
| Overlay partition-recovery evidence pack | Quorum/Theorem 8, negative UNL, drills, 6 findings | C-D01..C-D06 |
| Amendment lifecycle evaluation evidence pack | Amendment inventory, thresholds, lifecycle model, 7 findings | C-E01..C-E07 |
| Post-quantum release-signing migration pack | Release/image signing, hybrid dual signature, 10 findings | C-F01..C-F10 |
| Post-quantum TLS migration readiness pack | Peer TLS, hybrid KEM handshake, H-1 wire format, 10 findings | C-G01..C-G10 |

Repository names follow the pattern `postfiatd-<subject>-pack` under the author's public GitHub account; exact repository URLs are listed in each originating pack's README. This pack does not re-publish their contents — it consolidates their findings, re-runs their key measurements fresh, and adds the severity/exploitability ranking, the cross-surface interactions, the scorecard, and the single roadmap.

## What was re-run vs carried

- **Re-run fresh in this pack:** all ML-DSA/SLH-DSA sign/verify rates and sizes; all ML-KEM keygen/encaps/decaps timings; implicit rejection 108/108; hybrid handshake totals and wire bytes; dual-signature verify rates and controls C-1..C-5; classical Ed25519/X25519 baselines; all negative searches. See `outputs/` and `docs/CLAIMS.md` section A.
- **Carried (logs re-checked):** the live testnet window, agent probes, validator topology, partition drills, amendment inventory and lifecycle model. See `docs/CLAIMS.md` section B.
- **Simulated:** the amendment activation scenarios and the negative-UNL model. See `docs/CLAIMS.md` section C.
- **Unsupported:** three origin-pack judgements this pack could not re-derive, labelled [UNSUPPORTED] in `docs/CLAIMS.md` section D.
