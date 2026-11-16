"""Post-hoc diagnostic for DELAY-PERC-1; does not refit or tune original predictors.

Information boundary: post-hoc decisions are formed strictly from the public held-out
observations and preexisting observed-only static probabilities. Only after the
predictions are frozen are private labels read for scoring and world-bootstrap intervals.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from core import certify

METHODS = ('static_logistic', 'timed_logistic', 'dde_delayed', 'dde_no_delay', 'mc_event_posterior')


def read_csv(path):
    with open(path, newline='', encoding='utf8') as f:
        return list(csv.DictReader(f))


def public_predictions(root):
    """No evaluator label or private history is accessed by this function."""
    root = Path(root)
    pubs = {}
    with open(root / 'results/public/heldout.jsonl', encoding='utf8') as f:
        for line in f:
            case = json.loads(line)
            assert case['case_id'] not in pubs
            assert not {'truth', 'private_edges', 'native_arrival', 'label_actual'} & case.keys()
            pubs[case['case_id']] = case
    prediction_rows = [r for r in read_csv(root / 'results/public/observed_only_predictions.csv') if r['split'] == 'heldout']
    if len(prediction_rows) != len(pubs):
        raise AssertionError('Public prediction/observation counts differ')
    outputs = {}
    for row in prediction_rows:
        cid = row['case_id']
        if cid in outputs:
            raise AssertionError('Duplicate case ID')
        if cid not in pubs:
            raise AssertionError('Missing public case ID')
        case = pubs[cid]
        if row['world_id'] != case['world_id'] or row['mask_kind'] != case['mask_kind']:
            raise AssertionError('Public prediction does not match public case')
        cert = certify(case)
        if cert != row['reference_cert']:
            raise AssertionError(f'Public certificate inconsistency for {cid}')
        static = float(row['static_logistic'])
        if not 0 <= static <= 1:
            raise AssertionError('Bad static probability')
        prob = 1.0 if cert == 'YES' else 0.0 if cert == 'NO' else static
        outputs[cid] = dict(case_id=cid, world_id=case['world_id'], n=int(case['n']),
            mask_kind=case['mask_kind'], retention_requested=float(case['retention_requested']),
            cert=cert, hybrid_exact_then_static=prob,
            **{k: float(row[k]) for k in METHODS})
    return outputs


def scores(outputs, truth_rows, seed=20261115, bootstrap_reps=5000):
    truth = {r['case_id']: r for r in truth_rows}
    if len(truth) != len(outputs) or set(truth) != set(outputs):
        raise AssertionError('Evaluator IDs do not match public IDs')
    joined = []
    for cid, pred in outputs.items():
        row = truth[cid]
        y = int(row['label_actual'])
        if pred['world_id'] != row['world_id'] or pred['cert'] != row['reference_cert']:
            raise AssertionError(f'Label/certificate mismatch {cid}')
        if pred['cert'] == 'YES' and y != 1 or pred['cert'] == 'NO' and y != 0:
            raise AssertionError(f'Inconsistent reference certificate {cid}')
        joined.append(dict(pred, label_actual=y))

    def group_scores(rows):
        a = np.array([r['label_actual'] for r in rows], dtype=float)
        o = {k: float(np.mean([(r[k] - a[i])**2 for i, r in enumerate(rows)]))
            for k in METHODS + ('hybrid_exact_then_static',)}
        o['n_cases'] = len(rows)
        o['n_worlds'] = len({r['world_id'] for r in rows})
        o['n_yes'] = sum(r['cert'] == 'YES' for r in rows)
        o['n_no'] = sum(r['cert'] == 'NO' for r in rows)
        o['n_unknown'] = sum(r['cert'] == 'UNKNOWN' for r in rows)
        return o

    def world_ci(rows, a, b, boots):
        grouped = defaultdict(list)
        for r in rows:
            grouped[r['world_id']].append((r[a] - r['label_actual'])**2 - (r[b] - r['label_actual'])**2)
        ids = sorted(grouped)
        # Resample independent worlds as clusters. Weight by number of masks so
        # unresolved-only subsets with unequal counts retain case-weighted Brier.
        world_sums = np.asarray([sum(grouped[w]) for w in ids], dtype=float)
        world_counts = np.asarray([len(grouped[w]) for w in ids], dtype=float)
        rng = np.random.default_rng(seed)
        sample_ids = rng.integers(0, len(ids), size=(boots, len(ids)))
        bs = world_sums[sample_ids].sum(axis=1) / world_counts[sample_ids].sum(axis=1)
        return dict(difference=float(world_sums.sum()/world_counts.sum()),
            bootstrap_95pct=[float(x) for x in np.quantile(bs,[.025,.975])],
            worlds=len(ids), resamples=boots, seed=seed)

    # Frozen original comparison untouched. Additional comparison is retrospective.
    main=group_scores(joined)
    dedup = [r for r in joined if not (r['mask_kind'] == 'source_correlated' and r['retention_requested'] == 1.)]
    ambiguous = [r for r in joined if r['cert'] == 'UNKNOWN']
    certs = [r for r in joined if r['cert'] != 'UNKNOWN']
    for r in joined:
        if r['cert'] != 'UNKNOWN' and r['hybrid_exact_then_static'] != r['label_actual']:
            raise AssertionError('No exact certificate should disagree with factual outcome')
        if r['cert'] == 'UNKNOWN' and r['hybrid_exact_then_static'] != r['static_logistic']:
            raise AssertionError('Unresolved case not using unchanged static probability')
    tot_gain=main['static_logistic'] - main['timed_logistic']
    exact_gain=main['static_logistic'] - main['hybrid_exact_then_static']
    summary=dict(
        analysis_type='POST-HOC RETROSPECTIVE DIAGNOSTIC; no frozen pre-run comparison changed',
        heldout=main, dedup_100pct=group_scores(dedup), unresolved_only=group_scores(ambiguous), certified_only=group_scores(certs),
        temporal_minus_hybrid=world_ci(joined,'timed_logistic','hybrid_exact_then_static',bootstrap_reps),
        temporal_minus_hybrid_dedup=world_ci(dedup,'timed_logistic','hybrid_exact_then_static',bootstrap_reps),
        montecarlo_minus_hybrid=world_ci(joined,'mc_event_posterior','hybrid_exact_then_static',bootstrap_reps),
        montecarlo_minus_hybrid_unresolved=world_ci(ambiguous,'mc_event_posterior','hybrid_exact_then_static',bootstrap_reps),
        temporal_minus_hybrid_unresolved=world_ci(ambiguous,'timed_logistic','hybrid_exact_then_static',bootstrap_reps),
        static_to_temporal_gain=tot_gain,
        static_to_hybrid_gain=exact_gain,
        fraction_of_temporal_gain_accounted_for_by_exact_gate=exact_gain/tot_gain,
        fraction_of_temporal_gain_accounted_for_by_exact_gate_dedup=(group_scores(dedup)['static_logistic']-group_scores(dedup)['hybrid_exact_then_static'])/(group_scores(dedup)['static_logistic']-group_scores(dedup)['timed_logistic']),
        interpretation='Descriptive decomposition on the evaluated dataset; not a causal attribution or pre-registered claim.',
        information_boundary='Public predictions and observations determine hybrid; evaluator labels enter only in scores().')
    return joined,summary


def run(root, seed=20261115, boots=5000):
    root=Path(root)
    pub=public_predictions(root)
    scored=read_csv(root / 'results/evaluator_ONLY/heldout_scored.csv')
    rows,summary=scores(pub,scored,seed=seed,bootstrap_reps=boots)
    out=root/'results/posthoc_exact_static'
    out.mkdir(parents=True,exist_ok=True)
    with open(out/'heldout_predictions_evaluator_ONLY.csv','w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(sorted(rows,key=lambda x:x['case_id']))
    (out/'SUMMARY_POSTHOC.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default='.')
    ap.add_argument('--bootstrap-reps',type=int,default=5000)
    a=ap.parse_args()
    run(a.root,boots=a.bootstrap_reps)
