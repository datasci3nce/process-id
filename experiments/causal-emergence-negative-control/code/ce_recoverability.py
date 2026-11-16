#!/usr/bin/env python3
"""CE–Recoverability-1: exact finite Markov causal-power and evidence-mask audit.

Unmodified, declarative 3-bit product transition mechanisms and uniform interventions.
Primary CE metric: sufficiency + necessity - 1, ported from the official
PyMergence CE2.0 causal-primitives implementation. Sensitivity metric:
effectiveness = uniform-input mutual information / log2(number of states).
Report PREDECLARED MICRO->MESO->MACRO PATH, not global CE2.0 optimization.

All exact recoverability values sum the full 8**3 trajectory distribution. Masks are
observation restrictions, never interventions on the transition probabilities.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import pathlib
import numpy as np
import pandas as pd

Q_SPECS = {
    'emergent_stochastic': (0.92, 0.50, 0.50),
    'isotropic_stochastic_control': (0.92, 0.92, 0.92),
    'declining_path_stochastic_control': (0.92, 1.00, 1.00),
    'emergent_deterministic': (1.00, 0.50, 0.50),
    'all_deterministic_control': (1.00, 1.00, 1.00),
    'all_random_negative_control': (0.50, 0.50, 0.50),
}
P_VALUES = (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0)
SCALES = ('micro_8','meso_4','macro_2')
CLAIMS = ('micro_8','meso_4','macro_2')

STATES=np.arange(8,dtype=np.int16)
BITS=np.array([[(int(x)>>2)&1,(int(x)>>1)&1,int(x)&1] for x in STATES],dtype=np.int8)
HISTORIES=np.array(list(itertools.product(range(8), repeat=3)),dtype=np.int16)
HISTORY_BITS=BITS[HISTORIES].reshape(-1,9)
CLAIM_VALUES={
    'micro_8':HISTORIES[:,2].astype(np.int16),
    'meso_4':(HISTORIES[:,2]//2).astype(np.int16),
    'macro_2':(HISTORIES[:,2]//4).astype(np.int16),
}
GROUPS={
    'micro_8':np.arange(8,dtype=np.int16),
    'meso_4':(np.arange(8)//2).astype(np.int16),
    'macro_2':(np.arange(8)//4).astype(np.int16)
}
GROUP_MASKS=tuple(sum(1<<(t*3+j) for t in range(3)) for j in range(3))
NUISANCE_MASKS=tuple((i & 0b001001001)==0 for i in range(512))


def binary_info(q:float)->float:
    if q in (0.,1.):return 1.
    if q==0.5:return 0.
    return 1. + q*math.log2(q) + (1-q)*math.log2(1-q)


def transition_matrix(q):
    arr=np.ones((8,8),dtype=float)
    for j,prob in enumerate(q):
        arr*=np.where(BITS[:,j,None]==BITS[None,:,j],prob,1-prob)
    assert np.allclose(arr.sum(axis=1),1.)
    return arr


def aggregate_transition(P,group):
    gmax=int(group.max())+1
    agg=np.zeros((gmax,gmax),dtype=float)
    for i in range(gmax):
        sub=P[np.flatnonzero(group==i)]
        mapped=np.zeros((len(sub),gmax),dtype=float)
        for j in range(gmax):
            mapped[:,j]=sub[:,group==j].sum(axis=1)
        # Strong lumpability: all member states must induce identical aggregate successors.
        if np.max(np.abs(mapped-mapped[0]))>2e-13:
            raise AssertionError('Invalid coarse graining (not strongly lumpable)')
        agg[i]=mapped[0]
    assert np.allclose(agg.sum(axis=1),1.)
    return agg


def causal_power(P):
    """Normalized mutual information I(do(X~uniform);Y)/log2(n); PyMergence effectiveness."""
    n=P.shape[0]
    if n<2:return 0.0
    output=P.mean(axis=0)
    def ent(v):
        a=np.asarray(v)
        a=a[a>0]
        return float(-np.sum(a*np.log2(a)))
    h_out=ent(output)
    h_cond=sum(ent(row) for row in P)/n
    return float((h_out-h_cond)/math.log2(n))


def ce2_causal_primitives(P):
    """CE2.0 sufficiency + necessity - 1 for a uniform intervention distribution.

    Ported transparently from official PyMergence StochasticMatrix.suff_plus_nec
    implementation: avg_suff = E[P(e|c)]; avg_nec = E[1 -
    P(e|do(c' != c) uniform over n-1 alternatives)].
    """
    n=len(P)
    avg_suff=float(np.sum(P*P)/n)
    col_sums=P.sum(axis=0)
    necessity=1. - (col_sums[None,:] - P)/(n-1)
    avg_nec=float(np.sum(P*necessity)/n)
    return avg_suff+avg_nec-1.


def trajectory_weights(P):
    w=P[HISTORIES[:,0],HISTORIES[:,1]]*P[HISTORIES[:,1],HISTORIES[:,2]]/8.
    assert abs(w.sum()-1)<2e-13
    return w


def mask_statistics(weights,mask):
    mask=int(mask)
    observed=np.array([(mask>>i)&1 for i in range(9)],dtype=np.int64)
    value=HISTORY_BITS@ (observed * (1<<np.arange(9,dtype=np.int64)))
    total=np.bincount(value,weights=weights,minlength=512)
    positive=total>1e-13
    out={'mask':mask,'retained':int(observed.sum()),'observed_macro_at_t2':bool(observed[6])}
    for claim,v in CLAIM_VALUES.items():
        nv=int(v.max())+1
        masses=np.bincount(value+512*v,weights=weights,minlength=512*nv).reshape(nv,512)
        support=(masses>1e-13).sum(axis=0)
        recoverable=float(total[(support==1)&positive].sum())
        cond_entropy=np.zeros(512)
        for row in masses:
            prob=np.divide(row,total,out=np.zeros_like(row),where=positive)
            ok=prob>0
            cond_entropy[ok]-=prob[ok]*np.log2(prob[ok])
        out[f'recovery_{claim}']=recoverable
        out[f'entropy_{claim}']=float(np.sum(total*cond_entropy))
        if claim=='macro_2':
            pr=np.divide(masses[1],total,out=np.zeros(512),where=positive)
            out['bayes_brier_macro_2']=float(np.sum(total*pr*(1-pr)))
    # If no evidence, no claim identifiable; if all evidence, all claims identifiable.
    return out


def masks_for_scheme(scheme):
    if scheme=='independent':return range(512)
    if scheme=='grouped_by_component':
        return [sum(GROUP_MASKS[j] for j in range(3) if (grp>>j)&1) for grp in range(8)]
    if scheme=='macro_channel_blind':
        return [mask for mask in range(512) if (mask & GROUP_MASKS[0])==0]
    raise ValueError(scheme)


def mask_probability(mask,p,scheme):
    if scheme=='independent':
        k=int(mask).bit_count(); n=9
    elif scheme=='grouped_by_component':
        k=sum(bool(mask&g) for g in GROUP_MASKS);n=3
    elif scheme=='macro_channel_blind':
        k=int(mask).bit_count();n=6
    else:raise ValueError(scheme)
    if p==0:return float(k==0)
    if p==1:return float(k==n)
    return float(p**k*(1-p)**(n-k))


def calculate(output_dir:pathlib.Path, p_values=P_VALUES):
    output_dir=pathlib.Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    mechanism_rows=[]; mask_rows=[]; curve_rows=[]
    for name,q in Q_SPECS.items():
        P=transition_matrix(q);w=trajectory_weights(P)
        powers={scale:causal_power(aggregate_transition(P,g)) for scale,g in GROUPS.items()}
        ce2={scale:ce2_causal_primitives(aggregate_transition(P,g)) for scale,g in GROUPS.items()}
        rec={'model':name,'q_macro':q[0],'q_nuisance_1':q[1],'q_nuisance_2':q[2],
             'valid_strong_lumpability':True,'causal_power_micro_8':powers['micro_8'],
             'causal_power_meso_4':powers['meso_4'],'causal_power_macro_2':powers['macro_2'],
             'delta_cp_8_to_4':powers['meso_4']-powers['micro_8'],
             'delta_cp_4_to_2':powers['macro_2']-powers['meso_4'],
             'predeclared_path_gain':powers['macro_2']-powers['micro_8'],
             'ce2_primitives_micro_8':ce2['micro_8'],
             'ce2_primitives_meso_4':ce2['meso_4'],
             'ce2_primitives_macro_2':ce2['macro_2'],
             'ce2_delta_8_to_4':ce2['meso_4']-ce2['micro_8'],
             'ce2_delta_4_to_2':ce2['macro_2']-ce2['meso_4'],
             'ce2_net_delta_on_predeclared_path':ce2['macro_2']-ce2['micro_8'],
             'ce2_path_nondecreasing':bool(ce2['micro_8']<=ce2['meso_4']+1e-12 and ce2['meso_4']<=ce2['macro_2']+1e-12),
             'analytic_power_micro':sum(binary_info(x) for x in q)/3,
             'analytic_power_macro':binary_info(q[0])}
        assert abs(rec['analytic_power_micro']-powers['micro_8'])<1e-12
        assert abs(rec['analytic_power_macro']-powers['macro_2'])<1e-12
        mechanism_rows.append(rec)
        for scheme in ('independent','grouped_by_component','macro_channel_blind'):
            rows=[]
            for mask in masks_for_scheme(scheme):
                stats=mask_statistics(w,mask)
                r={'model':name,'scheme':scheme,**stats}
                rows.append(r);mask_rows.append(r)
            for p in p_values:
                probs=np.array([mask_probability(r['mask'],p,scheme) for r in rows])
                assert abs(probs.sum()-1)<1e-12,(name,scheme,p,probs.sum())
                line={'model':name,'scheme':scheme,'retention_probability':p,
                      'expected_records':sum(rr['retained']*v for rr,v in zip(rows,probs))}
                for metric in ('recovery_micro_8','recovery_meso_4','recovery_macro_2',
                               'entropy_micro_8','entropy_meso_4','entropy_macro_2',
                               'bayes_brier_macro_2'):
                    line[metric]=float(np.dot(probs,[r[metric] for r in rows]))
                curve_rows.append(line)
    mr=pd.DataFrame(mechanism_rows); mk=pd.DataFrame(mask_rows);cv=pd.DataFrame(curve_rows)
    mr.to_csv(output_dir/'causal_power_by_model.csv',index=False)
    mk.to_csv(output_dir/'per_mask_exact.csv',index=False)
    cv.to_csv(output_dir/'recoverability_curves_exact.csv',index=False)
    meta={
      'title':'CE–Recoverability 1, exact small-state factorial test',
      'models':Q_SPECS,
      'timesteps':3,'micro_states':8,'observation_channels':9,
      'observation_schemes':['independent','grouped_by_component','macro_channel_blind'],
      'total_mask_rows':len(mask_rows),'probability_measure':'uniform initial microstate, product Markov transition',
      'causal_power_measure':'Both PyMergence CE2.0 suff_plus_nec minus 1 (primary), and normalized intervention mutual information/effectiveness (sensitivity)',
      'coarse_graining_validity':'strong lumpability exact (row aggregate equality)',
      'claims':CLAIMS,
      'support_rule':'strictly positive compatible-history mass, no confidence threshold',
      'primary_comparison':'emergent_stochastic versus declining_path_stochastic_control and isotropic_stochastic_control; target-bit TPM and observation process held identical',
      'not_claimed':['full CE2.0 lattice search','causal emergence universal theorem','real agent transfer','measured DDE dynamics']}
    (output_dir/'DESIGN.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    return mr,mk,cv


def check_results(mr,mk,cv):
    def val(model,scheme,p,col):
        v=cv[(cv.model==model)&(cv.scheme==scheme)&(np.isclose(cv.retention_probability,p))]
        assert len(v)==1
        return float(v.iloc[0][col])
    for p in P_VALUES:
        for scheme in ('independent','grouped_by_component','macro_channel_blind'):
            for m,n in [('emergent_stochastic','isotropic_stochastic_control'),
                        ('emergent_stochastic','declining_path_stochastic_control'),
                        ('emergent_deterministic','all_deterministic_control')]:
                for col in ('recovery_macro_2','entropy_macro_2','bayes_brier_macro_2'):
                    assert abs(val(m,scheme,p,col)-val(n,scheme,p,col))<1e-12,(m,scheme,p,col)
            if scheme=='independent':
                assert abs(val('emergent_stochastic',scheme,p,'recovery_macro_2')-p)<1e-12
                assert abs(val('emergent_deterministic',scheme,p,'recovery_macro_2')-(1-(1-p)**3))<1e-12
                assert abs(val('all_random_negative_control',scheme,p,'recovery_micro_8')-p**3)<1e-12
            if scheme=='grouped_by_component':
                for model in Q_SPECS:
                    assert abs(val(model,scheme,p,'recovery_macro_2')-p)<1e-12
            if scheme=='macro_channel_blind':
                for model in Q_SPECS:
                    assert abs(val(model,scheme,p,'recovery_macro_2'))<1e-12
    assert mr.set_index('model').loc['emergent_stochastic','predeclared_path_gain']>0.35
    assert abs(mr.set_index('model').loc['isotropic_stochastic_control','predeclared_path_gain'])<1e-12
    assert mr.set_index('model').loc['emergent_stochastic','ce2_net_delta_on_predeclared_path']>0.5
    assert mr.set_index('model').loc['declining_path_stochastic_control','ce2_net_delta_on_predeclared_path']<0
    assert abs(mr.set_index('model').loc['all_deterministic_control','ce2_net_delta_on_predeclared_path'])<1e-12
    assert mk.groupby(['model','scheme']).size().to_dict()=={
        (model,scheme):count for model in Q_SPECS
        for scheme,count in [('independent',512),('grouped_by_component',8),('macro_channel_blind',64)]}
    return {'passed':True,'checks':['analytic micro/macro causal power','validity of strong lumpability',
                                    'matching macroscale recoverability and Brier',
                                    'independent observed-bit formulas','grouped-bit formulas','macro-blind negative control',
                                    'zero-CE random negative control','all masks retained in denominators'],
            'rows':{'models':len(mr),'mask_rows':len(mk),'curve_rows':len(cv)}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default=str(pathlib.Path(__file__).resolve().parents[1]/'results'))
    a=parser.parse_args()
    out=pathlib.Path(a.output)
    mr,mk,cv=calculate(out)
    result=check_results(mr,mk,cv)
    (out/'VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Exact causal-power and recoverability analysis complete:',result)
    print('\nCE2 sufficiency + necessity -1 along predeclared path:')
    print(mr[['model','ce2_primitives_micro_8','ce2_primitives_meso_4','ce2_primitives_macro_2','ce2_net_delta_on_predeclared_path']].to_string(index=False,float_format=lambda x:f'{x:.6f}'))
    print('\nNormalized intervention information/effectiveness (sensitivity):')
    print(mr[['model','causal_power_micro_8','causal_power_meso_4','causal_power_macro_2','predeclared_path_gain']].to_string(index=False,float_format=lambda x:f'{x:.6f}'))
    print('\nIndependent p=0.5:')
    print(cv[(cv.scheme=='independent')&(np.isclose(cv.retention_probability,.5))][['model','recovery_micro_8','recovery_meso_4','recovery_macro_2','bayes_brier_macro_2']].to_string(index=False,float_format=lambda x:f'{x:.6f}'))

if __name__=='__main__':main()
