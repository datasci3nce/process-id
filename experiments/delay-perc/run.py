"""One-command reproducible ER-DELAY-PERC-1 experiment. No external data or network calls."""
from __future__ import annotations
import argparse,csv,json,time,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from core import (make_world,make_mask,certify,scalar_features,montecarlo_prob,
                  dde_surrogate,stable_seed,ALLOWED_DELAYS)

MASKS=[('independent',p) for p in (.25,.50,.75,1.)]+[('source_correlated',p) for p in (.25,.50,.75,1.)]+[('targeted',p) for p in (.50,.75)]
METHODS=['static_logistic','timed_logistic','dde_delayed','dde_no_delay','dde_delayed_alone','mc_event_posterior']


def write_jsonl(path,records):
    with open(path,'w') as f:
        for row in records:f.write(json.dumps(row,separators=(',',':'),sort_keys=True)+'\n')


def tocsv(path,rows):
    if not rows:return
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(out,worlds_per_size=100,draws=96,seed=20261115,boots=1000):
    t0=time.monotonic();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pub_dir=out/'public'; evaluator=out/'evaluator_ONLY';pub_dir.mkdir(exist_ok=True);evaluator.mkdir(exist_ok=True)
    worlds=[]
    for n in [8,16,32,64]:
        for i in range(worlds_per_size):
            sp='development' if i<round(worlds_per_size*.6) else 'heldout'
            wid=f'{n:02d}_{i:03d}'
            worlds.append(make_world(wid,n,sp,stable_seed('world',seed,n,i)))
    # Fit only development-world generation priors; unavailable on held-out worlds.
    dev_edges=[e for w in worlds if w['split']=='development' for e in w['private_edges']]
    q=float(np.mean([e[2] for e in dev_edges]));dd=np.array([e[3] for e in dev_edges if e[2]])
    p_delay=np.array([(np.sum(dd==d)+.5)/(len(dd)+2) for d in ALLOWED_DELAYS],dtype=float)
    p_delay=p_delay/p_delay.sum()
    params={'q_from_development_private_training_records':q,
            'delay_prob_from_development_private_training_records':dict(zip(map(str,ALLOWED_DELAYS),map(float,p_delay))),
            'worlds_per_size':worlds_per_size,'draws':draws,'seed':seed,
            'calibration': 'logistic models fitted development-world rows only'}
    (out/'fit_parameters.json').write_text(json.dumps(params,indent=2))
    worldrows=[{k:w[k] for k in ['world_id','n','split','deadline','truth','native_arrival']}
               for w in worlds]
    tocsv(evaluator/'native_world_truth.csv',worldrows)
    write_jsonl(evaluator/'native_edge_ledgers.jsonl',[
        {'world_id':w['world_id'],'truth':w['truth'],'private_edges':w['private_edges']}
        for w in worlds])
    publics=[];rows=[];features=[]
    for ix,w in enumerate(worlds):
        for im,(kind,p) in enumerate(MASKS):
            case=make_mask(w,kind,p,stable_seed('mask',seed,w['world_id'],im))
            cid=f"{w['world_id']}_M{im:02d}";case['case_id']=cid
            public={k:v for k,v in case.items() if k!='mask_seed'}
            publics.append(public)
            static,timed=scalar_features(public)
            dd_score=dde_surrogate(public,q,p_delay,with_delay=True)
            zero_score=dde_surrogate(public,q,p_delay,with_delay=False)
            mc=montecarlo_prob(public,draws,stable_seed('MC',seed,cid),q,p_delay)
            predcert=certify(public)
            rows.append({'case_id':cid,'world_id':w['world_id'],'n':w['n'],
                 'split':w['split'],'mask_kind':kind,'retention':p,
                 'retention_actual':case['retention_actual'],'reference_cert':predcert,
                 'mc_event_posterior':mc,'label_actual':w['truth']})
            features.append({'static':static,'timed':static+timed,
                             'dde_delayed':static+[dd_score],
                             'dde_no_delay':static+[zero_score],
                             'dde_delayed_alone':[dd_score]})
        if (ix+1)%100==0:print('generated',ix+1,'of',len(worlds),'worlds; elapsed',round(time.monotonic()-t0,1),'s',flush=True)
    write_jsonl(pub_dir/'development.jsonl',[r for r in publics if r['case_id'].split('_M')[0] in {w['world_id'] for w in worlds if w['split']=='development'}])
    write_jsonl(pub_dir/'heldout.jsonl',[r for r in publics if r['case_id'].split('_M')[0] in {w['world_id'] for w in worlds if w['split']=='heldout'}])
    train=[i for i,r in enumerate(rows) if r['split']=='development']; test=[i for i,r in enumerate(rows) if r['split']=='heldout']
    y=np.array([r['label_actual'] for r in rows],dtype=int)
    models={}
    for name in METHODS:
        if name=='mc_event_posterior':continue
        X=np.array([f[name] if name!='static_logistic' and name!='timed_logistic' else f['static' if name=='static_logistic' else 'timed'] for f in features],dtype=float)
        model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1.0))
        model.fit(X[train],y[train])
        scores=model.predict_proba(X)[:,1]
        for r,score in zip(rows,scores):r[name]=float(score)
        models[name]={'num_features':X.shape[1], 'train_positive_frac':float(y[train].mean())}
    (out/'models_meta.json').write_text(json.dumps(models,indent=2))
    tocsv(out/'all_predictions_evaluator_ONLY.csv',rows)
    public_scores=[{k:r[k] for k in ['case_id','world_id','n','split','mask_kind','retention','retention_actual','reference_cert']+METHODS} for r in rows]
    tocsv(pub_dir/'observed_only_predictions.csv',public_scores)
    tocsv(evaluator/'heldout_scored.csv',[r for r in rows if r['split']=='heldout'])
    # Holdout analysis and bootstrap by world (not masks).
    held=[rows[i] for i in test]
    ref=Counter(r['reference_cert'] for r in held)
    supported=sum((r['reference_cert']=='YES' and r['label_actual']==1) or (r['reference_cert']=='NO' and r['label_actual']==0) for r in held)
    failures=sum((r['reference_cert']=='YES' and r['label_actual']==0) or (r['reference_cert']=='NO' and r['label_actual']==1) for r in held)
    stats={}
    for name in METHODS:
        ps=np.array([r[name] for r in held]);yt=np.array([r['label_actual'] for r in held])
        stats[name]={'brier':float(brier_score_loss(yt,ps)),
                      'auc':float(roc_auc_score(yt,ps)) if len(set(yt))>1 else None,
                      'positive_mean':float(ps.mean()), 'accuracy_at_0_5':float(np.mean((ps>=.5)==yt))}
    # Matched-world Brier diffs: negative = first method better.
    pairs=[('timed_logistic','static_logistic'),('dde_delayed','dde_no_delay'),
           ('dde_delayed','timed_logistic'),('mc_event_posterior','dde_delayed'),
           ('mc_event_posterior','timed_logistic')]
    wid=sorted({r['world_id'] for r in held});byid={z:[r for r in held if r['world_id']==z] for z in wid}
    rng=np.random.default_rng(stable_seed('bootstrap',seed));diffs={}
    for a,b in pairs:
        world_d=np.array([np.mean([(r[a]-r['label_actual'])**2-(r[b]-r['label_actual'])**2 for r in byid[w]]) for w in wid])
        sampled=rng.integers(0,len(wid),size=(boots,len(wid)))
        bootstrap=world_d[sampled].mean(axis=1)
        diffs[f'{a}_minus_{b}']={'difference':float(world_d.mean()),
            'cluster_bootstrap_95pct':list(map(float,np.quantile(bootstrap,[.025,.975]))),
            'worlds':len(wid)}
    grouped=[]
    for kind,p in MASKS:
        group=[r for r in held if r['mask_kind']==kind and r['retention']==p]
        row={'mask_kind':kind,'retention':p,'n_cases':len(group),'truth_rate':float(np.mean([r['label_actual'] for r in group])),
             'reference_yes':sum(r['reference_cert']=='YES' for r in group),
             'reference_no':sum(r['reference_cert']=='NO' for r in group),
             'reference_ambiguous':sum(r['reference_cert']=='UNKNOWN' for r in group),
             'mean_retention':float(np.mean([r['retention_actual'] for r in group]))}
        row.update({f'{name}_brier':float(np.mean([(r[name]-r['label_actual'])**2 for r in group])) for name in METHODS})
        grouped.append(row)
    tocsv(out/'retention_breakdown.csv',grouped)
    stats_by_size=[]
    for n in [8,16,32,64]:
        group=[r for r in held if r['n']==n]
        z={'n':n,'n_cases':len(group),'n_worlds':len({r['world_id'] for r in group}),
           'positive_rate':float(np.mean([r['label_actual'] for r in group])),
           'cert_coverage':float(np.mean([r['reference_cert']!='UNKNOWN' for r in group]))}
        z.update({f'{name}_brier':float(np.mean([(r[name]-r['label_actual'])**2 for r in group])) for name in METHODS})
        stats_by_size.append(z)
    tocsv(out/'size_breakdown.csv',stats_by_size)
    summary={'design':{'n_worlds':len(worlds),'dev_worlds':len(worlds)-len(wid),'heldout_worlds':len(wid),
                       'cases':len(rows),'heldout_cases':len(held),'masks_per_world':len(MASKS),
                       'heldout_truth_positive_rate':float(np.mean([r['label_actual'] for r in held]))},
             'reference_identification':{'yes':ref['YES'],'no':ref['NO'],'ambiguous':ref['UNKNOWN'],
                                         'certification_correct':supported,'certification_factual_errors':failures},
             'predictions':stats,'paired_world_bootstrap':diffs,
             'note':'The numeric DDE is a delayed linear influence surrogate, NOT generative truth, tested on synthetic agent-channel networks.'}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--worlds-per-size',type=int,default=100);p.add_argument('--draws',type=int,default=96);p.add_argument('--seed',type=int,default=20261115);p.add_argument('--boots',type=int,default=1000)
    a=p.parse_args();run(a.out,a.worlds_per_size,a.draws,a.seed,a.boots)
