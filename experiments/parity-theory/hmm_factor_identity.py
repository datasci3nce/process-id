#!/usr/bin/env python3
"""Exact numerical HMM=chain factor graph=Gibbs partition identity, plus
read-only recomputation of archived WOTH test scores. No new LLM calls.
"""
import argparse,zipfile,json,itertools,hashlib,math
from pathlib import Path
import numpy as np

def forward_Z(pi,A,B,y,mask):
    a=pi.copy()
    for t,v in enumerate(y):
        if t:a=a@A
        if mask[t]:a=a*B[:,v]
    return float(a.sum())

def brute_Z(pi,A,B,y,mask):
    k=len(pi);s=0.0
    for states in itertools.product(range(k),repeat=len(y)):
        q=pi[states[0]]
        for t,v in enumerate(y):
            if t:q*=A[states[t-1],states[t]]
            if mask[t]:q*=B[states[t],v]
        s+=q
    return float(s)

def main(inzip,out):
    z=zipfile.ZipFile(inzip)
    params=json.loads(z.read('results/train_priors_and_hmm.json'))
    predictions=json.loads(z.read('results/test_case_predictions.json'))
    original=json.loads(z.read('results/summary.json'))
    A=np.asarray(params['hmm_transition'],dtype=float)
    ec=np.asarray(params['emission_counts'],dtype=float)
    B=ec/ec.sum(axis=1,keepdims=True)
    pi=np.ones(3)/3
    y=[3,4,2,6,1,7]
    errs=[];values=[]
    for mask in itertools.product([False,True],repeat=len(y)):
        a=forward_Z(pi,A,B,y,mask);b=brute_Z(pi,A,B,y,mask)
        errs.append(abs(a-b));values.append((mask,a))
        assert abs(a-b)<=1e-12,('HMM/chain factor mismatch',mask,a,b)
    scores={k:{'cases':len(v),'mean_case_nll':float(np.mean([r['nll_per_token'] for r in v])),'token_weighted_nll':float(sum(r['tokens']*r['nll_per_token'] for r in v)/sum(r['tokens'] for r in v))} for k,v in predictions.items()}
    assert len(predictions['HMM_EMP'])==50
    assert abs(scores['HMM_EMP']['mean_case_nll']-original['methods']['HMM_EMP']['test_session_mean_nll'])<1e-12
    results={'source_archive_sha256':hashlib.sha256(Path(inzip).read_bytes()).hexdigest(),
      'source_messages':original['corpus']['messages'],'source_sessions':original['corpus']['sessions'],
      'test_sessions':original['n_test_sessions'],'test_cases':len(predictions['HMM_EMP']),
      'test_scores':scores,'numeric_identity':{'states':3,'length':len(y),'masks':len(errs),'max_abs_partition_difference':max(errs),'normalization_complete_missing':forward_Z(pi,A,B,y,[False]*len(y)),
      'example_observed_partition':forward_Z(pi,A,B,y,[True]*len(y)),
      'example_observed_free_energy':-math.log(forward_Z(pi,A,B,y,[True]*len(y)))},
      'note':'Identity check is on a six-step illustration using transition and emission parameters derived from the archived WOTH analysis; it does not reproduce the WOTH full corpus likelihood for this synthetic sequence. Archived test NLL metrics are independently recomputed from the 50 saved test-case predictions.'}
    Path(out).write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--out',default='hmm_factor_check.json');a=p.parse_args()
    print(json.dumps(main(a.archive,a.out),indent=2))
