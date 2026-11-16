#!/usr/bin/env python3
"""Known-edge deletion/percolation control on real derived Wiki graph.
Never interpret a held-out graph edge as proof of a private information transfer.
"""
import argparse, collections, csv, hashlib, json, math, pathlib

SALT='wiki-edge-2026-v1.1'

# v0.1.1 evaluation amendment, before full graph scoring:
# The evaluator has access to the full published reference edge set exclusively
# for establishing valid negatives. The scoring models receive ONLY the masked
# adjacency. A deleted published edge must NEVER become a negative example.
def choose_reference_negatives(source, target, visible_nodes, observed_indeg, indeg_groups,
                               full_out, n_decoys, mode, retain):
    """Select valid missing-link negatives from reference-graph non-neighbors.

    Reference edges are used ONLY to prevent false negatives. Observed graph
    indegree still determines candidate degree buckets. No missing reference
    edges enter feature computation or predictor ranking.
    """
    ref_neighbors=full_out.get(source,set())
    target_bucket=int(math.log2(1+observed_indeg[target]))
    pool=[n for n in indeg_groups[target_bucket]
          if n!=source and n!=target and n not in ref_neighbors]
    if len(pool)<n_decoys:
        pool=[n for n in visible_nodes
              if n!=source and n!=target and n not in ref_neighbors]
    decoys=sorted(pool,key=lambda n:stable('candidate',source,target,n,mode,retain))[:n_decoys]
    if any(n in ref_neighbors for n in decoys):
        raise AssertionError('Reference-positive edge selected as a negative')
    return decoys

def stable(*args):return int(hashlib.sha256('|'.join(map(str,args)).encode()).hexdigest()[:16],16)
def sha(s):return hashlib.sha256(str(s).encode()).hexdigest()[:16]
def load_edges(p):
    edges={}
    with open(p,encoding='utf8') as f:
        for line in f:
            if not line.strip():continue
            r=json.loads(line)
            a=r.get('from',r.get('source'));b=r.get('to',r.get('target'))
            if a is None or b is None:raise ValueError('Missing source/target keys: '+str(sorted(r)))
            if a==b:continue
            key=(str(a),str(b));edges[key]=edges.get(key,0)+int(r.get('count',1))
    if not edges:raise ValueError('No non-self directed edges.')
    return edges

def adjacency(edges):
    o=collections.defaultdict(set);inc=collections.defaultdict(set)
    for a,b in edges:
        o[a].add(b);inc[b].add(a)
    return o,inc

def study(edges,out,max_sources=800, decoys=19):
    dest=pathlib.Path(out);dest.mkdir(parents=True,exist_ok=True)
    out_full,in_full=adjacency(edges)
    test_sources=[s for s in sorted(out_full) if len(out_full[s])>=2 and stable('holdout-source',s)%5==0]
    test_sources=sorted(test_sources,key=lambda s:stable('subset',s))[:max_sources]
    # Evaluation secrets never placed in observed graph.
    held={(s,min(out_full[s],key=lambda t:stable('heldout-edge',s,t))) for s in test_sources}
    full_nodes=sorted(set(out_full)|set(in_full))
    rows=[];configs=[]
    for mode in ['independent','source_correlated']:
      for retain in [1.0,.75,.50,.25]:
        public={edge for edge in edges if edge not in held}
        if mode=='independent':
            public={edge for edge in public if stable('drop',edge[0],edge[1])%10000 < int(retain*10000)}
        else:
            public={edge for edge in public if stable('drop-source',edge[0])%10000 < int(retain*10000)}
        o,inc=adjacency({e:edges[e] for e in public})
        # Known-node restriction: a node absent from every observed edge is NOT disclosed to the auditor.
        nodes=sorted(set(o)|set(inc))
        indeg={n:len(inc[n]) for n in nodes}
        groups=collections.defaultdict(list)
        for n in nodes:groups[int(math.log2(1+indeg[n]))].append(n)
        ct=0;eligible_count=0
        for s,t in sorted(held):
            if s not in indeg or t not in indeg:
                # Count as unavailable, NOT an easier conditional subset with a different denominator.
                for method in ('random','degree','two_hop','common_in','path3'):
                    rows.append(dict(source_hash=sha(s),target_hash=sha(t),mask=mode,retention=retain,
                        method=method,rank=0,top1=0,mrr=0.,source_degree=len(o[s]),n_candidates=0,eligible=0))
                ct+=1;continue
            # Both endpoints remain observed from other edges, so this is strictly known-node reconstruction.
            negs=choose_reference_negatives(s,t,nodes,indeg,groups,out_full,decoys,mode,retain)
            if len(negs)<decoys:
                for method in ('random','degree','two_hop','common_in','path3'):
                    rows.append(dict(source_hash=sha(s),target_hash=sha(t),mask=mode,retention=retain,
                        method=method,rank=0,top1=0,mrr=0.,source_degree=len(o[s]),n_candidates=0,eligible=0))
                ct+=1;continue
            eligible_count+=1
            assert (s,t) in held and all((s,n) not in edges for n in negs), 'False-negative candidate in reference graph'
            options=[t]+negs
            scores={m:{} for m in ('random','degree','two_hop','common_in','path3')}
            for cand in options:
                scores['random'][cand]=stable('blind-uniform',s,cand,mode,retain)/2**64
                scores['degree'][cand]=indeg[cand]
                scores['two_hop'][cand]=sum(int(cand in o[mid]) for mid in o[s])
                scores['common_in'][cand]=len(inc[s]&inc[cand])
                scores['path3'][cand]=sum(sum(int(cand in o[k]) for k in o[mid]) for mid in o[s])
            for method,sc in scores.items():
                ranked=sorted(options,key=lambda x:(-sc[x],stable('tie',x,s)))
                rank=ranked.index(t)+1
                rows.append(dict(source_hash=sha(s),target_hash=sha(t),mask=mode,retention=retain,
                     method=method,rank=rank,top1=int(rank==1),mrr=round(1/rank,8),
                     source_degree=len(o[s]),n_candidates=len(options),eligible=1))
            ct+=1
        configs.append(dict(mask=mode,retention=retain,retained_edges=len(public),test_links_scored=ct,eligible_cases=eligible_count))
    fields=list(rows[0]) if rows else []
    if not rows:raise ValueError('No test edges scored; abort.')
    with open(dest/'edge_scores.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    table=[]
    for mode in ['independent','source_correlated']:
      for retain in [1.0,.75,.5,.25]:
       for method in ['random','degree','two_hop','common_in','path3']:
        subset=[r for r in rows if r['mask']==mode and r['retention']==retain and r['method']==method]
        table.append(dict(mask=mode,retention=retain,method=method,n=len(subset),top1=sum(r['top1'] for r in subset)/len(subset) if subset else None,mrr=sum(r['mrr'] for r in subset)/len(subset) if subset else None,eligible=sum(r['eligible'] for r in subset)))
    summary={'source_edges_unique':len(edges),'source_nodes':len(full_nodes),'heldout_links':len(held),
             'edge_mask_configs':configs,'methods':table,
             'negative_sampling':{'revision':'v0.1.1','rule':'Only evaluator-side reference-graph non-neighbors can be decoys; predictor features use observed graph only',
                                  'reference_positive_decoys':0},
             'limitations':['Derived mention/interaction graph edges, not authenticated causal transfers','Known-node known-edge task; the test edge is not a previously unrecorded action','Only selected source nodes and matched distractors tested','Published underlying graph is potentially a selected/derived sample']}
    (dest/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'edges':len(edges),'heldout':len(held),'summary_rows':len(table)},indent=2))
    return summary

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--edges',required=True);a.add_argument('--out',required=True);a.add_argument('--max-sources',type=int,default=800);z=a.parse_args()
 study(load_edges(z.edges),z.out,z.max_sources)
