# Manuscript consolidation: editorial map and claim ledger

**Revised 15 November 2026, v2.** Working manuscripts; do not overwrite the original sprint submission. The official cutoff is **16 November 2026, 12:59 PM Europe/Berlin (11:59 UTC)**, so work executed on the evening of November 15 after an earlier submission can still be **within the sprint deadline**. “After prior submission” does not establish that an experiment occurred after the sprint. Execution time, analysis time, manuscript revision time and submission timestamps remain distinct fields.

## Editorial decision

Keep two main manuscripts with distinct endpoints:

- **Paper 1 — The Missing Process:** What could an observer reconstruct or identify from incomplete records? Lead with the real-Wiki negative/conditional results and exact claim-specific recoverability; report the TPRN shortcut history as an audit motivation.
- **Paper 2 — Evidence Before Inference:** When should an auditor certify, predict, abstain or inspect another record? Lead with exact-certification logic, DELAY-PERC-1, the PROCESS-ID-0.2 empty-evaluation failure and the PROCESS-ID-0.3 non-LLM preflight. Do not imply that a real LLM auditor has been evaluated successfully.

Preserve **Correspondence Is Not Provenance** as a distinct, archived public-forensics manuscript. It concerns cross-service correspondence vs directed provenance and cannot be established by synthetic PROCESS-ID pairs or Wiki missing-edge retrieval. The three related lines must not be merged into an omnibus theory.

## Source and result provenance

| Claim | Status | Evidence reviewed for this consolidation | Use |
|---|---|---|---|
| Wiki revision dataset 14,591 revisions, 4,579 pages; 527 withheld editor labels across 237 test pages | Previously reported frozen result; raw source not re-ingested for this rewrite | *The Missing Process* 15-Nov submitted manuscript; research lineage | Paper 1 main, bounded to supplied recorded gaps |
| Page majority 91/527 Top-1 (17.3%); page-aware bridge 78/527 (14.8%); Top-5 29.0 vs 33.6% | Previously independently recalculated score arithmetic | Same manuscript and lineage | Paper 1 main; not unidentified private action reconstruction |
| Derived Wiki graph 199 withheld published links, 11,177 edges | Existing derived-record task | Same manuscript | Paper 1; not new causal links |
| Fixed-candidate graph ranking: 25% source-correlated shared-in 31.9% vs two-hop 11.1%; 64 masks/condition | **Provisional 15-Nov post-earlier-submission analysis (before cutoff)**; source-connected replay reported, but full pinned bytes + exact candidate lists and independent replay remain unverified in THIS revision | `AUDIT_AND_PAPER_SPLIT_DECISION.md` and Nov 15 results narrative | Paper 1 exploratory supplementary; avoid headline final numerical claim |
| Parity-graph exact claim recovery and free-energy density on up to 65,536 nodes | Executed prior numerical/theory check; established graph/linear-algebra equivalence | *The Missing Process* 15-Nov submitted manuscript | Paper 1, not new statistical-mechanics theorem |
| SCALE-1: claim-aware Brier .0666 vs content logistic .0910, supported 999 vs 1001, full exact 1276 | Corrected deterministic synthetic rerun after hash-order bug | Submitted manuscript and research lineage | **Paper 2** support-vs-prediction comparison; not Paper 1 main text |
| TPRN-2 424,625 cases, answer always last | Benchmark invalidated by construction shortcut | Research lineage and earlier manuscripts | Paper 1, methodological failure only |
| DELAY-PERC-1: exact 692/1600, unresolved 908; Brier static .2044, temporal .1965, MC .1602; derived full-gate Brier .1160 vs .0909 | Previously audited synthetic summaries; **full-gate Brier is arithmetic derived**, not independently rerun | `AUDIT_AND_PAPER_SPLIT_DECISION.md`, experimental notes | Paper 2 primary pipeline comparison, original archive replay outstanding |
| DELAY-PERC inspection, 320 cases / 160 worlds / 8 queries: at availability 100%, random/frozen/adaptive 97/137/241; at 50% 62/74/106; at 25% 46/47/53 | Earlier written audit provides exact summary counts; **per-case independent replay remains open** | `AUDIT_AND_PAPER_SPLIT_DECISION.md` | Paper 2 explicit cost/availability table; not a novel policy algorithm |
| One-record synthetic corruption: 30/709 wrong definite certificates (from 1,595 eligible alterations) | Engineered sensitivity study | Nov 15 post-sprint notes | Paper 2, not real attack-rate estimate |
| PROCESS-ID-0.2: 24 live worlds; 24 deferrals; 10 early v2 reads; 14 nonreads; zero eligible auditor evaluations | Checkpoint/code-output diagnosed in current conversation; format conditions mixed | User's Colab diagnostic logs and code excerpts | Paper 2 engineering negative control only |
| PROCESS-ID-0.3 72 matched opposite-truth pairs; 144 regular worlds; 576 masked cases; 864 acquisition trials; 12 out-of-model stress worlds | Reproducible deterministic preflight; zero LLM calls; executor and independent code auditing, not independent syscall monitoring | Mounted `PROCESS_ID_0_3/PROTOCOL.md`, README, summary, audits and code | Paper 2 deterministic methodological preflight only |
| PROCESS-ID-0.3 held-out certification rates 8/48, 32/48, 40/48 @ 100%; 4/48, 12/48, 16/48 @ 50% | Generator-defined mechanism and source-cost conditions | Original protocol and `preflight_summary_stdout.json` | Paper 2; route-aware is an optimal hand-coded baseline under the constructed distribution |
| PROCESS-ID-0.3 covert channel: 12/12 false NO outside model | Deliberate misspecification | Protocol + executor audit | Paper 2 stress control; **never** pool with within-model 0-error rate |
| Original acquisition auditor omitted full replay; separate checker detects corrupted retrieval traces | Additional audit strengthening | `PROCESS_ID_0_3_acquisition_replay_audit.py` + prior independent review | Paper 2 reproducibility issue; include checker in public release |

## What must not be claimed

1. No unique reconstruction of unrecorded private Wiki or Hugging Face actions from the Wiki graph tests.
2. No new universal percolation threshold, physical thermodynamic law, or demonstrated causal-emergence improvement for autonomous agents.
3. No AI-auditor accuracy or calibration result from PROCESS-ID-0.2; its selected test population was empty.
4. No trained auditor or learned inspection policy improvement in PROCESS-ID-0.3; it was non-LLM and deliberately route-aware.
5. No adversarially secure or independent OS attestation from the SQLite hash chain.
6. No global causal provenance or common actor identity inferred from separate public campaigns; preserve the `Correspondence Is Not Provenance` record independently.
7. No claim that pre-existing experiments were all run during the 13–15 November sprint.
8. No assertion that all publication numbers were independently rederived in this particular editing pass.

## Recommended final manuscript order

**Paper 1:** introduction and link-prediction precedents → claim-specific formalism (brief) → Wiki task protocols → editor and provisional fixed-candidate graph results → short exact parity context → limitations and dual use → shortcut history appendix. **No SCALE-1 results in main text.**

**Paper 2:** introduction and diagnosis/measurement-selection precedents → evidence contract and positive-vs-negative receipt asymmetry → DELAY-PERC full exact+predict pipeline and access controls → SCALE-1 support-vs-calibration → PROCESS-ID-0.2 live failure → PROCESS-ID-0.3 controlled audit and acquisition → omitted-channel failure → limitations and falsifiable next study.

## Submission gates

- [ ] Recover the **original DELAY-PERC-1 frozen outputs** and independently recompute the 692/1600 gate, 908 unresolved Briers, 320-case acquisition outcomes, uncertainty and cost denominators; add a full-population ungated baseline.
- [ ] Independently rerun the **fixed-candidate Wiki graph** analysis against the pinned original graph bytes, including 199 fixed targets, exact original 20-way candidate lists, 64 masks per condition, visibility failures, actual graph digest and script revision. Until then label results provisional in abstract/text.
- [ ] Add the independent **acquisition replay checker** to the PROCESS-ID-0.3 source bundle and demonstrate corruption-rejection in CI.
- [ ] Ensure PROCESS-ID-0.3 public observer features contain no pair IDs or evaluator-only labels; audit model prompt construction separately for a later live run.
- [x] Add directly relevant *verified primary bibliographic anchors*: Liben-Nowell & Kleinberg (2007), link prediction; Reiter (1987), diagnosis and discriminating measurements; de Kleer & Williams (1987), sequential model-based diagnosis and measurement choice. [ ] Expand the related-work review before journal submission; more than these anchors is needed.
- [ ] Reconcile experiment execution date, analysis date, **earlier-submission timestamp**, manuscript revision and cutoff separately; original sprint submission stays unchanged. The official Nov 16 cutoff is verified, so “post-sprint” for Nov 15 follow-up is misleading.
- [ ] Choose target venue/page limits; typeset and verify formulas, table denominators, supplementary reproducibility, limitations and dual-use declarations.

## Bottom line

Paper 1 is nearer to a defensible research manuscript because it has a real-record comparison plus clear negative controls, but even it does not demonstrate unknown private-action reconstruction. Paper 2 is a strong **methods/engineering technical report** with an auditable testbed; it needs an independent, genuinely agent-generated auditor evaluation before being promoted to a performance paper.

## V2 editorial changes and verification boundary

1. **Moved SCALE-1** out of Paper 1 into Paper 2.
2. **Restored DELAY-PERC exact-first pipeline:** 692/1600 certified, 908 unresolved; full-pipeline averages derived from saved summary and explicitly labelled as derived.
3. **Restored evidence-access comparisons** from prior audit notes; no per-case source replay claimed.
4. **Qualified Wiki editor Top-1** with page-cluster interval crossing zero; Top-5 interval separately positive.
5. **Corrected chronology** to November 15 post-earlier-submission but pre-deadline; source code and actual execution timestamps remain to be reconciled.
6. **Added verified nearest methodological precedents** for link prediction and active diagnosis.
7. **Distinguished positive and negative read certificates:** YES requires a trusted positive receipt; NO requires excluding all feasible routes; the omitted-channel stress is a designed failure case.

### Items verified this editorial pass

- File-level: the existing Markdown manuscripts and existing 15-Nov research audit notes were inspected and revised.
- Public source metadata: Apart Research official sprint page states cutoff 11:59 UTC on 16 Nov 2026 (12:59 CET, Berlin).
- Primary bibliography metadata: publishers list Liben-Nowell & Kleinberg (2007), DOI 10.1002/asi.20591; Reiter (1987), DOI 10.1016/0004-3702(87)90062-2; de Kleer & Williams (1987), DOI 10.1016/0004-3702(87)90063-4.

### Items *not* verified this editorial pass

- Full raw-source and independent candidate-matched Wiki replay. A prior source-connected rerun was documented, but its source bytes and fully reconstructible intermediate candidates are not contained in the mounted revision folder.
- The original DELAY-PERC per-case predictions and acquisition logs. Numbers come from an earlier audit memo, and computed gate averages are mathematical implications of those summary numbers.
- New prospective, independent LLM-auditor performance or out-of-distribution verification.