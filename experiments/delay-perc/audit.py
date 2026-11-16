"""Independent test of native world truth, observation/ledger consistency, and exact claim labels.
This uses NetworkX weighted shortest-path, not core.shortest or core.certify.
"""
import json,csv,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import networkx as nx
import numpy as np
import pandas as pd

def load(path):
 return [json.loads(line) for line in open(path)]

def shortest(n,edges):
 G=nx.DiGraph();G.add_nodes_from(range(n));G.add_weighted_edges_from(edges)
 try:return nx.shortest_path_length(G,0,n-1,weight='weight')
 except nx.NetworkXNoPath:return float('inf')

def independent_certificate(case):
 r={x['edge_idx']:x for x in case['observations']}
 proved=[];possible=[]
 for i,(u,v) in enumerate(case['potential_edges']):
  if i in r and r[i]['status']=='live':
   proved.append((u,v,r[i]['delay']));possible.append((u,v,r[i]['delay']))
  if i not in r:possible.append((u,v,1))
 if shortest(case['n'],proved)<=case['deadline']:return 'YES'
 if shortest(case['n'],possible)>case['deadline']:return 'NO'
 return 'UNKNOWN'

def audit(base):
 b=Path(base);ledgers={r['world_id']:r for r in load(b/'evaluator_ONLY'/'native_edge_ledgers.jsonl')}
 worlds={r['world_id']:r for r in csv.DictReader(open(b/'evaluator_ONLY'/'native_world_truth.csv'))}
 pred={r['case_id']:r for r in csv.DictReader(open(b/'all_predictions_evaluator_ONLY.csv'))}
 assert len(worlds)==400 and len(ledgers)==400 and len(pred)==4000
 for wid,l in ledgers.items():
  w=worlds[wid];n=int(w['n']);g=[(int(u),int(v),int(d)) for u,v,live,d in l['private_edges'] if live]
  actual=int(shortest(n,g)<=int(w['deadline']))
  assert actual==int(w['truth'])==l['truth'],('truth',wid)
 counts=Counter();p1=defaultdict(dict)
 for split in ['development','heldout']:
  for case in load(b/'public'/f'{split}.jsonl'):
   cid=case['case_id'];wid=case['world_id'];pr=pred[cid]
   assert pr['split']==split and pr['world_id']==wid
   assert 'truth' not in case and 'native_arrival' not in case and 'private_edges' not in case
   true=ledgers[wid]['private_edges']; n=int(worlds[wid]['n']);
   assert len(case['potential_edges'])==len(true)
   for i,(u,v) in enumerate(case['potential_edges']):
    assert [u,v]==[true[i][0],true[i][1]]
   for obs in case['observations']:
    i=obs['edge_idx'];assert 0<=i<len(true)
    assert obs['status']==('live' if true[i][2] else 'failed')
    assert obs['delay']==true[i][3]
   v=independent_certificate(case)
   assert v==pr['reference_cert'],('cert',cid,v,pr['reference_cert'])
   assert not (v=='YES' and int(worlds[wid]['truth'])!=1)
   assert not (v=='NO' and int(worlds[wid]['truth'])!=0)
   counts[(split,v)]+=1
   if case['retention_requested']==1:
    p1[wid][case['mask_kind']]=case['observations']
 assert all(p['source_correlated']==p['independent'] for p in p1.values())
 assert len(p1)==400
 print('Independent audit PASS:',sum(counts.values()),'cases;',len(worlds),'native worlds;',len(p1),'duplicate full masks recognized')
 print('Certificate counts by split:',dict(counts))
 return {'num_worlds':len(worlds),'num_cases':sum(counts.values()),'counts':{str(k):v for k,v in counts.items()},'duplicate_full_case_per_world':True}
if __name__=='__main__':
 d=audit(sys.argv[1] if len(sys.argv)>1 else 'results')
 Path('audit_result.json').write_text(json.dumps(d,indent=2))
