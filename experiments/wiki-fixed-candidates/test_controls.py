import random, unittest
from wiki_fixed_candidates import eval_graph, stable
from wiki_mask_replications import calc, mix
class Tests(unittest.TestCase):
 def test_hash(self):
  self.assertEqual(stable("holdout-source","Agent0Mass"),int("d7b698a281f2d2f5",16))
 def test_mix(self):
  self.assertTrue(all(0<=mix(x,r)<1 for x in [0,1,2**32-1] for r in [0,1,63]))
 def test_p1_invariant(self):
  rng=random.Random(91);nodes=[f"n{i}" for i in range(120)];E={}
  for s in nodes:
   for t in rng.sample([n for n in nodes if n!=s],25):E[s,t]=1
  rows,configs,held=eval_graph(E)
  for method in ["degree","two_hop","common_in","path3"]:
   a={r["source"]:r["rank"] for r in rows if r["p"]==1 and r["mode"]=="independent" and r["method"]==method}
   b={r["source"]:r["rank"] for r in rows if r["p"]==1 and r["mode"]=="source_correlated" and r["method"]==method}
   self.assertEqual(a,b)
  c=calc(E,reps=2)
  self.assertEqual(len(c),8)
if __name__=="__main__":unittest.main()
