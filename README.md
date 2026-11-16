# PROCESS-ID: Epistemic Reconstruction of Multi-Agent Processes

**Research-code and manuscript snapshot.** The papers are working drafts, not peer-reviewed publications. The experiments are distinct controlled studies, not a validated single end-to-end system.

## Research questions
When do partial observations determine a claim about a multi-agent execution history? When is a prediction merely plausible? Which additional records can resolve ambiguity, and how do conclusions fail when instrumentation is incomplete?

The repository collects related *distinct* experiments, not one validated end-to-end architecture.

## Start here
- [`experiments/process-id-03/`](experiments/process-id-03/): deterministic preflight for matched, observationally equivalent histories; *not* a natural LLM-agent oversight benchmark.
- [`experiments/process-id-02/`](experiments/process-id-02/): earlier LLM-agent workflow / scripted runner; 24-world live run had zero approved worlds and therefore no independent auditor evaluations. Original full live outputs are **not included**.
- [`experiments/delay-perc/`](experiments/delay-perc/): synthetic exact certification, static and temporal prediction, evidence acquisition.
- [`experiments/wiki-missing/`](experiments/wiki-missing/) and [`experiments/wiki-fixed-candidates/`](experiments/wiki-fixed-candidates/): known-record Wiki reconstruction and fixed-candidate graph masking. This does **not** identify private actions or directed provenance.
- [`experiments/scale1/`](experiments/scale1/), [`experiments/parity-theory/`](experiments/parity-theory/): synthetic identifiability, factor-graph controls and known-misspecification limits.
- [`papers/`](papers/): two **working** manuscripts, not peer reviewed.


## Previous research and code provenance
The November studies build on **TPRN, PO-ID, IPN and SWARM-HUNT**, which are **pre-sprint research**, not newly executed experiments in this repository. See [`docs/PRIOR_RESEARCH_LINEAGE.md`](docs/PRIOR_RESEARCH_LINEAGE.md) for what each tested, what survived critical audit, what remains unverified, and the boundaries of its claims. The original historical TPRN implementation is already public in [datasci3nce/tprn-missing-process](https://github.com/datasci3nce/tprn-missing-process). The original PO-ID, IPN and SWARM-HUNT bundles have not been copied into this public package pending their own release reviews.

## Data policy
Only source code, synthetic test fixtures, figures, and selected aggregate results are staged. Evaluator-only targets, private SQLite execution ledgers, individual masked evaluation rows, third-party raw Wiki exports, and nested original archive ZIPs are intentionally excluded. See [DATA_POLICY.md](DATA_POLICY.md).

## Reproduction
Some tests can be run directly, but experiments that use saved private/evaluator-only data require running their generator locally or obtaining access to a separate restricted evaluation package. Raw Wiki ingest and full fixed-candidate replay require fetching pinned third-party source material independently after checking its terms. The presence of source code does **not** imply all published result numbers can be reproduced from this public snapshot alone.

## Licensing
**License:** No open-source license has been selected. All rights remain reserved pending an explicit license decision. Third-party materials are not relicensed here.

## Status
Working research snapshot. See DATA_POLICY.md and SECURITY.md for release limitations.