# ER-FIXED-TASK-AUDIT-1: Exact checks, probabilistic inference, evidence acquisition and evaluation confounding

**Date:** 15 November 2026. **Status:** completed retrospective/post-original-finalization experimental controls; not independent preregistration. All new analyses use archived synthetic delayed-channel worlds, saved real-Wiki score rows, or the archived CE exact calculation. None provides real LLM-agent execution truth. The pre-run local plan is `PROTOCOL_BEFORE_NEW_ANALYSIS.md`. Additional Monte Carlo and random-seed sensitivity checks are exploratory and disclosed as such.

## Executive result

The most promising *operational* result is a simple and familiar strategy: **inspect missing records along a currently feasible, optimistic time-respecting path**, rechecking exact feasibility after each inspection. On 320 fixed-claim starting cases from 160 held-out synthetic channel worlds, that policy correctly identifies **241/320 (75.31%)** after up to eight additional record inspections; the prespecified stable-hash random-query comparator identifies **97/320 (30.31%)**; a naive one-edge cut-sensitivity heuristic identifies **161/320 (50.31%)**. Paired world-cluster bootstrap of the optimistic-minus-random difference gives **+45.0 pp, 95% interval [+38.44,+51.56] pp**. The 320 cases consist of two correlated starting masks per independent world, so they are not 320 independent worlds. A 30-seed sensitivity of randomized inspection yields mean 31.27%, range 29.38–32.81% at budget eight.

This is an *inspection-policy feasibility test*, not a new theorem or algorithm, not authenticated real-agent evidence, and not a claim that hidden records can be obtained on demand in deployed systems. **The principal epistemic benefit is that selected additional evidence converts UNKNOWN claims into logically supported YES/NO claims within a stipulated process model.**

## A. Fixed-task prediction, with exact certification first

**Data:** 1,600 held-out evaluation masks on 160 independent delayed channel worlds; exact checks identify 692 and leave 908 unresolved. Predictions were constructed from public observed-only predictions and exact checks; evaluator labels entered only for scoring. Original fitted predictors and pre-run comparisons remain unchanged.

| Fixed target / prediction method | All 1,600 Brier ↓ | UNKNOWN-only 908 Brier ↓ |
|:--|--:|--:|
| Exact certification, otherwise original static logistic | **0.116015** | **0.204431** |
| Exact certification, otherwise delayed DDE surrogate + static features | 0.115963 | 0.204341 |
| Exact certification, otherwise temporal logistic | 0.111513 | 0.196499 |
| Exact certification, otherwise event-time Monte Carlo | **0.090911** | **0.160195** |

For the exact-UNKNOWN subset, MC minus gated static Brier = **−0.04424**, world-cluster bootstrap 95% interval **[−0.06661,−0.02256]** across 159 represented worlds. Temporal logistic minus gated static = −0.00793 **[−0.01709,+0.00115]**; delayed DDE minus gated static = −0.00009 **[−0.00155,+0.00152]**. The Monte Carlo predictor uses the correct known topology, allowed link status/delay states, and **development-estimated link priors**. It is an approximate within-class posterior, not a correct-under-any-mechanism probability. Repetition masks belong to the same world; cluster resampling is descriptive, not a prospective hypothesis test.

**Prior sensitivity (exploratory, 768 draws per UNKNOWN case):** development-fitted prior Brier **0.15794**; setting live-link q=0.50 gives **0.20325**, q=0.85 gives **0.17811**, uniform delay distribution gives **0.16717**. Original 96-draw MC was **0.16019** on these cases. The difference between 96 and 768 draws is sampling variance/seed dependent, while changed q also changes the assumed process. This makes model-prior dependence explicit; it does **not** establish calibration outside the model class.

## B. Same audit claim and matched evidence-inspection budget

**Question:** Given a known potential channel graph, truthful selectively observed status/delay receipts and a deadline, did information reach the destination in time? All three selection policies start from **exactly the same masked observations** in each case (one independent 25% and one source-correlated 25% case per world); all receive the same number *up to* budget 8 of additional edge inspections, stopping if certified. Query choices use public topology and current observed receipts only. The private native ledger is used solely to answer the selected query and afterward check the certificate.

- **Random**: stable hashed permutation over unobserved edges.
- **Cut sensitivity**: pick an unobserved edge whose hypothetical removal most increases optimistic earliest-arrival time, with deterministic ties.
- **Optimistic path**: find shortest currently possible source-to-target route, assuming unobserved links are live at the minimum allowed delay; inspect its first unobserved edge, recompute and repeat.

| Additional queries | Random certified | Cut-sensitivity certified | Optimistic-path certified |
|---:|---:|---:|---:|
| 0 | 21/320 (6.56%) | 21/320 (6.56%) | 21/320 (6.56%) |
| 1 | 28/320 (8.75%) | 63/320 (19.69%) | 41/320 (12.81%) |
| 3 | 42/320 (13.13%) | 102/320 (31.88%) | 124/320 (38.75%) |
| 5 | 64/320 (20.00%) | 129/320 (40.31%) | 174/320 (54.38%) |
| 8 | 97/320 (30.31%) | 161/320 (50.31%) | **241/320 (75.31%)** |

At budget eight, optimistic-path minus random = +0.4500 (world-bootstrap CI [0.3844,0.5156]), cut-sensitivity minus random = +0.2000 ([0.1500,0.2500]). Cut sensitivity works better at budget 1, but path inspection becomes substantially better with repeated feedback. Each 8-node case is nearly solved by eight inspections (path 100%, random 95%); the advantage remains for 16 nodes (76.25% vs 13.75%), 32 nodes (58.75% vs 7.50%), and 64 nodes (66.25% vs 5.00%). **Important caveat:** all policies have the entire *potential topology*, including unobserved edges. A real investigator might not know which missing record to request, whether it exists, or whether it is authentic. A specialized path-selection heuristic is naturally advantaged in a network whose claim itself is shortest-arrival feasibility. It does not establish generic cross-domain performance.

## C. Evidence-authenticity assumption stress (exploratory)

For each of the 1,595 held-out cases with at least one observed record, flip one deterministically selected observed status (live→failed or failed→live at delay one), while continuing to treat the altered record as truthful. Of the 709 certificates issued after this intentional corruption, **30 contradict the native world truth (4.23% among issued certificates)**. This is a controlled violation of the **assumed-truthful receipt** contract. It is not a measured attack success rate, a cryptographic-signature evaluation, or a bound on deployment reliability. With truly authenticated records under the complete reference topology, the original 692 reference certificates had zero contradictions by construction. Therefore certification must explicitly name its assumptions and evidence trust model.

## D. Real-Wiki candidate-set confounding, plus paired eligibility sensitivity

In the saved derived Wiki 199-target ranking study, retention p=1 gives exactly the same visible graph under both independent and source-correlated deletion arms. However, candidate decoys are selected with a hash involving `mode` even at p=1. On this **same graph**, the held-out target rank differs across arms for **65/199 two-hop targets (32.7%)**, **103/199 shared-in-neighbor targets (51.8%)**, **110/199 degree targets**, and **92/199 three-hop targets**. Random-score changes also reflect an arm-dependent randomized score, so do not use its values to isolate candidate effects.

At 25% retention, the intersection of targets eligible in both masks contains 96 cases. On those same targets, two-hop vs shared-in-neighbor Top-1 is **26 vs 35** under independent masking, and **21 vs 61** under source-correlated masking. This fixes **target membership and node-visibility eligibility**, not the distractor sets; candidate changes remain. The original reversal is therefore an observed ranking contrast, **not a clean causal estimate of an evidence-percolation effect**. The complete original derived graph and per-condition candidate lists are not in the mounted archive, so a fixed-candidate full-corpus rerun is impossible here. No such rerun is claimed.

**Direct paper edit:** remove the abstract's overstrong word “proves” for Wiki graph robustness and add the same-graph candidate diagnostic. A revised 6-page LaTeX/PDF draft with those edits is packaged separately. Its results and provenance were not silently rewritten.

## E. CE 2.0 / DDE result interpretation

The exact CE–Recoverability-1 finite-state experiment deliberately factorizes the macro-target bit from nuisance bits. The target posterior obeys

\[
P(M_2\mid O_M,O_A,O_B)=P(M_2\mid O_M).
\]

Thus changing nuisance dynamics and thereby changing the **macro-minus-micro causal-power gain** cannot improve the *same* claim's Bayes-optimal inference under the same evidence. The experiment is a controlled counterexample / separation, **not** evidence that CE-guided representations improve an auditing task. No new interacting CE-2.0-optimized representation experiment is claimed; there is not enough appropriate causal intervention data in the archived traces to support it. The DELAY DDE surrogate remains a negative branch for this specific discrete-time-arrival generator. Neither result should be the headline of the original Wiki sprint submission.

## How to tighten *The Missing Process*

1. **Keep the central epistemic criterion:** report factual truth, model-relative identifiability/certification, and probability when unresolved as distinct outcomes. This is the strongest conceptual contribution.
2. **Correct the Wiki graph claim now:** same-graph candidate-set differences directly invalidate a clean causal-deletion interpretation of ranking curves. This is the most urgent direct manuscript correction, and it is included in the tightened draft.
3. **Retain the true negative results:** page-majority beats HMM Top-1, conventional exact checker beats complicated SCALE-1 certificates, DDE provides no incremental gain on the later channel task.
4. **Do not bury confounds:** changing eligible nodes, changing negatives, model-completeness, and receipt truth assumptions must stay visible.
5. **Use evidence acquisition as a follow-up illustration** of what epistemic infrastructure could *do*: request a small number of highly informative records to turn ambiguity into authorization-worthy evidence. It is not yet a real-agent deployment result; do not backfill it into the original frozen sprint comparison as if preregistered.
6. **One confirmatory next study** should use genuinely timestamped, independently authenticated instrumented agent workflows with evaluator-blind target claims, matched query budgets, strong simple strategies, and an intentionally omitted-mechanism arm. CE-guided compression and DDEs should be tested there only when a defensible continuous-state/causal model is available and compared on the same claim.

## Epistemics relevance and limits

**Yes, this is epistemics in a concrete technical sense:** it operationalizes the difference between a likely story and a justified conclusion; measures how missingness changes what is knowable; and tests how additional records can resolve uncertainty. It does not yet address whether actual deployed AI-agent evidence is truthful, available on request, semantically sufficient, or generated by the stipulated process model. The next research contribution should demonstrate the same properties on genuinely independently verified histories, not add mathematical vocabulary to a synthetic proxy.

## Reproducibility boundary

All new analyses are archival/post-hoc and paired by world where uncertainty is estimated. `run_audit.py` and `extra_controls.py` use archived public observations, original saved scores, and evaluator-only data with an explicit selection/scoring boundary. `PROTOCOL_BEFORE_NEW_ANALYSIS.md` was written before the first new analysis; additional random-seed and MC prior sensitivities were subsequent exploratory checks. Six added tests pass; original DELAY tests 11/11 and original CE tests 9/9 pass. Source files for original Wiki raw graph edges and the original revision body export are absent. CE2 formulas are reused from the earlier package; the official PyMergence code was not executed for this new audit. There is no new LLM API experiment.
