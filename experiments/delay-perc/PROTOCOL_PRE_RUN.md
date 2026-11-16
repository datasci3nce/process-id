# ER-DELAY-PERC-1: Frozen local protocol before generating outcomes

Research question: when identical potential communication graphs have different causal latencies, can time-respecting evidence improve prediction and exact identification of whether a token can reach its target by a deadline? Does a numerical DDE-inspired state model improve on simpler event-time inference?

**Worlds:** 400 independent generated directed acyclic agent-channel networks with 8,16,32,64 nodes (100 each). 240 developmental worlds use iid link success/latency; 160 held-out worlds use shared congestion mechanisms. Each world is a *channel network with a source token*, not a trace of real LLM cognition.

**Evidence:** ten masks per world: four independent retention probabilities 0.25,0.50,0.75,1.00; four transmitter-group retention probabilities with the same rates; two targeted removals at 0.50,0.75. Public graph contains potential edges and source/target/deadline, plus retained authenticated link calibration/status receipts. Evaluator privately retains all channel states and latencies.

**Ground truth:** replay of the recorded link network, with token arrival time the shortest true successful path delay. Timely-delivery predicate is arrival <= recorded deadline.

**Identifiability under reference model:** unknown links can be either failed or successful with allowed delay {1,2,4,6}; signed retained link evidence has exact status and latency. Reference certification YES if a proved-live on-time path exists, NO if even optimistic completion cannot deliver by deadline, UNKNOWN otherwise. Verify exactness by brute-force on small test graphs; do not confuse the factual predicate with identifiability. Certificate is conservative only under the declared mechanism/evidence rules, not for arbitrary agent activity.

**Comparators:** (a) static connectivity/count features, (b) temporal shortest-path observed/optimistic features, (c) event-driven Monte Carlo posterior of timed delivery over missing links using development-fitted prior, (d) numerical DDE-inspired delayed linear relaxation, and (e) DDE zero-delay ablation. All predictor features use only auditor-visible observations and development-fitted parameters. Logistic calibration is fitted on development worlds only; 160 held-out worlds are never used for tuning.

**Metrics:** primary heldout Brier for factual timely-delivery, with world-cluster CIs for paired differences; secondary AUROC, exact YES/NO/UNKNOWN reference identification, conservative-certification coverage, per-mask differences, runtime. Never conflate prediction and sound identification. Sampled 10 masks from each world, so 4,000 rows but only 400 independent histories. Sensitivity on held-out congestion worlds is an OOD stress test. At most descriptive measurement of evidence percolation; no phase-transition claim.

**Critical warnings:** the same source token reaches nodes via a discretely weighted shortest-time path; DDE is only a continuous-state *surrogate*, not ground-truth dynamics. Static topology and true link latencies are distinct; receipt observations pertain to link readiness. No external agent trace is used. No need to show DDE wins. The experiment is a follow-up to the sprint paper and is not part of the completed November 13-15 manuscript.
