#!/usr/bin/env python3
"""Evidence percolation in XOR factor graphs; exact partition functions from DSU rank.
Exploratory, synthetic: not independent evidence of general LLM-agent behavior.
"""
import argparse,csv,hashlib,json,math,random,time,collections
from pathlib import Path

SIZES=(4096,16384,65536)
BRIDGES=(1,4,16)
P=(.2,.35,.5,.65,.8)
SEEDS=(11,29)
REPS=5
PAIRS_PER_TYPE=32

class DSU:
    def __init__(self,n): self.par=list(range(n));self.sz=[1]*n;self.components=n;self.largest=1
    def find(self,x):
        while self.par[x]!=x:
            self.par[x]=self.par[self.par[x]];x=self.par[x]
        return x
    def union(self,a,b):
        a=self.find(a);b=self.find(b)
        if a==b:return False
        if self.sz[a]<self.sz[b]:a,b=b,a
        self.par[b]=a;self.sz[a]+=self.sz[b];self.components-=1
        self.largest=max(self.largest,self.sz[a]);return True

def seed_of(*xs):
    return int(hashlib.sha256('|'.join(map(str,xs)).encode()).hexdigest()[:15],16)

def make_graph(n,bridges,seed):
    rng=random.Random(seed_of(n,bridges,seed))
    half=n//2
    edges=[]
    for off in (0,half):
        for i in range(half):
            u=off+i
            edges.append((u,off+(i+1)%half))
            for _ in range(2):
                v=off+rng.randrange(half)
                if v!=u:edges.append((u,v))
    for _ in range(bridges):edges.append((rng.randrange(half),half+rng.randrange(half)))
    return edges

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    f=out/'parity_scale_masks.csv'
    hdr=['n','bridges','graphseed','retention','rep','mask_id','n_edges','kept_edges','components','largest_component_fraction','free_energy_per_node','within_identified','cross_identified','n_pairs_each','time_sec']
    stats=collections.Counter();start=time.monotonic()
    with f.open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=hdr);w.writeheader()
        for n in SIZES:
            half=n//2
            for b in BRIDGES:
                for gs in SEEDS:
                    edges=make_graph(n,b,gs)
                    sample_rng=random.Random(seed_of('pairs',n,b,gs))
                    within=[(sample_rng.randrange(half),sample_rng.randrange(half)) for _ in range(PAIRS_PER_TYPE)]
                    cross=[(sample_rng.randrange(half),half+sample_rng.randrange(half)) for _ in range(PAIRS_PER_TYPE)]
                    # Claim truth is a random planted assignment. All edge observations are consistent with it.
                    truth_bits=[sample_rng.getrandbits(1) for _ in range(n)]
                    for p in P:
                        for rep in range(REPS):
                            tm=time.monotonic(); rng=random.Random(seed_of('mask',n,b,gs,p,rep))
                            d=DSU(n);kept=0
                            for u,v in edges:
                                if rng.random()<p:
                                    # Observe parity value truth_bits[u]^truth_bits[v].
                                    # DSU connectivity is the exact row-space test for pairwise parity factors.
                                    kept+=1;d.union(u,v)
                            win=sum(d.find(u)==d.find(v) for u,v in within)
                            cro=sum(d.find(u)==d.find(v) for u,v in cross)
                            # Each CC admits one free binary gauge bit: Z=2^components,
                            # F=-ln(Z)=-components*ln(2), assuming unit hard-constraint factors.
                            id_=hashlib.sha256(f'{n}|{b}|{gs}|{p}|{rep}'.encode()).hexdigest()[:20]
                            row=dict(n=n,bridges=b,graphseed=gs,retention=p,rep=rep,mask_id=id_,n_edges=len(edges),kept_edges=kept,components=d.components,largest_component_fraction=d.largest/n,free_energy_per_node=-d.components*math.log(2)/n,within_identified=win,cross_identified=cro,n_pairs_each=PAIRS_PER_TYPE,time_sec=round(time.monotonic()-tm,4))
                            w.writerow(row);stats['masks']+=1;stats['claim_checks']+=2*PAIRS_PER_TYPE;stats['kept_edges']+=kept
            print('n',n,'masks',stats['masks'],'elapsed',round(time.monotonic()-start,1),flush=True)
    s=collections.defaultdict(lambda:{'n':0,'within':0,'cross':0,'lcc':0.0,'free_energy':0.0,'components':0.0})
    with f.open() as fh:
        for r in csv.DictReader(fh):
            key=(int(r['n']),int(r['bridges']),float(r['retention']))
            z=s[key];z['n']+=1;z['within']+=int(r['within_identified']);z['cross']+=int(r['cross_identified']);z['lcc']+=float(r['largest_component_fraction']);z['free_energy']+=float(r['free_energy_per_node']);z['components']+=int(r['components'])
    summary=[{'n_nodes':key[0],'bridges':key[1],'retention':key[2],'n_masks':v['n'],'within_recoverability':v['within']/(v['n']*PAIRS_PER_TYPE),'cross_recoverability':v['cross']/(v['n']*PAIRS_PER_TYPE),'mean_lcc':v['lcc']/v['n'],'free_energy_per_node':v['free_energy']/v['n'],'mean_components':v['components']/v['n']} for key,v in sorted(s.items())]
    with (out/'parity_scale_summary.csv').open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    manifest={'study':'Parities as a special factor graph; exact evidence deletion and statistical partition function','scope':'synthetic; exact mathematical benchmark; no new theorem or physical thermalization','node_sizes':SIZES,'bridges':BRIDGES,'retentions':P,'graphseeds':SEEDS,'masks_per_cell':REPS,'pairs_per_type':PAIRS_PER_TYPE,'masks':stats['masks'],'claim_checks':stats['claim_checks'],'total_retained_factors_processed':stats['kept_edges'],'elapsed_seconds':round(time.monotonic()-start,2)}
    (out/'parity_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def test_small():
    import itertools
    n=5;bits=[0,1,1,0,1];edges=[(0,1),(1,2),(3,4)]
    for mm in itertools.product((0,1),repeat=len(edges)):
        d=DSU(n)
        kept=[edge for edge,flag in zip(edges,mm) if flag]
        for u,v in kept:d.union(u,v)
        compatible=[]
        for x in itertools.product((0,1),repeat=n):
            if all(x[u]^x[v]==bits[u]^bits[v] for u,v in kept):compatible.append(x)
        assert len(compatible)==2**d.components
        for i in range(n):
            for j in range(n):
                identified=(len({x[i]^x[j] for x in compatible})==1)
                assert identified==(d.find(i)==d.find(j))
    print('small brute force partition/identifiability test PASS',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='parity_results');a=parser.parse_args();test_small();print(json.dumps(run(a.out),indent=2))
