# ER-FIXED-TASK-AUDIT-1 protocol (written before executing new analyses)
Date: 2026-11-15. Retrospective, post-sprint, not independent preregistration.

## Goal
Tighten the completed Missing Process paper without changing its frozen sprint outputs; separate exact certification, unresolved probabilistic prediction, missing-evidence selection, and Wiki scorer confounds. Treat CE2 and numerical DDE as auxiliary theories, not headline claims.

## A: Same-target prediction after exact gating (archival held-out channel networks)
Using the existing 1,600 held-out cases, compute exact-gated versions of each saved static, temporal, DDE, and MC probability. Report all-case and UNKNOWN-only Brier, log loss, binary rates and world-cluster bootstrap differences. Compare MC to gated static; MC must improve on the 908 UNKNOWN cases to retain a substantive prediction claim. No retraining or selection on test labels.

## B: Adaptive evidence acquisition (same saved held-out channel ledgers)
Use only the 160 held-out worlds' two starting cases (independent p=.25 and transmitter-group p=.25, indices M00 and M04) from frozen public observations. Candidate queries are currently unknown edge records. Public selection policies: (1) stable hashed random edge, (2) shortest optimistic time-respecting potential path with unknown edges given minimum delay 1, query its first unknown edge (3) myopic cut sensitivity: for every unknown edge, compare optimistic source-target shortest delay if edge is absent, query the one with highest increase. Ties stable by edge id. After choosing, reveal just that edge's original native status/delay and re-certify. Report n world pairs, exact identification at budgets 0,1,2,3,5,8 additional queries and total number of inspections, for all cases. Do not use hidden truth to select queries. The selection methods are heuristics, not novel algorithms. If they fail to beat random, report it.

## C: Correctness boundary
Among exact certificates, compute historical correctness under unchanged assumed-truthful fixed-topology model. Probe sensitivity to one explicit, *simulated* false observed status/delay per case (status inversion or delay replacement); report errors/contractions when certifier still treats that record as trusted. This is an illustrative assumption violation, not a realistic security adversary or a held-out mechanism result.

## D: Real-Wiki saved-row score audit
Use the real 199 held-out source-target pairs and saved per-method ranks. At 100% retention, compare independent vs source-correlated conditions (same visible graph; differing scorer candidate sampling). On a common always-eligible edge set at 25% independent and 25% source-correlated, compare two-hop versus shared-in. Report that neither analysis removes changing-candidate confounding. Raw graph bytes / candidate lists are unavailable; NO claim of fixed-candidate re-evaluation.

## E: CE fixed-target control
Use CE package results to verify macro target probability, Bayes Brier, and exact recoverability are invariant under matched nuisance changes; show CE gains cannot be used as a task improvement when posterior is independent of nuisance. No new CE2 optimized hierarchy, no new observed-agent mechanisms.

## Primary interpretation
If exact gating removes most apparent gains and inference helps only on UNKNOWN, tighten discussion to emphasize exact check + calibrated probabilistic inference. Treat evidence selection as post-sprint feasibility. Do not insert post-sprint analyses as sprint-period findings. Preserve original PDF and protocol. Make a distinct manuscript patch proposal and supplemental artifact.
