# CE–Recoverability-1 — Exact experiment and paper-ready note

**What this package does:** A finite exact test of whether CE 2.0 *fixed-path* changes in causal primitives predict recoverability of a fixed claim after independent or correlated evidence loss.

**Already executed:** 6 Markov mechanisms × (512 independent + 8 grouped + 64 target-blind masks) = 3,504 exact model-mask evaluations, integrating over all 512 three-step micro histories and possible observations. 126 model × mask-mechanism × retention summaries. 9 tests passed. No training, fitting, sampling, calls to LLMs, or hidden real data.

**Run from any fresh Python environment** with numpy, pandas, matplotlib, pytest installed:

```bash
python code/ce_recoverability.py --output results
python code/plot_results.py --root .
python -m pytest -q tests/
```

Files:

- `REPORT.md` — scientific interpretation, mathematics, and limitations
- `results/causal_power_by_model.csv` — both CE2 `suff_plus_nec−1` (primary) and normalized effectiveness (sensitivity)
- `results/per_mask_exact.csv` — complete 3,504-case exact mask evaluation
- `results/recoverability_curves_exact.csv` — all 126 recovery-curve rows
- `results/DESIGN.json`, `results/VERIFICATION.json` — inputs and checks
- `figures/*.png` — plots with no simulation error bars
- `code/*.py` — self-contained exact implementation and figures
- `tests/*.py` — exact, analytic and repeatability regression checks
- `MANIFEST_SHA256.txt` — hashes of every packaged file excluding the manifest itself

**Sources:** Erik Hoel, *Quantifying emergent complexity*, *Patterns*, 2026, https://doi.org/10.1016/j.patter.2025.101472; official PyMergence toolkit, pinned at https://github.com/EI-research-group/pymergence/tree/6e5cb45bf445a29e8c5fb7b2a01c56efbc6e06ef. We port the mathematical CP formulas and compare them with an explicit independent loop; we do not claim to have imported or run the official toolkit. 

**Scope caution:** The selected nested coarse-graining is dynamically valid, but not optimized over all partitions. We do not calculate Hoel's full emergent complexity across the partition lattice. Exact evidence identification assumes the complete declared mechanism family and perfectly truthful observations.
