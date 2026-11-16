# ER-DELAY-PERC-1 — Completed experimental report

**Status:** original experiment completed; **v0.1.1 documentary corrections and post-hoc comparator added 15 November 2026**. The original protocol, results, and held-out predictions are preserved unchanged. The independent native-ledger audit passed. **Date:** 15 November 2026. This is a new synthetic follow-up, **not** part of the completed AI × Epistemics sprint manuscript and not evidence from real LLM-agent traces.

## Research question

Can a time-respecting evidence model distinguish multi-agent signal-delivery histories that look identical as static graphs? Does a numerical delay-differential-equation (DDE) surrogate predict factual timely delivery better than a simpler event-time model? How does deleting simulated, assumed-truthful channel-status records affect claim-specific identifiability?

## Experiment and ground truth

400 independent layered *potential* channel graphs with 8, 16, 32 or 64 nodes (100 each), each with a source token, target, and deadline. Links have binary readiness and discrete simulated delay in `{1,2,4,6}` (independent conditions in development, source-correlated congestion in held-out worlds). The native simulator computes true earliest arrival from live links. The first 240 worlds (60 per size) use independent link conditions and train predictors/priors; 160 held-out worlds (40 per size) use shared transmitter congestion that changes link success and latency jointly. The held-out shift changes link probabilities and source-level dependence **within the same known candidate topology and allowed status/delay mechanism**; it does not test unknown processes or true model-class misspecification.

Each history is evaluated under ten record-retention masks: independent and transmitter-group retention at 25%, 50%, 75%, 100%; source-targeted deletion near 50% and 75%. Total 4,000 cases (2,400 development; 1,600 held-out). Repeated masks are correlated within world; uncertainty is bootstrapped **by world**. The identical 100%-retention mask appears in both independent and group arms; de-duplicated sensitivity appears below.

A retained simulated channel-status record reports the generator's assumed-truthful link readiness and, if live, its assigned latency. **No cryptographic signatures or independently authenticated execution provenance exist in this experiment.** Nonretained records leave the link completely unknown; they do **not** imply link failure. The potential graph is always known to all predictors. This is a *channel-network proxy*, not a faithful simulation of LLM cognition or human communication.

For each known topology, exact reference certification asks whether **every** completion of unobserved links and allowed delays agrees on timely arrival. A definite YES requires a fully witnessed on-time path; a definite NO requires every optimistic possible path to miss the deadline; otherwise the reference response is UNKNOWN. This is an exact property of this chosen mechanism class, independently checked by brute-force enumeration on small cases.

## Mathematical connection

Let `z_e` encode link readiness and `tau_e` its delay, and let `M` identify which simulated channel-status records were retained. The factual claim is

\[
T(H) = \mathbb{1}\bigl[\min_{\pi:s\leadsto t}\;\sum_{e\in\pi}\tau_e \le D\bigr],
\]

where failed links are not admissible on paths. Edge variables can be represented in a factor graph conditioned on the surviving records:

\[
P(H\mid O_M) \propto \prod_e \psi_e(z_e,\tau_e) \prod_{e:M_e=1}\delta[(z_e,\tau_e)=O_e].
\]

Thus the **posterior probability of a factual claim** and its **logical identification from surviving evidence** are different. The Monte Carlo baseline samples missing edge variables from development-fitted priors and recomputes the time-respecting predicate; the exact certifier checks compatible extreme histories without probabilities.

A separate numerical delayed linear influence surrogate has the conceptual form

\[
\dot x_i(t)=-\gamma x_i(t)+\sum_j \beta w_{ji}x_j(t-\tau_{ji}).
\]

The code uses explicit unit-step Euler updates, source forcing, fixed coefficients, and delay imputation for unobserved edges. It is **not** a validated continuous-state model of agent information or a general-purpose DDE solver. The no-delay surrogate sets each lag to zero while retaining identical features and training.

## Primary held-out results

| Observed-only method | Held-out Brier ↓ | AUROC ↑ |
|:--|--:|--:|
| Static topology/count/status logistic | 0.15075 | 0.8420 |
| ODE-like zero-delay surrogate + same static features | 0.15028 | 0.8425 |
| Fixed-coefficient delayed DDE surrogate + same static features | 0.14985 | 0.8427 |
| **Temporal shortest-path features + static features** | **0.11151** | **0.9140** |
| **Event-time Monte Carlo posterior (96 draws)** | **0.09091** | **0.9433** |

**Original frozen-model comparisons — world-cluster bootstrap (2,000 replicates, 160 held-out worlds):**

| Difference in Brier (first − second) | Difference | 95% cluster interval |
|:--|--:|:--|
| Temporal − static | −0.03923 | [−0.05196, −0.02777] |
| Delayed DDE − zero-delay | −0.00043 | [−0.00473, +0.00438] |
| Delayed DDE − temporal | +0.03833 | [+0.02736, +0.04988] |
| Event-time Monte Carlo − temporal | −0.02060 | [−0.03041, −0.01035] |

### Retrospective strong baseline: exact certification, then static prediction

The original comparisons omitted a conventional combination of two *already available* methods. After the independent review, we computed a stronger comparator without retraining or looking at private target values when constructing predictions. Recompute `certify(O)` from public observations, return `1` for `YES`, `0` for `NO`, and otherwise retain the development-trained static logistic probability unchanged.

| Held-out method | Brier (lower is better) | Evaluation status |
|:--|--:|:--|
| Static logistic | 0.15075 | Frozen original |
| **Exact certificate → static if UNKNOWN** | **0.11601** | **Post-hoc addition** |
| Temporal-path logistic | 0.11151 | Frozen original |
| Event-time Monte Carlo | **0.09091** | Frozen original |

The improvement of temporal over static is `0.03923`; the improvement of the exact-then-static policy over static is `0.03473`. Their ratio is **88.5%** (83.3% with the duplicate full-observation masks removed). This is a *descriptive decomposition of Brier gains for the measured policies*, not an estimate of a physical or causal mechanism.

Temporal minus exact-then-static has Brier difference **−0.00450**, post-hoc paired world-bootstrap 95% interval **[−0.00985, +0.00056]** (5,000 resamples, 160 held-out worlds). The difference is not robustly distinguishable from zero by this interval; an equivalence test was not performed. After removing the duplicate source-correlated 100%-retention cases, the Brier scores are **0.12390 (temporal)** versus **0.12891 (exact-then-static)**, difference −0.00500, interval **[−0.01094, +0.00062]**.

The strongest remaining evidence for useful inference beyond certification is on **908 UNKNOWN cases**: Monte Carlo Brier **0.16019**, temporal **0.19650**, static/exact-then-static **0.20443**. Monte Carlo minus exact-then-static is −0.04424, with a post-hoc world-bootstrap interval **[−0.06596, −0.02315]**, though the event-time model is closely matched to the simulator and uses development-fitted channel priors. This supports conditional probabilistic prediction of outcomes; it does **not** certify otherwise ambiguous histories.

The retrospective baseline is reproducible with `python posthoc_certified_static.py --root .`. It derives certificate decisions from public JSONL records; hidden outcomes are opened **only for scoring**. The amendment, original report snapshot, and new prediction CSV are supplied alongside the original artifacts.

These intervals measure sampling variation **within this synthetic held-out world generator**, not validity on actual agents. The event-time Monte Carlo model uses a prior fitted to development-world true link states; under misspecification, this advantage might not survive.

### Exact identifiability under evidence loss

Among 1,600 held-out partial-evidence evaluations, the reference certifier returns **YES: 168; NO: 524; UNKNOWN: 908**. Every certified answer agrees with the native hidden outcome (**0 observed certification errors among 692 certificates**). This is expected from an exact solver aligned with the stipulated evidence semantics; it does not imply zero empirical risk outside that model.

| Retained link records | Independent: identifiable | Source-correlated: identifiable |
|--:|--:|--:|
| 25% | 7/160 (4.4%) | 14/160 (8.8%) |
| 50% | 32/160 (20.0%) | 45/160 (28.1%) |
| 75% | 90/160 (56.3%) | 87/160 (54.4%) |
| 100% | 160/160 (100%) | 160/160 (100%) |

The precise differences between independent and group deletion depend on graph structure and which source groups are retained. There is no evidence here of a universal phase transition or a critical exponent. In general, removing one simulated channel record can reduce claim-specific certifiability even if network topology remains connected.

### Matched-topology constructive counterexample

A 3-node chain `A → B → C` has two live links and a deadline of 4 units. Delays `(1,2)` certify arrival; delays `(4,6)` certify non-arrival. Both have **exactly the same static directed graph and live-link indicators**. Our tests verify both determinations and ensure the static feature vector is identical. Time-respecting reachability, not static connectivity, distinguishes them.

### Sensitivity to duplicated full observation and nontrivial ambiguity

The 100%-retention test cases are present in both deletion schemes. Removing the redundant group-100% row from each world leaves **1,440 held-out cases**. Brier scores remain ordered: static `0.15386`, temporal `0.12391`, DDE `0.15322`, event-time MC `0.10101`.

Among the **908 reference-ambiguous held-out cases only**, Brier scores are static `0.20443`, temporal `0.19650`, DDE `0.20434`, event-time MC `0.16020`. The temporal model's advantage narrows when obvious fully certified instances are excluded. This is important: a gain from exploiting known records is not automatically a gain at resolving *ambiguous* hidden histories.

## Audit and limitations

- The independent auditor uses **NetworkX weighted shortest paths**, separately from the generator's topological dynamic program. It verified **400 native truths, 4,000 public cases, every retained simulated observation's agreement with the private ledger, and all 4,000 reference certificates**.
- Eight regression tests pass, including a small exhaustive 3-link certificate equivalence test and the same-topology/different-delay counterexample.
- Development/held-out split is **world-disjoint**. World/group masks are generated from deterministically sorted source groups and stable SHA-256-derived seeds.
- A mask changes the investigator's *visibility* of truthful link calibration records. It does not change the native links. Channel readiness is not the same thing as an actual agent deliberately sending a message.
- The source knows the potential graph. This does not reconstruct completely unrecorded agents or missing topology.
- The held-out shift tests altered parameters/correlations *inside* the reference class, not a new event ontology. The event-driven model is explicitly matched to a discrete-link truth simulator; using this simulator as ground truth structurally favors discrete-event methods over a continuous-state DDE surrogate.
- The DDE coefficients, Euler step, forcing and missing-lag imputation are fixed rather than tuned or validated against measured continuous agent states. The negative result concerns **this specific surrogate**, not the capability of DDEs generally.
- No real-world agent logs, unrecorded intent, thermodynamic equilibrium, true phase transition, or universal percolation law is established.

## What we learned

**Updated interpretation.** Exact checks explain most of the apparent gain of the temporal feature model over the static baseline. The incremental held-out Brier advantage over that stronger comparator is small and has a paired cluster interval including zero. Conventional event-time sampling retains an advantage on unresolved cases under this specified synthetic process family. This makes the clean distinction **certification under assumptions versus probabilistic prediction under uncertainty** the most defensible conclusion.


The useful mathematical organization is **temporal factor-graph inference + evidence deletion/percolation + exact claim identifiability**; no new physical law or phase transition was demonstrated. DDEs can model genuine delayed continuous states, but here the target is a discrete causal arrival event and a discrete-event posterior is the better matched baseline. The next real-workflow experiment would need measured latent states or repeated observations if it is to evaluate a DDE fairly. Without those, adding continuous dynamics is extra modeling assumption, not necessary scientific progress.
