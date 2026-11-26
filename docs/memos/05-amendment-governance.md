# Memo 05 — Amendment Governance

**Surface:** amendment lifecycle: inventory, majority thresholds, vote observability, vetoes, and activation timing.
**Pinned revision:** `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
**Verdict:** the best surface in the pack — the mechanism exists and is measured — but the votes that drive it cannot be observed. Score 2/5 (`docs/SCORECARD.md`).

## What this memo adds over the originating pack

The amendment pack measured the inventory and simulated the lifecycle. This memo ranks the findings by severity *and* exploitability, states plainly that the governance gap is observability rather than mechanism, and names the interaction that makes unobservable votes a security problem rather than a transparency preference.

## Findings on this surface (consolidated)

| ID | Sev | Exploit | Finding |
|----|-----|---------|---------|
| C-E01 | MEDIUM | Low | Per-amendment vote counts are not publicly observable |
| C-E02 | MEDIUM | Low | The vote-tracking amendment is itself disabled |
| C-E03 | LOW | Low | A lost majority restarts the full 2-week clock |
| C-E04 | LOW | Low | 24 h vote expiry can cost a majority |
| C-E05 | INFO | Low | The effective required fraction exceeds 67% (17/25 = 68%) |
| C-E06 | LOW | Low | 9 vetoes permanently block activation |
| C-E07 | INFO | Low | `PF_AccountExclusion` is disabled |

Register ranks: C-E01 26, C-E02 27, C-E03 45, C-E04 46, C-E06 47, C-E05 57, C-E07 58. Full text, sources, and fixes: `docs/REMEDIATION.md`.

## Measured facts (re-checked; live testnet, 2026-11-25)

- **Inventory:** 101 amendments, 64 enabled / 37 disabled, 0 changes vs the previous window (validated ledger 8363822, 2026-11-25 19:27 UTC; T13 `outputs/feature_inventory.log`).
- **Thresholds, verified in-tree:** pre-fix majority 204/256 (`SystemParameters.h:83`), post-fix 67/100 (`:85`), majority hold 2 weeks (`:88`) — `data/source_excerpts.json` E-08. Post-fix 67/100 with a strict `>` needs **17 of 25 votes (68.00%)**; pre-fix needed 19 (76.00%). The `fixAmendmentMajorityCalc` amendment is enabled, so the post-fix rule is the live one.
- **Vote counts are admin-only:** `AmendmentTable.cpp:1019-1028` emits `count`/`validations`/`threshold` only when `isAdmin` is true (excerpt E-09). The public `feature` RPC returns only enabled / supported / name.
- **Both PostFiat-specific amendments are disabled:** `PF_ValidatorVoteTracking` and `PF_AccountExclusion`. The vote-tracking amendment exists in code (`ValidatorVoteTracker.cpp:162`) but is off — the mechanism that would make votes observable is itself disabled.
- **Arithmetic:** majority hold 2 weeks = 1,209,600 s = 403,200 ledgers at 3.0000 s = 1,575.0 flag intervals (re-checked: 1209600/3 = 403200; 1209600/768 = 1575.0).

## Simulated activation timing (T13 model, not live observation)

| Scenario | Outcome |
|---|---|
| S-a fastest | 14 days |
| S-c majority lost/regained | day 23 |
| S-f 24 h expiry dip | day 20 |
| S-b 16/25 votes | never |
| S-e 9 vetoes | never |
| S-g pre-fix rule at 17 votes | never |

The 9-veto scenario (S-e, C-E06) is simulated, and it is labelled [SIMULATED] in `docs/CLAIMS.md` (S-03). A veto is a governance action by a validator, not a remote exploit — which is why its exploitability is Low even though its effect (permanent block) is total.

## Severity + exploitability ranking (why observability ranks first)

Neither C-E01 nor C-E02 is directly exploitable — nobody can forge a vote through them — so both carry Low exploitability. They still rank 26–27, first among the MEDIUM/Low group, because of what they hide:

1. **A vote that cannot be observed cannot be audited.** Whether an amendment reached its majority, lost it, or was vetoed is visible only to node operators with admin RPC access. Everyone else — including the operators who run the network — takes the outcome on trust.
2. **The tracking amendment is disabled.** This is not a missing feature; it is a feature that exists, is wired into the vote path, and is off. Enabling it (or publishing the tracker output) is a configuration decision, not an engineering project.
3. **The quorum decision rides on this surface.** The 67% vs 80% mainnet decision (C-C03) is an amendment decision. It will be voted on under vote counts nobody can observe, by validators whose keys have no PQ protection (Memo 02), and the result will be shipped in releases nobody signs (Memo 04). Each surface's gap is survivable alone; together they mean the network's most consequential decision is taken blind, by unauthenticated keys, and shipped unsigned.

That compounding is the reason C-E01/C-E02 outrank the other MEDIUM/Low findings in the register's ordering within their band, and why S2-1 (public vote counts) is a stage-2 priority rather than a nice-to-have.

## Cross-surface interactions

- **X-2 (with release signing):** unsigned releases + unobservable votes. A malicious release that changes voting behaviour is undetectable on both ends.
- **X-4 (with overlay/quorum):** governance and overlay share the 67% assumption class. The comment bound is wrong (C-D01) and the effective fraction is 68%, not 67% (C-E05). Both corrections belong in operator docs before any quorum decision.
- **With protocol signatures (Memo 01):** the PQ migration itself needs an amendment to activate. The approval path for the migration is the surface with the weakest observability. Fix observability (S2-1) before the migration amendment is proposed, or the migration will be approved by a vote nobody can audit.
- **With validator manifests (Memo 02):** vetoes are cast by validators; 9 vetoes block activation permanently. With 25 validators, 9 is more than a third — a minority with veto power. That is the specified behaviour, but it should be a conscious choice, recorded with the S4-1 quorum decision.

## The single most valuable fix on this surface

**S2-1: make per-amendment vote counts publicly readable** — either enable `PF_ValidatorVoteTracking` and publish its output, or expose `count`/`validations`/`threshold` on the public `feature` RPC. It costs a configuration change, closes both C-E01 and C-E02, and makes every other governance decision (quorum, migration, vetoes) auditable for the first time.
