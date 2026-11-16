# The Missing Process: Claim-Specific Recoverability from Incomplete Multi-Agent Records

**Revised working manuscript v2 · 15 November 2026 · not submitted or peer reviewed**  
**Author:** Kishore Kumar Mariappan, Independent Researcher

> **Version and chronology.** This rewrite was prepared on 15 November 2026 **after an earlier submission, but before the official November 16, 12:59 PM Berlin submission deadline**; “post-submission” does **not** mean “post-sprint.” The original submitted PDF is retained unchanged. The repaired fixed-candidate Wiki analysis was reported later on November 15 and remains **provisional pending an independent replay against the pinned derived-graph bytes and exact candidate lists**. Execution time, analysis time, version time, and submission time must be documented separately. Do not treat prior TPRN work as a fresh sprint experiment.

## Abstract

Incomplete execution records make it tempting to reconstruct a single hidden process from locally plausible traces. We distinguish three tasks that are often conflated: predicting a deliberately withheld *record*, identifying a proposition in a declared space of compatible histories, and making an attribution backed by trusted provenance. We audit two supplied-gap tasks on public Collusion Wiki-derived data rather than claim to reconstruct previously unrecorded agent actions. In 527 withheld editor-label cases drawn from 237 test pages, within-page majority achieves 91/527 Top-1 matches (17.3%) versus 78/527 (14.8%) for a page-aware Markov bridge; the paired page-cluster interval for the bridge-minus-majority difference includes zero (−2.47 percentage points, 95% interval [−5.95,+0.92]), so the data do **not** establish a general Top-1 advantage for either method. The bridge improves Top-5 retrieval from 29.0% to 33.6%. On 199 withheld published links from a derived graph, an original candidate-generation confound was uncovered: candidate sets changed across evidence masks. A subsequently repaired fixed-candidate analysis suggests that common-predecessor ranking is more robust than two-hop ranking under source-correlated deletion, **but the updated figures await independent source-level replay**. Exact synthetic parity constraints illustrate why global uncertainty alone cannot determine claim-specific identification. The contribution is a bounded empirical benchmark audit and a set of necessary interpretation controls, not a new general algorithm for hidden-action recovery or a thermodynamic law of AI agents.

## 1. Introduction

A distributed agent workflow can produce a final answer even when important intermediate actions are poorly observed. An agent may read a file, send a message, rely on an earlier artifact, or infer a state from a stale receipt. The surviving record may contain a final artifact, isolated message receipts and partial logs, but not the full execution path. A reconstruction system can offer candidate explanations. The harder question is whether the available evidence makes a particular historical claim necessary, merely probable, or unjustified.

We call this **the missing-process problem**. It has three distinct objects of evaluation. First, *record prediction* asks whether a model can recover a particular withheld editor label, edge or event from surrounding visible records. Second, *claim identification* asks whether all process histories compatible with the evidence agree about a specified proposition. Third, *authorized historical attribution* asks whether the evidence, its custody and its trust assumptions justify a consequential external claim. A high score on the first does not prove the second or third.

The TPRN program began with typed temporal relations and local graph matching, but benchmark audits revealed that strong scores sometimes came from candidate-generation conventions rather than substantive reconstruction. Details of those invalidated benchmarks are preserved in Appendix A so the main text remains focused on the real-record evaluations.

We offer **two empirical and one explanatory contribution**. (1) We audit the supplied-gap editor-label task against simple within-page baselines, paired page-cluster uncertainty, and candidate availability. (2) We expose the candidate-generation confound in the published-edge task and present a *provisional* fixed-candidate sensitivity analysis of structured evidence loss. (3) We explain, using standard exact parity constraints, why identification of a specific claim is not summarized by global entropy. The distinct synthetic question of certification versus probabilistic prediction (SCALE-1 and DELAY-PERC) belongs in the companion technical report.

The contribution is an audited set of distinctions, controls and empirical limitations, **not** a new universal reconstruction algorithm or a thermodynamic model of agent cognition.

### Closest related work and scope of novelty

Structural link prediction is established: neighbor overlap, local paths and related topology statistics are standard ranking signals (Liben-Nowell and Kleinberg, 2007; Adamic and Adar, 2003). Our shared-predecessor and directed two-hop methods are **baseline statistics, not new algorithms**. The evaluation differs from prospective link prediction: an evaluator deliberately hides an already published edge and supplies a fixed 20-candidate list. Consequently, scores measure *withheld known-edge retrieval under specified deletion masks*, not detection of unknown causal transfers or private events. The closest contribution here is auditing how candidate-set construction, endpoint visibility and grouped deletion alter apparent ranking robustness. The HMM and factor-graph connections also predate this work; we use them to clarify the meaning of evidence and inference, not as a new graphical-model theorem.

## 2. Formalizing the reconstructable claim

Let \(H\) be a complete execution history, \(M\) an evidence-retention pattern, and \(O_M(H)\) the records available to an observer. Let \(\Theta_{\rm ref}\) be a declared reference model specifying possible histories, trustworthy record semantics and permitted transitions. Define the compatible set

\[
\mathcal{C}_{\rm ref}(O_M)=\{h\in\Theta_{\rm ref}:h\text{ is consistent with }O_M\}.
\]

An audit target is a proposition \(T:H\mapsto\{0,1\}\), for example, “the verifier read artifact version 2 before the decision cutoff.” Its evidence status is

\[
D_T(O_M)=\begin{cases}
\text{CONTRADICTION},&\mathcal C_{\rm ref}(O_M)=\varnothing,\\
\text{YES},&T(h)=1\ \forall h\in\mathcal C_{\rm ref}(O_M),\\
\text{NO},&T(h)=0\ \forall h\in\mathcal C_{\rm ref}(O_M),\\
\text{UNKNOWN},&\text{otherwise}.
\end{cases}
\]

For a nonempty compatible set, \(T\) is identified exactly when all compatible histories have the same value of \(T\). This is **relative to the reference class**. If \(\Theta_{\rm ref}\) omits a genuine execution channel, even a logically correct definite certificate can be factually wrong. A separate predictive model can estimate \(p(T=1\mid O_M)\) while the set-valued certifier returns UNKNOWN; high posterior probability alone is not a logically complete certificate.

These distinctions matter for empirical design. A withheld *published* Wiki link has a recorded reference answer: the task is retrieval. It does not establish a unique explanation for how a private agent acted. Conversely, synthetic execution histories with native event logs can define a target proposition exactly, but their closed-world assumptions do not establish the prevalence of ambiguity in deployed agent systems.

### 2.1 Sequence and factor-graph views

An HMM factorizes a latent sequence via transition and emission factors. Forward–backward smoothing is sum-product inference on this chain. More general multi-agent histories require factors for execution success, inbox state, artifact version, message timing and dependency constraints. Their conditional distribution can be represented schematically as

\[
p_\theta(H\mid O_M)\propto \prod_a\psi_{a,\theta}(H_a)\prod_{e:M_e=1}\ell_e(o_e\mid H).
\]

For energy \(E_M(H)\) defined by these factors, the normalizer \(Z_M=\sum_H\exp[-E_M(H)]\) permits a variational free-energy representation. This is an established inferential identity, **not** evidence that LLM agents are physically thermalizing. Claim-conditioned partition functions \(Z_t=\sum_{H:T(H)=t}\exp[-E_M(H)]\) separate support for competing target values. Under exact hard constraints with positive weights on admissible histories, the claim is identified iff precisely one of \(Z_0,Z_1\) is positive. Both positive means non-identification; both zero means contradiction.

### 2.2 Retention is not transmission

Deleting records after an execution affects what an observer can infer, not what actually happened. A percolation-like record-retention parameter \(p\) must therefore be distinguished from a message-transmission probability governing the forward process. In a finite set of \(m\) potential observations, claim-specific recoverability under independent retention can be written

\[
R_T(p)=\sum_{S\subseteq[m]}\mathbf1\{D_T(O_S)\in\{\mathrm{YES},\mathrm{NO}\}\}p^{|S|}(1-p)^{m-|S|},
\]

assuming truthful observations and a fixed compatible-history model. This is a finite reliability curve, not a universal threshold or a certificate for any single realized mask. Correlated loss changes the distribution over subsets and can protect some witnesses while destroying others.

## 3. Data, protocol and evaluation boundaries

### 3.1 Masked recorded editor labels

The public Collusion Wiki export in the prior submission contains 14,591 revisions across 4,579 pages. A page-disjoint development/test construction yielded 527 held-out recorded editor labels from 237 test pages. The target revision is concealed in the evaluation view; all test cases are supplied gaps rather than automatically detected missing entries. In 71/527 cases the correct editor label is absent from the available candidate vocabulary. These cases remain in the denominator. An editor string is not a verified unique human or AI identity.

Models include previous or next visible editor, within-page majority, a Markov filter, a Markov bridge, and a page-aware bridge. We report Top-1 and Top-5, not an unsupported causal recovery claim. Cases cluster within pages, so uncertainty estimates should be clustered by page.

### 3.2 Masked published graph edges

A separately published derived graph contains 1,958 nodes and 11,177 directed unique edges. One published edge was withheld for each of 199 source nodes. Predictors rank a withheld endpoint among 20 candidates using retained adjacency; full-reference neighbors are excluded from the decoy pool to avoid labeling known published links as negatives. A key correction was to keep **the same candidate set across masking conditions**, and to count invisible endpoints as failures rather than silently reduce the evaluation denominator.

The original submitted graph analysis regenerated candidates as evidence changed; it therefore could not isolate the effect of retention. A later fixed-candidate analysis generated 64 masks per condition on the same fixed graph, comparing independent edge retention with source-correlated deletion. These repeated masks are not 64 independently sampled real-world graphs, and the reported comparisons still need source-byte replay against the pinned graph. They establish conditional robustness on this published graph, not a population-level agent-campaign effect.

### 3.3 Exact parity graph as explanatory control

In a controlled noiseless binary parity system, observed edges impose \(x_u\oplus x_v=y_{uv}\). A consistent graph with \(c(S)\) connected components has \(Z_S=2^{c(S)}\). For the relative parity claim \(x_u\oplus x_v\), identification occurs iff \(u\) and \(v\) are connected in the surviving graph. This supplies a **synthetic explanatory control**, not a Wiki generative mechanism or a new theorem. The separate SCALE-1 signed-receipt certification comparison is reported in Paper 2.

## 4. Results

### 4.1 Page-aware smoothing does not demonstrate a Top-1 improvement

| Method | Correct / 527 | Top-1 | Top-5 |
|---|---:|---:|---:|
| Previous editor | 73 | 13.9% | 13.9% |
| Next editor | 78 | 14.8% | 14.8% |
| Page majority | 91 | **17.3%** | 29.0% |
| Markov filter | 24 | 4.6% | 9.9% |
| Markov bridge | 33 | 6.3% | 13.9% |
| Page-aware bridge | 78 | 14.8% | **33.6%** |

The observed page-aware-minus-majority Top-1 difference is **−2.47 percentage points**, with an exploratory page-cluster bootstrap 95% interval **[−5.95,+0.92]** and 20 paired wins versus 33 losses. That interval includes zero: **the smoother has not demonstrated a Top-1 improvement**, but a population-level claim that majority is intrinsically superior is also unsupported. For Top-5, the bridge is **+4.55 points** ahead (page-cluster interval **[+1.92,+7.30]**). Cases are clustered within 237 test pages; neither interval licenses extrapolation to every Wiki page. The 71/527 out-of-vocabulary reference labels remain in the denominator. This is label interpolation, not recovery of an unknown private editor or actor.

### 4.2 Fixed-candidate Wiki masking: provisional source-level sensitivity result

| Retention | Two-hop, independent | Shared-in, independent | Two-hop, source-correlated | Shared-in, source-correlated |
|---|---:|---:|---:|---:|
| 100% | 66.3% | 43.7% | 66.3% | 43.7% |
| 50% | 38.0% | 32.8% | 28.2% | **39.0%** |
| 25% | 16.4% | 17.3% | 11.1% | **31.9%** |

*Exploratory analysis run after the earlier November 15 submission (still within the sprint deadline), not a result from that submitted version. The above averages use 64 masks per condition on **one** derived graph, 199 fixed targets and fixed 20-way candidate lists; source-connected rerun notes exist, but raw graph bytes, candidate lists and the complete replay script were **not available for independent re-execution in this editing pass**. Treat all four nontrivial rows as **provisional**, not independently verified publication findings. The original evaluation regenerated candidate sets across masks and is not pooled with this corrected protocol.*

A two-hop path \(s\to u\to t\) depends on two source groups under source-correlated deletion, while two edges \(u\to s\) and \(u\to t\) sharing a predecessor can survive together with their one source group. The elementary witness-survival probabilities are respectively proportional to \(p^2\) and \(p\) for this deletion mechanism. This accounts for a plausible local structural advantage of shared-in-neighbor ranking as retention falls, without implying a universal phase transition or identifying unrecorded causal edges. The fixed-candidate repair is essential: the earlier full-retention arms had nonidentical rankings because the distractor sets had been regenerated.

### 4.3 Explanatory control: claim-specific parity recovery

In an exactly solvable synthetic 65,536-node parity graph at 50% retained constraints, cross-community recovery was reported as 0.478 with one bridge versus 0.938 with four bridges, while the corresponding bulk free-energy densities were near −0.01788 and −0.01776. These are controlled examples of a **known connectivity/linear-algebra identity**: which proposition an observer asks about matters more than a single bulk summary. They are not measurements of the Wiki process and do not constitute a new statistical-physics principle.

## 5. Discussion

The main empirical evidence is intentionally narrow. The editor-label task shows that a conventional sequence model fails to establish a Top-1 gain over within-page frequencies, though it improves Top-5. The edge-ranking task exposes why comparisons across evidence-retention arms require *fixed candidate sets* and a fixed denominator; the corrected evidence-loss pattern remains provisional until raw-source replay. Exact parity constraints offer an interpretive example of claim-conditioned identification. None of these tasks establishes recovery of previously invisible private actions or directed cross-service causation.

A useful reconstruction pipeline should therefore have separate interfaces: **candidate proposal** (what might have happened), **reference-model identification** (what all compatible histories imply), and **provenance authorization** (what independently trustworthy evidence permits us to claim). The latter cannot be inferred automatically from a strong rank or a large posterior odds ratio. In particular, a hidden event inferred from public traces cannot be promoted to directed cross-provider provenance without discriminating records.

This distinction also clarifies how to use ideas from percolation and statistical mechanics. These tools organize constraint survival and probabilities over latent histories. They do not by themselves imply a physical temperature, universal phase transition, causal emergence, or thermodynamic explanation of agent behavior. The claim-conditioned reliability curve, not the survival of the largest component alone, is the appropriate object for an evidential question.

## 6. Limitations, reproducibility and dual use

The Wiki analysis uses recorded editor labels and published derived edges, not verified actor identities or hidden private actions. Curation and missingness may be nonrandom. The original graph benchmark changed candidate sets across retention conditions. The **corrected candidate-fixed table is a provisional follow-up** on repeated masks of one graph; the result cannot be treated as final until the full candidate identities, pinned graph hash and executable replay have been independently checked. The earlier archive preserved derived scores and source hashes but not the original raw Wiki revision bytes. The parity discussion assumes complete and truthful synthetic constraints. It cannot validate a Wiki causal or provenance graph.

The study has potential dual use in reconstructing activities from public traces. We report aggregate performance and evidence status rather than operational instructions for recovering private credentials or attributing intent. The findings do not establish that particular organizations or public-record actors conducted coordinated operations, nor do they connect separate public incidents into one causal campaign.

## 7. Conclusion

Recoverability depends on **which claim, which evidence, and which reference history class** are in view—not on rank accuracy or graph connectivity alone. The strongest currently audited real-record finding is that a page-aware temporal bridge did not demonstrate a Top-1 advantage over within-page frequencies, despite a Top-5 gain. A promising fixed-candidate link-ranking sensitivity result awaits source-level independent replication. That incomplete dependency is preferable to overstating provenance: a predicted withheld public edge is not evidence of a unique hidden agent process.

## Appendix A. Shortcut history (context, not a new result)

Earlier TPRN experiments included a label-leaking activity detector, a logical-completion task solved by a deterministic rule, a candidate task with an arity shortcut, and TPRN-2, where all **424,625** true candidates appeared last. These invalidated the corresponding claims of genuine inference. They motivated four benchmark controls used here: shuffle-invariant candidate scoring, fixed candidates across masks, endpoint visibility counted as abstention, and page/source-cluster uncertainty. None is presented as a newly run experiment in this manuscript revision.

## References and research provenance (working)

1. Yedidia, Freeman & Weiss (2005), *Constructing Free-Energy Approximations and Generalized Belief Propagation Algorithms*, IEEE Transactions on Information Theory. [Established factor-graph background; bibliographic details reproduced from the preceding manuscript.] 
2. Evans, Kenyon, Peres & Schulman (2000), *Broadcasting on Trees and the Ising Model*, Annals of Applied Probability. [Established tree-reconstruction background.]
3. Zdeborová & Krzakala (2016), *Statistical Physics of Inference: Thresholds and Algorithms*, Advances in Physics.
4. Collusion Wiki, public explorer revision export, https://collusion.wiki/explorer/download.html (source identified in preceding manuscript; version and hash must be verified for this rewrite).
5. WikiAgentSwarmInvestigation, derived agent-interaction graph, pinned commit `e152f85f9032a8e4a55dade4b7990defe5e138c9`, https://github.com/JoshuaDavid/WikiAgentSwarmInvestigation.
6. Liben-Nowell, D., and Kleinberg, J. (2007). “The link-prediction problem for social networks.” *JASIST* 58(7), 1019–1031. https://doi.org/10.1002/asi.20591. [Closest structural-prediction baseline literature; primary publisher metadata checked.]
7. Adamic, L. A., and Adar, E. (2003). “Friends and neighbors on the Web.” *Social Networks* 25(3), 211–230. [Common-neighbor family and local link signals.]
8. Mariappan, *The Missing Process: Epistemic Recoverability from Partial Multi-Agent Records*, AI × Epistemics Sprint manuscript, 15 November 2026 (earlier submission, not superseded).
9. Mariappan, *Research Lineage and Falsification Record*, companion research note, 15 November 2026.

**Submission gates (open):** independently replay fixed-candidate link scoring on the pinned derived graph with the original **199 target and candidate lists**, 64 masks per condition, visibility abstentions, graph checksum and independent script; independently verify all frozen result archives; complete original execution/analysis/submission timestamps; check official template and ethics appendix. The deadline currently listed by the organizer is **16 November 2026, 12:59 PM Berlin time**. A manuscript ready to submit must not present the provisional fixed-candidate numbers as independently validated.