#!/usr/bin/env python3
"""Draw report figures from the exact output CSVs; no random draws."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS={
'emergent_stochastic':'Emergent, stochastic target',
'isotropic_stochastic_control':'Isotropic stochastic control',
'declining_path_stochastic_control':'Declining-path control',
'emergent_deterministic':'Emergent, deterministic target',
'all_deterministic_control':'All deterministic control',
'all_random_negative_control':'All random (negative control)',
}

def run(root):
    root=Path(root);fdir=root/'figures';fdir.mkdir(exist_ok=True)
    mr=pd.read_csv(root/'results'/'causal_power_by_model.csv')
    cv=pd.read_csv(root/'results'/'recoverability_curves_exact.csv')
    xs=np.arange(3);tags=['Micro: 8','Meso: 4','Macro: 2']
    fig,ax=plt.subplots(figsize=(9.2,5.4))
    for _,r in mr.iterrows():
        m=r['model']
        v=[r[f'ce2_primitives_{s}'] for s in ('micro_8','meso_4','macro_2')]
        ax.plot(xs,v,marker='o',lw=2,label=LABELS[m])
    ax.set_xticks(xs,tags);ax.set_ylabel('CE 2.0 sufficiency + necessity − 1')
    ax.set_ylim(-.04,1.06);ax.set_title('Causal primitives across the predeclared valid path')
    ax.grid(alpha=.3);ax.legend(fontsize=8,ncol=2)
    fig.tight_layout();fig.savefig(fdir/'ce2_causal_power_path.png',dpi=180);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9.2,5.4))
    subset=cv[cv.scheme=='independent']
    # One from each pair is a coincident curve; explicitly annotate this in legend.
    for m,ls in [('emergent_stochastic','-'),('declining_path_stochastic_control','--'),('emergent_deterministic','-.'),('all_random_negative_control',':')]:
        ss=subset[subset.model==m]
        ax.plot(ss.retention_probability,ss.recovery_macro_2,marker='o',linestyle=ls,lw=2,label=LABELS[m])
    ax.set_xlabel('Independent retention probability p')
    ax.set_ylabel('Exact probability macro claim is identifiable')
    ax.set_ylim(-.04,1.05);ax.set_title('Target-matched causal systems have identical recoverability')
    ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(fdir/'macro_recoverability_independent.png',dpi=180);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9.2,5.4))
    names=['emergent_deterministic','all_deterministic_control','emergent_stochastic','declining_path_stochastic_control']
    for m in names:
        for sc,ls in [('independent','-'),('grouped_by_component','--')]:
            ss=cv[(cv.model==m)&(cv.scheme==sc)]
            ax.plot(ss.retention_probability,ss.recovery_macro_2,linestyle=ls,alpha=.85,
                    label=LABELS[m]+(' (indep)' if sc=='independent' else ' (grouped)'))
    ax.set_xlabel('Evidence retention p');ax.set_ylabel('Exact macro identifiability')
    ax.set_ylim(-.03,1.03);ax.set_title('Evidence geometry changes the recoverability curve')
    ax.grid(alpha=.3);ax.legend(fontsize=7,ncol=2)
    fig.tight_layout();fig.savefig(fdir/'mask_mechanism_comparison.png',dpi=180);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,5.4))
    subset=cv[(cv.scheme=='independent')&(np.isclose(cv.retention_probability,.5))]
    vals=mr.set_index('model')['ce2_net_delta_on_predeclared_path']
    short={
        'emergent_stochastic':'Emergent stochastic',
        'isotropic_stochastic_control':'Isotropic control',
        'declining_path_stochastic_control':'Declining control',
        'emergent_deterministic':'Emergent deterministic',
        'all_deterministic_control':'All deterministic',
        'all_random_negative_control':'All random',
    }
    shifts={
        'emergent_stochastic':(5,10),
        'isotropic_stochastic_control':(5,11),
        'declining_path_stochastic_control':(5,11),
        'emergent_deterministic':(-138,10),
        'all_deterministic_control':(5,11),
        'all_random_negative_control':(5,-18),
    }
    for _,r in subset.iterrows():
        m=r['model'];ax.scatter(vals[m],r.recovery_macro_2,s=75)
        ax.annotate(short[m],(vals[m],r.recovery_macro_2),xytext=shifts[m],textcoords='offset points',fontsize=9)
    ax.set_xlabel('Causal primitive change on fixed 8→4→2 path')
    ax.set_ylabel('Exact macro claim identification at p=0.5')
    ax.set_ylim(0,1.08);ax.set_xlim(-.19,.94);ax.set_title('Causal change does not determine claim recoverability')
    ax.grid(alpha=.3)
    fig.tight_layout();fig.savefig(fdir/'causal_gain_vs_recoverability.png',dpi=180);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();run(a.root)
