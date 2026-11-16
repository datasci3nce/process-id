#!/usr/bin/env python3
"""Reproduce source-paired, exploratory bootstrap for the fixed-candidate Wiki study."""
from __future__ import annotations
import argparse,collections,csv,random,pathlib

def fixed_lcg_bootstrap(d, B=5000):
    x=198341;means=[];n=len(d)
    for _ in range(B):
        sm=0
        for _ in range(n):
            x=(1664525*x+1013904223)&0xffffffff
            j=int((x/4294967296)*n)
            sm+=d[j]
        means.append(sm/n)
    means.sort()
    return sum(d)/n,(means[124],means[4874])

def run(path):
    rows=list(csv.DictReader(open(path)))
    group=collections.defaultdict(dict)
    for r in rows:
        if r['method'] not in ['two_hop','common_in']:continue
        key=(r['mode'],r['p'],r['source'])
        group[key][r['method']]=int(r['gated_top1'])
    for mode in ['independent','source_correlated']:
      for p in [1.0,.5,.25]:
        a=[v for (m,pp,s),v in sorted(group.items()) if m==mode and float(pp)==p]
        if not a:continue
        d=[v['common_in']-v['two_hop'] for v in a]
        mean,ci=fixed_lcg_bootstrap(d)
        print(mode,p,len(a),round(mean,6),tuple(round(x,6) for x in ci))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('rows',type=pathlib.Path);z=a.parse_args();run(z.rows)
