import unittest
import itertools
import numpy as np
from core import make_world, make_mask, certify, shortest, build_edge_views, montecarlo_prob, scalar_features, dde_surrogate
class TestCore(unittest.TestCase):
 def test_shortest(self):
  self.assertEqual(shortest(4,[(0,1,2),(0,2,5),(1,3,2),(2,3,1)]),4)
 def test_constructed_same_topology_different_time(self):
  def c(ds):
   return {'n':3,'deadline':4,'potential_edges':[[0,1],[1,2]],'observations':[{'edge_idx':0,'status':'live','delay':ds[0]},{'edge_idx':1,'status':'live','delay':ds[1]}]}
  self.assertEqual(certify(c([1,2])),'YES')
  self.assertEqual(certify(c([4,6])),'NO')
  self.assertEqual(scalar_features(c([1,2]))[0],scalar_features(c([4,6]))[0])
 def test_true_absence_ambiguity(self):
  c={'n':3,'deadline':4,'potential_edges':[[0,1],[1,2]],'observations':[]}
  self.assertEqual(certify(c),'UNKNOWN')
 def test_known_negative(self):
  c={'n':3,'deadline':4,'potential_edges':[[0,1],[1,2]],'observations':[{'edge_idx':0,'status':'failed','delay':None}]}
  self.assertEqual(certify(c),'NO')
 def test_exact_bruteforce_small(self):
  for statuses in itertools.product([-1,0,1,2,4,6],repeat=3):
   c={'n':4,'deadline':4,'potential_edges':[[0,1],[1,2],[2,3]],'observations':[]}
   allowed=[]
   for i,z in enumerate(statuses):
    if z!=-1:
     c['observations'].append({'edge_idx':i,'status':'failed' if z==0 else 'live','delay':int(z) if z>0 else None})
   for zz in itertools.product([0,1,2,4,6],repeat=3):
    if all(z==-1 or z==w for z,w in zip(statuses,zz)):
     e=[(i,i+1,w) for i,w in enumerate(zz) if w!=0]
     allowed.append(shortest(4,e)<=4)
   verdict='YES' if all(allowed) else 'NO' if not any(allowed) else 'UNKNOWN'
   self.assertEqual(certify(c),verdict)
 def test_observation_isolation(self):
  w=make_world(1,16,'development',10);c=make_mask(w,'independent',.5,11)
  pub=dict(c);pub['observations']=c['observations'].copy()
  self.assertFalse(any('truth' in x or 'private_edges' in x for x in pub))
  self.assertTrue(certify(c) in ('YES','NO','UNKNOWN'))
  self.assertTrue(0<=montecarlo_prob(c,32,100,.7,np.ones(4)/4)<=1)
  self.assertTrue(np.isfinite(dde_surrogate(c,.7,np.ones(4)/4)))
 def test_canonical_groups(self):
  w=make_world(1,32,'heldout',10)
  c=make_mask(w,'source_correlated',.5,11);d=make_mask(w,'source_correlated',.5,11)
  self.assertEqual(c,d)
 def test_certificates_sound(self):
  for n in [8,16,32,64]:
   for i in range(12):
    w=make_world(i,n,'heldout',i+51)
    for k in ('independent','source_correlated','targeted'):
     c=make_mask(w,k,.5,i+79);verdict=certify(c)
     self.assertFalse(verdict=='YES' and w['truth']==0)
     self.assertFalse(verdict=='NO' and w['truth']==1)
 if __name__=='__main__':unittest.main()
