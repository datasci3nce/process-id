# Evidence Before Inference: Certifying and Acquiring Process Evidence under Partial Observability

**Revised working technical report v2 · 15 November 2026 · not a confirmed autonomous-agent oversight result**  
**Author:** Kishore Kumar Mariappan, Independent Researcher

> **Draft status and chronology.** This revision incorporates results reported by 15 November 2026 after an earlier paper submission but **before** the sprint's official November 16, 12:59 PM Berlin deadline. It does **not** claim that the experiments formed a single preregistered study. The frozen DELAY-PERC source archive was not independently replayed for this editing pass, so its exact counts are reported as **previously audited**, not newly reproduced. PROCESS-ID-0.2 contains genuine LLM-selected actions but zero LLM-auditor evaluations; PROCESS-ID-0.3 is a controlled synthetic preflight with real sandbox file reads, not open-world supervision.

## Abstract

An auditor of a multi-agent workflow must decide not only what most likely happened but whether the available records justify a definite claim and whether inspecting another source would resolve uncertainty. We separate prediction, claim identification and evidence acquisition through an explicit compatibility-set decision rule. In an earlier synthetic delayed-network study, an event-time Monte Carlo predictor reduced Brier score on 908 initially unresolved held-out cases from 0.2044 for a static baseline to 0.1602, without converting probabilistic estimates into certificates. Record alteration exposed the separate trust problem: 30 of 709 definite certificates became factually wrong after one observed channel record was modified in each of 1,595 eligible cases. A subsequent 24-world live LLM-agent pilot completed execution but collapsed to universal coordinator deferral, leaving zero eligible model-auditor evaluations; delivery alone predicted its 10 early version-2 reads and 14 nonreads. We therefore designed a deterministic, executor-grounded preflight with 72 matched pairs of opposite execution truth but identical public evidence. In its 48-world held-out set, a two-unit evidence-acquisition budget certified 8 worlds with registered-first, 32 with auxiliary-first and 40 with a route-aware rule at full source availability; coverage fell to 4, 12 and 16 at 50% availability. All within-model certificates were sound by construction and independent replay, while a separate twelve-case undeclared-channel stress set caused twelve factually false negative certificates. These results establish a reproducible *evaluation contract* for evidence-aware process auditing, not an empirical advantage of learned auditors or a security guarantee. The central unresolved question is whether the same discipline improves decisions on independently instrumented, genuinely agent-generated histories.

## 1. Introduction

Distributed workflows routinely separate three entities that an auditor may accidentally conflate: what actually occurred in the executor, what an agent reports about its own activity, and what external records establish. A message saying “I verified the latest report” is not a read receipt. A delivered version is not necessarily the version a verifier read. A high predicted probability of success is not proof that required evidence exists.

This paper asks an operational question: **when should an auditor issue YES or NO, when should it return UNKNOWN, and when is it worthwhile to inspect another authenticated source?** We deliberately avoid treating this as a single classification benchmark. In particular, factual accuracy, support under a declared model, and authorization by trustworthy evidence must be separate outputs.

The research developed through two complementary routes. Prior delayed-network experiments studied probability estimates and record acquisition under a known simulated process. A later PROCESS-ID live pilot introduced LLM-selected worker, verifier and coordinator decisions with actual sandbox file reads. That pilot completed 24 worlds but produced no evaluable approval cases, revealing a flaw in task design rather than any success of the auditor. PROCESS-ID-0.3 then removed approval as a precondition for ground truth and constructed matched histories in which the available public evidence could not distinguish success from failure. This deterministic preflight makes the meaning of an evidence certificate auditable before asking a new LLM to predict or inspect.

We make three limited contributions: (i) a decision decomposition between certification, probabilistic inference and evidence acquisition; (ii) transparent failure analysis of a live agent-pilot evaluation; and (iii) a replayable deterministic preflight that proves observational ambiguity within a declared reference model and exposes its dependence on assumed instrumentation completeness.

### 1.1 Related work: diagnosis and measurement selection

Selecting evidence to distinguish compatible explanations is not new. Reiter's **theory of diagnosis from first principles** (1987) formalized candidate diagnoses and principles for discriminating measurements; de Kleer and Williams's **General Diagnostic Engine** (1987) combined model-based diagnosis, incremental measurements and information-theoretic selection. Our route-aware and optimistic-path policies are not algorithmic breakthroughs beyond this literature. The narrower object here is a *historical execution proposition* with executable artifact-read ground truth, explicit authenticated-receipt semantics, separate YES/NO/UNKNOWN authorization, and a deliberate test of what fails when channel coverage is omitted. This differs from classical component-fault isolation, but relies on the same core ideas of compatible hypotheses and informative observations.

## 2. Auditing contract

### 2.1 Target truth and evidential status

Let \(H^*\) denote the realized execution history, \(Y=T(H^*)\in\{0,1\}\) a binary target, \(O\) observed external records, and \(\Theta\) a declared class of permissible histories. Define

\[
\mathcal C_\Theta(O)=\{h\in\Theta:h\text{ satisfies the observed records and their declared trust semantics}\}.
\]

An exact evidence certifier returns YES if all compatible histories have \(T=1\), NO if all have \(T=0\), UNKNOWN if both values remain possible, and CONTRADICTION if no history is compatible. These are **logical statuses relative to \(\Theta\)**. A Bayesian or predictive model may also estimate \(p(Y=1\mid O)\) when the exact certifier returns UNKNOWN. Its estimate can be scored by Brier or log loss, but it does not remove a logically compatible alternative.

A practical decision layer additionally needs an authorization contract: which records, receipts, custody conditions and instrumented channels justify an output? **YES and NO are asymmetric.** A valid positive read receipt can establish a read *relative to that record's authenticity*. A categorical **NO** requires excluding **every route capable of producing the target read** in the relevant time window. Absence from a few trusted logs does not show global nonoccurrence unless coverage of all relevant routes is itself justified. A false certificate can arise from corrupted evidence or from a genuine unlisted mechanism, even if the compatibility checker is logically correct inside its declared model.

### 2.2 Evidence acquisition

Let \(e\) be a potentially inspectable record with cost \(c(e)\) and an availability event. An acquisition policy \(\pi\) selects records adaptively within budget \(B\), observes successful retrievals, and updates the compatibility set. We assess its **newly certified cases**, **factual certificate errors**, **cost**, and **failures or unavailable records**. A query policy must not be credited for simply revealing a label in a source whose completeness and authenticity are assumed away. An exact checker given all trusted evidence is an upper-bound reference, not a model that an LLM should be expected to beat on the same inputs.

All numerical comparisons below are conditional on the trust semantics and costs defined by their respective benchmark. They are not direct estimates of human investigation cost or deployment benefit.

## 3. Delayed-network evidence, conditional prediction and inspection

### 3.1 Full certification-then-prediction pipeline

The previously audited DELAY-PERC study models delayed message histories under a known synthetic network and a fixed target: did the required information arrive before a downstream action? **The conventional exact checker resolves 692 of 1,600 held-out claims (43.25%) and leaves 908 unresolved.** Only the unresolved cases require a probabilistic estimate. On those 908 cases, the reported Brier scores were:

| Method *only on unresolved cases* (n=908) | Brier ↓ |
|---|---:|
| Static predictor | 0.2044 |
| Delayed DDE surrogate | 0.2043 |
| Conventional temporal predictor | 0.1965 |
| Event-time Monte Carlo | **0.1602** |

Reported difference for event-time Monte Carlo minus static on unresolved cases: **−0.0442 Brier**, 95% held-out-world bootstrap interval **[−0.0666,−0.0226]**. This improves *prediction* conditional on the simulated prior and assumed missing-link probability. It does not create a logical certificate for an unresolved claim.

The following **complete-pipeline** Brier figures are transparent algebraic aggregations of the previously reported unresolved averages. They assume the 692 exact answers were factually correct and hence incur zero Brier. They were **not** independently recomputed from the original per-case file in this editing pass.

| Complete decision pipeline (all n=1,600) | Exact certificates | Predicted cases | Derived aggregate Brier ↓ |
|---|---:|---:|---:|
| Exact + static | 692 | 908 | **0.1160** |
| Exact + temporal | 692 | 908 | **0.1115** |
| Exact + event-time Monte Carlo | 692 | 908 | **0.0909** |

The absolute gain of replacing static with Monte Carlo **after the exact gate** is approximately **0.0251 aggregate Brier**, rather than the larger unresolved-only 0.0442 difference. This makes visible that the exact checker already settles much of the case population; it does **not**, by itself, quantify the counterfactual advantage over an ungated model because its full-population scores were not available for this revision. Prior sensitivity controls found that predictions can deteriorate if the assumed missing-link probability is changed. Any stronger claim that temporal inference explains the bulk of improvement requires a same-denominator ungated comparison from frozen artifacts.

### 3.2 Record acquisition with inaccessible evidence

The previously audited inspection experiment began from **320 matched starting cases across 160 independent held-out worlds**, allowing up to eight channel-record queries. The optimistic-path heuristic adaptively inspects an unknown edge on a presently feasible fast route; the frozen-path control commits to its initial route; neither is a novel active-diagnosis algorithm.

| Accessible queried records | Random | Frozen initial path | Adaptive optimistic path |
|---|---:|---:|---:|
| 100% | 97/320 | 137/320 | **241/320** |
| 50% | 62/320 | 74/320 | **106/320** |
| 25% | 46/320 | 47/320 | **53/320** |

A separate *one-edge-cut* policy resolved **161/320** at 100% availability; this is not the same as the frozen-path baseline. At full access, the reported adaptive-minus-frozen difference is **104/320 = 32.5 percentage points**, paired world-bootstrap interval **[+25.3,+39.7]**. At 25% access, the difference shrinks to **6/320 = 1.9 points**. These denominators and uncertainty figures come from the earlier audited research memo; **the complete frozen acquisition traces still require independent replay**. This test assumes known possible routes and queryable synthetic records rather than naturally discovered infrastructure evidence.

### 3.3 SCALE-1: probability does not authorize certification

The corrected SCALE-1 synthetic study generated **400 histories and 4,800 evidence masks**, with **160 held-out worlds (1,920 masks)**. The held-out claim-aware predictor had Brier **0.0666** versus **0.0910** for content-only logistic, but at the chosen certificate threshold it issued **999 supported and zero unsupported** decisions versus **1,001 supported and two unsupported** for content-only. The conventional full exact checker identified **1,276** cases with **zero unsupported** within the declared closed world. This is not learned-method superiority: improved probability estimates did not outperform conventional exact checking for support, and threshold-selected counts are not a fair *matched-risk* advantage claim.

### 3.4 Record alteration invalidates otherwise valid premises

A separate synthetic integrity stress deliberately altered one observed channel record in **1,595 eligible cases**. The unchanged certifier issued **709 definite conclusions**, **30** of which were factually wrong (4.23% of issued certificates). This measures sensitivity under a designed assumption violation, **not** a real attack prevalence or likelihood of manipulation. It illustrates that logical correctness under supplied evidence does not ensure the evidence itself is trustworthy.

## 4. PROCESS-ID-0.2: Live execution, empty evaluation

The next prototype ran Llama 3.3 70B Instruct through OpenRouter for worker, verifier and coordinator roles. Workers created sandbox report versions; the verifier selected an action; a deterministic executor performed actual Python file reads and logged events in SQLite; the coordinator could approve or defer. Logical delivery times were simulated. The run consumed approximately $0.00670 in reported or estimated charges across 76 accumulated API calls, including retries and resumed attempts. Its saved 24 execution checkpoints constitute a mixed-format-protocol engineering pilot after a worker repeatedly emitted `2 + 2` where JSON required a numeric literal.

The results exposed a fatal denominator problem. Coordinator decisions were `defer` in all 24 cases, and the implementation defined its original truth target only for approved worlds. Consequently, the nominal held-out LLM-auditor evaluation had **zero cases**. The automatically printed `all_certificates_factually_correct=True` was vacuously true; an independent audit expecting `baseline_scores.csv` failed because the empty evaluation produced no score rows. Neither auditor accuracy nor auditor calibration can be inferred from this run.

The raw execution still supported a descriptive analysis. Ten worlds had v2 delivered by tick 12 and the verifier selected `read_delivered` in all ten; fourteen worlds had no v2 delivery by tick 12 and the verifier selected `read_old` in all fourteen. All ten early `read_delivered` calls retrieved version 2 at tick 13; the other fourteen retrieved version 1. A delivery-only rule predicted the outcome in **24/24 worlds**. Seven undelivered cases had a direct-store route potentially available but did not use it. Because the verifier prompt included delivery status, the action distribution provides no evidence of sophisticated autonomous reconstruction and no randomized causal test of information-seeking.

This pilot should be reported as a **negative benchmark-design result**: the live execution harness worked, while selection on approval made the intended epistemic evaluation impossible. It motivated the next design's independence between execution truth and approval choice.

## 5. PROCESS-ID-0.3: Deterministic executor-grounded preflight

### 5.1 Target and construction

The preflight defines the target independently of coordinator approval:

\[
Y=\mathbf1\{\text{the verifier actually read v2 at a logical tick }<20\text{ through any channel}\}.
\]

Each successful read calls `Path.read_bytes()` on a sandbox artifact and yields an executor-side SQLite `artifact_read` event. An independent code auditor checks the ledgers and recomputes the target from events and artifact hashes; it does **not** use OS-level syscall tracing or an external cryptographic trust anchor.

The generator constructs 72 matched pairs (144 regular worlds): two report families times six mechanism families times six repetitions. Each pair has identical public task, delivery, access, requested action and verifier claim but opposite `Y`. The flip is achieved by a controlled registered I/O success/failure or a controlled auxiliary read. Mechanisms include a delivered read, store fetch, old-version read, skipped read, late read and denied fetch. These are executor interventions, **not emergent LLM actions**.

Pairs are split 48 train / 24 test, giving 96 training and 48 held-out worlds; no matched pair straddles splits. The test labels are balanced 24/24. This tests familiar mechanism types with pair separation and is **not** out-of-distribution generalization across unseen mechanisms.

### 5.2 Observational equivalence and exact certificates

The auditor's initial evidence excludes the outcome, intervention, private ledger and pair identifier. Public evidence is identical between the two members of every pair, despite opposite truth. Therefore any deterministic classifier receiving *only this public observation* must make the same prediction for both pair members and is correct on at most one per pair: the maximum balanced test accuracy is 50%.

The declared model assumes exactly two complete, trustworthy potential early-read channels: **registered** and **auxiliary**. A purchased channel receipt says whether that channel's early-read log contains v2. The exact certifier enumerates compatible `(registered-read, auxiliary-read)` Boolean assignments. Positive evidence from either channel establishes YES. NO requires that the remaining possible routes be excluded by receipts or public workflow constraints. Without sufficient information, it returns UNKNOWN. The protocol compared this enumerator with a distinct algebraic implementation.

Across 144 regular worlds and four evidence masks each, there were 576 masked cases and 0 wrong definite certificates within this assumed two-channel model. An independent audit checked 156 native SQLite ledgers (144 regular plus 12 separate stress worlds), file digests and hash chains. Ten regression tests passed. A later complementary replay checked 864 acquisition trials, including sensitivity to deliberately corrupted acquisition traces. Those audit checks validate consistency of this implementation and saved results, not external authentication of every real-world read.

### 5.3 Cost-constrained retrieval

The registered receipt costs one unit, the auxiliary receipt two units, and the total budget is two. At 100% availability, the held-out acquisition coverage was:

| Policy | Certified / 48 | Percentage |
|---|---:|---:|
| Registered-first | 8 | 16.7% |
| Auxiliary-first | 32 | 66.7% |
| Route-aware | **40** | **83.3%** |

With 50% deterministic source availability, the same policies certified 4/48 (8.3%), 12/48 (25.0%) and 16/48 (33.3%). An unavailable request still consumes the stipulated cost. The route-aware rule consults public workflow constraints to prioritize a receipt that can matter. The main result is **constructed by the generator and its pricing**: route-aware reaches the expected 40/48 maximum under the frozen two-unit acquisition problem. It is not an empirical learned-policy advantage, and a learned model cannot outperform the exact oracle given the same correct assumptions and evidence.

### 5.4 Omitted-channel stress

Twelve separate counterfactual histories add a third, *undeclared* successful read channel while both declared channels report no v2 read. The two-channel certifier returns definite NO in 12/12 cases, but executor-native ground truth is YES in all twelve. These are deliberately out-of-model examples and are **not** combined with the regular zero-error certificate rate. The result demonstrates sensitivity to the exhaustiveness assumption; it cannot estimate the frequency of omitted channels in deployed systems. The local hash chain verifies consistency of recorded events, not completeness of all channels and not resistance to an adversary able to rewrite and rehash the log.

## 6. What this does—and does not—show

Three separations survive. (i) **Exact certification precedes probability estimation**; in DELAY-PERC the gate settles 692/1,600 claims, and the probabilistic gain is restricted to the unresolved remainder. (ii) **Which evidence to query matters**, but the synthetic advantage of a conventional adaptive path rule erodes sharply as accessibility falls; classical model-based diagnosis already contains the core idea. (iii) **Certificate soundness depends on trusted receipt semantics and coverage of every relevant execution channel.** The engineered omitted-channel counterfactuals expose this assumption but do not estimate real failure frequencies.

It does **not** yet show that an LLM auditor improves over exact checking, learns better retrieval than a fixed route-aware rule, generalizes across unanticipated agent workflows, or recognizes an omitted channel without additional authenticated coverage information. The PROCESS-ID-0.2 run did not test the LLM auditor at all; PROCESS-ID-0.3 involved no model inference and used deliberately balanced interventions. The two studies must remain separate in all denominators and figures.

A worthwhile follow-up would freeze logging semantics and evidence budgets, execute independent genuinely LLM-selected action policies on held-out workflows, preserve truth using stronger instrumentation, include both approval and deferral without filtering away the target, and compare exact certificate + static inference, conventional probabilistic inference and an LLM auditor on the *same observations*. If the learned auditor does no better than simple rules or issues unsupported definite outputs, that should be reported as a negative result.

## 7. Limitations and dual-use considerations

The delayed-network, SCALE-1 and PROCESS-ID-0.3 datasets are synthetic. The 0.3 sample balance is imposed by construction, so its 50% public-only ceiling is a designed identifiability demonstration, not a measured incidence rate. The logged file-read truth relies on the same program that executes reads, although a separate audit program independently checks recorded events; no OS-level or external attestation exists. Logical ticks are not wall-clock distributed scheduling. The model is given an exhaustive two-channel assumption that is false by construction in the stress set. Costs and source availability are stipulated rather than collected from real infrastructure. The live 0.2 data mixed response-protocol versions and failed to yield an auditor denominator. The DELAY-PERC counts and complete-pipeline Brier aggregation require per-case frozen-source replay before being described as independently reproduced. The positive-versus-negative certificate asymmetry is conditional on record authentication and coverage, not a guarantee about a deployed system.

More capable evidence selection and provenance reconstruction could be used to infer operational behavior from fragmented logs. This report focuses on abstract, synthetic histories and clear evidence limits. It does not offer procedures for unauthorized access to private execution logs, nor does a model's reconstruction authorize external accusation, attribution or invasive data collection.

## 8. Conclusion

The central research object is not a single guessed hidden history but **a historical proposition whose evidential status can change as additional trusted records are inspected**. Evidence Before Inference separates a defensible certificate from a predictive estimate and from an acquisition strategy. The constructed PROCESS-ID-0.3 benchmark passes its deterministic checks, while PROCESS-ID-0.2 documents why evaluator design can invalidate a live pilot despite successful agent execution. The next scientific test must move beyond these feasibility demonstrations to independently instrumented real agent decisions with genuinely nontrivial evidence availability and strong conventional baselines.

## References and artifact provenance (working)

1. Mariappan, *The Missing Process: Epistemic Recoverability from Partial Multi-Agent Records*, AI × Epistemics Research Sprint submission, 15 November 2026. [Companion reconstruction paper, not an experimental result in this report.]
2. Reiter, R. (1987). “A theory of diagnosis from first principles.” *Artificial Intelligence* 32(1), 57–95. https://doi.org/10.1016/0004-3702(87)90062-2. [Competing explanations and discriminating measurements.]
3. de Kleer, J., and Williams, B. C. (1987). “Diagnosing multiple faults.” *Artificial Intelligence* 32(1), 97–130. https://doi.org/10.1016/0004-3702(87)90063-4. [Incremental model-based diagnosis and measurement selection.]
4. Mariappan, DELAY-PERC-1 delayed-network probability and evidence-inspection controls (earlier audited working results, original per-case archives required for independent replay).
5. Mariappan, SCALE-1 deterministic corrected reference benchmark (400 histories, 4,800 masks; prior research source).
6. Mariappan, `PROCESS-ID-0.2` live OpenRouter agent pilot (24 completed worlds; checkpoint and executor logs, 15 November 2026). [Mixed response-format engineering run; no eligible auditor evaluations.]
7. Mariappan, `PROCESS-ID-0.3` deterministic protocol, `0.3-preflight-1`, seed `20261115`, 15 November 2026. [144 execution worlds; source archive, private event-ledger results and independent auditor.]
8. PROCESS-ID-0.3 independent acquisition-trace replay script (post hoc additional audit; must be included in the public reproduction archive).

**Submission gates (open):** independently replay the original DELAY-PERC 1,600-claim and 320-case per-query outputs (including the ungated comparator and world-cluster uncertainty); reconcile SCALE-1 thresholds and risk; integrate acquisition-trace replay into the frozen PROCESS-ID-0.3 package; distinguish original execution timestamps and later manuscript revisions; do not claim a measured LLM-auditor advantage. The official sprint submission deadline is **16 November 2026, 12:59 PM Berlin time**; an earlier 15 November submission remains archived.