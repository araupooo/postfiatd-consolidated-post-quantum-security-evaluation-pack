# Consolidated Postfiatd Post-Quantum Security Evaluation Pack

A synthesis of seven prior postfiatd evaluation packs (protocol-signature benchmarks, ML-KEM assessment, network/agent reference, overlay partition-recovery, amendment lifecycle, release-signing migration, TLS migration readiness) against postfiatd at the pinned revision `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).

## What this pack contains

- **Five per-surface evaluation memos** (`docs/memos/`): protocol signatures, validator manifests + key handling, peer-transport TLS, release signing, amendment governance. Each adds a severity/exploitability ranking, cross-surface interactions, and the single most valuable fix — not a copy of the originating memos.
- **Consolidated risk register** (`data/risk_register.json`, `docs/RISK_REGISTER.md`): all **60 findings** (9 HIGH, 23 MEDIUM, 21 LOW, 7 INFO) ranked by severity *and* exploitability, each with pinned source file:line and a primary standard/measurement citation. Top three: unauthenticated `/api/tasks` read (rank 1), unsigned releases (rank 2), unsigned Docker images under mutable tags (rank 3).
- **Migration-readiness scorecard** (`data/scorecard.json`, `docs/SCORECARD.md`): overall **1.2 / 5** — measurement-complete, migration-not-started. Release signing scores 0/5; amendment governance is the best surface at 2/5.
- **One staged remediation roadmap** (`data/roadmap.json`, `docs/ROADMAP.md`): S0 (0–4 weeks, no new cryptography) through S4 (mainnet gate), with exit criteria per item and five labelled open design decisions (D-01..D-05).
- **Claim index** (`docs/CLAIMS.md`): every substantive claim labelled [MEASURED] / [SIMULATED] / [UNSUPPORTED]. Key measurements were **re-run fresh** in this pack's own harness (liboqs 0.14.0, single thread): ML-DSA-44 verify 27,521.9/s; ML-KEM-768 encaps 26.96 us / decaps 32.77 us; implicit rejection 108/108; hybrid handshake 170.17/183.13/206.37 us; Ed25519+ML-DSA-44 dual signature verify 5,051.9/s.
- **Two fully-specified wire formats:** the H-1 hybrid KEM handshake (3-byte header + 32 B X25519 + ML-KEM ciphertext) and the new **PFQS v1 release envelope** (8-byte header + 64 B Ed25519 + 2,420 B ML-DSA-44 = 2,492 B, AND-verification, exact-length check) — which closes the version/mode-byte gap the release-signing pack left open.
- **Reproducibility:** `reproduce.sh`, `SHA256SUMS`, `verify_digests.sh`, CI (`.github/workflows/ci.yml`, builds liboqs 0.14.0 from a fresh clone on `ubuntu-latest`).

## The single most valuable fix

**S0-1: sign every release** — publish an Ed25519 signature and a SHA-256 checksum file with every GitHub release, plus a verifier script. It closes the two highest-exploitability findings (unsigned releases, unsigned images) at near-zero cost and no protocol change, and it is the prerequisite for every later hybrid stage. Second: authenticate `/api/tasks` (S0-3).

## Cross-surface interactions (the value-add of this consolidation)

- **X-1** Anonymous TLS + unsigned releases: a MITM serves a tampered binary and nothing checks it.
- **X-2** Unsigned releases + unobservable amendment votes: a supply-chain compromise becomes a governance compromise with no alarm.
- **X-3** secp256k1-only validations + anonymous TLS: the validation signature is the *only* peer authentication.
- **X-4** Quorum comment bound + amendment thresholds: one faulty 67% assumption class affects two surfaces.
- **X-5** ML-KEM absent everywhere + harvest-now: recorded traffic and validations are exposed to future decryption/forgery.

## Reproduce

```sh
bash reproduce.sh   # measurements re-run into scratch; digests verified; REPRODUCE OK
bash verify_digests.sh
python3 scripts/check_excerpts.py --pin <pinned-postfiatd-checkout>
```

See `docs/REPRODUCTION.md` and `docs/FAILURE_MODES.md`. Findings and fixes: `docs/REMEDIATION.md`. Sources: `docs/SOURCES.md`.
