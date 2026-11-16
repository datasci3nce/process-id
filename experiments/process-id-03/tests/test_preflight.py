"""Zero-dependency test suite: python -m unittest discover -s tests -v"""
import collections
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
from process_id_03 import (run, certify, possible_states, reg_can_read_v2,
                           build_specs, acquisition, simple_rule_certificate)
from audit_independent import audit


class PreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='process_id_03_tests_')
        cls.root = Path(cls.tmp.name) / 'preflight'
        cls.summary = run(cls.root)
        cls.worlds = [json.loads(line) for line in
                      (cls.root / 'results/worlds_EVALUATOR_ONLY.jsonl').read_text().splitlines()]
        cls.masks = [json.loads(line) for line in
                     (cls.root / 'results/masked_cases_EVALUATOR_ONLY.jsonl').read_text().splitlines()]
        cls.acq = [json.loads(line) for line in
                   (cls.root / 'results/acquisition_traces_EVALUATOR_ONLY.jsonl').read_text().splitlines()]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_independent_audit_passes(self):
        result = audit(self.root)
        self.assertEqual(result['independent_audit'], 'PASS')
        self.assertEqual(result['verified_complete_hash_chains'], 156)

    def test_all_pairs_observationally_identical_with_opposite_truth(self):
        pairs = collections.defaultdict(list)
        for w in self.worlds:
            pairs[w['pair_id']].append(w)
        self.assertEqual(len(pairs), 72)
        for one, two in pairs.values():
            self.assertEqual(one['public'], two['public'])
            self.assertEqual(one['split'], two['split'])
            self.assertNotEqual(one['truth'], two['truth'])

    def test_positive_negative_and_split_balance(self):
        self.assertEqual(len(self.worlds), 144)
        self.assertEqual(sum(w['truth'] for w in self.worlds), 72)
        test = [w for w in self.worlds if w['split'] == 'test']
        self.assertEqual(len(test), 48)
        self.assertEqual(sum(w['truth'] for w in test), 24)
        self.assertEqual(len({w['pair_id'] for w in test}), 24)
        self.assertEqual(self.summary['best_possible_public_only_test_accuracy'], .5)

    def test_certificate_matches_explicit_enumeration_and_is_sound(self):
        self.assertEqual(len(self.masks), 576)
        counts = collections.Counter()
        lookup = {w['case_id']: w for w in self.worlds}
        for row in self.masks:
            world = lookup[row['case_id']]
            result = certify(world['public'], row['receipts'])
            self.assertEqual(result, row['certificate'])
            self.assertEqual(result, simple_rule_certificate(world['public'], row['receipts']))
            if result != 'UNKNOWN':
                self.assertEqual(result == 'YES', world['truth'])
            counts[result] += 1
        self.assertEqual(dict(counts), {'UNKNOWN': 312, 'YES': 144, 'NO': 120})

    def test_certificate_withholds_negative_without_coverage(self):
        route = next(w for w in self.worlds if reg_can_read_v2(w['public']))
        self.assertEqual(certify(route['public'], {'registered': False}), 'UNKNOWN')
        self.assertEqual(certify(route['public'], {'auxiliary': False}), 'UNKNOWN')
        self.assertEqual(certify(route['public'], {'registered': False, 'auxiliary': False}), 'NO')
        with self.assertRaises(ValueError):
            possible_states(route['public'], {'registered': 'nonboolean'})

    def test_late_reads_do_not_count_as_early(self):
        late = [w for w in self.worlds if w['mechanism'] == 'late_read']
        self.assertEqual(len(late), 24)
        self.assertTrue(all(not w['receipts']['registered'] for w in late))
        self.assertEqual(sum(w['truth'] for w in late), 12)

    def test_acquisition_budget_and_benchmark_baselines(self):
        self.assertEqual(len(self.acq), 864)
        observed = collections.Counter()
        for record in self.acq:
            self.assertLessEqual(record['spent'], record['budget'])
            self.assertEqual(sum(x['cost'] for x in record['trace']), record['spent'])
            if record['status'] != 'UNKNOWN':
                self.assertEqual(record['status'] == 'YES', record['truth'])
            if record['split'] == 'test' and record['availability'] == 1.0 and record['status'] != 'UNKNOWN':
                observed[record['policy']] += 1
        self.assertEqual(dict(observed),
                         {'registered_first': 8, 'auxiliary_first': 32, 'route_aware': 40})

    def test_out_of_model_stress_is_not_misrepresented_as_in_model(self):
        stress = [json.loads(line) for line in
                  (self.root / 'results/stress_OUT_OF_MODEL_EVALUATOR_ONLY.jsonl').read_text().splitlines()]
        self.assertEqual(len(stress), 12)
        for world in stress:
            self.assertTrue(world['out_of_model'])
            self.assertTrue(world['truth'])
            self.assertEqual(world['receipts'], {'registered': False, 'auxiliary': False})
            self.assertEqual(world['closed_world_certificate'], 'NO')

    def test_independent_audit_detects_artifact_tamper(self):
        first = self.worlds[0]
        path = self.root / 'sandbox_artifacts' / first['case_id'] / 'v2.json'
        saved = path.read_bytes()
        try:
            path.write_bytes(saved + b'CHANGED')
            with self.assertRaises(AssertionError):
                audit(self.root)
        finally:
            path.write_bytes(saved)
        self.assertEqual(audit(self.root)['independent_audit'], 'PASS')

    def test_reproducible_spec_and_no_network_import(self):
        self.assertEqual(build_specs(20261115), build_specs(20261115))
        self.assertEqual(self.summary['llm_calls'], 0)
        self.assertEqual(self.summary['openrouter_cost_usd'], 0)


if __name__ == '__main__':
    unittest.main()
