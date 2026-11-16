from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path(__file__).parent
fig=out/'figures';fig.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':160,'savefig.dpi':200})
rows=list(csv.DictReader(open(out/'results/parity_scale_summary.csv')))
S=[r for r in rows if int(r['n_nodes'])==65536]
fig1,ax=plt.subplots(figsize=(6.3,3.3))
for b,sty in [(1,'o-'),(4,'s-'),(16,'^-')]:
    x=sorted([r for r in S if int(r['bridges'])==b],key=lambda r:float(r['retention']))
    ax.plot([float(r['retention']) for r in x],[float(r['cross_recoverability']) for r in x],sty,label=f'Across communities, {b} bridges')
x=sorted([r for r in S if int(r['bridges'])==1],key=lambda r:float(r['retention']))
ax.plot([float(r['retention']) for r in x],[float(r['within_recoverability']) for r in x],'k--',label='Within community, 1 bridge',alpha=.65)
ax.set(xlabel='Evidence-edge retention probability',ylabel='Fraction of parity claims identified',ylim=(-.03,1.04),xlim=(.18,.82))
ax.legend(loc='lower right',fontsize=7);fig1.tight_layout();fig1.savefig(fig/'recoverability_65536.png');plt.close(fig1)
fig2,ax=plt.subplots(figsize=(6.3,3.15))
for b,sty in [(1,'o-'),(4,'s-'),(16,'^-')]:
    x=sorted([r for r in S if int(r['bridges'])==b],key=lambda r:float(r['retention']))
    ax.plot([float(r['retention']) for r in x],[float(r['free_energy_per_node']) for r in x],sty,label=f'{b} bridges')
ax.set(xlabel='Evidence-edge retention probability',ylabel='Exact hard-constraint free energy / node')
ax.legend(fontsize=8);fig2.tight_layout();fig2.savefig(fig/'free_energy_65536.png');plt.close(fig2)
s=json.load(open('/mnt/data/ER_SCALE_1_CANONICAL/results/evaluation/summary.json'))
m=['presence_logistic','content_logistic','content_hgb','claim_aware_logistic'];lab=['Presence/count','Content logistic','Content boosted','Claim-aware logistic']
y=[next(x['brier'] for x in s['prediction_scores'] if x['method']==k) for k in m]
fig3,ax=plt.subplots(figsize=(6.3,3.1))
ax.barh(lab[::-1],y[::-1]);ax.set_xlabel('Reference-identifiability Brier score (lower better)');ax.set_xlim(0,max(y)*1.15)
for i,v in enumerate(y[::-1]):ax.text(v+.002,i,f'{v:.4f}',va='center',fontsize=8)
fig3.tight_layout();fig3.savefig(fig/'scale1_fixed_brier.png');plt.close(fig3)
order=['strict_receipt','signed_only_exact','content_logistic','claim_aware_logistic','full_exact_reference']
labs=['Strict receipt','Signed-only exact','Content logistic','Claim-aware logistic','Full exact']
sup=[next(x['supported'] for x in s['policies'] if x['method']==k) for k in order]
err=[next(x['unsupported'] for x in s['policies'] if x['method']==k) for k in order]
fig4,ax=plt.subplots(figsize=(6.3,3.0));x=np.arange(len(order));ax.bar(x,sup,label='Supported');ax.bar(x,err,bottom=sup,label='Unsupported');ax.set_xticks(x,labs,rotation=18,ha='right');ax.set_ylabel('Certified claims / 1,920');ax.legend(fontsize=8)
fig4.tight_layout();fig4.savefig(fig/'scale1_fixed_certificates.png');plt.close(fig4)
print([str(x.name) for x in fig.iterdir()])
