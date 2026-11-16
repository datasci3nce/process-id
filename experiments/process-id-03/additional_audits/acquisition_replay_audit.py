"""Standalone acquisition-trace audit for PROCESS-ID-0.3; no generator imports."""
import sys, json, hashlib, sqlite3, collections
from pathlib import Path

root=Path(sys.argv[1]); result_dir=root/'results'
read=lambda name:[json.loads(x) for x in (result_dir/name).read_text().splitlines() if x.strip()]
worlds={w['case_id']:w for w in read('worlds_EVALUATOR_ONLY.jsonl')}
rows=read('acquisition_traces_EVALUATOR_ONLY.jsonl')
seed=20261115

def hval(*args):
    bits=json.dumps(list(args),sort_keys=True,separators=(',', ':'),ensure_ascii=False)
    return int(hashlib.sha256(bits.encode()).hexdigest()[:16],16)

def prove(p, observed):
    reg_possible=(p['tool_action']=='read_delivered' and p['delivery_receipt']) or (p['tool_action']=='fetch_store' and p['direct_access'])
    r=(False,True) if reg_possible else (False,)
    states=set(rv or av for rv in r for av in (False,True) if observed.get('registered',rv)==rv and observed.get('auxiliary',av)==av)
    assert states
    return 'YES' if states=={True} else 'NO' if states=={False} else 'UNKNOWN'

def receipts_from_ledger(case):
    con=sqlite3.connect(root/'private_ledgers'/f'{case}.sqlite')
    ev=[(t,k,json.loads(blob)) for t,k,blob in con.execute('SELECT tick,kind,payload from events')]
    con.close()
    return {c:any(t<20 and kind=='artifact_read' and p.get('channel')==c and p.get('version')==2 for t,kind,p in ev) for c in ('registered','auxiliary')}

cases=collections.Counter()
for idx, row in enumerate(rows):
    w=worlds[row['case_id']]
    public=w['public']
    actual=receipts_from_ledger(row['case_id'])
    order=('registered','auxiliary') if row['policy']=='registered_first' else ('auxiliary','registered') if row['policy']=='auxiliary_first' else ('registered','auxiliary') if ((public['tool_action']=='read_delivered' and public['delivery_receipt']) or (public['tool_action']=='fetch_store' and public['direct_access'])) else ('auxiliary','registered')
    costs={'registered':1,'auxiliary':2}
    seen={}; spent=0; trace=[]
    for channel in order:
        cost=costs[channel]
        if spent+cost>2: continue
        if prove(public,seen)!='UNKNOWN':break
        spent+=cost
        q=row['availability']
        avail=(q==1.0) or (hval('availability',seed,q,row['pair_id'],channel)%1_000_000 < int(q*1_000_000))
        if avail:seen[channel]=actual[channel]
        trace.append({'source':channel,'cost':cost,'retrieved':avail,'certificate':prove(public,seen)})
    expected=prove(public,seen)
    if (row['trace']!=trace or row['status']!=expected or row['spent']!=spent or row['truth']!=w['truth']):
        print('MISMATCH',idx,row['case_id'],row['policy'],'expected',expected,trace,'actual',row['status'],row['trace']);sys.exit(1)
    cases[(row['split'],row['availability'],row['policy'],expected)]+=1
print('FULL REPLAY PASS',len(rows),'acquisition records including source availability and per-step certificates')
print('Held-out cert counts:')
for (split,q,pol,status),n in sorted(cases.items()):
    if split=='test':print(q,pol,status,n)