# Migration-Readiness Scorecard

Per-surface migration readiness against post-quantum risk, postfiatd pinned revision `0085a1ff885d6a446369cf73a4430f75af22be55`.

**Scale (0–5 per surface):** 0 = no protection and no design; 5 = migrated, measured, and operated. Dimensions: measurement completeness, in-tree support, migration design, operational readiness. **Overall: 1.2 / 5** — the mean of the five surface scores.

| Surface | Score | Measurement | In-tree support | Migration design | Operational readiness | Blocking findings |
|---|---:|---:|---:|---:|---:|---|
| protocol-signatures | **2** | 5 | 0 | 4 | 1 | C-A01, C-A06 |
| validator-manifests-key-handling | **1** | 4 | 0 | 2 | 1 | C-A06, C-A05 |
| peer-transport-tls | **1** | 5 | 0 | 4 | 1 | C-G01, C-G06, C-G03 |
| release-signing | **0** | 5 | 0 | 4 | 0 | C-F01, C-F02, C-F09, C-F03 |
| amendment-governance | **2** | 5 | 3 | 2 | 2 | C-E01, C-E02 |

**Overall: 1.2 / 5.** Mean of the five surface scores (2+1+1+0+2)/5 = 1.2. The program is measurement-complete and migration-not-started: every number needed to plan the migration has been measured, but no surface has any PQ protection in production.

## protocol-signatures — 2/5

Benchmarks are complete and re-run fresh in this pack (ML-DSA-44 verify 27,521.9/s; SLH-DSA-128f 897.5/s; sizes verified against FIPS 204/205 and liboqs headers). Zero PQ code exists in the pinned tree; the dual-signature migration design (PFQS v1 envelope, docs/memos/04-release-signing.md) is fully specified, but no operator procedure exists yet.

Blocking findings: C-A01, C-A06.

## validator-manifests-key-handling — 1/5

Validation signatures are secp256k1-only by an explicit handshake check (Handshake.cpp:294); the single verification entry point makes extension easy but is also a single point of failure. No PQ validation format has been designed; key handling for PQ keys does not exist.

Blocking findings: C-A06, C-A05.

## peer-transport-tls — 1/5

Peer TLS is anonymous by code (verify_none both ends) and the hybrid KEM design is fully specified with a byte-exact wire format and fresh measurements (hybrid handshake 170.17/183.13/206.37 us). No ML-KEM exists in the TLS stack and no version floor is set, so nothing can be switched on today.

Blocking findings: C-G01, C-G06, C-G03.

## release-signing — 0/5

The worst surface: releases and images are published unsigned under mutable tags, with signing explicitly deferred. Measurement is complete and the PFQS v1 hybrid envelope (2,492 B, verify 5,051.9/s) is fully specified, but there are no keys, no rotation procedure, and no rollback protection. Nothing here is operated at all.

Blocking findings: C-F01, C-F02, C-F09, C-F03.

## amendment-governance — 2/5

The best surface: the mechanism exists, is measured live (101 amendments, 64 enabled / 37 disabled; thresholds 204/256 pre-fix and 67/100 post-fix verified in-tree), and the lifecycle model is simulated. The gap is observability, not mechanism: vote counts are admin-only and the vote-tracking amendment is itself disabled.

Blocking findings: C-E01, C-E02.

## Single most valuable fix

Stage S0 release signing (Ed25519 signature + SHA-256 checksum file + verifier script on every release, images pinned by digest). It closes the two highest-exploitability findings (C-F01, C-F02) at near-zero cost and no protocol change, and it is the prerequisite for every later hybrid stage: without signed releases, a signed hybrid envelope has nothing trustworthy to attach to.

## Second most valuable fix

Authenticate /api/tasks (C-C01): a one-line authorization check on a public endpoint that currently returns task JSON to any unauthenticated caller.
