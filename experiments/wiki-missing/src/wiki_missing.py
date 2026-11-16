#!/usr/bin/env python3
"""Real Wiki middle-revision identity reconstruction, explicit candidate/visibility boundaries.
No private missing text is used by the predictors. This is a known-record masking benchmark,
not inference of actual unrecorded revisions or individual agent identity.
"""
from __future__ import annotations
import argparse, collections, csv, gzip, hashlib, json, math, os, pathlib, random, statistics

SEED=20261115

def hashstr(s): return hashlib.sha256(str(s).encode()).hexdigest()[:16]
def stable_int(*s): return int(hashlib.sha256('|'.join(map(str,s)).encode()).hexdigest()[:16],16)
def unpack(obj,paths):
    for path in paths:
        x=obj
        for part in path.split('.'):
            if isinstance(x,dict): x=x.get(part)
            else: x=None
        if isinstance(x,(str,int,float)) and str(x).strip(): return str(x)
    return ''
def normalise(row, source):
    if source=='archive_extract':
        return dict(page=row.get('object_id',''), ts=row.get('timestamp',''),actor=row.get('actor_id',''),
                    revision=row.get('record_id',''),wiki=row.get('object_namespace',''),body='',id=row.get('record_id',''))
    wiki=unpack(row,['wiki','wiki_id','wiki_name','source_wiki'])
    page=unpack(row,['page_key','page_id','page','page_name','page_title','title','page.name','page.title','page.id'])
    revision=unpack(row,['revision_id','rev_id','revision','revision_seq','rev_seq','seq','id','rid','sequence'])
    ts=unpack(row,['write_ts','write_time','write_timestamp','written_at','timestamp','time','created_at','ts','saved_at','write_at','request_time'])
    actor=unpack(row,['label','agent_label','editor_label','editor','username','user','actor_id','actor','agent','editor_name'])
    body=unpack(row,['body','body_text','text','content','full_text','wikitext','source_text','revision.body'])
    if not page or not ts or not revision: return None
    return dict(page=wiki+'/'+page,ts=ts,actor=actor,revision=revision,wiki=wiki,body=body,id=revision)

def load(source, source_type='auto'):
    p=pathlib.Path(source)
    if source_type=='auto': source_type='archive_extract' if p.suffix.lower()=='.csv' else 'official'
    if source_type=='archive_extract':
        with open(p,encoding='utf8',newline='') as f: raw=list(csv.DictReader(f))
    else:
        opener=gzip.open if p.suffix=='.gz' else open
        with opener(p,'rt',encoding='utf8') as f: raw=[json.loads(line) for line in f if line.strip()]
    if not raw: raise ValueError('Empty input.')
    result=[]
    for item in raw:
        row=normalise(item,source_type)
        if row: result.append(row)
    if len(result)<0.9*len(raw):
        keys=sorted(set().union(*(x.keys() for x in raw[:5])))
        raise ValueError(f'FAIL-CLOSED schema coverage {len(result)}/{len(raw)}; sample keys: {keys}. Edit normalise() after inspecting the exact release schema.')
    if source_type=='official' and sum(bool(r['actor']) for r in result)<0.5*len(result):
        keys=sorted(set().union(*(x.keys() for x in raw[:5])))
        raise ValueError(f'FAIL-CLOSED: missing actor labels in over half the official records. Inspect schema keys {keys}.')
    for i,r in enumerate(result):r['rowkey']=str(i)
    # identity must derive from genuine record ID, not a text or content hash
    return result,dict(source_type=source_type,input_rows=len(raw),normalised_rows=len(result),schema_keys=sorted(set().union(*(x.keys() for x in raw[:3]))),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def build_cases(rows, max_cases_per_page=3):
    pages=collections.defaultdict(list)
    for r in rows:pages[r['page']].append(r)
    def sort_key(r):
        rev=r['revision']
        return (0,int(rev),r['ts'],r['rowkey']) if rev.isdecimal() else (1,r['ts'],rev,r['rowkey'])
    groups={p:sorted(v,key=sort_key) for p,v in pages.items()}
    cases=[]
    for page,rs in sorted(groups.items()):
        if len(rs)<3:continue
        # exact identical history rows are excluded to avoid ambiguous event reference
        candidates=[i for i in range(1,len(rs)-1) if rs[i]['actor'] and rs[i-1]['actor'] and rs[i+1]['actor']]
        if not candidates: continue
        # one to three cases per page, selected without Python hash-order dependence
        ordered=sorted(candidates,key=lambda i:stable_int('target-v1',page,rs[i]['revision'],SEED))
        indices=sorted(ordered[:max_cases_per_page])
        for i in indices:
            hidden=rs[i]
            observed=[r for j,r in enumerate(rs) if j!=i]  # hard exclusion: no hidden record anywhere
            actor_counts=collections.Counter(r['actor'] for r in observed if r['actor'])
            cases.append(dict(page=page,prev=rs[i-1]['actor'],nxt=rs[i+1]['actor'],label=hidden['actor'],
                              case_id=hashstr(page+'|'+hidden['revision']),
                              page_counts=actor_counts,prev_body=rs[i-1]['body'],next_body=rs[i+1]['body'],body=hidden['body'],
                              prev_ts=rs[i-1]['ts'],next_ts=rs[i+1]['ts']))
    return cases,groups

def split(page):
    # page-disjoint reproducible split, no target grouping leakage
    return 'train' if stable_int('split-v1',page,SEED)%10<7 else 'test'

def markov_train(groups):
    uni=collections.Counter(); edges=collections.defaultdict(collections.Counter)
    for page,rs in groups.items():
        if split(page)!='train':continue
        labs=[r['actor'] for r in rs if r['actor']]
        uni.update(labs)
        for a,b in zip(labs,labs[1:]):edges[a][b]+=1
    return uni,edges

def rank(case,uni,edges,method):
    pc=case['page_counts']; prev=case['prev']; nxt=case['nxt']
    # Candidate pool: training actors + actors actually visible on this page.  Ground-truth label never inserted.
    candidates=set(uni)|set(pc)
    if not candidates:return [],{}
    # Global transition estimation with prior mixing; both directions factorize through the unknown middle editor.
    k=max(1,len(candidates)); n=sum(uni.values())
    # Numeric scores in log-space: no use of target label or reference identity.
    scores={}
    for a in candidates:
        if method=='global': s=(uni[a]+0.1)/(n+0.1*k)
        elif method=='prev': s=1. if a==prev else 0.
        elif method=='next': s=1. if a==nxt else 0.
        elif method=='page_majority': s=(pc[a]+0.01)/(sum(pc.values())+.01*k)
        elif method=='hmm_filter':
            p0=(uni[a]+0.1)/(n+0.1*k)
            s=(edges[prev][a]+3*p0)/(sum(edges[prev].values())+3)
        elif method=='hmm_smooth':
            p0=(uni[a]+0.1)/(n+0.1*k)
            t0=(edges[prev][a]+3*p0)/(sum(edges[prev].values())+3)
            # back factor P(next | candidate a); unseen edit transitions softened with global prior
            nextprior=(uni[nxt]+0.1)/(n+0.1*k)
            t1=(edges[a][nxt]+3*nextprior)/(sum(edges[a].values())+3)
            s=t0*t1
        elif method=='page_hmm_smooth':
            p0=(uni[a]+0.1)/(n+0.1*k)
            t0=(edges[prev][a]+3*p0)/(sum(edges[prev].values())+3)
            nextprior=(uni[nxt]+0.1)/(n+0.1*k)
            t1=(edges[a][nxt]+3*nextprior)/(sum(edges[a].values())+3)
            loc=(pc[a]+0.5*p0)/(sum(pc.values())+0.5)
            s=t0*t1*loc
        else: raise ValueError(method)
        scores[a]=float(s)
    # Stable tie-breaking; do not use answer position, ids, or truth to rank.
    order=sorted(candidates,key=lambda a:(-scores[a],hashstr(a)))
    z=sum(scores.values())
    return order,{a:(v/z if z else 1./k) for a,v in scores.items()}

def leakage(case):
    text=case['body'].strip(); prev=case['prev_body'].strip();nxt=case['next_body'].strip()
    if not text:return {'has_body':False,'identical_to_neighbor':False,'verbatim_in_neighbor':False}
    return {'has_body':True,'identical_to_neighbor':text==prev or text==nxt,
            'verbatim_in_neighbor':(len(text)>=30 and (text in prev or text in nxt))}

def evaluate(source,out_dir,source_type='auto'):
    out=pathlib.Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    rows,meta=load(source,source_type)
    cases,groups=build_cases(rows)
    train=[c for c in cases if split(c['page'])=='train']
    test=[c for c in cases if split(c['page'])=='test']
    if not test: raise ValueError('No page-disjoint middle-record test cases; evaluation refused.')
    uni,edges=markov_train(groups)
    methods=['global','prev','next','page_majority','hmm_filter','hmm_smooth','page_hmm_smooth']
    results=[]; audit=[]
    for c in test:
        la=leakage(c);audit.append(la)
        for method in methods:
            order,pr=rank(c,uni,edges,method)
            eligible_top5=[x for x in order if pr.get(x,0)>0][:5]
            results.append(dict(case_id=c['case_id'],page_hash=hashstr(c['page']),method=method,
                correct=int(bool(order) and order[0]==c['label']),top5=int(c['label'] in eligible_top5),
                target_in_candidates=int(c['label'] in pr),confidence=round(pr.get(order[0],0),7) if order else 0,
                true_label_prob=round(pr.get(c['label'],0),7),truth_unseen_from_training=int(c['label'] not in uni),
                verbatim_in_neighbor=int(la['verbatim_in_neighbor'])))
    # protect label / hidden text: public exports contain only hashes, aggregated statistics
    with open(out/'evaluation_rows.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['case_id','page_hash','method','correct','top5','target_in_candidates','confidence','true_label_prob','truth_unseen_from_training','verbatim_in_neighbor']);writer.writeheader();writer.writerows(results)
    summary={'status':'COMPLETED','source':meta,'n_pages':len(groups),'n_histories':len(rows),
        'train_pages':sum(split(p)=='train' for p in groups),'test_pages':sum(split(p)=='test' for p in groups),
        'train_mask_cases':len(train),'test_mask_cases':len(test),
        'methods':{},'body_carryover_audit':{'n_test_cases_with_bodies':sum(a['has_body'] for a in audit),'verbatim_in_neighbor':sum(a['verbatim_in_neighbor'] for a in audit),'identical_to_neighbor':sum(a['identical_to_neighbor'] for a in audit)},
        'limitations':['Known recorded revision masked; not truly unobserved private events','Editor label is not a verified unique agent identity','No reference mechanism class for causal identifiability','Missing entire revision; target is edit label, not reconstructed message text','Correlated within-page test cases; no independent-case confidence claim']}
    for m in methods:
        xs=[r for r in results if r['method']==m]
        summary['methods'][m]={'n':len(xs),'top1':sum(r['correct'] for r in xs)/len(xs) if xs else None,
            'top5':sum(r['top5'] for r in xs)/len(xs) if xs else None,
            'candidate_coverage':sum(r['target_in_candidates'] for r in xs)/len(xs) if xs else None}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
    (out/'INPUT_SCHEMA.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!='limitations'},indent=2))
    return summary

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--out',required=True);a.add_argument('--source-type',default='auto',choices=['auto','official','archive_extract'])
    z=a.parse_args();evaluate(z.input,z.out,z.source_type)
