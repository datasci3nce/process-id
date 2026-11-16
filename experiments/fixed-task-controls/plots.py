from pathlib import Path
import pandas as pd,numpy as np,matplotlib.pyplot as plt
root=Path(__file__).resolve().parent;res=root/'results';out=root/'figures';out.mkdir(exist_ok=True)
ac=pd.read_csv(res/'acquisition_results.csv')
a=ac.groupby(['policy','k']).agg(hit=('identified','sum'),total=('n','sum')).reset_index();a['rate']=a.hit/a.total
fig,ax=plt.subplots(figsize=(8.2,4.8))
for method,label in [('random','Random queries'),('cut_sensitivity','Optimistic-cut sensitivity'),('optimistic_path','Optimistic shortest path')]:
 z=a[a.policy==method];ax.plot(z.k,100*z.rate,marker='o',label=label)
ax.set(xlabel='Additional record inspections',ylabel='Exactly identifiable claims (%)',ylim=(0,100),title='Fixed-claim evidence acquisition, 320 held-out starting cases')
ax.legend(loc='upper left');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/'evidence_acquisition.png',dpi=170);plt.close(fig)
sc=pd.read_csv(res/'prediction_scores.csv');fig,ax=plt.subplots(figsize=(8.6,4.7))
methods=['gate_static_logistic','gate_dde_delayed','gate_timed_logistic','gate_mc_event_posterior']
labels=['Exact → static','Exact → DDE','Exact → temporal','Exact → event-time MC']
allv=[sc[(sc.subset=='all')&(sc.method==m)].brier.iloc[0] for m in methods]
unk=[sc[(sc.subset=='unknown')&(sc.method==m)].brier.iloc[0] for m in methods]
x=np.arange(4);width=.37
ax.bar(x-width/2,allv,width,label='All held-out cases (n=1,600)');ax.bar(x+width/2,unk,width,label='Exact unresolved only (n=908)')
ax.set_xticks(x,labels,rotation=14);ax.set(ylabel='Brier score (lower better)',title='Exact certification separates solved from unresolved claims');ax.legend();fig.tight_layout();fig.savefig(out/'strong_baselines.png',dpi=170);plt.close(fig)
w=pd.read_csv(res/'wiki_same_graph_different_candidates.csv');fig,ax=plt.subplots(figsize=(7.8,4.4));z=w[w.method.isin(['two_hop','common_in','degree','path3'])]
ax.bar(z.method,z.changed_rank/199*100);ax.set(ylabel='Targets with changed rank (%)',ylim=(0,100),title='Same full-retention Wiki graph, different evaluation candidates');fig.tight_layout();fig.savefig(out/'wiki_candidate_confounding.png',dpi=170);plt.close(fig)
print('plots ready')
