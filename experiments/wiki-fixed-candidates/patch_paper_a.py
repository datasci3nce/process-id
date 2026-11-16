from pathlib import Path
import re
root=Path(__file__).resolve().parent
src=Path('/mnt/data/ER_WIKI_SPRINT_TIGHTENED_CANDIDATE_AUDIT/The_Missing_Process_Tightened.tex').read_text()
src=src.replace('\\date{\\small AI $\\times$ Epistemics Research Sprint (13--15 November 2026)\\\\[2pt] Track 2: Trust Infrastructure}', '\\date{\\small Research-sprint manuscript + clearly labeled post-frozen analysis (15 November 2026)}')
old='Separately, we mask 199 published edges in a derived 11,177-edge agent-interaction graph. Two-hop retrieval obtains 62.3\\% Top-1 with all other edges retained, declining to 16.1\\% under 25\\% independent retention; shared in-neighbor ranking is higher under severe source-correlated deletion, but changing candidate pools prevent a clean attribution to missingness.'
new='Separately, we mask 199 published edges in a derived 11,177-edge agent-interaction graph. The original graph scorer had changing distractor sets. A retrospective source-verified fixed-candidate rerun eliminates that confound: shared in-neighbor ranking exceeds two-hop ranking by 23.6 percentage points under one 25\\% source-correlated mask, and by 20.8 points on average over 64 new masks; both methods use identical candidate sets and a fixed denominator.'
assert old in src;src=src.replace(old,new)
start=src.index('\\begin{table}[t]',src.index('\\paragraph{Withheld published graph edges.}'))
end=src.index('\\paragraph{Why the deletion mechanism matters.}',start)
replacement=r'''\begin{table}[t]
\centering
\caption{\textbf{Retrospective fixed-candidate} derived-Wiki known-edge ranking. Top-1 percentages use 199 held-out links throughout; invisible target endpoints count as abstentions. All arms receive the identical 20 candidates per target, fixed before masking.}
\label{tab:wiki_graph}
\setlength{\tabcolsep}{3pt}\footnotesize
\begin{tabular}{@{}llrrr@{}}\toprule
Deletion & Retained & Two-hop & Shared-in & Eligible \\\midrule
Independent & 100\% & 66.3\% & 43.7\% & 199\\
 & 50\% & 38.7\% & 33.7\% & 169\\
 & 25\% & 15.6\% & 18.6\% & 140\\
Source-corr. & 100\% & 66.3\% & 43.7\% & 199\\
 & 50\% & 26.6\% & 38.7\% & 144\\
 & 25\% & 10.1\% & 33.7\% & 114\\\bottomrule
\end{tabular}
\end{table}

\paragraph{Evaluation repair, not a new held-out corpus.} In the original frozen study, even at full retention (identical visible graph), candidate resampling changed ranks across masking arms for 65/199 two-hop targets and 103/199 shared-in-neighbor targets. We subsequently retrieved the exact published derived edge file at pinned commit \texttt{e152f85f9032}, independently verified the original 199 held-out links and the 11,177-edge/1,958-node structure, and reran each ranker with one evaluator-supplied 20-way candidate set per target. Negatives are published-reference non-neighbors matched to the full-retention indegree bucket; reference edges are \emph{never} predictor features. Target endpoints absent from all retained edges are abstentions. At full retention all 199 ranks now match across deletion arms, as required. Changing candidate seeds five times preserves a source-correlated 25\% shared-in versus two-hop advantage of 20.1--24.1 percentage points. The primary fixed-candidate paired difference is +23.6 points (target-paired bootstrap 95\% interval [+16.6,+30.7], exploratory).

\paragraph{Repeated deletion masks.} As a distinct retrospective sensitivity test, we applied 64 reproducible independent or source-group deletion masks at each of 25\% and 50\% retention, retaining the same targets and candidates. At 25\%, shared-in and two-hop Top-1 average 31.9\% and 11.1\% under source-group deletion (shared-in better on all 64 masks), versus 17.3\% and 16.4\% under independent deletion (shared-in better on 38/64 masks). At 50\%, the corresponding means are 39.0\% versus 28.2\% for source groups (64/64 masks), and 32.8\% versus 38.0\% for independent deletion. Masks share the \emph{same underlying graph and targets}; these are finite-graph masking sensitivities, not 64 independent corpora or a claim of a universal percolation threshold.

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{figures/wiki_fixed_candidates_64_masks.png}
\caption{Post-frozen source-graph re-evaluation: mean Top-1 across 64 new masks per condition with fixed candidates and strict endpoint visibility. Source-group deletion favors common-predecessor witnesses.}
\label{fig:wiki_fixed}
\end{figure}

'''
src=src[:start]+replacement+src[end:]
src=src.replace('In particular, changing decoy sets even at full retention demonstrates that the observed ranking curve is not a pure percolation effect.', 'The repaired fixed-candidate analysis removes that particular evaluation confound, while the gap between witness-survival probabilities and retrieval accuracy remains: eligibility, ties, and available competing witnesses still matter.')
src=src.replace('Truthful signed native receipts, signed batch counts, and signed inbox snapshots impose reference constraints;', 'Simulated native receipts, batch counts, and inbox snapshots designated as trusted impose reference constraints;')
src=src.replace('no factual-label errors, authenticated-record contradictions, or world overlap', 'no factual-label errors, contradictions among stipulated trusted records, or world overlap')
src=src.replace('Third, on actual Wiki records, page-majority labels outperform Markov smoothing on Top-1; graph rankings vary across deletion conditions but a same-graph control confirms candidate-set confounding.', 'Third, on actual Wiki records, page-majority labels outperform Markov smoothing on Top-1. A repaired, post-frozen graph ranking study fixes evaluator candidate sets and recovers a deletion-mechanism-sensitive Top-1 contrast, but still evaluates known published edges, not hidden agent causation.')
src=src.replace("and its graph distractor sampling changes with retention.","; the original graph distractor sampling changed with retention, while the labeled post-frozen rerun fixes it.")
src=src.replace('First, the Wiki ranking result requires a fixed-candidate rerun on the raw graph to separate deletion from candidate sampling. A subsequent confirmatory study should instrument genuinely unseen workflows,', 'The fixed-candidate rerun resolves one evaluator confound but does not validate behavior outside this single derived graph. A subsequent confirmatory study should instrument genuinely unseen workflows,')
src=src.replace('\\noindent\\textbf{New in sprint (13--15 November):}', '\\noindent\\textbf{Original frozen sprint work (13--15 November):}')
src=src.replace('\\textbf{Pre-existing:} TPRN/PO-ID/IPN', '\\textbf{Post-frozen exploratory update (15 November):} source-verified fixed-candidate Wiki ranking, five candidate seeds and 64 masks per condition. These are not retrospective preregistration. \\textbf{Pre-existing:} TPRN/PO-ID/IPN')
src=src.replace('the amended v0.1.1 Wiki code, and archived WOTH-score recomputation.', 'the amended v0.1.1 Wiki code, the post-frozen source-pinned fixed-candidate rerun script, aggregate new scores, and archived WOTH-score recomputation.')
src=src.replace('Results were inspected retrospectively; local protocol freezing does not constitute independent preregistration.', 'The pinned published derived graph was directly read for post-frozen aggregation but cannot be redistributed as an unl icensed raw snapshot. Results were inspected retrospectively; local protocol freezing does not constitute independent preregistration.'.replace('unl icensed','unlicensed'))
src=src.replace('and its graph distractor sampling changes with retention.', 'and its original graph distractor sampling changed with retention; the post-frozen rerun fixes candidates without removing real-record provenance limits.')
src=src.replace('the paper provides aggregate evaluations', 'the paper provides aggregate evaluations')
# fix appendix statement
src=src.replace('the result archive preserves scores and pinned hashes, not raw bodies or full candidate lists; external source re-verification is still needed.', 'the result archive preserves scores and source-pinned code, not raw text bodies or copyrighted derived edge bytes; reproducing the post-frozen ranking requires fetching that same public graph commit.')
out=root/'Paper_A/The_Missing_Process_Repaired.tex';out.write_text(src)
print('Wrote',out,len(src))
