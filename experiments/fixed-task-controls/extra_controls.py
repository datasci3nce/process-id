#!/usr/bin/env python3
"""Additional exploratory/retrospective sensitivity checks, NOT frozen comparisons."""
from pathlib import Path
import sys,json,hashlib,os
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE/'results'
DR=Path(os.environ.get('ER_DELAY_ROOT', HERE/'inputs/ER_DELAY_PERCOLATION_1_v011' if (HERE/'inputs/ER_DELAY_PERCOLATION_1_v011').exists() else '/mnt/data/ER_DELAY_PERCOLATION_1_v011'))
sys.path.insert(0,str(HERE));from run_audit import loadpublic,options,fastpath,choose_query,certify,hashed,wbootstrap
sys.path.insert(0,str(DR));from core import montecarlo_prob,stable_seed

def acquisition_cis():
 a=pd.read_csv(OUT/'acquisition_paths_EVALUATOR_ONLY.csv')
 out=[]
 for k in [1,2,3,5,8]:
  z=a[a.k==k].pivot(index=['world_id','case_id','n','mask_kind'],columns='policy',values='identified').reset_index()
  for mask_kind,small in [('both',z)]+[(m,z[z.mask_kind==m]) for m in sorted(z.mask_kind.unique())]:
   for method in ['optimistic_path','cut_sensitivity']:
    x=small[method].to_numpy()-small['random'].to_numpy()
    pair=dict(k=k,mask_kind=mask_kind,method=method,n_cases=len(small),identified_method=int(small[method].sum()),identified_random=int(small['random'].sum()),diff=float(x.mean()))
    g=small.assign(delta=x).groupby('world_id').delta.agg(['sum','count'])
    vals=g['sum'].to_numpy();cnt=g['count'].to_numpy();rng=np.random.default_rng(1001+k)
    ids=rng.integers(0,len(vals),size=(3500,len(vals)))
    bs=vals[ids].sum(axis=1)/cnt[ids].sum(axis=1)
    pair['bootstrap_ci95']=np.quantile(bs,[.025,.975]).tolist();out.append(pair)
 pd.DataFrame(out).to_csv(OUT/'acquisition_paired_world_ci.csv',index=False)
 for size,part in a[a.k==8].groupby('n'):
  print('size',size,part.groupby('policy').identified.mean().to_dict())
 print(pd.DataFrame(out).query("mask_kind=='both' and k==8").to_string(index=False))

def random_replications(cases):
 native={}
 for s in (DR/'results/evaluator_ONLY/native_edge_ledgers.jsonl').read_text().splitlines():
  a=json.loads(s);native[a['world_id']]=a
 ids=sorted([c for c in cases if c.endswith('_M00') or c.endswith('_M04')]);rep=[]
 for seed in range(30):
  for cid in ids:
   c=json.loads(json.dumps(cases[cid]));world=native[c['world_id']]
   for k in range(9):
    if k==8 or certify(c)!='UNKNOWN':break
    opts=options(c)
    if not opts:break
    idx=min(opts,key=lambda z:hashed('random_sensitivity',seed,cid,k,z))
    u,v,live,delay=world['private_edges'][idx]
    c['observations'].append({'edge_idx':idx,'status':'live' if live else 'failed','delay':delay})
   rep.append(dict(seed=seed,case_id=cid,world_id=c['world_id'],n=c['n'],mask_kind=c['mask_kind'],identified=int(certify(c)!='UNKNOWN')))
 rr=pd.DataFrame(rep);rr.to_csv(OUT/'random_acquisition_30seeds.csv',index=False)
 s=rr.groupby('seed').identified.mean()
 print('random 30 seeds overall min/mean/max/std',float(s.min()),float(s.mean()),float(s.max()),float(s.std()))
 return rr

def mc_sensitivity(cases):
 fit=json.loads((DR/'results/fit_parameters.json').read_text())
 q0=fit['q_from_development_private_training_records'];dist=np.array([fit['delay_prob_from_development_private_training_records'][str(t)] for t in (1,2,4,6)])
 original=pd.read_csv(OUT/'scored_reanalyses_EVALUATOR_ONLY.csv')
 unknown=original[original.exact_now=='UNKNOWN'].copy()
 # Preselected sensitivity settings, not tuned on heldout labels.
 scenarios=[('dev_prior_768',q0,dist,768),('q_half_768',.50,dist,768),('q_high_768',.85,dist,768),('uniform_delay_768',q0,np.ones(4)/4,768)]
 result=[]
 for i,row in unknown.iterrows():
  c=cases[row.case_id]
  rec=dict(case_id=row.case_id,world_id=row.world_id,label_actual=row.label_actual,original_mc_96=row.mc_event_posterior)
  for name,q,d,n in scenarios:
   rec[name]=montecarlo_prob(c,n,stable_seed('exploratory',row.case_id,name),float(q),d)
  result.append(rec)
 d=pd.DataFrame(result);d.to_csv(OUT/'unresolved_mc_prior_sensitivity_EVALUATOR_ONLY.csv',index=False)
 scores={name:float(np.mean((d[name]-d.label_actual)**2)) for name,_,_,_ in scenarios}
 scores['original_mc_96']=float(np.mean((d.original_mc_96-d.label_actual)**2))
 dump={'scenario':scores,'n_cases':len(d),'prior_source':'Original fitted development-world prior for dev_prior_768; others are untuned post-hoc sensitivity settings','MC_estimation_noise':'Each MC probability approximates one fixed scenario posterior; low draw count causes variance; not a full posterior validation'}
 (OUT/'mc_sensitivity_summary.json').write_text(json.dumps(dump,indent=2)+'\n')
 print('MC sensitivity',dump)

def main():
 cases,_=loadpublic();acquisition_cis();random_replications(cases);mc_sensitivity(cases)
if __name__=='__main__':main()
