# Staged Remediation Roadmap

One roadmap for all five surfaces, postfiatd pinned revision `0085a1ff885d6a446369cf73a4430f75af22be55`. Stages are sequential: each stage's exit criteria gate the next. The single most valuable fix is S0-1 (release signing); the second is S0-3 (authenticate `/api/tasks`).

## S0 — Stop the bleeding: no protocol change, no new cryptography (0-4 weeks)

S0 closes the highest-exploitability findings first. Nothing in S0 needs a new algorithm, a fork, or an amendment.

### S0-1 — closes C-F01

Publish an Ed25519 signature and a SHA-256 checksum file with every GitHub release, plus a verifier script in the repo.

**Exit criterion:** A release exists whose signature verifies with the published key; the upgrade docs point at the verifier.

### S0-2 — closes C-F02

Pin Docker images by digest (image@sha256:...) in deployment docs; stop directing operators to -latest tags.

**Exit criterion:** No deployment doc references a mutable -latest tag.

### S0-3 — closes C-C01, C-C02

Require authentication on /api/tasks (or strip the endpoint for anonymous callers); return 401/403, not 200, for anonymous reads.

**Exit criterion:** Anonymous GET /api/tasks returns 401/403; authenticated reads unchanged.

### S0-4 — closes C-G03, C-G04

Set an explicit TLS version floor (TLS 1.2 minimum) and an explicit TLS 1.3 ciphersuite list for the peer port; pass the operator ssl_ciphers list to the peer listener.

**Exit criterion:** Peer TLS policy is written down and enforced by the context, not by OpenSSL defaults.

### S0-5 — closes C-D01

Correct the quorum comment in ValidatorList.cpp: state that the pi+pj < .33*ni bound holds only at zero Byzantine faults.

**Exit criterion:** Comment text matches Theorem 8; the correction is reviewed.

### S0-6 — closes C-C04, C-C05, C-C06

Publish /robots.txt; return a real 404 for unknown /api/* paths; document API rate limits.

**Exit criterion:** Probes P-01..P-06 re-run: shell/robots/404 behavior as documented.

## S1 — Hybrid protection on the two exposed paths: releases and peer transport (1-3 months)

S1 is the first stage that ships post-quantum cryptography. The hybrid (classical + PQ, AND-verification) shape means a break in either half alone does not break the system.

### S1-1 — closes C-F04, C-F06

Ship the PFQS v1 hybrid release envelope (8-byte header + 64 B Ed25519 + 2,420 B ML-DSA-44 = 2,492 B, AND-verification, exact-length check) alongside the S0 Ed25519 signature.

**Exit criterion:** A release carries a PFQS v1 envelope that verifies at 5,051.9/s and rejects stripped halves (controls C-4/C-5).

### S1-2 — closes C-F09

Publish the release-key rotation procedure (key generation, publication, revocation, rotation cadence) and name the key custodian role.

**Exit criterion:** Rotation procedure exists in the repo and has been exercised once on a test release.

### S1-3 — closes C-F03

Add a signed manifest sequence number to releases (rollback protection) and enforce monotonic sequence on upgrade.

**Exit criterion:** An operator cannot be rolled back to an older signed release without an explicit override.

### S1-4 — closes C-G06, C-B01

Implement the hybrid KEM peer handshake (H-1 wire: 3-byte header + 32 B X25519 pubkey + ML-KEM ciphertext; 803/1,123/1,603 B) behind a testnet flag.

**Exit criterion:** Two testnet peers complete a hybrid handshake; measured totals match this pack (170.17/183.13/206.37 us).

## S2 — Governance observability and PQ validation signatures (3-6 months)

S2 turns the two observability gaps (votes, validations) from findings into operated features.

### S2-1 — closes C-E01, C-E02

Make per-amendment vote counts publicly readable (or enable PF_ValidatorVoteTracking and publish its output); a vote must be observable to be auditable.

**Exit criterion:** The public feature RPC (or a published tracker) shows count/validations/threshold per amendment.

### S2-2 — closes C-A06, C-A01

Design and testnet-gate ML-DSA validation signatures for validator manifests (dual-signed validations during transition; secp256k1 retained until the network migrates).

**Exit criterion:** A testnet validator publishes a dual-signed validation that verifies under both schemes.

### S2-3 — closes C-G05

Allow TLS 1.3 in the outbound HTTPS client (validator-site and exclusion-list fetches).

**Exit criterion:** Outbound fetches negotiate TLS 1.3 where the server offers it.

## S3 — PQ in the TLS stack and long-lived signatures (6-12 months)

S3 depends on an upstream OpenSSL provider with ML-KEM support; if none is available, the S1 hybrid handshake stays the transport protection and S3 is re-planned.

### S3-1 — closes C-G06, C-B06

Add ML-KEM to the TLS stack via an OpenSSL provider (open decision D-02: provider choice) and negotiate hybrid ciphersuites on the peer port.

**Exit criterion:** Peer TLS negotiates a hybrid key exchange on testnet; the X-Wing all-zero check is enforced in the combiner.

### S3-2 — closes C-F05, C-A03

Evaluate SLH-DSA-128f for long-lived release signatures (stateless, hash-based; 17,088 B, verify 897.5/s) as a second PQ half for archival releases.

**Exit criterion:** A dated decision record: SLH-DSA adopted or rejected for archival releases, with the measured costs attached.

### S3-3 — closes C-B10, C-B02

Apply the FIPS 203 section 7.3 length check in the application layer wherever ML-KEM ciphertexts are accepted.

**Exit criterion:** Invalid-length ciphertexts are rejected with an explicit error before decapsulation.

## S4 — Mainnet readiness: close the governance and quorum gates (mainnet gate)

S4 is a gate, not a workstream: mainnet does not proceed while any surface scores below 4.

### S4-1 — closes C-C03, C-D02

Decide the 67% -> 80% quorum revert explicitly and record the decision; do not go to mainnet on an undecided quorum.

**Exit criterion:** A dated decision record names the mainnet quorum and the evidence for it.

### S4-2 — closes C-A01, C-B01, C-G01, C-F01

Complete the PQ migration on all five surfaces (scorecard >= 4 on every surface) before mainnet; re-run this pack's benchmarks on the migration build.

**Exit criterion:** Scorecard re-issued with every surface >= 4 and fresh measurements attached.

## Open design decisions

Every unspecified byte or undecided choice is listed here explicitly. Nothing in this roadmap is silently unspecified.

### D-01 — open

Release-key distribution and rotation procedure: not specified in this pack; S1-2 must define it. Until then, PFQS v1 envelopes are verifiable but their keys have no published lifecycle.

### D-02 — open

ML-KEM TLS provider choice (which OpenSSL provider supplies ML-KEM, and which hybrid ciphersuites are negotiated): not specified; S3-1 must choose. The S1 hybrid handshake does not depend on it.

### D-03 — open

Signed manifest sequence / rollback field: PFQS v1 has no timestamp or sequence field by design; rollback protection is a separate S1-3 manifest field, not part of the envelope.

### D-04 — open

SLH-DSA adoption for archival releases: deferred to S3-2 with measured costs attached; ML-DSA-44 is the only PQ half in PFQS v1.

### D-05 — open

Mainnet quorum (67% vs 80%): undecided; S4-1 is the decision gate. The 67% comment bound (C-D01) is wrong regardless of which quorum is chosen.
