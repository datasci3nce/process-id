"""Regression tests for the post-hoc baseline and information boundary."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from posthoc_certified_static import public_predictions, scores

class TestPosthoc(unittest.TestCase):
    @staticmethod
    def example(idx, obs, cert, prob):
        return ({'case_id':f'x{idx}', 'world_id':'test_world', 'n':2, 'deadline':2,
                'potential_edges':[[0,1]], 'observations':obs,
                'mask_kind':'independent', 'retention_requested':.5},
                {'case_id':f'x{idx}','world_id':'test_world','split':'heldout','mask_kind':'independent',
                 'reference_cert':cert,'static_logistic':str(prob), 'timed_logistic':'0.5',
                 'dde_delayed':'0.5','dde_no_delay':'0.5','mc_event_posterior':'0.5'})

    def test_public_predictions_without_evaluator_labels(self):
        # No evaluator_ONLY directory or hidden truth is present at all here.
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); p=base/'results/public';p.mkdir(parents=True)
            e=[self.example(1,[{'edge_idx':0,'status':'live','delay':1}],'YES',.2),
               self.example(2,[{'edge_idx':0,'status':'failed','delay':None}],'NO',.8),
               self.example(3,[],'UNKNOWN',.37)]
            with open(p/'heldout.jsonl','w') as f:
                for o,_ in e: f.write(json.dumps(o)+'\n')
            with open(p/'observed_only_predictions.csv','w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(e[0][1]));w.writeheader();w.writerows([row for _,row in e])
            out=public_predictions(base)
            self.assertEqual([out[f'x{i}']['hybrid_exact_then_static'] for i in range(1,4)], [1.,0.,.37])
            self.assertEqual([out[f'x{i}']['cert'] for i in range(1,4)], ['YES','NO','UNKNOWN'])

    def test_score_labels_not_used_to_choose_baseline(self):
        p={'x1':{'case_id':'x1','world_id':'w1','n':2,'mask_kind':'independent',
                 'retention_requested':.5,'cert':'UNKNOWN','hybrid_exact_then_static':.37,
                 'static_logistic':.37,'timed_logistic':.4,'dde_delayed':.5,
                 'dde_no_delay':.5,'mc_event_posterior':.55}}
        label0=[{'case_id':'x1','world_id':'w1','reference_cert':'UNKNOWN','label_actual':'0'}]
        label1=[{'case_id':'x1','world_id':'w1','reference_cert':'UNKNOWN','label_actual':'1'}]
        p['x2']={'case_id':'x2','world_id':'w2','n':2,'mask_kind':'independent',
                 'retention_requested':.5,'cert':'YES','hybrid_exact_then_static':1.,
                 'static_logistic':.8,'timed_logistic':.8,'dde_delayed':.8,
                 'dde_no_delay':.8,'mc_event_posterior':.8}
        certrow={'case_id':'x2','world_id':'w2','reference_cert':'YES','label_actual':'1'}
        for label in [label0,label1]:
            joined,scores_obj=scores(p,label+[certrow],bootstrap_reps=20)
            self.assertEqual({row['case_id']:row['hybrid_exact_then_static'] for row in joined}, {'x1':.37,'x2':1.})
            self.assertEqual(scores_obj['heldout']['n_cases'],2)

    def test_mismatched_evaluator_ids_rejected(self):
        p={'x1':{'case_id':'x1','world_id':'w1','cert':'YES','hybrid_exact_then_static':1.,
                 'static_logistic':.5,'timed_logistic':.5,'dde_delayed':.5,'dde_no_delay':.5,'mc_event_posterior':.5}}
        with self.assertRaises(AssertionError):
            scores(p,[{'case_id':'x2','world_id':'w1','reference_cert':'YES','label_actual':'1'}],bootstrap_reps=10)

if __name__=='__main__': unittest.main()
