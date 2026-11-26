# Memo 02 — Validator Manifests and Key Handling

**Surface:** validator manifests, validation signatures, and the key handling behind them.
**Pinned revision:** `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
**Verdict:** the weakest trust anchor in the network. Score 1/5 (`docs/SCORECARD.md`).

## What this memo adds over the originating packs

No single originating pack owned this surface: the lattice pack measured signatures, the network pack measured the live validator list, the overlay pack measured quorum. This memo pulls those three threads together and ranks them as one surface.

## Findings on this surface (consolidated)

| ID | Sev | Exploit | Finding |
|----|-----|---------|---------|
| C-A06 | MEDIUM | Medium | Validator validation signatures are secp256k1-only |
| C-A05 | MEDIUM | Medium | One verification entry point: easy to extend, single point of failure |
| C-C03 | MEDIUM | Low | Track the 67% → 80% quorum revert as a mainnet gate |
| C-D02 | MEDIUM | Low | Do not treat UNL uniformity as verified |
| C-D03 | MEDIUM | Low | A sub-quorum side cannot self-rescue via the negative UNL |
| C-D04 | LOW | Low | Do not use converged/diverged flags as a partition detector |
| C-D05 | LOW | Low | Plan ledger catch-up capacity for long partitions |
| C-D06 | INFO | Low | Reconnection pacing is adequate for healing |

Register ranks: C-A06 11, C-A05 10, C-C03 22, C-D02 24, C-D03 25, C-D04 43, C-D05 44, C-D06 56. Full text, sources, and fixes: `docs/REMEDIATION.md`.

## Measured facts (re-checked, not re-run)

- **Live validator list, seq 31:** 25 validators, quorum 17 (67%) vs 20 (80% upstream), overlap 21/25 vs 23/25 (T11 `outputs/validator_topology.log`).
- **Handshake gate:** the peer handshake rejects any node public key that is not secp256k1 — `src/xrpld/overlay/detail/Handshake.cpp:294` (`data/source_excerpts.json` E-06). This is the line that must be widened for any PQ validation; it is also the line that currently guarantees every validation in the network is classically signed.
- **Quorum arithmetic:** the comment bound `pi + pj < .33*ni` (`ValidatorList.cpp:1927-1928`, excerpt E-07) holds only at zero Byzantine faults. Under the comment's own fault model, Theorem 8 certifies nothing at 67% (required overlap 28.5 > 25). The 21/25 overlap figure is the zero-Byzantine bound.
- **Partition drills D-01..D-04:** 4/4 PASS (T12). Minimum survivable partition 17 (68%) at 67% quorum; max crash loss 8 at 67%; detection ≥ 1 flag period (~768 s); negative UNL: max listed 7, quorum after full listing 15.
- **Key handling:** no PQ key handling exists anywhere in the pinned tree — the negative search (`outputs/negative_search.log`) finds zero ML-DSA/ML-KEM/SLH-DSA references in `src/` or `include/`. There is no PQ key generation, storage, rotation, or revocation code to migrate; all of it must be written.

## Severity + exploitability ranking (why this surface scores 1/5)

The surface has no HIGH-severity finding of its own, and that understates it. The ranking that matters:

1. **C-A06 (rank 11) is the surface's keystone.** Every validation is secp256k1. There is no second signature scheme, no hybrid, and no fallback. The exploitability is Medium only because the exploit needs a cryptographically relevant quantum computer — but the exposure is *harvest-now*: validations are public, recorded forever, and forgeable the day such a machine exists.
2. **C-A05 (rank 10) cuts both ways.** One verification entry point means one place to extend (good for migration) and one place to break (bad for assurance). Until the entry point has per-algorithm test vectors and a fuzz target, it is a single point of failure. This claim is carried from the originating pack and labelled [UNSUPPORTED] in `docs/CLAIMS.md` (U-01) — this pack did not re-derive the call graph.
3. **C-D02/C-D03 (ranks 24–25) are the operational shadow of the same 67% assumption.** The quorum the network runs on (17/25) is the quorum the comment mis-justifies (C-D01, rank 23) and the quorum the mainnet gate must decide (C-C03, rank 22). Three findings, one assumption class.

## Cross-surface interactions

- **With protocol signatures (Memo 01):** one workstream, not two. The ML-DSA-44 measured in Memo 01 (verify 27,521.9/s, sig 2,420 B) is the PQ half for dual-signed validations. The validation format must be specified with every byte fixed, as PFQS v1 does for releases — that specification does not exist yet and is an S2-2 deliverable.
- **With peer TLS (Memo 03):** the validation signature is the only peer authentication, because peer TLS is anonymous (X-3). If the validation layer fails, the peer layer has nothing behind it. Conversely, the S1 hybrid KEM handshake protects session confidentiality but does *not* authenticate the peer — it must never be described as doing so.
- **With amendment governance (Memo 05):** the quorum (67% vs 80%) is both an overlay parameter and a governance decision. The amendment that changes it is voted on by the same validators whose keys this surface manages, under vote counts nobody can observe (C-E01). A quorum change is therefore decided by an unobservable vote among keys that have no PQ protection.
- **With release signing (Memo 04):** the release key-rotation procedure (S1-2) is the template for validator key rotation, which does not exist either. Write the release procedure first; reuse its shape for validators.

## The single most valuable fix on this surface

**Dual-sign validations on testnet (S2-2).** It is the only fix that puts PQ protection on the network's trust anchor, and it de-risks every later step: the validation format, the key handling, and the handshake gate all get exercised before mainnet. The cheaper fixes (correcting the comment, S0-5; deciding the quorum, S4-1) are necessary but change no cryptography.

## What this pack does not claim

- The UNL uniformity judgement (C-D02) is carried, not re-derived (CLAIMS.md U-03). The measured overlap figures (21/25 at 67%) stand; the judgement that uniformity cannot be assumed is the originating pack's.
- No PQ validation format is proposed here. S2-2 must specify it byte-exactly.
