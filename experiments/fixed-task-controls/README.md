# ER-FIXED-TASK-AUDIT-1

Post-original-finalization research audit, 15 November 2026.

**Read first:** `REPORT.md` (results and limitations), `PAPER_TIGHTENING_NOTE.md` (specific manuscript changes), `PROTOCOL_BEFORE_NEW_ANALYSIS.md` (before-run plan).

**New analysis scripts:** `run_audit.py` (exact gate, evidence acquisition, one-record corruption, Wiki candidate confound, CE fixed-target control), `extra_controls.py` (paired CIs, 30 random inspection seeds, Monte Carlo prior sensitivity), `plots.py` (figures).

**Data:** `inputs/` includes archived DELAY-v0.1.1, Wiki score archive and CE source archives (previously completed, unchanged). The evaluator-only ledger/labels are in the original DELAY archive and new scored outputs; DO NOT treat these as auditor-visible. `wiki_saved/` contains copied archived Wiki score rows for convenient reading. `results/` contains evaluator-only derived files and tables. The new scripts create no new real-world data, authenticate no receipts and use no LLM API.

**Reproduce in a fresh environment** with Python, numpy, pandas, matplotlib, pytest, and unzip:

```bash
bash reproduce.sh
```

The replay unpacks the three unchanged source archives under `inputs/` (if needed) and overwrites newly derived output CSVs/JSONs. It is a retrospective reanalysis, not independent preregistration. The source Wiki revision texts and complete raw derived graph edges are unavailable, so this archive cannot independently rerun the original Wiki ingestion or a fixed-candidate graph study.

`ER_WIKI_SPRINT_TIGHTENED_CANDIDATE_AUDIT/` contains the revised six-page draft, editable LaTeX and manuscript figures, separate from the frozen sprint original. **Official submission-template compliance remains unverified.**
