"""Private evaluator: generates complete native ledgers and reference exact labels.
Do not give evaluator/ to deployed predictor. All labels are computed by MILP
from retained evidence, not by copying factual truth.
"""
import argparse, csv, json, random, time, hashlib, platform
from pathlib import Path
from collections import Counter
from scale1_core import SIZES,FAMILIES,RETENTIONS,MASK_TYPES,make_world,sample_mask,ExactOracle,jsonl_write

def seed_of(*xs):return int(hashlib.sha256('|'.join(map(str,xs)).encode()).hexdigest()[:15],16)

def run(out,per_size_family=16,base_seed=260115):
    out=Path(out);(out/'public').mkdir(parents=True,exist_ok=True)
    (out/'evaluator_only').mkdir(parents=True,exist_ok=True)
    aud={'development':[],'heldout':[]};labels=[];truth=[];summary=Counter()
    t0=time.monotonic()
    for fam in FAMILIES:
        split='development' if fam in FAMILIES[:3] else 'heldout'
        for n in SIZES:
            for rep in range(per_size_family):
                s=seed_of(base_seed,fam,n,rep)
                wid=hashlib.sha256(f'ER-SCALE1|{base_seed}|{fam}|{n}|{rep}'.encode()).hexdigest()[:20]
                public,all_records,hidden=make_world(s,n,fam,wid)
                solver=ExactOracle(public)
                check=solver.query(all_records)
                assert check['status']=='ok' and check['identified'] and check['value']==hidden['claim_truth'],(wid,check,hidden)
                truth.append(hidden)
                for retention in RETENTIONS:
                    for mask_type in MASK_TYPES:
                        masked=sample_mask(all_records,public,
                           random.Random(seed_of(s,retention,mask_type)),retention,mask_type)
                        ref=solver.query(masked)
                        if ref['status']!='ok':raise RuntimeError('Reference solver failure '+str((wid,retention,mask_type,ref)))
                        if ref['identified'] and ref['value']!=hidden['claim_truth']:
                            raise RuntimeError('Truth mismatch')
                        eid=hashlib.sha256(f'{wid}|{retention}|{mask_type}'.encode()).hexdigest()[:24]
                        aud[split].append({'example_id':eid,'world_id':wid,'claim':public['claim'],
                              'public':public,'records':masked})
                        labels.append({'example_id':eid,'world_id':wid,'split':split,'family':fam,
                            'n_agents':n,'retention':retention,'mask_type':mask_type,
                            'actual_retention':round(len(masked)/len(all_records),5),
                            'n_available':len(all_records),'n_observed':len(masked),
                            'claim_truth':hidden['claim_truth'],
                            'ref_identified':int(ref['identified']),
                            'ref_value':ref['value'],'ref_can_false':int(ref['can_false']),
                            'ref_can_true':int(ref['can_true'])})
                        summary[(split,'examples')]+=1
                        summary[(split,'identified')]+=int(ref['identified'])
                        summary[(split,'truth_true')]+=hidden['claim_truth']
                summary[(split,'worlds')]+=1
                if summary[(split,'worlds')]%80==0:
                    print(f'generated {split}: {summary[(split,"worlds")]} worlds; elapsed {time.monotonic()-t0:.1f}s',flush=True)
    for split,rows in aud.items():jsonl_write(out/'public'/f'{split}.jsonl',rows)
    jsonl_write(out/'evaluator_only'/'actual_worlds.jsonl',truth)
    keys=list(labels[0]);
    with (out/'evaluator_only'/'reference_labels.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(labels)
    # Give development supervision only; heldout labels stay evaluator-only.
    # Hash world ID produces folds without exposing mechanism name.
    with (out/'development_labels_ONLY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['example_id','world_id','ref_identified','ref_value','development_fold'])
        w.writeheader()
        for r in labels:
            if r['split']=='development':w.writerow({k:v for k,v in
             [('example_id',r['example_id']),('world_id',r['world_id']),
              ('ref_identified',r['ref_identified']),('ref_value',r['ref_value']),('development_fold',seed_of(r['world_id'])%4)]})
    manifest={'base_seed':base_seed,'per_size_family':per_size_family,
      'design':{'sizes':SIZES,'families':FAMILIES,'retentions':RETENTIONS,'masks':MASK_TYPES},
      'worlds':len(truth),'examples':len(labels),
      'development':len(aud['development']),'heldout':len(aud['heldout']),
      'python':platform.python_version(),'numpy':__import__('numpy').__version__,
      'scipy':__import__('scipy').__version__,
      'run_seconds':round(time.monotonic()-t0,3),'summary':{str(k):v for k,v in summary.items()},
      'label_definition':'both target truth values feasible vs exactly one under truthful signed records and public known attempt topology',
      'scope':'SYNTHETIC closed-world topology only; not real LLM agents; not novel theorem'}
    (out/'generation_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--per-size-family',type=int,default=16)
    p.add_argument('--seed',type=int,default=260115);a=p.parse_args()
    print(json.dumps(run(a.out,a.per_size_family,a.seed),indent=2))
