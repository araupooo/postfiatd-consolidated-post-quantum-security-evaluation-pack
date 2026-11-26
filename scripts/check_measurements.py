#!/usr/bin/env python3
"""check_measurements.py — structural check of a measurement run.

Reads the measurement logs in $MEASUREMENT_OUTDIR (default outputs/)
and verifies structure, not absolute rates (rates vary by machine;
see docs/FAILURE_MODES.md):
  - every algorithm block present in benchmark-pq.log, controls PASS,
    measured lengths equal to the FIPS/liboqs parameter table;
  - ML-KEM RESULT lines present, implicit rejection 108/108, sizes exact;
  - hybrid handshake arithmetic client + server == total (within 0.02:
    the three values are rounded to 2 decimals independently),
    wire bytes exact, controls PASS, all-zero X25519 rejected;
  - dual-signature envelope 2,484 B, controls C-1..C-5 PASS;
  - classical Ed25519 baseline present;
  - the FIPS-205-name probe log matches the vendored evidence
    (ALGORITHM_NOT_ENABLED).

Exit 0 with "CHECK OK" only when every check passes. Prints one
verbose [step] line per check as it runs.
"""
import os
import re
import sys

OUTDIR = os.environ.get("MEASUREMENT_OUTDIR", "outputs")
PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    p = os.path.join(OUTDIR, name)
    if not os.path.isfile(p):
        print(f"[FAIL] missing log: {p}")
        sys.exit(1)
    return open(p).read()


def check(cond, label):
    print(f"[step] {label}: {'PASS' if cond else 'FAIL'}")
    if not cond:
        sys.exit(1)


SIG_LENGTHS = {
    "ML-DSA-44": (2420, 1312),
    "ML-DSA-65": (3309, 1952),
    "ML-DSA-87": (4627, 2592),
    "SPHINCS+-SHA2-128s-simple": (7856, 32),
    "SPHINCS+-SHA2-128f-simple": (17088, 32),
}
KEM_SIZES = {
    "ML-KEM-512": (800, 1632, 768, 32),
    "ML-KEM-768": (1184, 2400, 1088, 32),
    "ML-KEM-1024": (1568, 3168, 1568, 32),
}

pq = read("benchmark-pq.log")
for alg, (sig_len, pk_len) in SIG_LENGTHS.items():
    check(f"algorithm: {alg}" in pq, f"benchmark-pq block present: {alg}")
    # length lines appear once per block; check the expected values exist
    check(f"length_signature: {sig_len}" in pq, f"{alg} signature length {sig_len} B")
    check(f"length_public_key: {pk_len}" in pq, f"{alg} public-key length {pk_len} B")
check(pq.count("control_valid_signature_verifies: PASS") >= 7,
      "benchmark-pq controls: valid verifies (7 blocks)")
check(pq.count("control_tampered_signature_rejected: PASS") >= 7,
      "benchmark-pq controls: tampered rejects (7 blocks)")
check("--- ML-DSA-44 (2048-byte payload) ---" in pq,
      "benchmark-pq 2048-byte payload block present")
check("--- SLH-DSA-SHA2-128f (2048-byte payload) ---" in pq,
      "benchmark-pq 2048-byte SLH-DSA block present")

kem = read("benchmark-kem.log")
for alg, (pk, sk, ct, ss) in KEM_SIZES.items():
    m = re.search(rf"{re.escape(alg)}: liboqs pk=(\d+) sk=(\d+) ct=(\d+) ss=(\d+)", kem)
    check(m is not None, f"benchmark-kem sizes line present: {alg}")
    check(m and tuple(map(int, m.groups())) == (pk, sk, ct, ss),
          f"{alg} sizes exact pk={pk} sk={sk} ct={ct} ss={ss}")
    check(re.search(rf"RESULT {re.escape(alg)} keygen_us=[\d.]+ encaps_us=[\d.]+ decaps_us=[\d.]+ n=500", kem) is not None,
          f"benchmark-kem RESULT line present: {alg}")
check("RESULT implicit_rejection_total 108/108" in kem,
      "benchmark-kem implicit rejection 108/108")

hyb = read("hybrid_bench.log")
for alg in ("ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"):
    m = re.search(rf"RESULT {re.escape(alg)} hybrid client_us=([\d.]+) server_us=([\d.]+) total_us=([\d.]+) n=200", hyb)
    check(m is not None, f"hybrid_bench RESULT line present: {alg}")
    c, s, t = map(float, m.groups())
    # Tolerance 0.02: client, server, and total are each rounded to 2
    # decimals independently, so the sum of the rounded halves can
    # differ from the rounded total by one unit in the last place.
    check(abs((c + s) - t) < 0.02, f"{alg} arithmetic client+server==total")
check("RESULT hybrid all_zero_x25519 rc=-1 rejected_by_openssl" in hyb,
      "hybrid_bench all-zero X25519 rejected")
check("[PASS] hybrid client/server shared secrets agree" in hyb,
      "hybrid_bench shared secrets agree")
check("RESULT bench_hybrid OK" in hyb, "hybrid_bench completed OK")

dual = read("hybrid_dual_sig_bench.log")
check("hybrid_signature_len: 2484" in dual,
      "dual-sig envelope 2484 B (64 Ed25519 + 2420 ML-DSA-44)")
for c in ("C-1", "C-2", "C-3", "C-4", "C-5"):
    check(f"control {c}: PASS" in dual, f"dual-sig control {c} PASS")
check("hybrid_verify_ops_per_sec:" in dual, "dual-sig verify rate present")

classical = read("benchmark-classical.log")
check(re.search(r"EdDSA \(Ed25519\)\s+[\d.]+s\s+[\d.]+s\s+[\d.]+\s+[\d.]+", classical) is not None,
      "benchmark-classical Ed25519 sign/verify rates present")

probe = read("negative_fips205_names.log")
check("result: ALGORITHM_NOT_ENABLED" in probe,
      "FIPS 205 name probe: SLH-DSA-SHA2-128s not registered")
vendored = open(os.path.join(PACK, "outputs", "negative_fips205_names.log")).read()
check(probe == vendored, "FIPS 205 name probe log byte-identical to vendored evidence")

print("CHECK OK")
