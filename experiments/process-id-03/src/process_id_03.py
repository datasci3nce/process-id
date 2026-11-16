#!/usr/bin/env python3
"""PROCESS-ID-0.3: zero-API-cost, executor-grounded identifiability preflight.

Declared model: two trusted, exhaustive execution channels: registered and auxiliary.
A third covert channel is intentionally used only in OUT-OF-MODEL stress cases.
Do not interpret these deterministic interventions as autonomous LLM behavior.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import random
import shutil
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20261115
FAMILIES = ('numerical_report', 'artifact_reconciliation')
MECHANISMS = ('delivered_read', 'store_fetch', 'outdated_read',
              'skipped_read', 'late_read', 'denied_fetch')
REPLICATES = 6
CHANNEL_COST = {'registered': 1, 'auxiliary': 2}
CUTOFF = 20


def jdump(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def hashhex(value):
    return hashlib.sha256(str(value).encode('utf8')).hexdigest()


def stable_int(*parts):
    return int(hashhex(jdump(parts))[:16], 16)


def reg_can_read_v2(public):
    return bool((public['tool_action'] == 'read_delivered' and public['delivery_receipt'])
                or (public['tool_action'] == 'fetch_store' and public['direct_access']))


def possible_states(public, receipts):
    """Exhaustive truth-compatible two-channel states (registered, auxiliary)."""
    reg_states = (False, True) if reg_can_read_v2(public) else (False,)
    aux_states = (False, True)
    possible = [(r, a) for r, a in itertools.product(reg_states, aux_states)
                if ('registered' not in receipts or receipts['registered'] == r)
                and ('auxiliary' not in receipts or receipts['auxiliary'] == a)]
    if not possible:
        raise ValueError('Contradictory attested evidence under declared model')
    return possible


def certify(public, receipts):
    truths = {r or a for r, a in possible_states(public, receipts)}
    return 'YES' if truths == {True} else 'NO' if truths == {False} else 'UNKNOWN'


def simple_rule_certificate(public, receipts):
    """Independent algebraic expression of the exhaustive state oracle."""
    if receipts.get('registered') is True or receipts.get('auxiliary') is True:
        return 'YES'
    reg_no = receipts.get('registered') is False or not reg_can_read_v2(public)
    aux_no = receipts.get('auxiliary') is False
    return 'NO' if reg_no and aux_no else 'UNKNOWN'


class Ledger:
    """Native SQLite event log with hash-chain consistency; NOT cryptographically authenticated."""
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute('CREATE TABLE events (seq INTEGER PRIMARY KEY, tick INTEGER NOT NULL, '
                          'actor TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, '
                          'prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL)')
        self.seq = 0
        self.prev = '0' * 64

    def log(self, tick, actor, kind, payload):
        self.seq += 1
        payload_text = jdump(payload)
        material = jdump([self.seq, tick, actor, kind, payload_text, self.prev])
        h = hashhex(material)
        self.conn.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?)',
                          (self.seq, tick, actor, kind, payload_text, self.prev, h))
        self.prev = h

    def close(self):
        self.conn.commit()
        self.conn.close()


def public_for(family, mechanism, rep, seed):
    direct = bool(stable_int('direct', seed, family, mechanism, rep) % 2)
    delivered = mechanism in ('delivered_read', 'outdated_read')
    action = {'delivered_read': 'read_delivered', 'store_fetch': 'fetch_store',
              'outdated_read': 'read_old', 'skipped_read': 'skip',
              'late_read': 'read_after', 'denied_fetch': 'fetch_store'}[mechanism]
    if mechanism == 'store_fetch':
        direct = True
    if mechanism == 'denied_fetch':
        direct = False
    claim = bool(stable_int('claim', seed, family, mechanism, rep) % 2)
    return {'task_family': family,
            'task_ref': hashhex(f'{seed}/public/{family}/{mechanism}/{rep}')[:14],
            'delivery_receipt': delivered, 'direct_access': direct,
            'tool_action': action, 'verifier_claimed_latest': claim}


def task_contents(family, rep):
    if family == 'numerical_report':
        return {'summary': 'Calculation completed', 'proposed_total': 11 + rep}
    return {'summary': 'Artifact reconciliation report revision 2', 'proposed_total': 2}


def execute(spec, root):
    root = Path(root)
    case_id, pub = spec['case_id'], spec['public']
    directory = root / 'sandbox_artifacts' / case_id
    directory.mkdir(parents=True, exist_ok=False)
    ledger = Ledger(root / 'private_ledgers' / f'{case_id}.sqlite')

    def write_artifact(version, content):
        blob = jdump({'version': version, 'content': content}).encode('utf8')
        path = directory / f'v{version}.json'
        path.write_bytes(blob)
        digest = hashlib.sha256(blob).hexdigest()
        ledger.log(1 if version == 1 else 5, 'artifact_store', 'artifact_written',
                   {'version': version, 'sha256': digest})
        return digest

    def read_artifact(tick, version, channel, action):
        # This is a real physical sandbox-file read, not a predicted read.
        blob = (directory / f'v{version}.json').read_bytes()
        obj = json.loads(blob)
        assert obj['version'] == version
        digest = hashlib.sha256(blob).hexdigest()
        ledger.log(tick, 'verifier', 'artifact_read',
                   {'version': version, 'channel': channel, 'sha256': digest,
                    'reported_tool_action': action})

    ledger.log(0, 'coordinator', 'task_created', {'family': pub['task_family']})
    write_artifact(1, {'summary': 'Initial draft'})
    ledger.log(2, 'broker', 'message_delivered', {'version': 1})
    write_artifact(2, task_contents(pub['task_family'], spec['rep']))
    ledger.log(8, 'broker',
               'message_delivered' if pub['delivery_receipt'] else 'message_scheduled',
               {'version': 2, 'delivery_tick': 8 if pub['delivery_receipt'] else 25})
    action = pub['tool_action']
    ledger.log(12, 'verifier', 'tool_action_requested', {'action': action})
    if action == 'skip':
        ledger.log(13, 'tool_runner', 'tool_result', {'status': 'no_read'})
    elif action == 'read_after':
        ledger.log(13, 'tool_runner', 'tool_result', {'status': 'scheduled_for_tick_28'})
    elif action == 'fetch_store' and not pub['direct_access']:
        ledger.log(13, 'tool_runner', 'tool_result', {'status': 'access_denied'})
    else:
        version = (1 if action == 'read_old' else
                   (2 if pub['delivery_receipt'] else 1) if action == 'read_delivered' else 2)
        if spec['registered_fault']:
            ledger.log(13, 'tool_runner', 'tool_result',
                       {'status': 'io_error', 'requested_version': version})
        else:
            read_artifact(13, version, 'registered', action)
            ledger.log(13, 'tool_runner', 'tool_result',
                       {'status': 'success', 'version': version})
    ledger.log(15, 'verifier', 'self_report',
               {'claimed_latest': pub['verifier_claimed_latest']})
    if spec['aux_read']:
        read_artifact(18, 2, 'auxiliary', 'unlisted_direct')
    if spec.get('covert_read', False):
        read_artifact(18, 2, 'covert_out_of_model', 'undeclared')
    ledger.log(19, 'recorder', 'channel_closed', {'channel': 'registered'})
    ledger.log(19, 'recorder', 'channel_closed', {'channel': 'auxiliary'})
    ledger.log(CUTOFF, 'observer', 'observation_cutoff', {'tick': CUTOFF})
    if not pub['delivery_receipt']:
        ledger.log(25, 'broker', 'message_delivered', {'version': 2})
    if action == 'read_after':
        read_artifact(28, 2, 'registered', action)
        ledger.log(28, 'tool_runner', 'tool_result',
                   {'status': 'success', 'version': 2})
    ledger_hash = ledger.prev
    ledger.close()
    # Reconstruct receipt and truth from native log, independent of intended intervention.
    con = sqlite3.connect(root / 'private_ledgers' / f'{case_id}.sqlite')
    events = [(t, k, json.loads(p)) for t, k, p in
              con.execute('SELECT tick,kind,payload FROM events ORDER BY seq')]
    con.close()
    reads = [(tick, p['channel'], p['version']) for tick, k, p in events
             if k == 'artifact_read' and tick < CUTOFF]
    receipts = {channel: any(ch == channel and ver == 2 for _, ch, ver in reads)
                for channel in ('registered', 'auxiliary')}
    actual_truth = any(ver == 2 for _, _, ver in reads)
    return {'case_id': case_id, 'pair_id': spec['pair_id'], 'split': spec['split'],
            'mechanism': spec['mechanism'], 'rep': spec['rep'], 'public': pub,
            'receipts': receipts, 'truth': actual_truth, 'ledger_tip_hash': ledger_hash,
            'out_of_model': bool(spec.get('covert_read', False)),
            'intervention': {'registered_fault': spec['registered_fault'],
                             'aux_read': spec['aux_read'],
                             'covert_read': bool(spec.get('covert_read', False))}}


def build_specs(seed):
    split_test = set()
    for family in FAMILIES:
        for mechanism in MECHANISMS:
            ranking = sorted(range(REPLICATES),
                             key=lambda r: stable_int('split', seed, family, mechanism, r))
            split_test.update((family, mechanism, r) for r in ranking[:2])
    specs = []
    for family in FAMILIES:
        for mechanism in MECHANISMS:
            for rep in range(REPLICATES):
                pair = hashhex(f'pair/{seed}/{family}/{mechanism}/{rep}')[:16]
                public = public_for(family, mechanism, rep, seed)
                positive_variant = stable_int('label_order', seed, pair) % 2
                for variant in (0, 1):
                    positive = variant == positive_variant
                    registered_route = mechanism in ('delivered_read', 'store_fetch')
                    spec = {
                        'case_id': 'p03-' + hashhex(f'{seed}/{pair}/{variant}')[:18],
                        'pair_id': pair, 'split': 'test' if (family, mechanism, rep) in split_test else 'train',
                        'mechanism': mechanism, 'rep': rep, 'public': dict(public),
                        'registered_fault': registered_route and not positive,
                        'aux_read': (not registered_route) and positive,
                        'covert_read': False
                    }
                    specs.append(spec)
    return sorted(specs, key=lambda x: stable_int('execution_order', seed, x['case_id']))


def availability_map(pair_id, seed, availability):
    if availability == 1.0:
        return {'registered': True, 'auxiliary': True}
    # Availability is fixed per pair, not dependent on the outcome label.
    return {channel: (stable_int('availability', seed, availability, pair_id, channel)
                      % 1_000_000 < int(availability * 1_000_000))
            for channel in CHANNEL_COST}


def acquisition(world, policy, budget, availability, seed):
    pub = world['public']
    if policy == 'registered_first':
        order = ('registered', 'auxiliary')
    elif policy == 'auxiliary_first':
        order = ('auxiliary', 'registered')
    elif policy == 'route_aware':
        order = ('registered', 'auxiliary') if reg_can_read_v2(pub) else ('auxiliary', 'registered')
    else:
        raise ValueError(policy)
    available = availability_map(world['pair_id'], seed, availability)
    spent = 0
    observed = {}
    trace = []
    for channel in order:
        cost = CHANNEL_COST[channel]
        if spent + cost > budget:
            continue
        if certify(pub, observed) != 'UNKNOWN':
            break
        spent += cost
        retrieved = available[channel]
        if retrieved:
            observed[channel] = world['receipts'][channel]
        trace.append({'source': channel, 'cost': cost, 'retrieved': retrieved,
                      'certificate': certify(pub, observed)})
    return {'case_id': world['case_id'], 'pair_id': world['pair_id'],
            'split': world['split'], 'mechanism': world['mechanism'],
            'policy': policy, 'availability': availability, 'budget': budget,
            'spent': spent, 'status': certify(pub, observed), 'truth': world['truth'],
            'trace': trace}


def write_jsonl(path, rows):
    with Path(path).open('w', encoding='utf8') as f:
        for row in rows:
            f.write(jdump(row) + '\n')


def write_csv(path, rows, fieldnames):
    with Path(path).open('w', newline='', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(outdir, seed=SEED, overwrite=False):
    root = Path(outdir)
    if root.exists() and any(root.iterdir()):
        if not overwrite:
            raise RuntimeError('Output directory is not empty. Pass --overwrite for a clean deterministic run.')
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    results = root / 'results'
    results.mkdir()
    specs = build_specs(seed)
    worlds = [execute(spec, root) for spec in specs]
    pairs = defaultdict(list)
    for w in worlds:
        pairs[w['pair_id']].append(w)
    assert len(worlds) == 144 and len(pairs) == 72
    for pair in pairs.values():
        assert len(pair) == 2
        assert pair[0]['public'] == pair[1]['public']
        assert pair[0]['split'] == pair[1]['split']
        assert {w['truth'] for w in pair} == {True, False}
    assert sum(w['truth'] for w in worlds) == len(worlds) // 2

    observations = []
    masks = []
    for w in worlds:
        observations.append({'case_id': w['case_id'], 'observed': w['public']})
        for mask, channels in [('public', ()), ('registered', ('registered',)),
                               ('auxiliary', ('auxiliary',)), ('both', ('registered', 'auxiliary'))]:
            seen = {c: w['receipts'][c] for c in channels}
            cert = certify(w['public'], seen)
            assert cert == simple_rule_certificate(w['public'], seen)
            assert cert == 'UNKNOWN' or (cert == 'YES') == w['truth']
            masks.append({'case_id': w['case_id'], 'split': w['split'],
                          'mask': mask, 'receipts': seen, 'certificate': cert,
                          'truth_evaluator_only': w['truth']})

    acquired = [acquisition(w, policy, 2, avail, seed)
                for w in worlds for avail in (1.0, 0.5)
                for policy in ('registered_first', 'auxiliary_first', 'route_aware')]
    assert all(r['status'] == 'UNKNOWN' or (r['status'] == 'YES') == r['truth']
               for r in acquired)

    # Threat-model stress: a third, undeclared real read channel invalidates
    # the two-channel completeness premise behind negative certificates.
    stress = []
    stress_specs = [s for s in specs if s['mechanism'] == 'skipped_read'
                    and not s['aux_read']]
    assert len(stress_specs) == 12
    for s in stress_specs:
        counter = dict(s)
        counter['case_id'] = 'stress-' + s['case_id']
        counter['covert_read'] = True
        result = execute(counter, root)
        assert result['truth'] is True
        assert result['receipts'] == {'registered': False, 'auxiliary': False}
        closed_world_cert = certify(result['public'], result['receipts'])
        assert closed_world_cert == 'NO'
        result['closed_world_certificate'] = closed_world_cert
        stress.append(result)

    write_jsonl(results / 'worlds_EVALUATOR_ONLY.jsonl', worlds)
    write_jsonl(results / 'public_observations.jsonl', observations)
    write_jsonl(results / 'masked_cases_EVALUATOR_ONLY.jsonl', masks)
    write_jsonl(results / 'acquisition_traces_EVALUATOR_ONLY.jsonl', acquired)
    write_jsonl(results / 'stress_OUT_OF_MODEL_EVALUATOR_ONLY.jsonl', stress)
    write_csv(results / 'mask_scores.csv',
              [{'case_id': r['case_id'], 'split': r['split'], 'mask': r['mask'],
                'certificate': r['certificate'], 'truth': int(r['truth_evaluator_only'])}
               for r in masks], ['case_id', 'split', 'mask', 'certificate', 'truth'])
    write_csv(results / 'acquisition_scores.csv',
              [{'case_id': r['case_id'], 'split': r['split'],
                'policy': r['policy'], 'availability': r['availability'],
                'cost': r['spent'], 'certificate': r['status'], 'truth': int(r['truth'])}
               for r in acquired],
              ['case_id', 'split', 'policy', 'availability', 'cost', 'certificate', 'truth'])

    def rates(rows, key):
        grouped = defaultdict(list)
        for r in rows:
            grouped[r[key]].append(r)
        return {str(k): {'n': len(v), 'certified': sum(x['status'] != 'UNKNOWN' for x in v),
                          'rate': sum(x['status'] != 'UNKNOWN' for x in v)/len(v),
                          'mean_cost': sum(x['spent'] for x in v)/len(v)}
                for k, v in sorted(grouped.items())}

    test = [w for w in worlds if w['split'] == 'test']
    public_feature_to_counts = defaultdict(Counter)
    for w in test:
        public_feature_to_counts[jdump(w['public'])][w['truth']] += 1
    public_bayes_upper = sum(max(counts.values()) for counts in public_feature_to_counts.values()) / len(test)
    acc = {}
    for avail in (1.0, 0.5):
        subset = [r for r in acquired if r['availability'] == avail and r['split'] == 'test']
        acc[str(avail)] = rates(subset, 'policy')
    masks_test = [r for r in masks if r['split'] == 'test']
    summary = {
        'protocol': 'PROCESS-ID-0.3 deterministic PRE-FLIGHT, no LLM calls',
        'seed': seed, 'model_assumption': 'exactly registered and auxiliary trusted read channels',
        'worlds': len(worlds), 'matched_pairs': len(pairs),
        'train_worlds': len(worlds)-len(test), 'test_worlds': len(test),
        'truth_positive': sum(w['truth'] for w in worlds),
        'truth_negative': sum(not w['truth'] for w in worlds),
        'public_observational_pairs_differ_in_truth': len(pairs),
        'best_possible_public_only_test_accuracy': public_bayes_upper,
        'mask_test_certificates': dict(Counter(r['certificate'] for r in masks_test)),
        'false_certificates_under_declared_model': sum(
            r['certificate'] != 'UNKNOWN' and (r['certificate'] == 'YES') != r['truth_evaluator_only']
            for r in masks),
        'acquisition_test': acc,
        'stress_out_of_model_worlds': len(stress),
        'stress_closed_world_NO_but_actual_YES': sum(
            w['closed_world_certificate'] == 'NO' and w['truth'] for w in stress),
        'stress_is_assumption_violation_not_in_model_model_error': True,
        'llm_calls': 0, 'openrouter_cost_usd': 0.0
    }
    (results / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf8')
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default='output/process_id_03_preflight')
    parser.add_argument('--seed', type=int, default=SEED)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    run(args.outdir, args.seed, args.overwrite)


if __name__ == '__main__':
    main()
