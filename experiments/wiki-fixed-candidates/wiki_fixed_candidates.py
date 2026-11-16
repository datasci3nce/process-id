#!/usr/bin/env python3
"""Fixed-candidate Wiki held-out edge re-evaluation.

Uses source graph commit e152f85f9032a8e4a55dade4b7990defe5e138c9.
Reference adjacency is used *only by evaluator* to select non-edge decoys.
Predictor sees masked adjacency and fixed supplied candidate identities.
Do not redistribute original published graph; rerun from source.
"""
import argparse, collections, csv, hashlib, json, math, pathlib, random

RAW_URL = ('https://raw.githubusercontent.com/JoshuaDavid/WikiAgentSwarmInvestigation/'
           'e152f85f9032a8e4a55dade4b7990defe5e138c9/'
           'analyses/agent-graph/outputs/edges.jsonl')

def stable(*parts):
    return int(hashlib.sha256('|'.join(map(str, parts)).encode()).hexdigest()[:16], 16)

def load_edges(path):
    edges={}
    with open(path,encoding='utf-8') as f:
        for ln in f:
            if not ln.strip(): continue
            obj=json.loads(ln); s,t=str(obj['from']),str(obj['to'])
            if s!=t: edges[s,t]=edges.get((s,t),0)+int(obj.get('count',1))
    return edges

def adj(edges):
    out,inc=collections.defaultdict(set),collections.defaultdict(set)
    for s,t in edges: out[s].add(t);inc[t].add(s)
    return out,inc

def setup(edges):
    fout,finc=adj(edges)
    sources=[s for s in sorted(fout) if len(fout[s])>=2 and stable('holdout-source',s)%5==0]
    sources=sorted(sources,key=lambda s:stable('subset',s))[:800]
    held=sorted((s,min(fout[s],key=lambda t:stable('heldout-edge',s,t))) for s in sources)
    H=set(held);base={e:weight for e,weight in edges.items() if e not in H}
    bo,bi=adj(base);nodes=sorted(set(bo)|set(bi))
    deg={n:len(bi[n]) for n in nodes}
    buckets=collections.defaultdict(list)
    for n in nodes:buckets[int(math.log2(1+deg[n]))].append(n)
    return fout,held,base,nodes,deg,buckets

def candidates(fout,held,nodes,deg,buckets,seed='fixed-candidate'):
    res={}
    for s,t in held:
        b=int(math.log2(1+deg[t])); pool=[n for n in buckets[b] if n not in (s,t) and n not in fout[s]]
        if len(pool)<19:pool=[n for n in nodes if n not in (s,t) and n not in fout[s]]
        assert len(pool)>=19
        dec=sorted(pool,key=lambda n:stable(seed,s,t,n))[:19]
        assert not set(dec)&fout[s]
        res[s]=[t]+dec
    return res

def eval_graph(edges,seed='fixed-candidate'):
    fout,held,base,nodes,deg,buckets=setup(edges)
    options=candidates(fout,held,nodes,deg,buckets,seed)
    records=[];configs=[]
    for mode in ['independent','source_correlated']:
        for p in (1.,.75,.5,.25):
            if mode=='independent':
                obs={e:w for e,w in base.items() if stable('drop',e[0],e[1])%10000<int(p*10000)}
            else:
                obs={e:w for e,w in base.items() if stable('drop-source',e[0])%10000<int(p*10000)}
            o,inc=adj(obs);seen=set(o)|set(inc)
            configs.append(dict(mode=mode,p=p,retained=len(obs),eligible=sum(s in seen and t in seen for s,t in held)))
            for s,t in held:
                opts=options[s];eligible=int(s in seen and t in seen)
                sm={m:{} for m in ['degree','two_hop','common_in','path3']}
                for c in opts:
                    sm['degree'][c]=len(inc[c]);sm['two_hop'][c]=sum(c in o[mid] for mid in o[s]);
                    sm['common_in'][c]=len(inc[s]&inc[c]);
                    sm['path3'][c]=sum(sum(c in o[k] for k in o[mid]) for mid in o[s])
                for method,sc in sm.items():
                    ranked=sorted(opts,key=lambda x:(-sc[x],stable('tie',x,s)))
                    rank=ranked.index(t)+1
                    records.append(dict(source=s,target=t,mode=mode,p=p,method=method,rank=rank,
                                        top1=int(rank==1),gated_top1=int(rank==1)*eligible,
                                        mrr=1/rank,gated_mrr=eligible/rank,eligible=eligible))
    return records,configs,held

def summarize(rows):
    m=collections.defaultdict(list)
    for r in rows:m[(r['mode'],r['p'],r['method'])].append(r)
    return [dict(mode=k[0],p=k[1],method=k[2],n=len(v),eligible=sum(r['eligible'] for r in v),
                 top1=sum(r['top1'] for r in v),gated_top1=sum(r['gated_top1'] for r in v),
                 mrr=sum(r['mrr'] for r in v)/len(v),gated_mrr=sum(r['gated_mrr'] for r in v)/len(v))
            for k,v in sorted(m.items())]

def main():
    a=argparse.ArgumentParser();a.add_argument('--edges',type=pathlib.Path,required=True);a.add_argument('--out',type=pathlib.Path,required=True)
    a.add_argument('--candidate-seed',default='fixed-candidate');z=a.parse_args();z.out.mkdir(parents=True,exist_ok=True)
    raw=z.edges.read_bytes()
    git_sha=hashlib.sha1((f'blob {len(raw)}\0').encode()+raw).hexdigest()
    if len(raw)>500_000: assert git_sha=='55af9d43bfa79d60c3c3c48cd8381ec8b7ddd671', f'Pinned Git blob mismatch: {git_sha}'
    ed=load_edges(z.edges);rows,configs,held=eval_graph(ed,z.candidate_seed)
    if len(ed)==11177:
        assert len(held)==199 and len(set(n for e in ed for n in e))==1958
    # Core invariant: 100% retention same graph, candidate set, tie order -> identical ranking.
    for method in ['degree','two_hop','common_in','path3']:
        pairs={(r['source'],r['mode']):r['rank'] for r in rows if r['p']==1 and r['method']==method}
        for s,t in held:assert pairs[s,'independent']==pairs[s,'source_correlated']
    with open(z.out/'ranking_rows.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    summ=summarize(rows)
    with open(z.out/'summary.csv','w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(summ[0]));wr.writeheader();wr.writerows(summ)
    (z.out/'metadata.json').write_text(json.dumps(dict(source=RAW_URL,unique_edges=len(ed),held=len(held),
                         candidate_seed=z.candidate_seed,configs=configs),indent=2))
    print('unique_edges',len(ed),'held',len(held)); print('fixed p1',[(x['method'],x['top1'],x['gated_top1']) for x in summ if x['p']==1 and x['mode']=='independent'])
    print('gated p25',[(x['mode'],x['method'],x['gated_top1']) for x in summ if x['p']==.25 and x['method'] in ('two_hop','common_in')])

if __name__=='__main__':main()
