"""Independent output-integrity and data-boundary audit, no learned predictions."""
import argparse,collections,csv,json,hashlib
from pathlib import Path
from scale1_core import path_truth

def run(root):
 root=Path(root)
 priv={q['world_id']:q for q in map(json.loads,(root/'evaluator_only'/'actual_worlds.jsonl').open())}
 with (root/'evaluator_only'/'reference_labels.csv').open() as f:labels=list(csv.DictReader(f))
 byid={r['example_id']:r for r in labels}
 checked=0;receipts_checked=0;worlds=set();splitworlds=collections.defaultdict(set)
 allpublic=[]
 for split in ('development','heldout'):
  with (root/'public'/f'{split}.jsonl').open() as f:
   for line in f:
    row=json.loads(line);pub=row['public'];wid=row['world_id'];P=priv[wid];L=byid[row['example_id']]
    if split!=L['split']:raise AssertionError('split mismatch')
    if set(row)!=set(('example_id','world_id','claim','public','records')):raise AssertionError('public schema mismatch')
    if pub['world_id']!=wid or 'family' in pub or 'claim_truth' in pub or 'edge_native_success' in pub:
     raise AssertionError('public leak')
    if P['family'] in ('spoof_ack','stale_replica') and split!='heldout':raise AssertionError('mechanism leakage')
    if P['family'] in ('direct','relay','retry') and split!='development':raise AssertionError('mechanism leakage')
    truth=path_truth(pub['n_agents'],pub['edges'],P['edge_native_success'])
    if int(truth[-1])!=P['claim_truth']:raise AssertionError('private forward truth wrong')
    if int(L['claim_truth'])!=P['claim_truth']:raise AssertionError('ref factual mismatch')
    if int(L['ref_identified']) and int(L['ref_value'])!=P['claim_truth']:raise AssertionError('identified contradicts actual')
    for r in row['records']:
     k=r['kind'];v=r['value'];ids=r['edges']
     if k=='signed_native':valid=P['edge_native_success'][ids[0]]==v
     elif k=='signed_batch':valid=sum(P['edge_native_success'][i] for i in ids)==v
     elif k=='signed_inbox':valid=int(truth[r['meta']['agent']])==v
     else:valid=k=='weak_ack'
     if not valid:raise AssertionError('invalid authenticated receipt '+row['example_id'])
     receipts_checked+=1
    worlds.add(wid);splitworlds[split].add(wid);checked+=1
 if len(splitworlds['development'] & splitworlds['heldout']):raise AssertionError('same world across splits')
 assert checked==len(labels) and len(worlds)==len(priv)
 assert len(worlds)==400 and checked==4800
 assert all(sum(x['world_id']==wid for x in labels)==12 for wid in worlds)
 out={'worlds':len(worlds),'cases':checked,'authenticated_and_weak_records_checked':receipts_checked,
      'development_worlds':len(splitworlds['development']),'heldout_worlds':len(splitworlds['heldout']),
      'auth_receipt_violations':0,'factual_label_errors':0,'actual_truth_disagreements':0,
      'public_private_field_leak_violations':0,'split_world_overlap':0}
 (root/'DATA_INTEGRITY_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--results',default='results');p=a.parse_args()
 print(json.dumps(run(p.results),indent=2))
