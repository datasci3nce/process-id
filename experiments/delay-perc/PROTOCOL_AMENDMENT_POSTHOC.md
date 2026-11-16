# ER-DELAY-PERC-1: Post-hoc correction and interpretation addendum

**Date:** 2026-11-15. **Status:** retrospective clarification; not a pre-registered revision.

This amendment preserves `PROTOCOL_PRE_RUN.md`, the original model-fitting code, original predictions, private histories, and baseline comparison exactly as generated. The frozen protocol uses the words "signed" and "authenticated" inaccurately; those statements are **superseded**, not quietly rewritten. The revision below is a documentation correction, not a new result from the frozen protocol.

## Corrections

1. **Observation semantics.** The experiment has simulated, assumed-truthful link-status/latency records. Neither a digital signature nor an authenticated execution/provenance chain is implemented. Package SHA-256 checks protect file consistency only. References to "signed/authenticated receipts" in the old protocol/report mean simulated status records under an assumption of correctness, *not* cryptographic authentication.
2. **Strong deterministic baseline.** A previously omitted conventional comparator is now added retrospectively: independently recompute the exact three-state certificate using *only public observations*, return probability 1 for YES, 0 for NO, and the existing development-trained static predictor for UNKNOWN. This uses no private labels for predictions and no held-out tuning. It is scored post-hoc on the unchanged held-out evaluator outcomes. See `posthoc_certified_static.py` and `results/posthoc_exact_static/`.
3. **Scope of distribution shift.** Development data have iid channel conditions, while held-out data have source-shared congestion changing link readiness and latency distributions/correlation. Both follow the known potential topology, permitted link-status ontology and allowed delays. The evaluation is a *within-model-family parameter/correlation shift*; it does not test a new communication mechanism, unknown graph topology, actual agent reads, or out-of-class execution histories.
4. **DDE claim.** The evaluated DDE is one fixed-coefficient, Euler-discretized delayed linear influence surrogate with imputed unknown lags, trained/evaluated against a discrete shortest-path truth generator. This experiment provides no evidence against DDEs in settings with measurable continuous states or actual delay dynamics.

## Decision rule and endpoints

The comparison uses the same factual binary timely-arrival target and unchanged 1,600 held-out evidence masks. A separate exact certifier establishes status YES, NO, or UNKNOWN **under the stipulated model**. The post-hoc baseline is

\[
\widehat p_{\mathrm{exact+static}}(O)=
\begin{cases}
1 & \mathrm{cert}(O)=\mathrm{YES},\\
0 & \mathrm{cert}(O)=\mathrm{NO},\\
\widehat p_{\mathrm{static}}(O) & \mathrm{cert}(O)=\mathrm{UNKNOWN}.
\end{cases}
\]

Post-hoc metrics include case-weighted Brier, paired **world-cluster bootstrap** intervals, a duplicated-100%-mask sensitivity, and an UNKNOWN-only analysis. The certificates were already part of the original method; using them for a stronger baseline is a legitimate comparison, not a discovery of a new algorithm. No sample-size expansion, refitting, or model selection is introduced.

## Research interpretation

The Brier score decomposes descriptively into the benefit obtained by deterministically handling decided cases and any residual advantage on unresolved cases. This is an accounting identity for *these policies*, not a causal attribution. Predicting truth on unresolved cases does not prove a claim's unique support. Zero observed certification errors within the exact model do not generalize to incomplete causal reference models.

The complete, originally executed study remains available unchanged in `ER_DELAY_PERCOLATION_1_COMPLETE.zip`; `REPORT_ORIGINAL_UNAMENDED.md` and `MANIFEST_ORIGINAL_FROZEN_SHA256.txt` in this amendment package preserve the original description and checksums.
