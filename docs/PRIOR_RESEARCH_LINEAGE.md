# Research lineage: TPRN, PO-ID, IPN, and SWARM-HUNT

**Status:** prior research, principally September 2026; **not** work newly conducted for the November 13–15, 2026 AI × Epistemics Research Sprint. This is a historical and methodological guide, not an independent replication of every archived result. The November manuscripts and the experiments in this repository have their own stated evaluation scope.

## What is and is not in this repository

The files under `experiments/` implement the newer Wiki missing-record, DELAY-PERC, SCALE-1 and PROCESS-ID work. **The original historical TPRN, PO-ID, IPN and SWARM-HUNT packages are not included in this release.** The author's existing [TPRN GitHub repository](https://github.com/datasci3nce/tprn-missing-process) separately publishes TPRN code, archived outputs, and the first two reports. The additional historical research bundles are retained separately and require individual checks for licensing, privacy, evaluator-only truth and provenance before public release.

| Prior program | What it asked | Surviving lesson | Reproduction / release boundary |
|---|---|---|---|
| **TPRN (Temporal-Persistence Reconstruction Network)** | Can typed temporal and persistent-object process representations help retrieve missing process structure? | Local typed relations and historical state can be predictively useful; high reconstruction scores do not certify a unique past | See existing [TPRN repository](https://github.com/datasci3nce/tprn-missing-process). Do not conflate its matched-card generator transfer with unseen-process generalization |
| **PO-ID (partial-observability / proposition-identifiability studies)** | Which available observations make a particular historical proposition distinguishable from alternatives? | Evidence sufficiency is claim-specific and dependent on the reference mechanisms and instrumented channels | Original `tprn_po_id_v08`, `po_id3`, `po_id4`, XFAM and acquisition archives retained separately; not presently staged here |
| **IPN (Identifiability-Percolation Network)** | Can typed message passing estimate candidate probabilities, answerability, and value of inspecting missing evidence? | Neural prediction and evidence support are distinct; hybrid methods must be benchmarked against explicit constraints | Original IPN design, notebooks and earlier known-node Wiki outputs not embedded; archived scores need provenance-checked replay |
| **SWARM-HUNT** | Can candidate distributed processes be detected in mixed activity, and what do their links actually prove? | Namespace identity, attributed transfer, and joint work require different evidence; apparent continuity is insufficient | Original SWARM-HUNT-1/2A/2A.1/2B code bundles retained separately; not in this new release |

## 1. TPRN: representation and reconstruction

TPRN is a **family of experiments and representations**, not a single validated end-to-end forensic model. Its typed process graphs distinguish agents, activities, messages, artifacts, tools/services, authority, and effects; event ordering and persistent carriers constrain possible histories. Early experiments used Weisfeiler–Lehman-like local graph retrieval, spectral and transport methods, activity filtering, and typed-path evidence-loss tests.

The program's most instructive findings include failures. A first activity detector leaked labels. A factor-reconstruction task was matched by a simple logical rule. A META-STRUCTURE benchmark contained a minimum-arity shortcut. In **TPRN-2, 424,625 candidate tasks placed the correct answer last**, so the benchmark could be solved perfectly by presentation order without reconstructing a process. These invalidate the corresponding reconstruction claims, not the value of representing process semantics.

The later matched three-model experiment used the **same 100 latent process cards** surfaced by different generators. The existing repo reports compact-feature mean off-diagonal balanced accuracy 0.610 versus PCA 0.592 and richer TPRN-FULL 0.508. This establishes limited generator/rendering transfer on **familiar underlying cards**, not independent recovery of unseen process families. The TPRN-ID branch separately found historical state improved certain artifact-state and missing-history predictions under its benchmark; predictive signal still does not establish unique provenance.

**Connection to the November paper:** TPRN is antecedent motivation for strict shortcut audits and typed evidence, **not a new sprint algorithm**. The November Wiki tasks should be assessed against simple page and link-prediction baselines, not against TPRN's most favorable prior results.

## 2. PO-ID: proposition-relative identifiability

PO-ID shifted the target from *which process seems likely?* to *can the observation distinguish the possible histories that disagree on a particular claim?* For deterministic observations `g(H)`, a non-identifiability witness is a pair of reachable histories `H1`, `H2` such that `g(H1) = g(H2)` while the proposition `T(H1) != T(H2)`. A definite certificate is justified only if **all histories** compatible with the observed evidence and **declared reference model** agree on the target claim.

The PO-ID experimental series compared restricted telemetry, candidate histories and additional observations. The surviving conclusion is narrower than universal identifiability: **which source matters depends on the claim**, and a fitted reference class can omit a real mechanism. The related XFAM proposal/tests concerned transfer across changed mechanisms; they should be dated and described precisely from their original frozen files. Selective inspection was also studied; an earlier adaptive greedy acquisition policy did **not** show a material advantage over a fixed cascade at matched costs.

**Connection to PROCESS-ID-0.3:** the matched-pair benchmark operationalizes the same counterhistory logic. Its 72 paired histories with identical public views but opposite read outcomes were constructed by the generator; they prove a controlled ambiguity test, not real-world prevalence. A later retrieved execution receipt can resolve some pairs under the declared instrumentation model.

## 3. IPN: learned answerability under evidence loss

IPN stands for **Identifiability-Percolation Network**. The dated September 5 design specifies a typed message-passing representation with three heads: (1) candidate posterior `q(z|E)`, (2) probability the target is answerable or identifiable from the available evidence, and (3) predicted *pivotality* of a missing record for resolving the target. The plan compares learned inference/inspection against exact factor-graph, spectral and value-of-information (VOI) procedures, with explicit constraints against false completion.

An earlier **known-node Wiki** control reported safe-identification yields of **0.510** for factor+spectral, **0.559** for IPN, **0.729** for explicit constraints→IPN, and **0.757** for a broader confirmation pipeline. These are archived results on a different task than the November masked-editor and masked-edge experiments; **they are not independently reproduced by this public snapshot and should not be represented as new November findings**. They do not identify unknown private actions, and the additional confirmation steps and cost make a naïve “IPN is best” conclusion inappropriate.

**Connection to the November papers:** prediction/calibration and evidence-supported certification need separate metrics. SCALE-1 and DELAY-PERC emphasize that a more accurate predictor may fail to improve supported decisions over a conventional exact checker.

## 4. SWARM-HUNT: separating candidate links from stronger claims

SWARM-HUNT-1 proposed using typed trace evidence to locate distributed process candidates among mixed background activity. The historical record reports useful within-generator recovery, but also spurious or burdensome background chains. Follow-up tests progressively narrowed the semantic claim:

- **2A — Object identity:** matching strings on different services do not imply a shared persistent object. Namespace/context (and sometimes object version) must be established.
- **2A.1 — Attributed transfer:** even a producer writing `X` and a consumer reading `X` does not establish that the consumer read the particular version produced by that writer. Source/version/receipt binding matters.
- **2B — Coordination:** a connected, sequential, persistent process is not necessarily joint work by multiple actors; shared scheduling, common instructions, independent reuse or one controller can generate continuity. A reported 20% stress-cell workload was fixed by the constructed design, not an estimated natural ambiguity rate.

These are **separate propositions**, not a guaranteed inference ladder from connection to transfer to collaboration. Earlier synthetic counterexamples motivate the November emphasis on evidence authorization, but they do not prove attribution to real people, organizations, or a particular public agent incident. The prior SWARM-HUNT source bundles are retained for possible separately reviewed release.

## Chronology and epistemic boundary

Historical progression was not simply `TPRN → SWARM-HUNT → PO-ID`. The PO-ID and acquisition experiments were already underway **before SWARM-HUNT**; the intellectual organization in the new papers follows the questions rather than pretending one monolithic model steadily improved. TPRN examines proposal and prediction, PO-ID asks identifiability, IPN probes learned answerability/inspection, and SWARM-HUNT tests semantic attribution boundaries. The November studies add distinct record-reconstruction and controlled evidence-acquisition evaluations, not retroactive validation of all previous branches.

| Claim type | Evidence level |
|---|---|
| Withheld *record* accurately predicted | Predictive ranking; can be scored on known records |
| Historical claim identified under model | All declared-compatible histories agree; still model-relative |
| Historical/provenance attribution authorized | Requires authentic, complete-enough, claim-specific receipts and custody; not implied by a score |

## Source pointers and reproducibility warnings

1. [TPRN historical GitHub code and archived reports](https://github.com/datasci3nce/tprn-missing-process) (existing external repo; not copied into this release).
2. *The Missing Process: Epistemic Recoverability from Partial Multi-Agent Records* — original November 15, 2026 sprint PDF; its provenance paragraph explicitly labels TPRN/SWARM-HUNT/PO-ID/IPN as pre-existing.
3. *Research Lineage and Falsification Record* — historical chronology and scientific limits (prior internal companion note; not newly independently reproduced here).
4. *From TPRN to SWARM-HUNT to URLQUERY* — retrospective historical synthesis, with many early results explicitly marked conversation-recorded rather than artifact-verified.
5. September 5, 2026, *IPN-1 Design: Identifiability-Percolation Networks* — frozen research proposal.
6. Archived bundle names (not embedded here): `tprn_po_id_v08.zip`, `tprn_po_id4_bundle.zip`, `tprn_swarm_hunt1_bundle.zip`, `tprn_swarm_hunt2a_bundle.zip`, `tprn_swarm_hunt2a1_bundle.zip`, `tprn_swarm_hunt2b_bundle.zip`.

**Publication check:** Original historical source and results must be independently inspected for full datasets, hidden evaluator labels, third-party content, credentials, and reproducibility before importing any older bundle into a public repo. A public ZIP is *not* a substitute for an audit of the original archives.