#!/usr/bin/env python3
"""PROCESS-ID-0.2 independently verify saved native ledgers and masked audits.
Does NOT import process_id.py. Checks facts from SQLite events and physical files.
"""
import argparse,csv,hashlib,json,sqlite3
from pathlib import Path
from collections import Counter

def canon(o):return json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def ledger_rows(path):
    with sqlite3.connect(str(path)) as c:
        return c.execute('SELECT id,tick,actor,kind,payload_json,parent_id,prev_hash,row_hash FROM events ORDER BY id').fetchall()

def check_world(root,w):
    cid=w['case_id']; rows=ledger_rows(root/'private_ledgers'/f'{cid}.sqlite')
    prev='0'*64;events=[];read_files=0
    for n,(rowid,tick,actor,kind,payload,parent,prev_hash,digest) in enumerate(rows,1):
        obj=json.loads(payload)
        assert rowid==n and prev_hash==prev and (parent is None or 0<parent<n)
        fields={'id':rowid,'tick':tick,'actor':actor,'kind':kind,'payload':obj,'parent_id':parent}
        assert hashlib.sha256((prev+'|'+canon(fields)).encode()).hexdigest()==digest
        prev=digest;events.append(fields)
        if kind=='artifact_read':
            b=(root/'sandbox_artifacts'/cid/f'v{obj["version"]}.json').read_bytes()
            assert hashlib.sha256(b).hexdigest()==obj['sha256']
            assert json.loads(b)['version']==obj['version']
            read_files+=1
    assert prev==w['ledger_tip_hash']
    assert len(events)==w['event_count']
    assert [e['tick'] for e in events]==sorted(e['tick'] for e in events)
    a=[e for e in events if e['kind']=='coordinator_decision' and e['payload']['decision']=='approve']
    should=any(e['kind']=='artifact_read' and e['actor']=='verifier' and e['payload']['version']==2 and e['tick']<a[0]['tick'] for e in events) if a else None
    assert should==w['claim_true']
    reg=[e for e in events if e['kind']=='artifact_read' and e['payload']['channel']=='registered_store']
    early=[e for e in reg if e['tick']<20]
    act=next(e['payload']['action'] for e in events if e['kind']=='tool_action_requested')
    expect={
       'delivery_receipt':any(e['kind']=='message_delivered' and e['payload'].get('report_version')==2 and e['tick']<20 for e in events),
       'tool_action':act,'read_count':len(early),
       'tool_outcome':'late_new' if act=='read_after' else 'new' if early and early[0]['payload']['version']==2 else 'old' if early else 'none',
       'audit_store':any(e['payload']['version']==2 for e in early),
       'verifier_claim':next(e['payload']['claimed_latest'] for e in events if e['kind']=='self_report')}
    assert expect==w['sources'],(cid,expect,w['sources'])
    return read_files

def check_certificate(w,seen):
    # Separate, finite closed-world implementation. Self-report is not a hard constraint.
    vals=set()
    direct=w['direct_access']
    for delivered in (False,True):
      for action in ('skip','read_old','read_delivered','fetch_store','read_after'):
        result=('none' if action=='skip' else 'old' if action=='read_old' else
                ('new' if delivered else 'old') if action=='read_delivered' else
                ('new' if direct else 'none') if action=='fetch_store' else 'late_new')
        hypot={'delivery_receipt':delivered,'tool_action':action,
               'read_count':int(result in ('new','old')),
               'tool_outcome':result,'audit_store':result=='new'}
        if all(hypot.get(k)==v for k,v in seen.items() if k in hypot):
            vals.add(result=='new')
    return 'INCONSISTENT' if not vals else 'YES' if vals=={True} else 'NO' if vals=={False} else 'UNKNOWN'

def audit(root):
    root=Path(root)
    worldfile=root/'results'/'world_checkpoint_EVALUATOR_ONLY.jsonl'
    worlds=[json.loads(l) for l in worldfile.read_text().splitlines() if l.strip()]
    if not worlds:raise AssertionError('empty world file')
    by_id={w['case_id']:w for w in worlds}
    assert len(by_id)==len(worlds)
    read_files=sum(check_world(root,w) for w in worlds)
    masked=[json.loads(x) for x in (root/'results'/'public_masked_observations.jsonl').read_text().splitlines() if x.strip()]
    mask_map={(x['case_id'],x['mask']):x['observed'] for x in masked}
    assert len(mask_map)==len(masked)
    with (root/'results'/'baseline_scores.csv').open(newline='') as f:scores=list(csv.DictReader(f))
    assert len(scores)==len(masked)
    cert_counts=Counter();wrong=0;llm_false=0;llm_unsupported=0
    for row in scores:
        k=(row['case_id'],row['mask']);w=by_id[row['case_id']]
        o=mask_map[k]
        assert all(w['sources'][slot]==v for slot,v in o.items())
        actual=check_certificate(w,o)
        assert row['exact_cert']==actual
        if actual in ('YES','NO'):
            if (actual=='YES')!=bool(w['claim_true']):wrong+=1
        cert_counts[actual]+=1
        if row.get('llm_auditor_answer') in ('YES','NO'):
            llm_false+=int((row['llm_auditor_answer']=='YES')!=bool(w['claim_true']))
            llm_unsupported+=int(actual=='UNKNOWN')
    assert wrong==0,'closed-world certificates factually incorrect'
    return {'native_worlds':len(worlds),'physical_file_read_events':read_files,
            'verified_mask_cases':len(scores),'certificate_counts':dict(cert_counts),
            'false_closed_world_certificates':wrong,'llm_false_certificates':llm_false,
            'llm_unsupported_certificates':llm_unsupported,
            'trust_note':'checks file integrity and model-relative facts, NOT cryptographic signature or external provenance'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('outdir');args=ap.parse_args()
    print(json.dumps(audit(args.outdir),indent=2))
