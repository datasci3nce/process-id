#!/usr/bin/env python3
"""Replicated independent-vs-source-group masks on fixed Wiki graph.
Exact same seeded 32-bit mix used in external source-connected audit.
This is a secondary post-hoc sensitivity, not an independently held-out corpus.
"""
from __future__ import annotations
import argparse,collections,csv,json,math,pathlib
from wiki_fixed_candidates import stable,load_edges,setup,candidates,adj

MASK32=(1<<32)-1

def mix(x,rep):
    v=(int(x) ^ ((int(rep)+1)*0x9e3779b1 & MASK32)) & MASK32
    v=((v^(v>>16))*0x85ebca6b)&MASK32
    v=((v^(v>>13))*0xc2b2ae35)&MASK32
    return ((v^(v>>16))&MASK32)/2**32

def calc(edges, seed='fixed-candidate',reps=64):
    fullout,held,base,nodes,deg,buckets=setup(edges)
    opts=candidates(fullout,held,nodes,deg,buckets,seed)
    es=[(s,t,stable('mask_base_edge',s,t)&MASK32,stable('mask_base_source',s)&MASK32) for s,t in base]
    out=[]
    for mode in ['independent','source_correlated']:
     for p in [0.5,0.25]:
      for rep in range(reps):
       masked={(s,t):1 for s,t,ke,ks in es if mix(ke if mode=='independent' else ks,rep)<p}
       o,inc=adj(masked);seen=set(o)|set(inc);cnt2=cntc=elig=only2=onlyc=0
       for s,t in held:
        visible=int(s in seen and t in seen);elig+=visible
        options=opts[s]
        scores2={c:sum(c in o[mid] for mid in o[s]) for c in options}
        scoresc={c:len(inc[s]&inc[c]) for c in options}
        top2=int(min(options,key=lambda c:(-scores2[c],stable('tie',c,s)))==t)*visible
        topc=int(min(options,key=lambda c:(-scoresc[c],stable('tie',c,s)))==t)*visible
        cnt2+=top2;cntc+=topc;only2+=top2 and not topc;onlyc+=topc and not top2
       out.append(dict(mode=mode,p=p,rep=rep,retained=len(masked),eligible=elig,two=cnt2,common=cntc,
                       delta=(cntc-cnt2)/len(held),two_only=only2,common_only=onlyc))
    return out

def main():
    a=argparse.ArgumentParser();a.add_argument('--edges',type=pathlib.Path,required=True);a.add_argument('--out',type=pathlib.Path,required=True)
    z=a.parse_args();z.out.mkdir(parents=True,exist_ok=True)
    edges=load_edges(z.edges);out=calc(edges)
    with open(z.out/'mask_replicates.csv','w',newline='') as f:
        w=csv.DictWriter(f,list(out[0]));w.writeheader();w.writerows(out)
    for mode in ['independent','source_correlated']:
      for p in [0.5,0.25]:
       subset=[r for r in out if r['mode']==mode and r['p']==p]
       print(mode,p,'n',len(subset),'mean two',sum(r['two'] for r in subset)/len(subset)/199,
             'mean common',sum(r['common'] for r in subset)/len(subset)/199,
             'mean delta',sum(r['delta'] for r in subset)/len(subset),
             'common wins',sum(r['delta']>0 for r in subset))
if __name__=='__main__':main()
