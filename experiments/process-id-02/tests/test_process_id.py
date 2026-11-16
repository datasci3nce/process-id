import hashlib, json, os, random, sqlite3, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import process_id as p

class FixedBackend:
    def __init__(self,action='skip',approve=True,claim=True):
        self.action=action;self.approve=approve;self.claim=claim
    def worker(self,task,rng):return {'summary':'This is a test report', 'proposed_total':2}
    def verifier(self,task,context,rng):return {'action':self.action,'statement':'I verified the latest report.', 'claimed_latest':self.claim}
    def coordinator(self,task,context,rng):return {'decision':'approve' if self.approve else 'defer','reason':'test'}

class TestProcessId(unittest.TestCase):
    def test_all_worlds_and_masks_exact_checker(self):
        slots=p.SLOTS
        for direct in (False,True):
            worlds=p.possible_worlds(direct)
            self.assertEqual(len(worlds),10)
            for w in worlds:
                self.assertEqual(p.certify(worlds,w['observations']),'YES' if w['target'] else 'NO')
                for mask in range(1<<len(slots)):
                    observation={slot:w['observations'][slot] for i,slot in enumerate(slots) if mask&(1<<i)}
                    cert=p.certify(worlds,observation)
                    self.assertIn(cert,('YES','NO','UNKNOWN'))
                    if cert in ('YES','NO'):
                        self.assertEqual(cert=='YES',w['target'])
    def test_non_authoritative_claim_never_proves_read(self):
        for direct in (False,True):
            self.assertEqual(p.certify(p.possible_worlds(direct),{'verifier_claim':True}),'UNKNOWN')
            self.assertEqual(p.certify(p.possible_worlds(direct),{'verifier_claim':False}),'UNKNOWN')
    def test_contradiction_not_false_cert(self):
        poss=p.possible_worlds(True)
        self.assertEqual(p.certify(poss,{'tool_action':'skip','audit_store':True}),'INCONSISTENT')
    def test_real_file_actions_and_native_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            for idx,action in enumerate(p.ACTIONS):
                for direct in (False,True):
                    cid=f'pid-{idx*2+int(direct):04d}'
                    w=p.world_execution(tmp,cid,'numerical_report','normal',direct,FixedBackend(action),random.Random(idx*123+8))
                    self.assertTrue(w['approved'])
                    self.assertEqual(p.certify(p.possible_worlds(direct),w['sources']),'YES' if w['claim_true'] else 'NO')
                    for ver in (1,2):
                        self.assertTrue((Path(tmp)/'sandbox_artifacts'/cid/f'v{ver}.json').exists())
                    with sqlite3.connect(str(Path(tmp)/'private_ledgers'/f'{cid}.sqlite')) as db:
                        rows=db.execute('SELECT tick,actor,kind,payload_json FROM events ORDER BY id').fetchall()
                        ticks=[x[0] for x in rows]
                        self.assertEqual(ticks,sorted(ticks))
                        for tick,actor,kind,payload in rows:
                            payload=json.loads(payload)
                            if kind=='artifact_read':
                                b=(Path(tmp)/'sandbox_artifacts'/cid/f'v{payload["version"]}.json').read_bytes()
                                self.assertEqual(hashlib.sha256(b).hexdigest(),payload['sha256'])
    def test_misspecified_hidden_channel_fools_closed_world_certifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=p.world_execution(tmp,'pid-9999','artifact_reconciliation','normal',False,FixedBackend('skip',True),random.Random(9),stress=True)
            self.assertEqual(w['claim_true'],True)
            self.assertEqual(p.certify(p.possible_worlds(False),w['sources']),'NO')
            self.assertTrue(w['stress_hidden_channel'])
    def test_approved_vs_deferred_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=p.world_execution(tmp,'pid-0000','artifact_reconciliation','normal',False,FixedBackend('skip',False),random.Random(3))
            self.assertIsNone(w['claim_true'])
            self.assertFalse(w['approved'])
    def test_ledger_detects_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            l=p.Ledger(Path(tmp)/'e.sqlite')
            l.log(1,'a','x',{'v':2});l.log(2,'b','y',{'v':3})
            self.assertTrue(l.verify())
            l.db.execute("UPDATE events SET payload_json=? WHERE id=1",(json.dumps({'v':999}),))
            l.db.commit()
            with self.assertRaises(AssertionError):l.verify()
            l.close()
    def test_acquisition_never_false_certifies_closed_world(self):
        cases=[]
        for d in (False,True):
            for w in p.possible_worlds(d):
                cases.append((d,w))
        train=[]
        for i,(direct,w) in enumerate(cases):
            train.append({'scenario':'normal','direct_access':direct,'delivered_before':w['delivered_before'],'action':w['action'],'claim_true':w['target']})
        prior=p.train_prior(train)
        for i,(direct,w) in enumerate(cases):
            w2={'scenario':'normal','direct_access':direct,'sources':w['observations'],'case_id':f'pid-{i:04d}'}
            possible=p.possible_worlds(direct)
            for policy in ('random','fixed','adaptive'):
                q=p.acquire(w2,{},possible,prior,policy,4,1.0,'all_hidden',20261115)
                if q['status'] in ('YES','NO'):
                    self.assertEqual(q['status']=='YES',w['target'])
    def test_openrouter_parser_cost_and_cap_without_network(self):
        class FakeResponse:
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self):return json.dumps({'id':'req-1','model':'mock','usage':{'prompt_tokens':90,'completion_tokens':20,'cost':.01},'choices':[{'message':{'content':'{"action":"skip","statement":"none","claimed_latest":false}'}}]}).encode()
        with patch.dict(os.environ,{'OPENROUTER_API_KEY':'TEST-ONLY'},clear=False):
            b=p.OpenRouterAgents('mock',max_spend_usd=.015,max_calls=5)
            with patch('urllib.request.urlopen',return_value=FakeResponse()):
                r=b.call('verifier','test',p.ACTIONS)
                self.assertEqual(r['action'],'skip')
                self.assertEqual(len(b.calls),1)
                self.assertAlmostEqual(b.spent_usd,.01)
                b.call('verifier','test',p.ACTIONS)
                self.assertEqual(len(b.calls),2)
                with self.assertRaises(RuntimeError):b.call('verifier','test',p.ACTIONS)

if __name__=='__main__':unittest.main(verbosity=2)

class TestMockedLiveEndToEnd(unittest.TestCase):
    def test_mock_api_live_backend_full_pipeline_and_resume(self):
        # This is a MOCK API integration test, not a live LLM experiment.
        class FakeResponse:
            def __init__(self,obj):self.obj=obj
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return json.dumps(self.obj).encode()
        count={'n':0}
        def mock_urlopen(request,timeout=0):
            req=json.loads(request.data.decode())
            prompt=req['messages'][1]['content']
            count['n']+=1
            if prompt.startswith('You are the worker.'):
                output={'summary':'Worker generated mock report','proposed_total':2}
            elif prompt.startswith('You are a verifier'):
                output={'action':'read_delivered' if count['n']%2 else 'skip','statement':'Mock report','claimed_latest':True}
            elif prompt.startswith('You are coordinator'):
                output={'decision':'approve','reason':'Mock approval'}
            elif prompt.startswith('Audit the exact claim'):
                output={'answer':'INSUFFICIENT_EVIDENCE','probability_yes':0.5,'explanation':'Mock response'}
            else:raise AssertionError('Unknown prompt '+prompt[:90])
            return FakeResponse({'id':f'mock-{count["n"]}', 'model':'mock/test',
               'usage':{'prompt_tokens':120,'completion_tokens':50,'cost':0.0001},
               'choices':[{'message':{'content':json.dumps(output)}}]})
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'OPENROUTER_API_KEY':'TEST-MOCK-ONLY'}),patch('urllib.request.urlopen',side_effect=mock_urlopen):
            a=p.run(tmp,backend='openrouter',n_per_cell=2,model='mock/test',max_spend_usd=.1)
            self.assertEqual(a['execution_worlds'],12)
            self.assertEqual(a['direct_llm_auditor']['evaluations'],len(list((Path(tmp)/'results'/'llm_audit_checkpoint.jsonl').read_text().splitlines())))
            self.assertTrue(a['all_certificates_factually_correct'])
            self.assertGreater(a['live_api']['billable_calls'],36)
            paid=count['n']
            b=p.run(tmp,backend='openrouter',n_per_cell=2,model='mock/test',max_spend_usd=.1)
            self.assertEqual(count['n'],paid,'resume must not re-bill calls')
            self.assertEqual(b['live_api']['billable_calls'],a['live_api']['billable_calls'])
            self.assertAlmostEqual(b['live_api']['reported_or_estimated_cost_usd'],a['live_api']['reported_or_estimated_cost_usd'],places=10)
