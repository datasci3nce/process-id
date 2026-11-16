# Research audit and paper split decision

**Date:** 2026-11-15. **Assessment:** two distinct drafts are justified; the second remains exploratory.

## Major resolved problem: candidate-set confounding in the derived Wiki graph

The frozen v0.1.1 known-edge ranking changed distractor sets per deletion arm. At 100% retention the underlying graph was the same yet 65/199 two-hop and 103/199 shared-in-neighbor ranks differed, so the apparent percolation effect was not isolated.

The new source-connected rerun reads the original pinned derived graph (11,177 edges, 1,958 nodes) and recreates the original 199 source-target withheld links. It freezes 19 evaluator-side reference non-neighbor distractors plus the true target for each test link before applying any masks. Predictors receive only observed adjacency; fixed candidate identities are handed to the evaluator. Endpoint invisibility produces abstention on the fixed 199-link denominator. The 100% retention arms now match exactly per target. Five fixed-candidate seeds retain the 25% source-group shared-in-over-two-hop difference between **20.1 and 24.1 percentage points**.

The primary fixed-candidate source-correlated 25%-retention scores are **20/199 (10.1%) two-hop** and **67/199 (33.7%) shared-in-neighbors**. Their paired difference is **+23.6 points**, with exploratory target-bootstrap 95% interval about **[+16.6,+30.7] points**. A simple witness-level mechanism explains the direction: under source-group retention a two-hop directed chain usually uses two source groups and survives with factor p^2, but a shared-in common predecessor's two outgoing edges use one group and survive with factor p. This does not directly predict ranking accuracy, because ties, multiple witnesses, and visibility matter.

A further **64 masking realizations per group × p**, all on one fixed graph, gives at 25% independent retention mean two-hop/shared-in Top-1 **16.4%/17.3%**, and at 25% source-correlated retention **11.1%/31.9%**. Under correlated deletion shared-in wins **64/64** masks; independent has mixed directions. At 50%, independent **38.0%/32.8%**, source-correlated **28.2%/39.0%**. These are controlled masking realizations, **not independent graphs or an inferred universal threshold**. The new model provides a legitimate reason to describe the published Wiki graph as evidence of *deletion-mechanism-dependent ranking robustness* while carefully distinguishing published links from private causal provenance.

**Remaining replication boundary:** the source came through the public GitHub connector. Since the owner has no explicit redistribution license, raw graph bytes are omitted from the bundled ZIP; the Python reproduction scripts are provided with the pinned URL and Git blob hash. A fully independent replay on the graph bytes is still needed externally before the strongest empirical presentation.

## Distinct synthetic active-auditing result

The later DELAY-PERC study evaluates a *fixed factual claim* about whether information reached a target by a deadline, not a macro versus micro claim comparison. An exact reference checker settles **692/1600** claims and leaves 908 unresolved. On unresolved claims, event-time Monte Carlo lowers Brier from static **0.20443 to 0.16020**, mean difference **-0.04424** (95% world-bootstrap **[-0.06661,-0.02256]**), conditional on the synthetic prior class. A DDE surrogate offers no meaningful additional gain.

At eight new inspections starting from 320 identical paired low-retention masks from 160 held-out worlds, original policies certify **97 random, 161 one-edge-cut and 241 adaptive optimistic-path**. A new stronger **frozen-initial-path** comparator certifies 137. Adaptive replanning beats that comparator by **104/320 = 32.5 points** (95% paired world-bootstrap **[+25.3,+39.7] points**). This is a conventional adaptive path heuristic for a path-deadline task, not a general new algorithm.

A new truth-independent record-query accessibility intervention dramatically limits the potential value: at **50%** accessible missing records, eight-query certificates are **62 random, 74 frozen, 106 adaptive**; at **25%** accessibility, **46 random, 47 frozen, 53 adaptive**. At 100% availability those are **97, 137, 241**. The benefit depends on being able to obtain relevant records at all.

Two explicitly non-natural *assumption-violation stresses* delimit interpretation: one altered record gives **30 false among 709 certificates**, and adding an otherwise unlisted live one-step direct channel in 38/160 held-out worlds creates **135 false among the 692 preexisting certificates**, all false NO. Neither percentage is a real attack rate; both intentionally change the truth while continuing to apply the old model-relative checker.

## Paper split

- **Paper A** (*The Missing Process*) is the principal paper. It has the real-record HMM negative result, fixed-candidate published-link retrieval, finite parity connectivity/partition-function identity and SCALE-1 negative learner result. Its claim is bounded: source-correlation changes ranking robustness on a fixed derived graph; exact claim identification is mathematically characterized under explicit constraints. It does not establish an actual agent causal graph or a new criticality theory. The expanded draft is seven pages. The original submitted/sprint six-page draft is preserved.
- **Paper B** (*Evidence Before Inference*) is a separately defensible short *synthetic feasibility technical report*. Its target is exact certification, residual probabilistic prediction, and queryable evidence acquisition with strong simple baselines and deliberately unavailable-record controls. It adds a distinct operational question, but needs real instrumented multi-agent workflows and stronger cross-generator evaluation before a major-publication novelty claim. Three pages.
- **CE 2.0 / DDE** should not headline either. The CE toy mechanism factorizes nuisance dynamics from the target; it demonstrates nonimplication, not task improvement. The numerical DDE surrogate did not outperform conventional discrete event-time inference; neither is evidence of new agent-scale emergence.

## Most important next evidence for publication

A fully instrumented agent benchmark with separate native truth ledger, independently verified record authenticity, an unseen-mechanism test arm, fixed audit target and matched query budget. Measure calibration on unresolved claims, exact-certification errors, certification coverage per query and inability-to-retrieve rate. Include full delay-aware state, exact checker, a strong probabilistic predictor, random queries, frozen route, and adaptive route. This is a proposed prospective validation, **not completed in the current package**.

## Scientific bottom line

Yes, this is technical epistemics: it makes the distinction between **true**, **probable**, and **evidentially justified** executable, and tests whether targeted evidence acquisition can turn an uncertain claim into a supported one. The main limit remains dependence on a declared model and evidence source. The goal is reliable justification under partial observability, not novel PDE/DDE physics or causal-emergence claims.
