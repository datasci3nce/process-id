"""Private evaluation ONLY. Must never be imported or invoked by deployable scorer."""
import argparse,csv,json,math,collections,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import beta
from sklearn.metrics import roc_auc_score
from scale1_core import jsonl_write

METHODS=('presence_logistic','content_logistic','content_hgb','claim_aware_logistic')

def load(path):
    with open(path) as f:return [json.loads(line) for line in f if line.strip()]

def cpupper(k,n,alpha=.05):
    if not n:return None
    if k==n:return 1.0
    return float(beta.ppf(1-alpha,k+1,n-k))

def measure_policy(rows,which,thresholds):
    t=(thresholds.get(which) or {}).get('selected') if which in METHODS else None
    cert=[]
    for r in rows:
        if which=='strict_receipt':value=r['receipt_value']
        elif which=='signed_only_exact':value=r['signed_only_value'] if r['signed_only_cert'] else None
        elif which=='full_exact_reference':value=r['ref_value'] if r['ref_identified'] else None
        elif which=='fitted_exact':value=r['fitted_value'] if r['fitted_cert'] else None
        elif which in METHODS:
            value=r['signed_only_value'] if r['signed_only_cert'] else (
                r['fitted_value'] if t is not None and r['fitted_cert'] and r[which]>=t else None)
        else:raise ValueError(which)
        if value is not None:
            cert.append((r,int(value),bool(r['ref_identified'] and r['ref_value']==int(value))))
    good=sum(z[2] for z in cert);bad=len(cert)-good
    wrong=sum(r['claim_truth']!=v for r,v,ok in cert)
    groups=collections.defaultdict(list)
    for r,v,ok in cert:groups[r['world_id']].append(ok)
    bad_worlds=sum(not all(a) for a in groups.values())
    return {'method':which,'threshold_dev':t,'certified':len(cert),'supported':good,'unsupported':bad,
        'wrong':wrong,'coverage_supported':good/len(rows),
        'unsupported_risk':bad/max(1,len(cert)),
        'worlds_with_certification':len(groups),'worlds_with_any_unsupported':bad_worlds,
        'world_any_unsupported_upper95':cpupper(bad_worlds,len(groups))}

def calc_brier_auroc(rows,method):
    y=np.asarray([r['ref_identified'] for r in rows]);p=np.asarray([r[method] for r in rows]);
    return {'method':method,'brier':float(np.mean((p-y)**2)),
            'auroc':float(roc_auc_score(y,p)) if len(set(y))>1 else None,
            'calibration_abs_error':float(abs(p.mean()-y.mean()))}

def group_bootstrap_diff(rows,a,b,iterations=1000,seed=260115):
    rng=np.random.default_rng(seed)
    groups={}
    for r in rows:groups.setdefault(r['world_id'],[]).append(r)
    ids=list(groups)
    agg=[]
    for wid in ids:
        xs=groups[wid]
        agg.append((sum((q[a]-q['ref_identified'])**2-(q[b]-q['ref_identified'])**2 for q in xs),len(xs)))
    num=np.array([x[0] for x in agg]);den=np.array([x[1] for x in agg])
    idx=rng.integers(0,len(ids),(iterations,len(ids)))
    vals=num[idx].sum(axis=1)/den[idx].sum(axis=1)
    return {'comparison':f'{a} minus {b}','observed':float(num.sum()/den.sum()),
            'world_bootstrap_CI95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],
            'world_groups':len(ids)}

def run(private_labels,predictions,thresholds_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with open(private_labels,newline='') as f:all_labels=list(csv.DictReader(f))
    lab={q['example_id']:q for q in all_labels if q['split']=='heldout'}
    preds=load(predictions)
    if len(preds)!=len(lab) or set(q['example_id'] for q in preds)!=set(lab):
        raise ValueError('Held-out evaluator join mismatch')
    th=json.loads(Path(thresholds_path).read_text())
    merged=[]
    for p in preds:
        y=lab[p['example_id']]
        row={**p,**{k:y[k] for k in ('family','n_agents','retention','mask_type','actual_retention')}}
        row.update({'ref_identified':int(y['ref_identified']),
          'ref_value':(int(y['ref_value']) if y['ref_value']!='' else None),
          'claim_truth':int(y['claim_truth'])})
        if row['ref_identified'] and row['ref_value']!=row['claim_truth']:
            raise RuntimeError('Bad reference identification')
        merged.append(row)
    rates=[measure_policy(merged,k,th) for k in
          ('strict_receipt','signed_only_exact','full_exact_reference','fitted_exact')+METHODS]
    briers=[calc_brier_auroc(merged,k) for k in METHODS]
    comparisons=[group_bootstrap_diff(merged,'claim_aware_logistic','content_logistic'),
                 group_bootstrap_diff(merged,'claim_aware_logistic','content_hgb')]
    slices=[]
    for field in ('n_agents','retention','mask_type','family'):
        for value in sorted(set(q[field] for q in merged)):
            s=[q for q in merged if q[field]==value]
            slices.append({'field':field,'value':value,'cases':len(s),
                     'unique_worlds':len(set(q['world_id'] for q in s)),
                     'reference_identifiable':sum(q['ref_identified'] for q in s),
                     'reference_identifiable_rate':sum(q['ref_identified'] for q in s)/len(s),
                     'signed_only_supported':measure_policy(s,'signed_only_exact',th)['supported'],
                     'content_supported':measure_policy(s,'content_logistic',th)['supported'],
                     'claim_aware_supported':measure_policy(s,'claim_aware_logistic',th)['supported']})
    jsonl_write(out/'heldout_scored_PRIVATE.jsonl',merged)
    with (out/'policy_metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rates[0]));w.writeheader();w.writerows(rates)
    with (out/'percolation_slices.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(slices[0]));w.writeheader();w.writerows(slices)
    data={'heldout_cases':len(merged),'heldout_worlds':len(set(r['world_id'] for r in merged)),
          'known_event_topology':True,'closed_world':True,
          'truth_true':sum(r['claim_truth'] for r in merged),
          'reference_identifiable':sum(r['ref_identified'] for r in merged),
          'fitted_contradictions':sum(r['fitted_contra'] for r in merged),
          'policies':rates,'prediction_scores':briers,'paired_world_bootstrap':comparisons,
          'leakage_warning':'Heldout labels must not enter train_predict; scorer reads public observations and development labels only',
          'phase_transition_claim':'NONE; exploratory finite-size evidence reliability only'}
    (out/'summary.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-labels',required=True)
    p.add_argument('--predictions',required=True);p.add_argument('--thresholds',required=True)
    p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(run(a.private_labels,a.predictions,a.thresholds,a.out),indent=2))
