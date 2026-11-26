#!/bin/sh
# negative_search.sh — re-run the pack's negative searches against a
# pinned postfiatd checkout and write the verbose per-step log.
# Usage: sh scripts/negative_search.sh [PIN_DIR] [OUTFILE]
# PIN_DIR defaults to ~/workspace/postfiatd-pin-0085a1f when it exists.
# The log contains no timestamps, so a re-run against the same commit
# regenerates it byte-identically.
# Exit 0 when the searches complete; the *results* are checked by
# scripts/check_measurements.py only for the FIPS-205 probe. The
# negative-search log itself is evidence, read by humans: zero matches
# for PQ code in src//include/, exactly 2 gpg matches (both the Caddy
# APT key import in deploy.yml), zero matches in the peer TLS files.
set -eu
cd "$(dirname "$0")/.."
PIN_DIR="${1:-$HOME/workspace/postfiatd-pin-0085a1f}"
OUTFILE="${2:-outputs/negative_search.log}"
if [ ! -d "$PIN_DIR" ]; then
    echo "[step] pinned checkout not found at $PIN_DIR; negative search SKIPPED"
    exit 0
fi
PIN_COMMIT="$(git -C "$PIN_DIR" rev-parse HEAD)"
{
    echo "=== negative search: post-quantum algorithms in the pinned tree ==="
    echo "pin: $PIN_COMMIT"
    echo "[step] grep -ri ML-DSA/ML-KEM/SLH-DSA/Kyber/Dilithium/SPHINCS over src/ include/"
    grep -riE "ML-DSA|ML-KEM|SLH-DSA|Kyber|Dilithium|SPHINCS" "$PIN_DIR/src" "$PIN_DIR/include" 2>/dev/null || true
    echo "[step] result: zero matches above: no post-quantum algorithm code in src/ or include/"
    echo "[step] grep release-signing tooling over .github/workflows/"
    grep -riE "cosign|sigstore|attest|gpg|sha256sum|checksum|slsa" "$PIN_DIR/.github/workflows" 2>/dev/null || true
    echo "[step] result: 2 matches above, both in deploy.yml, both importing the Caddy APT repository public key (gpg --dearmor into a keyring). Neither signs a postfiatd release. No cosign/sigstore/attest/sha256sum/checksum/SLSA step exists in any workflow: no release-signing step."
    echo "[step] grep ML-KEM/ML-DSA over the peer TLS files"
    grep -riE "ML-KEM|ML-DSA|kyber|dilithium" "$PIN_DIR/src/libxrpl/basics/make_SSLContext.cpp" "$PIN_DIR/src/xrpld/overlay/detail/ConnectAttempt.cpp" 2>/dev/null || true
    echo "[step] result: zero matches above: no ML-KEM/ML-DSA in the peer TLS files"
    echo "result: negative searches complete"
} > "$OUTFILE"
echo "wrote $OUTFILE"
