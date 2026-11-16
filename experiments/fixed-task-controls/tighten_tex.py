from pathlib import Path
src=Path('/mnt/data/ER_FIXED_TASK_AUDIT_1/The_Missing_Process_Submission.tex').read_text()
repls=[
('shared in-neighbor scoring proves more robust to severe source-correlated deletion, subject to changing candidate pools.',
 'shared in-neighbor ranking is higher under severe source-correlated deletion, but changing candidate pools prevent a clean attribution to missingness.'),
('This is evidence that different local statistics respond differently to structured evidence loss. It is \\emph{not} evidence of an identified causal percolation threshold: degree-matched negative candidate sets are regenerated for every retention condition, and eligible-node counts change. We have not performed a fixed-candidate ablation using raw graph bytes.',
 'These are observed candidate-ranking contrasts, not an isolated causal effect of edge deletion: degree-matched negative sets are regenerated for every condition, and eligible-node counts change. A post-hoc same-graph check makes this confound directly measurable: at 100\\% retention, the two masking arms contain identical visible edges, but the held-out target rank changes for 65/199 two-hop cases and 103/199 shared-in-neighbor cases solely because candidate sampling depends on the arm. The 25\\% reversal therefore cannot establish a causal percolation effect. Raw graph edges and candidate lists are unavailable for the necessary fixed-candidate rerun.'),
('Third, on actual Wiki records, page-majority labels outperform Markov smoothing on Top-1, while structurally distinct graph scores respond differently to retention.',
 'Third, on actual Wiki records, page-majority labels outperform Markov smoothing on Top-1; graph rankings vary across deletion conditions but a same-graph control confirms candidate-set confounding.'),
('The next confirmatory study should instrument genuinely unseen workflows, independently preserve native truth, and freeze target-specific constraints, mechanism classes, and inspection budgets.',
 'First, the Wiki ranking result requires a fixed-candidate rerun on the raw graph to separate deletion from candidate sampling. A subsequent confirmatory study should instrument genuinely unseen workflows, independently preserve native truth, and freeze target-specific constraints, mechanism classes, and inspection budgets.'),
]
for a,b in repls:
 if a not in src:raise Exception('Missing patch string '+a[:80])
 src=src.replace(a,b,1)
dst=Path('/mnt/data/ER_WIKI_SPRINT_TIGHTENED_CANDIDATE_AUDIT/The_Missing_Process_Tightened.tex')
dst.write_text(src)
print('wrote',dst,src.count('same-graph'))
