"""Post-hoc verification of ER-DELAY-PERC-1. No model fitting or new worlds.

Usage: python reproduce_review.py ORIGINAL.zip --output review_results.json
Also accepts the extracted ER_DELAY_PERCOLATION_1 directory. Requires NumPy.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import heapq
import json
import math
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

METHODS = ['static_logistic', 'timed_logistic', 'dde_delayed',
           'dde_no_delay', 'mc_event_posterior']

def distance(n, edges):
    adjacency = defaultdict(list)
    for u, v, delay in edges:
        adjacency[u].append((v, delay))
    distances = [math.inf] * n
    distances[0] = 0
    queue = [(0, 0)]
    while queue:
        time, u = heapq.heappop(queue)
        if time != distances[u]:
            continue
        for v, delay in adjacency[u]:
            proposed = time + delay
            if proposed < distances[v]:
                distances[v] = proposed
                heapq.heappush(queue, (proposed, v))
    return distances[n - 1]

def certify(case):
    observations = {r['edge_idx']: r for r in case['observations']}
    proved, possible = [], []
    for index, (u, v) in enumerate(case['potential_edges']):
        observation = observations.get(index)
        if observation is None:
            possible.append((u, v, 1))
        elif observation['status'] == 'live':
            edge = (u, v, observation['delay'])
            proved.append(edge)
            possible.append(edge)
    if distance(case['n'], proved) <= case['deadline']:
        return 'YES'
    if distance(case['n'], possible) > case['deadline']:
        return 'NO'
    return 'UNKNOWN'

def brier(rows, method):
    return float(np.mean([(r[method] - r['y']) ** 2 for r in rows]))

def review(root):
    results = root / 'results'
    def read_jsonl(name):
        return [json.loads(line) for line in (results / name).read_text().splitlines() if line.strip()]
    ledgers = {r['world_id']: r for r in read_jsonl('evaluator_ONLY/native_edge_ledgers.jsonl')}
    with (results / 'evaluator_ONLY/native_world_truth.csv').open() as stream:
        truths = {r['world_id']: r for r in csv.DictReader(stream)}
    with (results / 'all_predictions_evaluator_ONLY.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    predictions = {r['case_id']: r for r in rows}
    assert len(predictions) == len(rows)
    for row in rows:
        row['y'] = int(row['label_actual'])
        for method in METHODS:
            row[method] = float(row[method])
    for world, ledger in ledgers.items():
        truth = truths[world]
        arrival = distance(int(truth['n']), [(u, v, d) for u, v, live, d in ledger['private_edges'] if live])
        assert int(arrival <= int(truth['deadline'])) == ledger['truth'] == int(truth['truth'])
        expected = truth['native_arrival']
        assert (not expected and math.isinf(arrival)) or (expected and arrival == int(expected))
    cases = read_jsonl('public/development.jsonl') + read_jsonl('public/heldout.jsonl')
    certificates, receipt_count = {}, 0
    for case in cases:
        native = ledgers[case['world_id']]['private_edges']
        assert case['potential_edges'] == [[u, v] for u, v, _, _ in native]
        assert len({r['edge_idx'] for r in case['observations']}) == len(case['observations'])
        for observation in case['observations']:
            index = observation['edge_idx']
            assert observation['status'] == ('live' if native[index][2] else 'failed')
            assert observation['delay'] == native[index][3]
            receipt_count += 1
        verdict = certify(case)  # Uses public observations only.
        certificates[case['case_id']] = verdict
        assert verdict == predictions[case['case_id']]['reference_cert']
        if verdict != 'UNKNOWN':
            assert int(verdict == 'YES') == ledgers[case['world_id']]['truth']
    assert len(certificates) == len(cases) == len(rows)
    held = [r for r in rows if r['split'] == 'heldout']
    for row in held:
        verdict = certificates[row['case_id']]
        row['cert_then_static'] = 1.0 if verdict == 'YES' else 0.0 if verdict == 'NO' else row['static_logistic']
        row['cert_then_timed'] = 1.0 if verdict == 'YES' else 0.0 if verdict == 'NO' else row['timed_logistic']
    ambiguous = [r for r in held if certificates[r['case_id']] == 'UNKNOWN']
    identified = [r for r in held if certificates[r['case_id']] != 'UNKNOWN']
    scores = {name: {'n': len(part), **{m: brier(part, m) for m in METHODS}}
              for name, part in [('all', held), ('ambiguous', ambiguous), ('identified', identified)]}
    wrappers = {m: brier(held, m) for m in ['cert_then_static', 'cert_then_timed']}
    def improvement_share(part):
        total = sum((r['static_logistic']-r['y'])**2 - (r['timed_logistic']-r['y'])**2 for r in part)
        certified = sum((r['static_logistic']-r['y'])**2 - (r['timed_logistic']-r['y'])**2
                        for r in part if certificates[r['case_id']] != 'UNKNOWN')
        return certified / total
    worlds = sorted({r['world_id'] for r in held})
    rng = np.random.default_rng(2026111501)
    indices = rng.integers(0, len(worlds), size=(4000, len(worlds)))
    contrasts = {}
    for first, second in [('timed_logistic', 'cert_then_static'), ('cert_then_timed', 'cert_then_static'),
                          ('mc_event_posterior', 'cert_then_static')]:
        values = np.array([np.mean([(r[first]-r['y'])**2-(r[second]-r['y'])**2
                                   for r in held if r['world_id'] == world]) for world in worlds])
        contrasts[first + '_minus_' + second] = {
            'difference': float(values.mean()),
            'world_bootstrap_95pct': np.quantile(values[indices].mean(axis=1), [.025, .975]).tolist()}
    deduplicated = [r for r in held if not (r['mask_kind'] == 'source_correlated' and float(r['retention']) == 1.0)]
    verified_files = 0
    for line in (root / 'MANIFEST_SHA256.txt').read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((root / name.lstrip('*')).read_bytes()).hexdigest() == digest
        verified_files += 1
    return {
        'scope': 'Post-hoc reanalysis of saved predictions and generated histories; no new training, simulations, or LLM calls.',
        'independent_verification': {'worlds': len(ledgers), 'cases': len(cases), 'receipts': receipt_count,
                                    'mismatches': 0, 'original_manifest_files': verified_files,
                                    'heldout_verdicts': dict(Counter(certificates[r['case_id']] for r in held))},
        'saved_method_brier': scores,
        'posthoc_certification_wrapper_brier': wrappers,
        'share_of_original_improvement_on_identified_cases': improvement_share(held),
        'posthoc_bootstrap': {'seed': 2026111501, 'replicates': 4000, 'worlds': len(worlds), 'contrasts': contrasts},
        'deduplicated_sensitivity': {'n': len(deduplicated),
            'brier': {m: brier(deduplicated, m) for m in METHODS + ['cert_then_static', 'cert_then_timed']},
            'share_of_original_improvement_on_identified_cases': improvement_share(deduplicated)},
        'limits': ['Certificates assume the declared known topology, truthful receipts, and delay support.',
                   'The original NetworkX auditor was not executed successfully in this environment because NetworkX is absent; this script independently uses heap-based Dijkstra.',
                   'Bootstrap intervals describe world-sampling variation in this synthetic generator, not real-agent transfer.',
                   'The wrapper was selected after inspecting the completed experiment; it is not a prospective primary endpoint.']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.input.is_file():
        input_hash = hashlib.sha256(args.input.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            with zipfile.ZipFile(args.input) as archive:
                for name in archive.namelist():
                    if not (destination / name).resolve().is_relative_to(destination.resolve()):
                        raise ValueError('Unsafe archive path')
                archive.extractall(destination)
            result = review(destination / 'ER_DELAY_PERCOLATION_1')
        result['input_zip_sha256'] = input_hash
    else:
        result = review(args.input)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
