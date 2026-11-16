"""Auditor process. ONLY reads public observations and development labels.
It never imports the generator, private ledger, or evaluator labels at runtime.
The shared core provides documented solver and observation-schema functions.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math,time,collections
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scale1_core import ExactOracle,receipt_baseline,cheap_features,jsonl_write

FIELDS=('example_id','world_id','claim','public','records')
METHODS=('presence_logistic','content_logistic','content_hgb','claim_aware_logistic')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def graph_features(public):
    es=[e for e in public['edges'] if e['v']=='v1' and e['when']=='before']
    n=public['n_agents'];ind=[0]*n;out=[0]*n
    for e in es:out[e['src']]+=1;ind[e['dst']]+=1
    return {'edges_per_agent':len(es)/n,'source_degree':out[0],
            'target_indegree':ind[-1], 'mean_indegree':sum(ind)/n,
            'max_indegree':max(ind),'mean_outdegree':sum(out)/n,
            'max_outdegree':max(out)}

def compute_rows(path):
    outputs=[];arrays=[];graphs={};stats=collections.Counter();t0=time.monotonic()
    with open(path) as f:
        for line in f:
            if not line.strip():continue
            q=json.loads(line)
            if set(q)!=set(FIELDS):raise ValueError('public schema mismatch; hidden labels?')
            pub=q['public'];records=q['records']
            if 'family' in pub or 'claim_truth' in pub or 'edge_native_success' in pub:
                raise ValueError('private fields in public topology')
            if not all(set(r)=={'id','kind','edges','value','group','signer','meta'} for r in records):
                raise ValueError('unexpected receipt schema')
            world=q['world_id'];
            if world not in graphs:graphs[world]=(ExactOracle(pub),graph_features(pub))
            solver,gf=graphs[world]
            signed_only=[r for r in records if r['kind'] in ('signed_native','signed_inbox')]
            robust=solver.query(signed_only,fit=False)
            fitted=solver.query(records,fit=True)
            for name,x in [('robust',robust),('fitted',fitted)]:
                if x['status']=='timeout_or_unknown':raise RuntimeError(f'{name} solver failed on {q["example_id"]}')
            base=cheap_features(pub,records)
            baseline=receipt_baseline(pub,records)
            f_presence={k:v for k,v in base.items() if k.startswith('count_') or k.startswith('fraction_') or k in
                         ('n_agents','n_attempts','n_real_attempts','n_stale_attempts','n_after_action','n_records')}
            f_content=dict(base)
            f_claim=dict(f_content)
            f_claim.update(gf)
            f_claim.update({'fitted_cert':int(fitted['identified']),
                   'fitted_contra':int(fitted['status']=='inconsistent'),
                   'fitted_value_true':float(fitted['value']==1),
                   'signed_only_cert':int(robust['identified']),
                   'signed_only_value_true':float(robust['value']==1)})
            arrays.append({'presence_logistic':f_presence,'content_logistic':f_content,
                           'content_hgb':f_content,'claim_aware_logistic':f_claim})
            outputs.append({'example_id':q['example_id'],'world_id':world,'receipt_value':baseline,
              'signed_only_cert':int(robust['identified']),'signed_only_value':robust['value'],
              'signed_only_contra':int(robust['status']=='inconsistent'),
              'fitted_cert':int(fitted['identified']),'fitted_value':fitted['value'],
              'fitted_contra':int(fitted['status']=='inconsistent')})
            stats['rows']+=1
            if stats['rows']%1200==0:print('features',path.name,stats['rows'],'elapsed',round(time.monotonic()-t0,1),flush=True)
    return outputs,arrays,stats


def matrix(samples,method,keys):
    return np.asarray([[float(row[method].get(k,0)) for k in keys] for row in samples],dtype=np.float64)

def build(method):
    if method=='content_hgb':
        return HistGradientBoostingClassifier(max_iter=130,max_leaf_nodes=15,
             learning_rate=.06,l2_regularization=5,min_samples_leaf=20,random_state=260115)
    return Pipeline([('scale',StandardScaler()),
       ('model',LogisticRegression(C=1.,max_iter=3500,solver='lbfgs',random_state=260115))])

def train_predict(public_dir,labels_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    public_dir=Path(public_dir)
    development,xa,_=compute_rows(public_dir/'development.jsonl')
    heldout,xb,_=compute_rows(public_dir/'heldout.jsonl')
    with open(labels_path,newline='') as f:labels=list(csv.DictReader(f))
    train_y={r['example_id']:r for r in labels}
    if len(train_y)!=len(labels) or set(train_y)!={x['example_id'] for x in development}:
        raise ValueError('development label key mismatch')
    y=np.array([int(train_y[x['example_id']]['ref_identified']) for x in development])
    folds=np.array([int(train_y[x['example_id']]['development_fold']) for x in development])
    byworld=collections.defaultdict(set)
    for row,fold in zip(development,folds):byworld[row['world_id']].add(fold)
    if any(len(s)>1 for s in byworld.values()):raise ValueError('leakage: world split across folds')
    print('dev rows',len(development),'test rows',len(heldout),'dev worlds',len(byworld),flush=True)
    infos={}
    for method in METHODS:
        keys=sorted(set().union(*(set(q[method]) for q in xa)))
        X=matrix(xa,method,keys);XT=matrix(xb,method,keys)
        oof=np.empty(len(y))
        for fold in sorted(set(folds)):
            tr=folds!=fold;te=~tr
            model=build(method);model.fit(X[tr],y[tr]);oof[te]=model.predict_proba(X[te])[:,1]
        model=build(method);model.fit(X,y);pred=model.predict_proba(XT)[:,1]
        for x,z in zip(development,oof):x[method]=float(z)
        for x,z in zip(heldout,pred):x[method]=float(z)
        infos[method]={'terms':len(keys),'train_worlds':len(byworld),'folds':len(set(folds)),
            'min_train_prob':round(float(oof.min()),5),'max_train_prob':round(float(oof.max()),5)}
        print(method,'features',len(keys),'dev Brier',round(float(np.mean((oof-y)**2)),5),flush=True)
    # Thresholds require only development supervision, including adjudicated ref_value.
    thresholds={};records=[]
    for method in METHODS:
        candidates=[]
        for threshold in (.5,.7,.8,.9,.95,.99):
            cert=bad=good=0
            per_world=collections.defaultdict(lambda:[0,0])
            for x in development:
                gt=train_y[x['example_id']]
                value=x['signed_only_value'] if x['signed_only_cert'] else (
                       x['fitted_value'] if x['fitted_cert'] and x[method]>=threshold else None)
                if value is None:continue
                cert+=1;ok=gt['ref_identified']=='1' and str(value)==gt['ref_value']
                good+=int(ok);bad+=int(not ok)
                per_world[x['world_id']][0]+=1
                per_world[x['world_id']][1]+=int(not ok)
            nworld=sum(bool(k[0]) for k in per_world.values())
            bworld=sum(k[1]>0 for k in per_world.values())
            upper=1-(.05)**(1/nworld) if bworld==0 and nworld else 1.
            # Conservative Wilson upper bound for world with any unsupported certificate.
            if bworld and nworld:
                from scipy.stats import beta
                upper=float(beta.ppf(.95,bworld+1,nworld-bworld))
            candidates.append({'threshold':threshold,'certifications':cert,'supported':good,'unsupported':bad,
                 'observed_risk':bad/max(1,cert),'world_any_bad':bworld,'certifying_worlds':nworld,
                 'upper95_world_any_bad':upper})
        valid=[x for x in candidates if x['upper95_world_any_bad']<=.05]
        chosen=sorted(valid,key=lambda x:(x['supported'],-x['unsupported'],-x['threshold']),reverse=True)[0] if valid else None
        thresholds[method]={'selected':chosen['threshold'] if chosen else None,
           'selection':'development OOF world-any-error one-sided upper<=5%, then max supported',
           'candidates':candidates}
        for x in candidates:records.append({'method':method,**x})
    jsonl_write(out/'development_OOF.jsonl',development)
    jsonl_write(out/'heldout_predictions.jsonl',heldout)
    (out/'thresholds_FROZEN_DEV_ONLY.json').write_text(json.dumps(thresholds,indent=2,sort_keys=True)+'\n')
    with (out/'threshold_grid_DEV_ONLY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    manifest={'models':infos,'inputs_sha256':{
       'development':sha(public_dir/'development.jsonl'),
       'heldout':sha(public_dir/'heldout.jsonl'),'dev_supervision':sha(labels_path)},
       'threshold_rule':'selected on development OOF only; no held-out evaluator access',
       'columns_include':'receipt proof, signed-only exact, misspecified fitted exact, predictions',
       'heldout_predictions_sha256':sha(out/'heldout_predictions.jsonl')}
    (out/'PREDICTOR_FREEZE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--public',required=True)
    ap.add_argument('--development-labels',required=True);ap.add_argument('--out',required=True)
    x=ap.parse_args()
    print(json.dumps(train_predict(x.public,x.development_labels,x.out),indent=2))
