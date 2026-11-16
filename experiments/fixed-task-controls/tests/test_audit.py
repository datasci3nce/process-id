import sys
from pathlib import Path
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import run_audit
RES=HERE/'results'

def test_public_only_before_scoring():
 cs,pr=run_audit.loadpublic()
 assert len(cs)==1600
 assert 'label_actual' not in pr.columns
 assert not any('private_edges' in c or 'truth' in c for c in cs.values())

def test_gate_correct_and_only_replaces_certified():
 d=pd.read_csv(RES/'scored_reanalyses_EVALUATOR_ONLY.csv')
 assert len(d)==1600
 unknown=d.exact_now=='UNKNOWN'
 for k in ['static_logistic','timed_logistic','dde_delayed','dde_no_delay','mc_event_posterior']:
  assert np.allclose(d.loc[unknown,'gate_'+k],d.loc[unknown,k])
  assert ((d.loc[~unknown,'gate_'+k]-d.loc[~unknown,'label_actual']).abs()<1e-12).all()

def test_acquisition_exact_and_matched():
 d=pd.read_csv(RES/'acquisition_paths_EVALUATOR_ONLY.csv')
 assert len(d)==320*3*9
 assert d.groupby(['case_id','policy']).size().eq(9).all()
 assert not (((d.cert=='YES')&(d.factual_truth==0))|((d.cert=='NO')&(d.factual_truth==1))).any()
 assert d.groupby(['case_id','policy']).identified.apply(lambda z:(z.diff().fillna(0)>=0).all()).all()
 # all approaches see identical starting observation count within case
 z=d[d.k==0].pivot(index='case_id',columns='policy',values='n_observed')
 assert z.nunique(axis=1).eq(1).all()

def test_wiki_full_retention_cannot_be_percolation_effect():
 x=pd.read_csv(RES/'wiki_same_graph_different_candidates.csv').set_index('method')
 assert x.loc['two_hop','changed_rank']==65
 assert x.loc['common_in','changed_rank']==103

def test_corrupt_stress_labels():
 x=pd.read_csv(RES/'single_corrupted_observation_STRESS.csv')
 assert len(x)==1595
 assert x.new_cert.sum()==709 and x.cert_error.sum()==30

def test_ce_same_macro_prediction_by_construction():
 x=pd.read_csv(RES/'ce_saved_exact_curves_source_copy.csv')
 names=['emergent_stochastic','isotropic_stochastic_control','declining_path_stochastic_control']
 d=x[x.model.isin(names)]
 for (scheme,p),g in d.groupby(['scheme','retention_probability']):
  assert len(g)==3
  assert np.max(g.recovery_macro_2)-np.min(g.recovery_macro_2)<1e-12
  assert np.max(g.bayes_brier_macro_2)-np.min(g.bayes_brier_macro_2)<1e-12
