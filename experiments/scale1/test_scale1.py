import unittest,random,json
from itertools import product
from scale1_core import *

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.public,self.records,self.private=make_world(4782,4,'spoof_ack','test')
        self.oracle=ExactOracle(self.public)
    def test_full_signed_consistent(self):
        a=self.oracle.query(self.records)
        self.assertEqual(a['value'],self.private['claim_truth']);self.assertTrue(a['identified'])
    def test_empty_both_possible(self):
        a=self.oracle.query([])
        self.assertEqual((a['can_false'],a['can_true']),(True,True))
    def test_weak_ack_ignored(self):
        rs=[r for r in self.records if r['kind']=='weak_ack']
        self.assertEqual(self.oracle.query(rs),self.oracle.query([]))
    def test_public_contains_no_truth(self):
        s=json.dumps(self.public)
        self.assertNotIn('native_success',s)
        self.assertNotIn('claim_truth',s)
        self.assertNotIn('family',s)
    def test_mask_no_status_knowledge(self):
        a=sample_mask(self.records,self.public,random.Random(99),.5,'targeted')
        b=[{**x,'value':(1-x['value']) if isinstance(x['value'],int) and x['kind']!='signed_batch' else x['value']} for x in self.records]
        c=sample_mask(b,self.public,random.Random(99),.5,'targeted')
        self.assertEqual([x['id'] for x in a],[x['id'] for x in c])
    def test_truth_replay(self):
        self.assertEqual(int(path_truth(4,self.public['edges'],self.private['edge_native_success'])[-1]),self.private['claim_truth'])
    def test_oracle_bruteforce_small(self):
        p,r,priv=self.public,self.records,self.private
        self.assertLessEqual(len(p['edges']),15)
        for retained in ([],r[::4],r[1::3],r,r[::2]):
            yes=set()
            for bits in product((0,1),repeat=len(p['edges'])):
                got=path_truth(p['n_agents'],p['edges'],bits)
                def valid(x):
                    if x['kind']=='signed_native':return bits[x['edges'][0]]==x['value']
                    if x['kind']=='signed_batch':return sum(bits[i] for i in x['edges'])==x['value']
                    if x['kind']=='signed_inbox':return int(got[x['meta']['agent']])==x['value']
                    return True
                if all(valid(x) for x in retained):yes.add(int(got[-1]))
            a=self.oracle.query(retained)
            self.assertEqual(a['can_false'],0 in yes)
            self.assertEqual(a['can_true'],1 in yes)
    def test_monotonic_identification(self):
        for n in (4,16,64):
            p,r,priv=make_world(123+n,n,'stale_replica','t');o=ExactOracle(p)
            rng=random.Random(555)
            for _ in range(8):
                ids=rng.sample(range(len(r)),min(14,len(r)))
                a=o.query([r[j] for j in ids[:7]]);b=o.query([r[j] for j in ids])
                if a['identified']:
                    self.assertTrue(b['identified']);self.assertEqual(a['value'],b['value'])
    def test_signed_receipt_policy_sound(self):
        for n in (4,8,32):
            p,r,priv=make_world(222+n,n,'direct','test');o=ExactOracle(p)
            rng=random.Random(22)
            for _ in range(8):
                m=sample_mask(r,p,rng,.65,'independent')
                v=receipt_baseline(p,m)
                if v is not None:
                    ref=o.query(m)
                    self.assertTrue(ref['identified']);self.assertEqual(v,ref['value'])
    def test_broken_bad_signed_record_is_inconsistent(self):
        p,r,priv=self.public,self.records,self.private
        first=next(x for x in r if x['kind']=='signed_native')
        forged={**first,'value':1-first['value']}
        q=self.oracle.query(r+[forged])
        self.assertEqual(q['status'],'inconsistent')

if __name__=='__main__':unittest.main()
