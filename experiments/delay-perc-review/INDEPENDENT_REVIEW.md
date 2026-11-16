# ER-DELAY-PERC-1: independent review and post-hoc baseline

Reviewed 15 November 2026. This document assesses the existing synthetic experiment. It does not modify the original protocol, generate new worlds, fit new models, or make LLM calls.

## Verdict

The latency-and-deadline question is a legitimate refinement of the original recoverability problem. The completed study is a useful synthetic reference. Its main empirical conclusion should be narrowed: most of the temporal predictor's improvement over the timing-blind baseline comes from cases already decidable by simple exact constraints. The tested fixed-coefficient DDE surrogate supplies no demonstrated incremental benefit. This does not resolve the general value of DDEs or establish a new agent-dynamics law.

## Verification performed

- All eight supplied unit tests passed.
- All 22 original manifest entries matched their file hashes.
- Recomputed saved Brier scores from all 4,000 rows; the held-out evaluation has 1,600 rows from 160 worlds.
- Used a separate heap-based Dijkstra implementation to replay 400 native synthetic worlds, reconcile 123,184 retained receipt appearances, and recheck all 4,000 certification labels. No mismatches were found.
- The supplied NetworkX audit script could not run in this environment because NetworkX was unavailable. The separate implementation above avoids importing the experiment's shortest-path or certificate functions.
- The package describes a local pre-run freeze. File contents and the final manifest alone do not independently establish the chronology of that freeze.

The input ZIP SHA-256 is `a94fae752b9ab5961e48512ddd57e6dc8bbf0bbabe230cf7d2791f0c28f7e367`.

## Main post-hoc finding

`scalar_features` supplies the temporal logistic model with the predicates that a proved path meets the deadline and that an optimistic path meets the deadline. These are also the predicates used by the exact certifier. They are computed from public observations; this is not hidden-label leakage.

Of the 1,600 held-out rows, 692 are exactly identifiable under the declared reference semantics and 908 are ambiguous. On identifiable rows, the static predictor has Brier 0.08030688 while the temporal predictor has Brier 0.00000317. On ambiguous rows the corresponding scores are 0.20443127 and 0.19649913.

Consequently, 88.53% of the original aggregate squared-error improvement occurs on already identifiable rows. Removing the duplicated source-correlated full-observation rows leaves 1,440 rows and reduces this share to 83.30%; the interpretation persists.

An elementary post-hoc comparator first runs the public-observation exact certifier. It returns probability one for YES, zero for NO, and otherwise keeps the saved static predictor's probability. No held-out truth is used to select these outputs, and no new fitting is performed.

| Method | Held-out Brier |
|---|---:|
| Original static predictor | 0.15074747 |
| Exact certifier, then static predictor when UNKNOWN | 0.11601475 |
| Original temporal predictor | 0.11151463 |
| Exact certifier, then temporal predictor when UNKNOWN | 0.11151326 |
| Original event-time Monte Carlo | 0.09091051 |

The temporal predictor's remaining improvement over the certifier-plus-static comparator is 0.00450012 Brier points. A post-hoc paired world bootstrap with 4,000 replicates and seed 2026111501 gives an interval for temporal-minus-comparator of [-0.00973837, +0.00057647]. The interval includes zero. This does not establish equivalence; it does not demonstrate a clear incremental advantage in this sample.

Monte Carlo retains an improvement of 0.02510424 over the same comparator, with a post-hoc interval for MC-minus-comparator of [-0.03760524, -0.01257629]. It uses the appropriate discrete arrival predicate and development-fitted edge priors. Its held-out independence assumption is misspecified by shared congestion, but the allowed history support and arrival rule remain correct.

All new comparator choices and intervals are retrospective diagnostics. Preserve the original frozen results and report this addition separately.

## Interpretation corrections

1. **The implemented networks have 8, 16, 32 and 64 nodes.** The pasted summary's 4–64 range is inaccurate.
2. **Receipts are simulated and assumed truthful.** They contain edge indices, readiness and latency; this package implements no receipt signatures or cryptographic verification. File hashes protect the packaged bytes, not the provenance of real execution events. Use “simulated truthful channel-status records” rather than “signed native execution receipts.”
3. **The graph has fixed readiness and delay per edge within each world.** It is a weighted channel-network delivery problem. There are no scheduled contacts, changing availability windows, actual send/read events, LLM policies, or observed continuous belief states. Latency-aware reachability is a precise description; broader claims about reconstructing asynchronous agent activity require additional validation.
4. **The DDE comparison is deliberately a surrogate comparison.** It uses fixed coefficients, unit-step Euler updates, imputed delays, clipping, and a scalar output. The data-generating truth is a discrete earliest-arrival rule. The result supports no detected benefit for this particular implementation, not a rejection of DDE models.
5. **The mechanism shift changes probabilities and dependencies, not the certifier's admissible history support.** Both development and held-out worlds remain within the exact certifier's declared known-topology, truthful-record and allowed-delay class. Zero certificate errors therefore do not establish open-world robustness.
6. **Theoretical exactness is assumption-relative.** The certifier's optimistic and pessimistic completions are sufficient because arrival is monotone in edge availability and speed under this model. No new theorem or phase transition is demonstrated by the reported curves.

## Research interpretation

The evidence supports this statement: observed channel latencies make exact deadline checks possible, those checks account for most of the temporal classifier's aggregate advantage, and a conventional sampled event-time model additionally improves probability estimates on unresolved cases within the tested synthetic setting.

This is progress in locating which part of inference is useful. It does not show that combining additional mathematical frameworks produces a transferable new method. Keep this follow-up separate from the completed Wiki paper and avoid treating the DDE comparison as a new mandatory direction.

## Reproduction

With Python and NumPy installed:

```bash
python reproduce_review.py ER_DELAY_PERCOLATION_1_COMPLETE.zip --output review_results.json
```

The script also accepts the extracted experiment directory. It uses only the original saved records and predictions, independently recomputes certification from public cases, verifies the original manifest, and reproduces the post-hoc comparisons. The original experiment ZIP is required and is not duplicated in this review package.
