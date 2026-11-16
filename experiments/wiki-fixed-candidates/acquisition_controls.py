#!/usr/bin/env python3
"""Post-hoc synthetic evidence-inspection controls.
Archives are frozen. Hidden ledger is consulted ONLY to answer chosen queries and evaluate truth.
"""
from __future__ import annotations
import csv, hashlib, json, os, sys, copy
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
DELAY=Path(os.environ.get('ER_DELAY_ROOT', str(ROOT/'source_data/ER_DELAY_PERCOLATION_1_v011' if (ROOT/'source_data/ER_DELAY_PERCOLATION_1_v011').exists() else Path('/mnt/data/ER_DELAY_PERCOLATION_1_v011'))))
sys.path.insert(0,str(DELAY))
from core import certify

def hashed(*parts):
    return int(hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:16],16)
def options(case):
    return sorted(set(range(len(case['potential_edges'])))-{int(o['edge_idx']) for o in case['observations']})
def fastpath(case):
    g=case['potential_edges'];obs={int(o['edge_idx']):o for o in case['observations']};n=case['n']
    d=[10**8]*n;d[0]=0;prev=[None]*n
    for i,(u,v) in enumerate(g):
        o=obs.get(i)
        if o is not None and o['status']=='failed':continue
        w=1 if o is None else int(o['delay'])
        if d[u]+w<d[v] or (d[u]+w==d[v] and prev[v] is not None and i<prev[v]):
            d[v]=d[u]+w;prev[v]=i
    cur=n-1;path=[]
    while cur!=0 and prev[cur] is not None:
        i=prev[cur];path.append(i);cur=g[i][0]
    return list(reversed(path)) if cur==0 else []


def native_public():
    pub={};private={}
    for line in (DELAY/'results/public/heldout.jsonl').read_text().splitlines():
        d=json.loads(line);pub[d['case_id']]=d
    for line in (DELAY/'results/evaluator_ONLY/native_edge_ledgers.jsonl').read_text().splitlines():
        d=json.loads(line);private[d['world_id']]=d
    return pub,private

def available_edges(case, rate):
    """Deterministic case-independent edge availability, independent of truth and masking."""
    if rate==1.:return set(range(len(case['potential_edges'])))
    return {i for i in range(len(case['potential_edges']))
            if hashed('accessibility-v1',case['world_id'],i)%10000<int(rate*10000)}

def next_query(case, policy, step, available, fixed_plan):
    missing=set(options(case)) & available
    if not missing:return None
    if policy=='random':return min(missing,key=lambda i:hashed('independent',case['world_id'],case['case_id'],i,step))
    if policy=='frozen_path':
        path=[i for i in fixed_plan if i in missing]
        if path:return path[0]
        return min(missing,key=lambda i:hashed('frozenfallback',case['case_id'],i,step))
    if policy=='adaptive_path':
        # Inaccessible unobserved edges are not usable when planning a certifiable YES witness.
        planning=copy.deepcopy(case)
        excluded=set(options(case))-available
        planning['observations'].extend({'edge_idx':i,'status':'failed','delay':None} for i in excluded)
        path=[i for i in fastpath(planning) if i in missing]
        if path:return path[0]
        # If no accessible complete path exists, probing other accessible edges may still
        # help prune alternatives, but cannot guarantee certification.
        path=[i for i in fastpath(case) if i in missing]
        if path:return path[0]
        return min(missing,key=lambda i:hashed('pathfallback',case['case_id'],i,step))
    raise ValueError(policy)

def run():
    pub,priv=native_public();cases=sorted(c for c in pub if c.endswith('_M00') or c.endswith('_M04'))
    assert len(cases)==320
    rows=[]
    for cidx,cid in enumerate(cases):
        base=pub[cid];native=priv[base['world_id']];assert len(native['private_edges'])==len(base['potential_edges'])
        for rate in [1.,.5,.25]:
            available=available_edges(base,rate)
            for policy in ['random','frozen_path','adaptive_path']:
                case=copy.deepcopy(base)
                first=fastpath(case);fixed_plan=[i for i in first if i in options(case)]
                for k in range(9):
                    cert=certify(case);factual=native['truth']
                    if cert=='YES':assert factual==1
                    if cert=='NO':assert factual==0
                    rows.append(dict(case_id=cid,world_id=base['world_id'],n=base['n'],mask_kind=base['mask_kind'],
                       availability=rate,policy=policy,budget=k,cert=cert,correct=int(cert!='UNKNOWN'),
                       queried=len(case['observations'])-len(base['observations']),available_unknown_initial=len(available&set(options(base)))))
                    if cert!='UNKNOWN':
                        for remaining in range(k+1,9):
                            rows.append(dict(case_id=cid,world_id=base['world_id'],n=base['n'],mask_kind=base['mask_kind'],
                               availability=rate,policy=policy,budget=remaining,cert=cert,correct=1,
                               queried=len(case['observations'])-len(base['observations']),available_unknown_initial=len(available&set(options(base)))))
                        break
                    if k==8:break
                    idx=next_query(case,policy,k,available,fixed_plan)
                    if idx is None:
                        for remaining in range(k+1,9):
                            rows.append(dict(case_id=cid,world_id=base['world_id'],n=base['n'],mask_kind=base['mask_kind'],
                               availability=rate,policy=policy,budget=remaining,cert='UNKNOWN',correct=0,
                               queried=len(case['observations'])-len(base['observations']),available_unknown_initial=len(available&set(options(base)))))
                        break
                    u,v,live,delay=native['private_edges'][idx]
                    assert [u,v]==case['potential_edges'][idx]
                    case['observations'].append({'edge_idx':idx,'status':'live' if live else 'failed','delay':delay})
        if cidx%80==0:print('processed',cidx,'/',len(cases),flush=True)
    d=pd.DataFrame(rows);assert len(d)==320*3*3*9
    assert d.groupby(['case_id','policy','availability']).correct.apply(lambda s:(s.diff().fillna(0)>=0).all()).all()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    d.to_csv(out/'acquisition_additional_controls_EVALUATOR_ONLY.csv',index=False)
    agg=d.groupby(['availability','policy','budget']).agg(n=('correct','size'),identified=('correct','sum'),
        mean_queries=('queried','mean'),mean_available_missing=('available_unknown_initial','mean')).reset_index()
    agg.to_csv(out/'acquisition_control_rates.csv',index=False)
    # Paired bootstrap: retain the two masks per world together.
    boot=[];rng=np.random.default_rng(11529)
    for rate in [1.,.5,.25]:
      t=d[(d.availability==rate)&(d.budget==8)]
      pv=t.pivot(index=['world_id','case_id'],columns='policy',values='correct')
      for aa,bb in [('adaptive_path','random'),('adaptive_path','frozen_path'),('frozen_path','random')]:
        z=(pv[aa]-pv[bb]).groupby(level=0).agg(['sum','count']);vals=z['sum'].to_numpy();den=z['count'].to_numpy();sel=rng.integers(0,len(vals),(5000,len(vals)))
        bs=vals[sel].sum(axis=1)/den[sel].sum(axis=1)
        boot.append(dict(availability=rate,comparator=f'{aa}-{bb}',delta_mean=float((pv[aa]-pv[bb]).mean()),
                         ci_lower=float(np.quantile(bs,.025)),ci_upper=float(np.quantile(bs,.975))))
    pd.DataFrame(boot).to_csv(out/'acquisition_control_paired_bootstrap.csv',index=False)
    print(agg[(agg.budget==8)][['availability','policy','identified','n','mean_queries']].to_string(index=False))
    print(pd.DataFrame(boot).to_string(index=False))
if __name__=='__main__':run()
