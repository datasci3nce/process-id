from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
out=Path('results');figs=Path('figures');figs.mkdir(exist_ok=True)
R=pd.read_csv(out/'retention_breakdown.csv')
fig,ax=plt.subplots(figsize=(7.2,4.2))
for k in ('independent','source_correlated','targeted'):
 d=R[R.mask_kind==k].sort_values('retention')
 ax.plot(d['mean_retention'],(d['reference_yes']+d['reference_no'])/d['n_cases'],marker='o',label=k.replace('_',' '))
ax.set(xlabel='Fraction of simulated channel records retained',ylabel='Exact claim-certification fraction',ylim=(-.05,1.05),title='Recoverability under evidence deletion')
ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(figs/'certification_percolation.png',dpi=180);plt.close(fig)
S=pd.read_csv(out/'size_breakdown.csv')
fig,ax=plt.subplots(figsize=(7.2,4.2))
for name,label in [('static_logistic','Static topology'),('timed_logistic','Temporal path'),('dde_delayed','Delayed Euler DDE'),('mc_event_posterior','Event-time Monte Carlo')]:
 ax.plot(S['n'],S[name+'_brier'],marker='o',label=label)
ax.set(xlabel='Agent nodes',ylabel='Held-out Brier score (lower is better)',title='Prediction by system size');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(figs/'brier_by_size.png',dpi=180);plt.close(fig)
