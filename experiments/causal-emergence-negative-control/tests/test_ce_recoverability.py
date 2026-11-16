import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import numpy as np
from ce_recoverability import (Q_SPECS,P_VALUES,GROUPS,transition_matrix,aggregate_transition,causal_power,
                                ce2_causal_primitives,trajectory_weights,mask_statistics,calculate,check_results)

def test_causal_primitives_extremes():
    assert abs(ce2_causal_primitives(np.eye(8))-1)<1e-12
    assert abs(ce2_causal_primitives(np.ones((8,8))/8))<1e-12

def test_causal_primitives_match_official_loop_form():
    P=transition_matrix(Q_SPECS['emergent_stochastic'])
    n=len(P)
    a=sum(P[i,j]*(P[i,j]+1-sum(P[k,j] for k in range(n) if k!=i)/(n-1)) for i in range(n) for j in range(n))/n-1
    assert abs(a-ce2_causal_primitives(P))<1e-12

def test_strong_lumpability():
    for q in Q_SPECS.values():
        P=transition_matrix(q)
        for g in GROUPS.values():
            agg=aggregate_transition(P,g)
            assert np.allclose(agg.sum(axis=1),1.)

def test_uniform_input_power():
    assert abs(causal_power(np.eye(8))-1.)<1e-12
    assert abs(causal_power(np.ones((8,8))/8))<1e-12

def test_unobserved_and_full_observation():
    for q in Q_SPECS.values():
        w=trajectory_weights(transition_matrix(q))
        for claim in ('micro_8','meso_4','macro_2'):
            assert abs(mask_statistics(w,0)[f'recovery_{claim}'])<1e-12
            assert abs(mask_statistics(w,511)[f'recovery_{claim}']-1)<1e-12

def test_exact_mask_reference_on_hand_calculated_case():
    w=trajectory_weights(transition_matrix(Q_SPECS['emergent_stochastic']))
    # bit6 is direct observed macro at t=2
    assert abs(mask_statistics(w,1<<6)['recovery_macro_2']-1)<1e-12
    # Only macro t0 observed, stochastic nonzero transitions keep both macro t2 values feasible
    assert abs(mask_statistics(w,1<<0)['recovery_macro_2'])<1e-12
    # Same observation for deterministic macro propagation is sufficient
    d=trajectory_weights(transition_matrix(Q_SPECS['emergent_deterministic']))
    assert abs(mask_statistics(d,1<<0)['recovery_macro_2']-1)<1e-12

def test_complete_experiment(tmp_path):
    mr,mk,cv=calculate(tmp_path)
    assert check_results(mr,mk,cv)['passed']
    assert len(mk)==len(Q_SPECS)*(512+8+64)

def test_reproducible_outputs(tmp_path):
    a=tmp_path/'a';b=tmp_path/'b'
    calculate(a);calculate(b)
    for f in ('causal_power_by_model.csv','per_mask_exact.csv','recoverability_curves_exact.csv','DESIGN.json'):
        assert (a/f).read_bytes()==(b/f).read_bytes()

def test_zero_causal_random_control_has_easier_macro_task():
    q=Q_SPECS['all_random_negative_control'];w=trajectory_weights(transition_matrix(q))
    stats=mask_statistics(w,1<<6)
    assert stats['recovery_macro_2']==1.
    assert stats['recovery_micro_8']==0.
