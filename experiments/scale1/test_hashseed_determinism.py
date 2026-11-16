"""Regression check: mask selection is independent of Python hash randomization."""
from pathlib import Path
import subprocess, sys, os, json, tempfile

HERE=Path(__file__).resolve().parent
SCRIPT=r'''
import random,json,sys
from scale1_core import make_world,sample_mask,digest
s=int('1234567'); p,records,_=make_world(s,16,'spoof_ack','id')
res={}
for t in ('independent','correlated','targeted'):
    keep=sample_mask(records,p,random.Random(67890),.5,t)
    res[t]={'count':len(keep),'signature':digest(sorted(r['id'] for r in keep))}
print(json.dumps(res,sort_keys=True))
'''
seeds=[1,2,3,7,100]
outs=[]
for v in seeds:
    env=os.environ.copy();env['PYTHONHASHSEED']=str(v)
    env['PYTHONPATH']=str(HERE)
    proc=subprocess.run([sys.executable,'-c',SCRIPT],env=env,text=True,capture_output=True,check=True)
    outs.append(json.loads(proc.stdout))
assert all(x==outs[0] for x in outs),outs
assert 'correlated' in outs[0]
print(f'PASS: all three mask types identical across PYTHONHASHSEED={seeds}')
print(json.dumps(outs[0],indent=2))
