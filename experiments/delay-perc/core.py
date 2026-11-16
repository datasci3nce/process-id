"""Discrete delayed transmission, missing simulated channel-status records, and exact claim identification.

Only the experiment generator/evaluator may read world['private_edges']; scoring functions
below accept public case dictionaries with potential edges and selectively retained simulated observations.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
import numpy as np

ALLOWED_DELAYS = (1, 2, 4, 6)
INF = 10**8


def shortest(n, edges, *, source=0, target=None):
    """Topologically ordered directed acyclic graph shortest arrival time."""
    if target is None: target=n-1
    d=[INF]*n; d[source]=0
    for u,v,w in edges:
        if d[u]<INF:
            t=d[u]+int(w)
            if t<d[v]: d[v]=t
    return d[target]


def worlds_graph(n, rng):
    """Five-layer directed graph; backbone ensures a potential source-target path."""
    interiors=list(range(1,n-1)); layers=[[0]]
    for a in np.array_split(np.asarray(interiors,dtype=int),4):
        layers.append([int(z) for z in a])
    layers.append([n-1])
    edge_set=set()
    backbone=[int(rng.choice(l)) for l in layers[1:-1]]
    path=[0]+backbone+[n-1]
    edge_set.update(zip(path[:-1],path[1:]))
    for k in range(len(layers)-1):
        upper=layers[k+1]
        for u in layers[k]:
            choices=min(len(upper), 2 if k==0 else int(rng.choice([1,2,3],p=[.35,.50,.15])))
            for v in rng.choice(upper,size=choices,replace=False): edge_set.add((u,int(v)))
    # Optional stage-skipping channels, with known potential topology.
    for k in range(len(layers)-2):
        if rng.random()<.22:
            u=int(rng.choice(layers[k]));v=int(rng.choice(layers[k+2]));edge_set.add((u,v))
    return sorted(edge_set)


def make_world(world_id,n,split,seed):
    rng=np.random.default_rng(int(seed)); graph=worlds_graph(n,rng)
    source_congestion={u:bool(rng.random()<.36) for u,v in graph}
    private=[]
    for u,v in graph:
        if split=='development':
            q=.70; fast=.60
        else:
            q=.46 if source_congestion[u] else .83
            fast=.18 if source_congestion[u] else .73
        live=bool(rng.random()<q)
        if live:
            delay=int(rng.choice([1,2] if rng.random()<fast else [4,6]))
        else:
            delay=None
        private.append((u,v,live,delay))
    # deadline is set using potential graph alone (not private outcomes).
    earliest=shortest(n,[(u,v,1) for u,v in graph]);deadline=int(earliest+rng.choice([2,4,6,8]))
    true_time=shortest(n,[(u,v,d) for u,v,live,d in private if live])
    return {'world_id':world_id,'n':n,'split':split,'deadline':deadline,
            'graph':graph,'private_edges':private,'truth':int(true_time<=deadline),
            'native_arrival':int(true_time) if true_time<INF else None}


def make_mask(world,kind,p,seed):
    rng=np.random.default_rng(int(seed));edges=world['private_edges'];m=len(edges)
    if kind=='independent':
        keep=rng.random(m)<p
    elif kind=='source_correlated':
        sources=sorted({u for u,_,_,_ in edges});groups={u:bool(rng.random()<p) for u in sources}
        keep=np.array([groups[u] for u,_,_,_ in edges],dtype=bool)
    elif kind=='targeted':
        # Remove sources in descending out-degree order, ties resolved deterministically.
        deg=defaultdict(int)
        for u,_,_,_ in edges:deg[u]+=1
        sources=sorted(deg,key=lambda u:(-deg[u],u))
        dropped=set();removed=0
        for u in sources:
            if removed>=round((1-p)*m):break
            dropped.add(u);removed+=deg[u]
        keep=np.array([u not in dropped for u,_,_,_ in edges],dtype=bool)
    else: raise ValueError(kind)
    obs=[]
    for i,(u,v,live,delay) in enumerate(edges):
        if keep[i]:obs.append({'edge_idx':i,'status':'live' if live else 'failed','delay':delay})
    return {'world_id':world['world_id'],'n':world['n'],'deadline':world['deadline'],
            'potential_edges':[[int(u),int(v)] for u,v in world['graph']],
            'observations':obs,'mask_kind':kind,'retention_requested':float(p),
            'retention_actual':float(np.mean(keep)),'mask_seed':int(seed)}


def build_edge_views(case,missing_fast=1):
    g=case['potential_edges'];obs={int(x['edge_idx']):x for x in case['observations']}
    proved=[];potential=[];proved_static=[];potential_static=[]
    for idx,(u,v) in enumerate(g):
        o=obs.get(idx)
        if o is None:
            potential.append((u,v,missing_fast));potential_static.append((u,v,1))
        elif o['status']=='live':
            proved.append((u,v,o['delay']));potential.append((u,v,o['delay']))
            proved_static.append((u,v,1));potential_static.append((u,v,1))
    return proved,potential,proved_static,potential_static


def certify(case):
    """Exact 3-state reference certificate under arbitrary unknown status and allowed delays."""
    proven,possible,_,_=build_edge_views(case)
    d1=shortest(case['n'],proven);d2=shortest(case['n'],possible)
    if d1<=case['deadline']: return 'YES'
    if d2>case['deadline']: return 'NO'
    return 'UNKNOWN'


def scalar_features(case):
    proved,possible,sp,sa=build_edge_views(case)
    deadline=case['deadline'];n=case['n'];m=len(case['potential_edges'])
    num=len(case['observations']);nlive=sum(o['status']=='live' for o in case['observations'])
    npfail=num-nlive
    dp=shortest(n,proved);da=shortest(n,possible)
    dsp=shortest(n,sp);dsa=shortest(n,sa)
    safe=lambda d:float(min(d,deadline+10))
    # shared static features have no latency information
    static=[n,m,deadline,num/max(1,m),nlive/max(1,m),npfail/max(1,m),
            float(dsp<INF),float(dsa<INF),safe(dsp),safe(dsa),
            int(case.get('mask_kind')=='source_correlated'),int(case.get('mask_kind')=='targeted')]
    # temporal extension uses observed latencies and optimistic 1-unit unknown edge completion
    timed=[safe(dp),safe(da),float(dp<=deadline),float(da<=deadline),
           float(deadline-safe(dp)),float(deadline-safe(da)),
           max(0.,float(safe(dp)-safe(da)))]
    return static,timed


def montecarlo_prob(case,n_draws,seed,q,delay_dist):
    rng=np.random.default_rng(int(seed));n=int(case['n']);m=len(case['potential_edges'])
    records={int(x['edge_idx']):x for x in case['observations']}
    a=np.full((n_draws,n),INF,dtype=np.int32);a[:,0]=0
    for k,(u,v) in enumerate(case['potential_edges']):
        obs=records.get(k)
        if obs is not None and obs['status']=='failed': continue
        if obs is not None:
            time=a[:,u]+int(obs['delay'])
        else:
            live=rng.random(n_draws)<q
            delay=rng.choice(np.array(ALLOWED_DELAYS),size=n_draws,p=delay_dist)
            time=np.where(live,a[:,u]+delay,INF)
        a[:,v]=np.minimum(a[:,v],time)
    return float(np.mean(a[:,n-1]<=case['deadline']))


def dde_surrogate(case,q,delay_dist,with_delay=True):
    """Explicit Euler discretization of a linear delayed influence system (not token dynamics)."""
    n=case['n'];deadline=case['deadline'];T=deadline+1
    o={int(z['edge_idx']):z for z in case['observations']}
    arr=[];deg=np.zeros(n,dtype=float)
    unknown_tau=int(round(float(np.dot(np.array(ALLOWED_DELAYS),delay_dist))))
    for i,(u,v) in enumerate(case['potential_edges']):
        if i in o:
            if o[i]['status']=='failed': continue
            w=1.;tau=int(o[i]['delay'])
        else:w=q;tau=unknown_tau
        if not with_delay:tau=0
        arr.append((u,v,w,tau));deg[v]+=1
    states=np.zeros((T+1,n),dtype=float);states[:,0]=1.
    gamma=.55;gain=1.5
    for t in range(T):
        states[t+1,1:]=(1-gamma)*states[t,1:]
        for u,v,w,tau in arr:
            k=t-tau
            if k>=0:
                states[t+1,v]+=gain*w*states[k,u]/max(1.,deg[v])
        # Keep Euler surrogate stable for a range of graph densities.
        np.clip(states[t+1],0.,30.,out=states[t+1]);states[t+1,0]=1.
    target=states[min(deadline,T),n-1]
    return float(np.log1p(target))


def stable_seed(*args):
    b='|'.join(map(str,args)).encode()
    return int.from_bytes(hashlib.sha256(b).digest()[:8],'big')%(2**32)
