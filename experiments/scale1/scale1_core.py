"""ER SCALE-1: independently instrumented binary artifact handoffs, exact MILP oracle.

Closed-world event topology: attempted transfer edges are public; native success bits,
recipient state, and full receipt ledger are private. This is NOT a benchmark of
unrecorded actions. The reference oracle assumes authenticated records are truthful,
weak acknowledgements may be fabricated, and all candidate transfers are known.
"""
from __future__ import annotations
import hashlib, json, random, math
from dataclasses import dataclass
from collections import defaultdict, deque
import numpy as np
from scipy import sparse
from scipy.optimize import milp, Bounds, LinearConstraint

SIZES=(4,8,16,32,64)
FAMILIES=('direct','relay','retry','spoof_ack','stale_replica')
RETENTIONS=(.25,.5,.75,.9)
MASK_TYPES=('independent','correlated','targeted')
STATUS='sha256:v1-consistent-artifact'


def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def path_truth(n,edges,success):
    """Independent actual delivery propagation. Ignores post-action and v0 edges."""
    got=[False]*n;got[0]=True
    for i in range(1,n):
        got[i]=any(got[e['src']] and success[j] for j,e in enumerate(edges)
                   if e['dst']==i and e['v']=='v1' and e['when']=='before')
    return got


def make_world(seed,n,family,world_id):
    rng=random.Random(seed)
    if family not in FAMILIES:raise ValueError(family)
    # Potential transfers are generated independently of actual success bits.
    arcs=set((i,i+1,'v1','before') for i in range(n-1))
    extra={'direct':2,'relay':2,'retry':3,'spoof_ack':2,'stale_replica':3}[family]
    for _ in range(n*extra):
        a=rng.randrange(n-1);b=rng.randrange(a+1,n)
        v='v0' if family=='stale_replica' and rng.random()<.28 else 'v1'
        arcs.add((a,b,v,'before'))
    for _ in range(max(2,n//3)):
        a=rng.randrange(n-1);b=rng.randrange(a+1,n)
        arcs.add((a,b,'v1','after'))
    ordered=sorted(arcs,key=lambda x:(x[1],x[0],x[2],x[3]))
    edges=[{'id':f'E{i:04d}','src':a,'dst':b,'v':v,'when':w,
            'time':(b+1 if w=='before' else n+2),
            'hash':(STATUS if v=='v1' else 'sha256:stale-v0'),
            'group':f'G{(a+b)//4:03d}'} for i,(a,b,v,w) in enumerate(ordered)]
    success=[]
    prob={'direct':.72,'relay':.58,'retry':.66,'spoof_ack':.56,'stale_replica':.61}[family]
    for e in edges:
        p=prob + (.06 if e['dst']==e['src']+1 else 0)
        success.append(int(rng.random()<p))
    got=path_truth(n,edges,success)
    # Records are generated from the private native trace, never reconstructed from model reports.
    records=[]
    def rec(kind,edge_ids,value,group,signer,extra=None):
        j=len(records)
        records.append({'id':f'R{j:05d}','kind':kind,'edges':edge_ids,'value':value,
                        'group':group,'signer':signer,'meta':extra or {}})
    for j,e in enumerate(edges):
        # Authenticated results for every native execution in private ledger.
        rec('signed_native',[j],success[j],e['group'],'native-executor')
        # Untrusted success acknowledgements; spoof and stale-shift generators change their likelihood.
        spoof_p={'direct':.04,'relay':.06,'retry':.08,'spoof_ack':.62,'stale_replica':.35}[family]
        if success[j]:ack=int(rng.random()<.93)
        else:ack=int(rng.random()<spoof_p)
        rec('weak_ack',[j],ack,e['group'],'untrusted-agent')
    # Cross-event signed batch counts: do NOT expose each constituent status individually.
    # These are genuine aggregate measurements, e.g. number of accepted transfers in a batch.
    shuffled=list(range(len(edges)));rng.shuffle(shuffled)
    for k in range(0,min(len(edges)//2,n*2)*2,2):
        a,b=shuffled[k:k+2]
        rec('signed_batch',[a,b],int(success[a]+success[b]),f'B{k//2//3:03d}','native-aggregator')
    # Authenticated node inbox snapshots are rare; target snapshot is not guaranteed.
    snap_nodes=set(rng.sample(range(1,n),max(1,n//8)))
    for i in sorted(snap_nodes):
        rec('signed_inbox',[],int(got[i]),f'S{i//4:03d}','native-inbox',{'agent':i,'time':'before_action'})
    # Timing and action records are part of the public topology; the truth is not exposed.
    public={'schema':'ER-SCALE-1/1.0','world_id':world_id,'claim':f'agent_{n-1}_received_v1_before_action',
            'n_agents':n,'source':0,'target':n-1,'artifact_hash':STATUS,'edges':edges}
    private={'world_id':world_id,'family':family,'edge_native_success':success,
             'inbox_before_action':[int(x) for x in got], 'claim_truth':int(got[-1]),
             'native_ledger_hash':digest({'edges':edges,'native_success':success})}
    return public,records,private


def sample_mask(records, public, rng, retention, typ):
    if typ=='independent':
        keep=[r for r in records if rng.random()<retention]
    elif typ=='correlated':
        groups=sorted({r['group'] for r in records})
        kept_groups={g for g in groups if rng.random()<retention}
        keep=[r for r in records if r['group'] in kept_groups]
    elif typ=='targeted':
        # Mechanism-aware *masking* protocol sees topology + record types only, never native truth.
        # Retain background preferentially; selectively delete receipts on target-relevant paths.
        n=public['n_agents'];edges=public['edges']
        upstream={n-1};downstream={0}
        change=True
        while change:
            prev=len(upstream)+len(downstream)
            for e in edges:
                if e['dst'] in upstream:upstream.add(e['src'])
                if e['src'] in downstream:downstream.add(e['dst'])
            change=prev!=len(upstream)+len(downstream)
        pivotal=set(j for j,e in enumerate(edges) if e['src'] in downstream and e['dst'] in upstream and e['v']=='v1' and e['when']=='before')
        weights=[3.0 if (r['kind']=='signed_native' and r['edges'] and r['edges'][0] in pivotal) or
                 (r['kind']=='signed_batch' and any(i in pivotal for i in r['edges'])) or
                 (r['kind']=='signed_inbox' and r['meta']['agent']==n-1) else 1.0 for r in records]
        # Keep exactly approximately p fraction, but preference to remove informative receipts.
        k=round(retention*len(records))
        priorities=[(rng.random()**w,-j) for j,w in enumerate(weights)]
        # Larger scores more likely retained for lower w; all weights independent of outcomes.
        order=sorted(range(len(records)),key=lambda i:priorities[i],reverse=True)
        keep=[records[j] for j in sorted(order[:k])]
    else:raise ValueError(typ)
    return keep


class ExactOracle:
    """MILP exact finite Boolean feasibility oracle; no solver access to true native bits.
    Returns identification with separate feasible claim=0 and claim=1 checks.
    """
    def __init__(self,public):
        self.public=public;self.edges=public['edges'];self.n=public['n_agents'];self.m=len(self.edges)
        # all native success variables e, reception r, and effective delivery z for v1/pre edges
        self.active=[j for j,e in enumerate(self.edges) if e['v']=='v1' and e['when']=='before']
        self.zi={j:self.m+self.n+k for k,j in enumerate(self.active)}
        self.vars=self.m+self.n+len(self.active)
        self.r=lambda i:self.m+i
        rows=[];lo=[];hi=[]
        def add(coefs,lb=-np.inf,ub=np.inf):rows.append(coefs);lo.append(lb);hi.append(ub)
        add({self.r(0):1},1,1)
        incoming=defaultdict(list)
        for j in self.active:
            e=self.edges[j];z=self.zi[j];ru=self.r(e['src'])
            incoming[e['dst']].append(z)
            add({z:1,ru:-1},ub=0)
            add({z:1,j:-1},ub=0)
            add({z:1,ru:-1,j:-1},lb=-1)
        for i in range(1,self.n):
            zs=incoming.get(i,[])
            if not zs:add({self.r(i):1},0,0)
            else:
                for z in zs:add({self.r(i):1,z:-1},lb=0)
                add({self.r(i):1,**{z:-1 for z in zs}},ub=0)
        self.base_rows=rows;self.base_low=lo;self.base_high=hi
        self.lower=np.zeros(self.vars);self.upper=np.ones(self.vars)
        self.cost=np.zeros(self.vars)
        self.integer=np.ones(self.vars,dtype=int)

    def _constraints(self,records,fit):
        rows=list(self.base_rows);low=list(self.base_low);high=list(self.base_high)
        def add(d,a,b):rows.append(d);low.append(a);high.append(b)
        for x in records:
            k=x['kind'];v=int(x['value']);ids=x['edges']
            if k=='signed_native' or (fit and k=='weak_ack'):
                add({ids[0]:1},v,v)
            elif k=='signed_batch':
                # Signed aggregate may constrain multiple unknown status bits jointly.
                add({j:1 for j in ids},v,v)
            elif k=='signed_inbox':
                add({self.r(x['meta']['agent']):1},v,v)
        ii=[];jj=[];vv=[]
        for i,row in enumerate(rows):
            for j,v in row.items():ii.append(i);jj.append(j);vv.append(v)
        A=sparse.coo_matrix((vv,(ii,jj)),shape=(len(rows),self.vars)).tocsr()
        return LinearConstraint(A,np.asarray(low),np.asarray(high))

    def query(self,records,fit=False,time_limit=2.0):
        c=self._constraints(records,fit)
        ans=[]
        for val in (0,1):
            bounds=Bounds(self.lower,self.upper.copy())
            # Fix claim r_target=value by variable bound. No access to true realized claim.
            bounds.lb[self.r(self.n-1)]=val
            bounds.ub[self.r(self.n-1)]=val
            res=milp(self.cost,integrality=self.integer,bounds=bounds,constraints=c,
                     options={'time_limit':time_limit,'presolve':True,'disp':False})
            if res.status==0:ans.append(True)
            elif res.status==2:ans.append(False)
            else:return {'status':'timeout_or_unknown','can_false':None,'can_true':None,
                         'identified':None,'value':None,'solver_status':res.status}
        neg,pos=ans
        return {'status':('inconsistent' if not neg and not pos else 'ok'),
                'can_false':bool(neg),'can_true':bool(pos),
                'identified':bool(neg!=pos),'value':(int(pos) if neg!=pos else None),'solver_status':0}


def receipt_baseline(public,records):
    """Simple sound witness: positive signed path or a signed exact final inbox snapshot."""
    goal=public['target'];n=public['n_agents'];edges=public['edges']
    signed={x['edges'][0]:x['value'] for x in records if x['kind']=='signed_native'}
    signed_snap={x['meta']['agent']:x['value'] for x in records if x['kind']=='signed_inbox'}
    if goal in signed_snap:return int(signed_snap[goal])
    gotten=[False]*n;gotten[0]=True
    for i in range(1,n):
        gotten[i]=any(gotten[e['src']] and signed.get(j)==1 for j,e in enumerate(edges)
                      if e['dst']==i and e['v']=='v1' and e['when']=='before')
    return 1 if gotten[-1] else None


def cheap_features(public,records):
    """Observed-only, variable-size invariant features. No private ledger or oracle."""
    f={'n_agents':public['n_agents'],'n_attempts':len(public['edges']),
       'n_real_attempts':sum(int(e['when']=='before' and e['v']=='v1') for e in public['edges']),
       'n_stale_attempts':sum(int(e['v']!='v1') for e in public['edges']),
       'n_after_action':sum(int(e['when']=='after') for e in public['edges']),
       'n_records':len(records)}
    for kind in ('signed_native','weak_ack','signed_batch','signed_inbox'):
        x=[r for r in records if r['kind']==kind]
        f['count_'+kind]=len(x)
        f['fraction_'+kind]=len(x)/max(1,len(public['edges']))
        f['sum_'+kind]=sum(int(y['value']) for y in x)
    goal=public['target']
    f['target_snap_present']=sum(int(x['kind']=='signed_inbox' and x['meta']['agent']==goal) for x in records)
    f['auth_positive_inbound']=sum(int(r['kind']=='signed_native' and r['value']==1 and
                       public['edges'][r['edges'][0]]['dst']==goal and
                       public['edges'][r['edges'][0]]['v']=='v1' and
                       public['edges'][r['edges'][0]]['when']=='before') for r in records)
    f['auth_negative_inbound']=sum(int(r['kind']=='signed_native' and r['value']==0 and
                       public['edges'][r['edges'][0]]['dst']==goal and
                       public['edges'][r['edges'][0]]['v']=='v1' and
                       public['edges'][r['edges'][0]]['when']=='before') for r in records)
    f['receipt_cert']=float(receipt_baseline(public,records) is not None)
    return f


def jsonl_write(path,rows):
    with open(path,'w') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
