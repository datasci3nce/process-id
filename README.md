# PROCESS-ID — Epistemic Reconstruction of Multi-Agent Processes

**Public research snapshot (partial upload).** This repository currently contains two revised working papers, a research-lineage guide, release/data policies, and a replay-audit script. The full vetted experiment code, tests, summary results, and figures are **not yet committed here**. Do not interpret this repository as a complete, independently reproducible release.

## Research question

When do partial observations uniquely support a claim about a multi-agent execution history? When is a reconstruction merely probable? Which new observations would resolve ambiguity, and how do results depend on instrumentation and the assumed model?

## Papers

- [Paper 1 — *The Missing Process* (working draft)](papers/Paper_1_The_Missing_Process_REVISED_V2.md): masked recorded editor labels, withheld published Wiki links, structural baseline and evidence-loss audits.
- [Paper 2 — *Evidence Before Inference* (working draft)](papers/Paper_2_Evidence_Before_Inference_REVISED_V2.md): separate certification from prediction and inspection, with synthetic SCALE-1, DELAY-PERC and PROCESS-ID studies.
- [Editorial map and scientific claim ledger](papers/Editorial_Map_Claim_Ledger_REVISED_V2.md).

Neither manuscript has been peer reviewed; the sprint-submission PDF is a separate version.

## Research provenance

The November work builds on **TPRN, PO-ID, IPN, and SWARM-HUNT**, which predate the November 13–15, 2026 AI × Epistemics sprint. See the [prior-research lineage](docs/PRIOR_RESEARCH_LINEAGE.md). The earlier [TPRN code repository](https://github.com/datasci3nce/tprn-missing-process) is separate. Historical PO-ID, IPN, and SWARM-HUNT bundles are not being re-released here.

## Reproducibility status

- Present: manuscripts, claim ledger, provenance guide, [one PROCESS-ID acquisition replay-audit script](experiments/process-id-03/additional_audits/acquisition_replay_audit.py).
- Not yet present: source generators and dependencies required to run the replay script; complete experiment implementations, tests, outputs, figures and derived Wiki graph source bytes.
- Source audits remain bounded by the declared evidence model; omitted channels can invalidate definite conclusions.
- The full public-safe code snapshot is available from the author for manual Git upload; see [upload instructions](PUBLISH_TO_GITHUB.md).

## Release and rights

See [DATA_POLICY.md](DATA_POLICY.md) and [SECURITY.md](SECURITY.md). No open-source license has yet been selected; repository visibility alone grants no permission to reuse third-party assets.
