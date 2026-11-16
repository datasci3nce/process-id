#!/usr/bin/env python3
"""Post-sprint, no retraining. Saved public cases and original evaluator labels are kept separate until scoring."""
from __future__ import annotations
import os,sys,json,hashlib,math,itertools,collections
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
DR=Path(os.environ.get('ER_DELAY_ROOT', HERE/'inputs/ER_DELAY_PERCOLATION_1_v011' if (HERE/'inputs/ER_DELAY_PERCOLATION_1_v011').exists() else '/mnt/data/ER_DELAY_PERCOLATION_1_v011'))
WR=HERE/'wiki_saved'
sys.path.insert(0,str(DR))
from core import certify,shortest,build_edge_views
ROOT=HERE/'results';ROOT.mkdir(exist_ok=True)

def dump(obj,p):
 (ROOT/p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def loadpublic():
 cases={}
 for s in (DR/'results/public/heldout.jsonl').read_text().splitlines():
  c=json.loads(s);assert not {'label_actual','private_edges','truth'}&set(c)
  cases[c['case_id']]=c
 pred=pd.read_csv(DR/'results/public/observed_only_predictions.csv')
 pred=pred[pred.split=='heldout'].copy();assert len(pred)==len(cases)==1600
 pred['exact_now']=[certify(cases[i]) for i in pred.case_id]
 assert (pred.exact_now==pred.reference_cert).all()
 return cases,pred

def wbootstrap(data,keyA,keyB,boot=3500):
 d=data.copy();d['delta']=(d[keyA]-d.label_actual)**2-(d[keyB]-d.label_actual)**2
 grouped=d.groupby('world_id').delta.agg(['sum','count'])
 vals=grouped['sum'].to_numpy();den=grouped['count'].to_numpy()
 rng=np.random.default_rng(44901);indexes=rng.integers(0,len(vals),(boot,len(vals)))
 out=vals[indexes].sum(axis=1)/den[indexes].sum(axis=1)
 return {'delta_mean':float(d.delta.mean()),'ci95':list(map(float,np.quantile(out,[.025,.975]))),'worlds':len(vals),'cases':len(d)}

def calcA(cases,pr):
 data=pr.copy()
 truth=pd.read_csv(DR/'results/evaluator_ONLY/heldout_scored.csv')[['case_id','world_id','label_actual']]
 data=data.merge(truth,on=['case_id','world_id'],validate='one_to_one')
 names=['static_logistic','timed_logistic','dde_delayed','dde_no_delay','mc_event_posterior']
 for k in names:
  data['gate_'+k]=np.where(data.exact_now=='YES',1.,np.where(data.exact_now=='NO',0.,data[k]))
 assert (data.loc[data.exact_now=='YES','label_actual']==1).all()
 assert (data.loc[data.exact_now=='NO','label_actual']==0).all()
 subsets={'all':data,'unknown':data[data.exact_now=='UNKNOWN'],'certified':data[data.exact_now!='UNKNOWN'],
 'no_duplicate_100pct':data[~((data.mask_kind=='source_correlated')&(data.retention==1.))]}
 def brier(df,k):return float(np.mean((df[k]-df.label_actual)**2))
 def logloss(df,k):
  p=np.clip(df[k].to_numpy(float),1e-8,1-1e-8);y=df.label_actual.to_numpy(float)
  return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
 score=[]
 for sub,df in subsets.items():
  for k in names+['gate_'+k for k in names]:
   score.append(dict(subset=sub,method=k,n=len(df),worlds=df.world_id.nunique(),brier=brier(df,k),logloss=logloss(df,k)))
 pd.DataFrame(score).to_csv(ROOT/'prediction_scores.csv',index=False)
 comparisons={
   'gated_mc_minus_gated_static_all':wbootstrap(data,'gate_mc_event_posterior','gate_static_logistic'),
   'gated_mc_minus_gated_static_unknown':wbootstrap(subsets['unknown'],'gate_mc_event_posterior','gate_static_logistic'),
   'gated_timed_minus_gated_static_unknown':wbootstrap(subsets['unknown'],'gate_timed_logistic','gate_static_logistic'),
   'gated_dde_minus_gated_static_unknown':wbootstrap(subsets['unknown'],'gate_dde_delayed','gate_static_logistic'),
   'gated_mc_minus_gated_timed_unknown':wbootstrap(subsets['unknown'],'gate_mc_event_posterior','gate_timed_logistic'),
  }
 dump(comparisons,'prediction_paired_intervals.json')
 data.to_csv(ROOT/'scored_reanalyses_EVALUATOR_ONLY.csv',index=False)
 print('A all brier:',pd.DataFrame(score).query("subset=='all'")[['method','brier']].to_string(index=False));return data

def hashed(*a):return int.from_bytes(hashlib.sha256('|'.join(map(str,a)).encode()).digest()[:8],'big')
def options(case):return sorted(set(range(len(case['potential_edges'])))-{int(o['edge_idx']) for o in case['observations']})
def fastpath(case):
 g=case['potential_edges'];obs={int(o['edge_idx']):o for o in case['observations']}
 n=case['n'];dist=[10**8]*n;dist[0]=0;prev=[None]*n
 for idx,(u,v) in enumerate(g):
  o=obs.get(idx)
  if o is not None and o['status']=='failed':continue
  w=1 if o is None else int(o['delay']);d=dist[u]+w
  if d<dist[v] or (d==dist[v] and prev[v] is not None and idx<prev[v]):
   dist[v]=d;prev[v]=idx
 cur=n-1;path=[]
 while cur!=0 and prev[cur] is not None:
  idx=prev[cur];path.append(idx);cur=g[idx][0]
 if cur: return []
 return list(reversed(path))
def choose_query(case,policy,step):
 opts=options(case)
 if not opts:return None
 if policy=='random': return min(opts,key=lambda z:hashed('independent',case['world_id'],case['case_id'],z,step))
 if policy=='optimistic_path':
  path=fastpath(case)
  missing=set(opts);choices=[z for z in path if z in missing]
  if choices:return choices[0]
  return min(opts,key=lambda z:hashed('pathfallback',case['case_id'],z,step))
 if policy=='cut_sensitivity':
  base=shortest(case['n'],build_edge_views(case)[1]);scores=[]
  for idx in opts:
   u,v=case['potential_edges'][idx]
   potential=build_edge_views(case)[1]
   # 'unknown' edge has w=1; drop it to test optimistic path sensitivity
   removal=[(a,b,w) for a,b,w in potential if (a,b)!=(u,v)]
   after=shortest(case['n'],removal)
   score=min(after,10**5)-min(base,10**5)
   scores.append((-score,hashed('cut',case['case_id'],idx),idx))
  return min(scores)[2]
 raise ValueError(policy)

def calcB(cases):
 native={}
 for s in (DR/'results/evaluator_ONLY/native_edge_ledgers.jsonl').read_text().splitlines():
  z=json.loads(s);native[z['world_id']]=z
 ids=sorted([c for c in cases if c.endswith('_M00') or c.endswith('_M04')]);assert len(ids)==320
 pol=['random','optimistic_path','cut_sensitivity'];rows=[]
 for cid in ids:
  original=cases[cid];world=native[original['world_id']]
  assert len(world['private_edges'])==len(original['potential_edges'])
  for method in pol:
   case=json.loads(json.dumps(original))
   for k in range(9):
    cert=certify(case)
    rows.append(dict(case_id=cid,world_id=original['world_id'],n=original['n'],mask_kind=original['mask_kind'],policy=method,k=k,cert=cert,identified=int(cert!='UNKNOWN'),factual_truth=world['truth'],n_observed=len(case['observations'])))
    if k==8 or cert!='UNKNOWN':
     # Still score as identified under all remaining budget levels (policy stops once solved).
     for remaining in range(k+1,9):
      rows.append(dict(case_id=cid,world_id=original['world_id'],n=original['n'],mask_kind=original['mask_kind'],policy=method,k=remaining,cert=cert,identified=int(cert!='UNKNOWN'),factual_truth=world['truth'],n_observed=len(case['observations'])))
     break
    idx=choose_query(case,method,k)
    if idx is None:
     for remaining in range(k+1,9):
      rows.append(dict(case_id=cid,world_id=original['world_id'],n=original['n'],mask_kind=original['mask_kind'],policy=method,k=remaining,cert=cert,identified=0,factual_truth=world['truth'],n_observed=len(case['observations'])))
     break
    u,v,live,delay=world['private_edges'][idx]
    assert [u,v]==case['potential_edges'][idx]
    case['observations'].append({'edge_idx':idx,'status':'live' if live else 'failed','delay':delay})
    # Status and delay released to the algorithm only AFTER public selection.
   
 a=pd.DataFrame(rows)
 assert len(a)==320*3*9 and not a.duplicated(['case_id','policy','k']).any()
 assert a.groupby(['case_id','policy']).identified.apply(lambda x:(x.diff().fillna(0)>=0).all()).all()
 assert (((a.cert=='YES')&(a.factual_truth==0))|((a.cert=='NO')&(a.factual_truth==1))).sum()==0
 a.to_csv(ROOT/'acquisition_paths_EVALUATOR_ONLY.csv',index=False)
 agg=a.groupby(['mask_kind','policy','k']).agg(rate=('identified','mean'),identified=('identified','sum'),n=('identified','size'),mean_inspected=('n_observed','mean')).reset_index()
 agg.to_csv(ROOT/'acquisition_results.csv',index=False)
 print('B:',agg[agg.k.isin([0,1,2,3,5,8])].to_string(index=False));return a

def calcC(cases):
 data=pd.read_csv(ROOT/'scored_reanalyses_EVALUATOR_ONLY.csv');actual=dict(zip(data.case_id,data.label_actual));out=[]
 for cid,c in cases.items():
  if not c['observations']:continue
  idx=hashed('corrupt_1',cid)%len(c['observations']);o=c['observations'][idx]
  changed=json.loads(json.dumps(c));r=changed['observations'][idx]
  if r['status']=='failed':r['status']='live';r['delay']=1
  else:r['status']='failed';r['delay']=None
  bad=certify(changed);orig=certify(c)
  out.append(dict(case_id=cid,world_id=c['world_id'],orig=orig,corrupted=bad,actual=actual[cid],observed=len(c['observations']),cert_error=int((bad=='YES' and actual[cid]==0) or (bad=='NO' and actual[cid]==1)),new_cert=int(bad!='UNKNOWN'),orig_cert=int(orig!='UNKNOWN')))
 d=pd.DataFrame(out);d.to_csv(ROOT/'single_corrupted_observation_STRESS.csv',index=False)
 summary={k:(int(v) if isinstance(v,np.integer) else v) for k,v in {'total':len(d),'original_certified':int(d.orig_cert.sum()),'corrupted_certified':int(d.new_cert.sum()),'incorrect_certificates':int(d.cert_error.sum()),'incorrect_among_certified':float(d.cert_error.sum()/max(1,d.new_cert.sum()))}.items()}
 dump(summary,'corrupted_observation_stress_summary.json')
 print('C',summary)
 return d

def calcD():
 (ROOT/'wiki_common_eligible.jsonl').unlink(missing_ok=True)
 df=pd.read_csv(WR/'graph_percolation_results/edge_scores.csv')
 assert len(df)==7960
 # At full retention, both modes have identical visible edge set but different candidate sampling.
 d=df[df.retention==1].pivot_table(index=['source_hash','target_hash','method'],columns='mask',values=['rank','top1','eligible'],aggfunc='first')
 out=[]
 for method in sorted(df.method.unique()):
  s=d.xs(method,level='method')
  # pivot multiindex with (field,mask)
  ra=s[('rank','independent')].astype(int);rb=s[('rank','source_correlated')].astype(int)
  aa=s[('top1','independent')].astype(int);bb=s[('top1','source_correlated')].astype(int)
  out.append(dict(method=method,n=len(s),changed_rank=int((ra!=rb).sum()),changed_top1=int((aa!=bb).sum()),top1_indep=int(aa.sum()),top1_group=int(bb.sum()),mean_abs_rank_diff=float(abs(ra-rb).mean())))
 pd.DataFrame(out).to_csv(ROOT/'wiki_same_graph_different_candidates.csv',index=False)
 # Fully paired finite fixed source-target IDs; eligibility intersection across BOTH masks at retention .25
 for p in [.25,.50,.75,1.]:
  q=df[(df.retention==p)&df.method.isin(['two_hop','common_in'])].pivot_table(index=['source_hash','target_hash'],columns=['mask','method'],values=['top1','eligible','rank'],aggfunc='first')
  needed=[('eligible','independent','two_hop'),('eligible','source_correlated','two_hop')]
  s=q[(q[needed[0]]==1)&(q[needed[1]]==1)];
  for mode in ['independent','source_correlated']:
   a=s[('top1',mode,'two_hop')].astype(int);b=s[('top1',mode,'common_in')].astype(int)
   x=dict(retention=p,mode=mode,n_always_eligible=len(s),two_hop_top1=int(a.sum()),common_in_top1=int(b.sum()),twohop_only=int(((a==1)&(b==0)).sum()),commonin_only=int(((b==1)&(a==0)).sum()))
   (ROOT/'wiki_common_eligible.jsonl').open('a').write(json.dumps(x)+'\n')
 print('D:',pd.DataFrame(out).to_string(index=False))
 print('D intersections:',(ROOT/'wiki_common_eligible.jsonl').read_text())

def calcE():
 cr=pd.read_csv(Path(os.environ.get('ER_CE_ROOT', HERE/'inputs/ER_CE_RECOVERABILITY_1' if (HERE/'inputs/ER_CE_RECOVERABILITY_1').exists() else '/mnt/data/ER_CE_RECOVERABILITY_1'))/'results/causal_power_by_model.csv')
 r=pd.read_csv(Path(os.environ.get('ER_CE_ROOT', HERE/'inputs/ER_CE_RECOVERABILITY_1' if (HERE/'inputs/ER_CE_RECOVERABILITY_1').exists() else '/mnt/data/ER_CE_RECOVERABILITY_1'))/'results/recoverability_curves_exact.csv')
 print('E CE cols',list(cr.columns),'CURVE cols',list(r.columns))
 r.to_csv(ROOT/'ce_saved_exact_curves_source_copy.csv',index=False)
 # No added inference; report control algebra with original original report.
 out={'status':'Source-verified fixed-target control; not a new optimizer evaluation',
      'fact':'For independent nuisance transitions and independently masked observations, P(M2 | OM,OA,OB) = P(M2 | OM). Hence changing nuisance dynamics cannot improve the Bayes-optimal reconstruction of this same target.',
      'implication':'CE-guided selection cannot obtain a strictly better optimal same-target Bayes score from these nuisance variables in this factorized task; performance comparisons need interacting models or finite-resource constraints.'}
 dump(out,'ce_fixed_target_control.json')

def main():
 cases,pr=loadpublic();calcA(cases,pr);calcB(cases);calcC(cases);calcD();calcE()
if __name__=='__main__':main()
