# ER-DELAY-PERC-1 — Synthetic delayed multi-agent evidence experiment

**Completed experiment; v0.1.1 corrected interpretive report and post-hoc baseline.** Do not conflate this with the earlier sprint Wiki evaluation or a real multi-agent LLM trace study.

## Contents

- `PROTOCOL_PRE_RUN.md` — locally frozen experimental design before execution
- `core.py` — graph and native link-state generator, exact claim identification, observed-only baselines
- `run.py` — execute 400-world benchmark, fit development models, save held-out scores and world-level uncertainty intervals
- `audit.py` — independent NetworkX audit of records, ground-truth arrivals, and reference identifiability
- `test_core.py` — small exhaustive tests and regression checks
- `results/public/` — auditor-visible partial evidence and corresponding visible predictions
- `results/evaluator_ONLY/` — private native ledgers, hidden factual outcomes and scored results; never pass to predictor
- `results/{SUMMARY.json,retention_breakdown.csv,size_breakdown.csv}` — main findings
- `figures/` — plots
- `REPORT.md` — revised scientific report incorporating the stronger post-hoc baseline
- `PROTOCOL_AMENDMENT_POSTHOC.md` — explicitly dated corrections to record semantics, scope, and interpretation
- `REPORT_ORIGINAL_UNAMENDED.md`, `MANIFEST_ORIGINAL_FROZEN_SHA256.txt` — original text and manifest preserved for audit history
- `posthoc_certified_static.py`, `test_posthoc.py` — auditor-visible exact-gate/static prediction, post-hoc scoring, tests
- `results/posthoc_exact_static/` — new evaluator-scored predictions and post-hoc uncertainty
- `figures/posthoc_strong_baseline.png` — comparative visualization, labeled retrospective

## Reproduction from the included results

Requires Python 3.10+ with NumPy, NetworkX, scikit-learn, Pandas, Matplotlib.

```bash
python -m unittest discover -p 'test_*.py' -v
python audit.py results
python posthoc_certified_static.py --root .
```

## Full rerun from clean environment

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run.py --out rerun --worlds-per-size 100 --draws 96 --boots 2000 --seed 20261115
python audit.py rerun
```

Optional plots: `python plot.py` from the package directory, where `results/` is the supplied evaluation directory.

## Cautions

- Full observation at p=1 is duplicated across two mask arms; both primary and de-duplicated sensitivity are reported.
- Every held-out world has 10 masks. Use world-cluster confidence intervals, not row-level independence.
- The graph is a known-potential-topology synthetic **channel** graph with link-state records; no external real-world ground-truth agent transfer claims.
- The DDE is a fixed-coefficient numerical influence surrogate, not an independently validated model of LLM beliefs.
- The exact YES/NO/UNKNOWN reference class assumes simulated observations assumed truthful and unknown-link possibilities with delays in `{1,2,4,6}`.

## Important documentary correction

Earlier versions called generated evidence records "signed" or "authenticated". The simulator neither signs records nor checks cryptographic provenance. They are **assumed-truthful simulated observations**. The original frozen protocol is retained, not silently edited; see `PROTOCOL_AMENDMENT_POSTHOC.md`. The original predictions were not refitted, and the new exact-gate comparator is retrospective. The held-out shift is confined to link parameter distributions and source correlations within the permitted process family. No actual LLM-agent records or missing-mechanism generalization are evaluated.
