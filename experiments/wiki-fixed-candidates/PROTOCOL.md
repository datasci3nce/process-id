# Two-paper resolution protocol — 15 November 2026

This is an exploratory, post-sprint analysis. The prior six-page sprint study and later posthoc analyses are preserved unchanged.

## A. Real derived Wiki graph

Download *the exact pinned published derived edges file* (Git commit e152f85f9032a8e4a55dade4b7990defe5e138c9). Reuse original deterministic 199 test sources and held-out edges. Freeze each target's 20-way candidate set using the complete *published reference graph only to eliminate false negatives*; match distractors to the indegree bucket on the undeleted training graph, and do not regenerate candidates for mask arms or evidence fractions. Freeze the tie-breaking hash across all arms. Freeze the 199-case denominator. Report both (i) fixed-known-universe ranking, where candidate identities are given even when a node is isolated by deletion, and (ii) **strict observable-endpoint gated** ranking where unseen source or target means abstention/zero score. Independent and source-correlated masks use the original deterministic masks. Run candidate-set seed sensitivity and report matched-arm target results and paired bootstrap intervals. At p=1 the two masking arms must match *per target*.

This tests conditional sensitivity of the ranking algorithms to the published observed graph and mask, not real causal provenance or private hidden transfers. No new physical or epistemic phase-transition claim is permitted. This run is not preregistered and source has no explicit redistribution license; do not bundle raw graph contents.

## B. Delayed-network evidence acquisition and inference

Reuse all 160 original held-out synthetic worlds and the same fixed claim/observation masks; no retraining on evaluation labels. Add a no-adaptation / frozen-first-path acquisition baseline, a query-unavailability stress, and an omitted mechanism / false-receipt stress if feasible. Include the original random and cut-sensitivity baselines. Test held-out results with world-cluster bootstrap and report not only certification rate but cost, correctness and support coverage.

## Paper rule

Paper A is the amended real-Wiki + exact parity paper. Paper B is a distinct post-sprint proof-of-concept on certification, uncertainty, and evidence acquisition under stated discrete delayed-network assumptions. DDE and CE 2.0 remain negative/scope studies unless a matched fixed-target improvement survives. Split only if Paper B presents a genuinely distinct empirically checked protocol with limitations, not a new causal-emergence headline.
