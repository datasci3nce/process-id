"""Deliberately adversarial omitted-channel stress; NOT a natural-world estimate."""
from pathlib import Path
import json, sys, os, hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parent
R=Path(os.environ.get('ER_DELAY_ROOT', str(ROOT/'source_data/ER_DELAY_PERCOLATION_1_v011' if (ROOT/'source_data/ER_DELAY_PERCOLATION_1_v011').exists() else Path('/mnt/data/ER_DELAY_PERCOLATION_1_v011'))))
sys.path.insert(0,str(R))
from core import certify
def hashed(*parts):return int(hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:16],16)

ledgers={}
for line in (R/'results/evaluator_ONLY/native_edge_ledgers.jsonl').read_text().splitlines():
 w=json.loads(line);ledgers[w['world_id']]=w
selected=set(w for w in ledgers if hashed('omitted-topology-v1',w)%5==0)
rows=[]
for line in (R/'results/public/heldout.jsonl').read_text().splitlines():
 c=json.loads(line);w=ledgers[c['world_id']];orig=int(w['truth']);target_new=int(orig or c['world_id'] in selected)
 cert=certify(c);assert cert in ['YES','NO','UNKNOWN']
 rows.append(dict(case_id=c['case_id'],world_id=c['world_id'],original_truth=orig,truth_with_omitted_channel=target_new,omitted_channel_added=int(c['world_id'] in selected),orig_certificate=cert,incorrect_modified=int(cert=='NO' and target_new==1) or int(cert=='YES' and target_new==0)))
d=pd.DataFrame(rows)
summary=dict(heldout_worlds=d.world_id.nunique(),worlds_with_hypothetical_unmodeled_shortcut=d.loc[d.omitted_channel_added==1,'world_id'].nunique(),
    heldout_masks=len(d),issued=int((d.orig_certificate!='UNKNOWN').sum()),
    false_certificates=int(d.incorrect_modified.sum()), false_NO=int(((d.orig_certificate=='NO')&(d.truth_with_omitted_channel==1)).sum()),
    false_YES=int(((d.orig_certificate=='YES')&(d.truth_with_omitted_channel==0)).sum()),
    original_truth_invariance_for_unmodified_worlds=bool((d.loc[~d.world_id.isin(selected),'original_truth']==d.loc[~d.world_id.isin(selected),'truth_with_omitted_channel']).all()))
res=ROOT/'results';res.mkdir(exist_ok=True);(res/'omitted_topology_stress_summary.json').write_text(json.dumps(summary,indent=2)+'\n');d.to_csv(res/'omitted_topology_stress_EVALUATOR_ONLY.csv',index=False)
print(summary)
