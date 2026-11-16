# ER-DELAY-PERC-1 — Completed experimental report

**Status:** executed; locally frozen protocol before execution, independent native-ledger audit passed. **Date:** 15 November 2026. This is a new synthetic follow-up, **not** part of the completed AI × Epistemics sprint manuscript and not evidence from real LLM-agent traces.

## Research question

Can a time-respecting evidence model distinguish multi-agent signal-delivery histories that look identical as static graphs? Does a numerical delay-differential-equation (DDE) surrogate predict factual timely delivery better than a simpler event-time model? How does deletion of authenticated channel-status receipts affect claim-specific identifiability?

## Experiment and ground truth

400 independent layered *potential* channel graphs with 8, 16, 32 or 64 nodes (100 each), each with a source token, target, and deadline. Links have independent binary readiness and discrete measured delay in `{1,2,4,6}`. The native simulator computes true earliest arrival from live links. The first 240 worlds (60 per size) use independent link conditions and train predictors/priors; 160 held-out worlds (40 per size) use shared transmitter congestion that changes link success and latency jointly. Mechanism shift is in channel conditions, not graph topology or agent policy.

Each history is evaluated under ten signed-record masks: independent and transmitter-group retention at 25%, 50%, 75%, 100%; source-targeted deletion near 50% and 75%. Total 4,000 cases (2,400 development; 1,600 held-out). Repeated masks are correlated within world; uncertainty is bootstrapped **by world**. The identical 100%-retention mask appears in both independent and group arms; de-duplicated sensitivity appears below.

A retained signed receipt reports a link's verified readiness and, if live, its latency. Nonretained records leave the link completely unknown; they do **not** imply link failure. The potential graph is always known to all predictors. This is a *channel-network proxy*, not a faithful simulation of LLM cognition or human communication.

For each known topology, exact reference certification asks whether **every** completion of unobserved links and allowed delays agrees on timely arrival. A definite YES requires a fully witnessed on-time path; a definite NO requires every optimistic possible path to miss the deadline; otherwise the reference response is UNKNOWN. This is an exact property of this chosen mechanism class, independently checked by brute-force enumeration on small cases.

## Mathematical connection

Let `z_e` encode link readiness and `tau_e` its delay, and let `M` identify which signed receipts were retained. The factual claim is

\[
T(H) = \mathbb{1}\bigl[\min_{\pi:s\leadsto t}\;\sum_{e\in\pi}\tau_e \le D\bigr],
\]

where failed links are not admissible on paths. Edge variables can be represented in a factor graph conditioned on the surviving receipts:

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

**World-cluster bootstrap (2,000 replicates, 160 held-out worlds):**

| Difference in Brier (first − second) | Difference | 95% cluster interval |
|:--|--:|:--|
| Temporal − static | −0.03923 | [−0.05196, −0.02777] |
| Delayed DDE − zero-delay | −0.00043 | [−0.00473, +0.00438] |
| Delayed DDE − temporal | +0.03833 | [+0.02736, +0.04988] |
| Event-time Monte Carlo − temporal | −0.02060 | [−0.03041, −0.01035] |

These intervals measure sampling variation **within this synthetic held-out world generator**, not validity on actual agents. The event-time Monte Carlo model uses a prior fitted to development-world true link states; under misspecification, this advantage might not survive.

### Exact identifiability under evidence loss

Among 1,600 held-out partial-evidence evaluations, the reference certifier returns **YES: 168; NO: 524; UNKNOWN: 908**. Every certified answer agrees with the native hidden outcome (**0 observed certification errors among 692 certificates**). This is expected from an exact solver aligned with the stipulated evidence semantics; it does not imply zero empirical risk outside that model.

| Retained link receipts | Independent: identifiable | Source-correlated: identifiable |
|--:|--:|--:|
| 25% | 7/160 (4.4%) | 14/160 (8.8%) |
| 50% | 32/160 (20.0%) | 45/160 (28.1%) |
| 75% | 90/160 (56.3%) | 87/160 (54.4%) |
| 100% | 160/160 (100%) | 160/160 (100%) |

The precise differences between independent and group deletion depend on graph structure and which source groups are retained. There is no evidence here of a universal phase transition or a critical exponent. In general, removing one authenticated receipt can reduce claim-specific certifiability even if network topology remains connected.

### Matched-topology constructive counterexample

A 3-node chain `A → B → C` has two live links and a deadline of 4 units. Delays `(1,2)` certify arrival; delays `(4,6)` certify non-arrival. Both have **exactly the same static directed graph and live-link indicators**. Our tests verify both determinations and ensure the static feature vector is identical. Time-respecting reachability, not static connectivity, distinguishes them.

### Sensitivity to duplicated full observation and nontrivial ambiguity

The 100%-retention test cases are present in both deletion schemes. Removing the redundant group-100% row from each world leaves **1,440 held-out cases**. Brier scores remain ordered: static `0.15386`, temporal `0.12391`, DDE `0.15322`, event-time MC `0.10101`.

Among the **908 reference-ambiguous held-out cases only**, Brier scores are static `0.20443`, temporal `0.19650`, DDE `0.20434`, event-time MC `0.16020`. The temporal model's advantage narrows when obvious fully certified instances are excluded. This is important: a gain from exploiting known receipts is not automatically a gain at resolving *ambiguous* hidden histories.

## Audit and limitations

- The independent auditor uses **NetworkX weighted shortest paths**, separately from the generator's topological dynamic program. It verified **400 native truths, 4,000 public cases, every retained receipt's agreement with private ledger, and all 4,000 reference certificates**.
- Eight regression tests pass, including a small exhaustive 3-link certificate equivalence test and the same-topology/different-delay counterexample.
- Development/held-out split is **world-disjoint**. World/group masks are generated from deterministically sorted source groups and stable SHA-256-derived seeds.
- A mask changes the investigator's *visibility* of truthful link calibration records. It does not change the native links. Channel readiness is not the same thing as an actual agent deliberately sending a message.
- The source knows the potential graph. This does not reconstruct completely unrecorded agents or missing topology.
- The event-driven model is explicitly matched to a discrete-link truth simulator; using this simulator as ground truth structurally favors discrete-event methods over a continuous-state DDE surrogate.
- The DDE coefficients/lag imputation are fixed rather than tuned exhaustively. The negative result means **this tested surrogate** has no detectable extra benefit, not that all DDE models fail.
- No real-world agent logs, unrecorded intent, thermodynamic equilibrium, true phase transition, or universal percolation law is established.

## What we learned

The useful link is **temporal factor-graph inference + evidence percolation + exact claim identifiability**. DDEs can model genuine delayed continuous states, but here the target is a discrete causal arrival event and a discrete-event posterior is the better matched baseline. The next real-workflow experiment would need measured latent states or repeated observations if it is to evaluate a DDE fairly. Without those, adding continuous dynamics is extra modeling assumption, not necessary scientific progress.
