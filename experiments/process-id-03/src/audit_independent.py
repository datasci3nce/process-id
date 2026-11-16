#!/usr/bin/env python3
"""Independent forensic audit. Does not import the generator or trust its truth labels."""
import argparse
import collections
import hashlib
import json
import sqlite3
from pathlib import Path


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_rows(path):
    return [json.loads(l) for l in Path(path).read_text(encoding='utf8').splitlines() if l.strip()]


def audit(root):
    root = Path(root)
    results = root / 'results'
    regular = read_rows(results / 'worlds_EVALUATOR_ONLY.jsonl')
    stress = read_rows(results / 'stress_OUT_OF_MODEL_EVALUATOR_ONLY.jsonl')
    masks = read_rows(results / 'masked_cases_EVALUATOR_ONLY.jsonl')
    acquisitions = read_rows(results / 'acquisition_traces_EVALUATOR_ONLY.jsonl')
    all_worlds = regular + stress
    assert len(regular) == 144 and len(stress) == 12
    assert len({w['case_id'] for w in all_worlds}) == len(all_worlds)
    base = {}
    for w in all_worlds:
        con = sqlite3.connect(f"file:{root/'private_ledgers'/(w['case_id']+'.sqlite')}?mode=ro", uri=True)
        events = list(con.execute('SELECT seq,tick,actor,kind,payload,prev_hash,event_hash FROM events ORDER BY seq'))
        con.close()
        assert events, w['case_id']
        last = '0' * 64
        event_objs = []
        previous_tick = -1
        writes = {}
        for expected_seq, event in enumerate(events, 1):
            seq, tick, actor, kind, payload_text, prev_hash, event_hash = event
            assert seq == expected_seq and prev_hash == last, w['case_id']
            assert tick >= previous_tick, ('event ticks out of order', w['case_id'], tick, previous_tick)
            previous_tick = tick
            parsed = json.loads(payload_text)
            assert canonical(parsed) == payload_text, ('noncanonical event', w['case_id'])
            computed = sha(canonical([seq, tick, actor, kind, payload_text, prev_hash]).encode('utf8'))
            assert event_hash == computed, ('hash mismatch', w['case_id'])
            last = computed
            event_objs.append((tick, actor, kind, parsed))
            if kind == 'artifact_written':
                writes[parsed['version']] = parsed['sha256']
        assert last == w['ledger_tip_hash'], ('tip mismatch', w['case_id'])
        assert set(writes) == {1, 2}
        for version, expected_digest in writes.items():
            path = root / 'sandbox_artifacts' / w['case_id'] / f'v{version}.json'
            blob = path.read_bytes()
            assert sha(blob) == expected_digest, ('artifact tamper', w['case_id'], version)
            assert json.loads(blob)['version'] == version
        for tick, actor, kind, payload in event_objs:
            if kind == 'artifact_read':
                assert actor == 'verifier'
                assert payload['sha256'] == writes[payload['version']]
        channels_closed = collections.Counter(
            p['channel'] for tick, _, kind, p in event_objs
            if kind == 'channel_closed' and tick == 19)
        assert channels_closed == {'registered': 1, 'auxiliary': 1}
        observed_read = {(p['channel'], p['version']) for tick, _, kind, p in event_objs
                         if kind == 'artifact_read' and tick < 20}
        truth = any(ver == 2 for ch, ver in observed_read)
        reg = ('registered', 2) in observed_read
        aux = ('auxiliary', 2) in observed_read
        assert truth == w['truth'], ('wrong label', w['case_id'])
        assert w['receipts'] == {'registered': reg, 'auxiliary': aux}, ('wrong receipt', w['case_id'])
        assert bool(w['out_of_model']) == any(ch == 'covert_out_of_model' for ch, _ in observed_read)
        base[w['case_id']] = w
    pairs = collections.defaultdict(list)
    for w in regular:
        pairs[w['pair_id']].append(w)
    assert len(pairs) == 72 and all(len(a) == 2 for a in pairs.values())
    for a, b in pairs.values():
        assert a['public'] == b['public'] and a['truth'] != b['truth']
        assert a['split'] == b['split']
    assert len(masks) == len(regular) * 4
    mask_counts = collections.Counter()
    for row in masks:
        w = base[row['case_id']]
        assert row['truth_evaluator_only'] == w['truth']
        assert all(w['receipts'][key] == val for key, val in row['receipts'].items())
        # Model oracle: registered route possible only for timely delivered v2 or authorized fetch.
        p = w['public']
        reg_possible = ((p['tool_action'] == 'read_delivered' and p['delivery_receipt'])
                        or (p['tool_action'] == 'fetch_store' and p['direct_access']))
        reg_range = [False, True] if reg_possible else [False]
        compatible_truths = {(reg or aux) for reg in reg_range for aux in [False, True]
                             if ('registered' not in row['receipts'] or row['receipts']['registered'] == reg)
                             and ('auxiliary' not in row['receipts'] or row['receipts']['auxiliary'] == aux)}
        assert compatible_truths, ('inconsistent observation', w['case_id'])
        expected = ('YES' if compatible_truths == {True} else
                    'NO' if compatible_truths == {False} else 'UNKNOWN')
        assert row['certificate'] == expected, ('incorrect oracle', w['case_id'])
        if expected != 'UNKNOWN':
            assert (expected == 'YES') == w['truth']
        mask_counts[expected] += 1
    assert len(acquisitions) == len(regular) * 3 * 2
    acq_counts = collections.Counter()
    for row in acquisitions:
        w = base[row['case_id']]
        assert row['truth'] == w['truth']
        assert row['spent'] <= row['budget']
        assert sum(x['cost'] for x in row['trace']) == row['spent']
        assert len({x['source'] for x in row['trace']}) == len(row['trace'])
        if row['status'] != 'UNKNOWN':
            assert (row['status'] == 'YES') == w['truth']
            acq_counts[(row['policy'], row['availability'])] += 1
    assert sum(w['truth'] for w in regular) == 72
    assert all(w['truth'] for w in stress)
    assert all(w['closed_world_certificate'] == 'NO' for w in stress)
    return {
        'independent_audit': 'PASS',
        'verified_regular_worlds': len(regular),
        'verified_stress_worlds': len(stress),
        'verified_complete_hash_chains': len(all_worlds),
        'verified_matched_public_pairs': len(pairs),
        'verified_mask_cases': len(masks),
        'mask_certificates': dict(mask_counts),
        'verified_acquisition_trials': len(acquisitions),
        'stress_model_violations': len(stress),
        'note': 'Event+blob consistency verified; does not independently instrument OS-level file reads.'
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    args = ap.parse_args()
    print(json.dumps(audit(args.outdir), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
