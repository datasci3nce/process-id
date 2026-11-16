import sys, pathlib, json, tempfile, csv, subprocess, os, collections
P=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'src'))
import wiki_missing as W
import wiki_graph as G

def test_official_schema_sample():
    r={'page_id':'dse/TestPage','wiki':'dse','seq':2,'time':'2026-06-15T10:00:00Z','label':'A','body':'some public text'}
    x=W.normalise(r,'official')
    assert x and x['actor']=='A' and x['revision']=='2' and x['body']=='some public text'

def test_hmm_bridge_factorization():
    # a single hidden state with observed left/right neighbors
    uni=collections.Counter({'A':6,'B':4})
    edges=collections.defaultdict(collections.Counter, {'A':collections.Counter({'A':2,'B':4}),'B':collections.Counter({'A':3,'B':1})})
    c={'page_counts':collections.Counter({'A':2,'B':1}),'prev':'A','nxt':'B'}
    rank,p=W.rank(c,uni,edges,'hmm_smooth')
    q={}
    for a in ['A','B']:
        prior=(uni[a]+.1)/(10+.2)
        fw=(edges['A'][a]+3*prior)/(6+3)
        bn=(edges[a]['B']+3*(uni['B']+.1)/(10+.2))/(sum(edges[a].values())+3)
        q[a]=fw*bn
    z=sum(q.values())
    assert abs(p['A']-q['A']/z)<1e-12

def test_no_hidden_label_in_candidate_pool():
    c={'page_counts':collections.Counter({'a':2}),'prev':'a','nxt':'a','label':'SECRET'}
    rank,prob=W.rank(c,collections.Counter({'a':3}),collections.defaultdict(collections.Counter),'hmm_smooth')
    assert 'SECRET' not in prob
    c['label']='OTHER_SECRET'
    assert W.rank(c,collections.Counter({'a':3}),collections.defaultdict(collections.Counter),'hmm_smooth')[1]==prob

def test_masking_no_hidden_event_in_neighbors():
    rows=[]
    for i,a in enumerate(['a','b','c','d']):rows.append(dict(page='P',revision=str(i),ts=str(i),actor=a,body='',rowkey=str(i)))
    cases,_=W.build_cases(rows,3)
    assert all(c['label'] not in c['page_counts'] for c in cases)

def test_page_disjoint():
    assert W.split('P')==W.split('P')
    rows=[dict(page='P',revision=str(i),ts=str(i),actor='a',body='',rowkey=str(i)) for i in range(4)]
    cases,groups=W.build_cases(rows,3)
    u,_=W.markov_train(groups)
    assert bool(u)==(W.split('P')=='train')

def test_graph_edge_exact_mask():
    edges={(str(i),str((i+j)%13)):1 for i in range(13) for j in (1,2,3,4)}
    with tempfile.TemporaryDirectory() as td:
        out=G.study(edges,pathlib.Path(td),max_sources=5,decoys=4)
        assert all(x['n']==out['heldout_links'] for x in out['methods'])
        assert all(x['n']>0 for x in out['methods'] if x['retention']==1.0)
        assert 0<=out['methods'][0]['top1']<=1

def test_removed_true_edge_cannot_be_negative():
    from collections import defaultdict
    # s->u is a TRUE edge that disappeared in a partial observation;
    # u is still visible through an unrelated edge. It must not become a decoy.
    full=defaultdict(set, {'s':{'t','u'}})
    nodes=['s','t','u','v','w']
    indeg={'s':1,'t':1,'u':1,'v':1,'w':1}
    groups=defaultdict(list, {1:nodes})
    d=G.choose_reference_negatives('s','t',nodes,indeg,groups,full,2,'independent',0.5)
    assert set(d)=={'v','w'} and 'u' not in d and 't' not in d

def test_full_vs_observed_neighbors_differ():
    # Check that the previous code's negative pool contains a reference-positive.
    full={'s':{'t','u'}}
    observed={'s':{'t'}}
    nodes=['s','t','u','v']
    old=[n for n in nodes if n not in ('s','t') and n not in observed['s']]
    assert 'u' in old
    from collections import defaultdict
    indeg={'s':1,'t':1,'u':1,'v':1}
    groups=defaultdict(list,{1:nodes})
    fixed=G.choose_reference_negatives('s','t',nodes,indeg,groups,full,1,'independent',0.5)
    assert fixed==['v']

def test_graph_result_no_false_negatives():
    edges={(str(i),str((i+j)%31)):1 for i in range(31) for j in range(1,8)}
    from collections import defaultdict
    full,_=G.adjacency(edges)
    nodes=sorted({v for e in edges for v in e})
    indeg={x:6 for x in nodes}
    groups=defaultdict(list,{2:nodes})
    for s in nodes:
        t=next(iter(sorted(full[s])))
        for retain in (1.,.75,.5,.25):
            n=G.choose_reference_negatives(s,t,nodes,indeg,groups,full,19,'source_correlated',retain)
            assert len(n)==19 and all((s,x) not in edges for x in n)

def test_determinism_two_hashseeds():
    # Portable local test: works in fresh Colab, no mounted archive dependency.
    with tempfile.TemporaryDirectory() as td:
        dd=pathlib.Path(td)
        src=dd/'fixture.csv'
        with open(src,'w',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['object_id','timestamp','actor_id','record_id','object_namespace'])
            w.writeheader()
            for page in range(26):
                for step in range(5):
                    w.writerow({'object_id':f'page{page}',
                                'timestamp':f'2026-06-18T12:{step:02d}:00Z',
                                'actor_id':f'agent{(page+step*3)%7}',
                                'record_id':f'r{page}_{step}', 'object_namespace':'wiki'})
        for seed in ('7','19'):
            subprocess.run([sys.executable,str(P/'src/wiki_missing.py'),'--input',str(src),
                            '--source-type','archive_extract','--out',str(dd/seed)],
                 check=True,stdout=subprocess.DEVNULL,env={**os.environ,'PYTHONHASHSEED':seed})
        for name in ('evaluation_rows.csv','SUMMARY.json'):
            assert (dd/'7'/name).read_bytes()==(dd/'19'/name).read_bytes()

if __name__=='__main__':
    funcs=[(x,obj) for x,obj in list(globals().items()) if x.startswith('test_') and callable(obj)]
    for name,fn in funcs:fn();print('PASS',name)
    print('PASS',len(funcs),'tests')
