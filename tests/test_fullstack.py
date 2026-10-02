import sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from app.server import ensure_seed,DB
from app.core.storage import load_events
from app.core.engine import EDE
from app.core.config import ACTORS,CAPACITIES
from app.core.requirements import DEFAULT_REQUIREMENT
from app.core.design import generate_topologies
from app.core.ingest import load,readiness

class EDETests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):ensure_seed()
 def test_ingest_and_observe(self):
  e=load_events(DB);self.assertGreater(len(e),10);self.assertEqual(readiness(e)['trajectory_observation'],'READY');o=EDE(e).overview();self.assertGreater(o['system']['units'],0)
 def test_trajectory(self):
  e=load_events(DB);u=sorted({x.unit_id for x in e})[0];t=EDE(e).trajectory(u);self.assertGreater(t['event_count'],0);self.assertIn('velocity',t);self.assertIn('coherence',t)
 def test_discovery(self):
  d=EDE(load_events(DB)).discover();self.assertTrue(d['nodes']);self.assertTrue(d['transitions']);self.assertIn('limits',d)
 def test_search(self):
  e=EDE(load_events(DB));r=e.design_search(ACTORS,DEFAULT_REQUIREMENT,CAPACITIES,5,.85,2,'structural');self.assertEqual(r['candidate_count'],156);self.assertIn('frontier',r)
 def test_simulation(self):
  e=load_events(DB);top=generate_topologies(ACTORS,DEFAULT_REQUIREMENT)[0];r=EDE(e).simulate(top,DEFAULT_REQUIREMENT,CAPACITIES,volume=5,days=7,shock_day=4,shock=3);self.assertEqual(len(r['daily']),7);self.assertIn('peak_utilisation',r)
 def test_replay_and_trace(self):
  e=load_events(DB);eng=EDE(e);top=generate_topologies(ACTORS,DEFAULT_REQUIREMENT)[0];u=sorted({x.unit_id for x in e})[0];rp=eng.replay(u,top,DEFAULT_REQUIREMENT,CAPACITIES);tr=eng.mechanism_trace(top,DEFAULT_REQUIREMENT,CAPACITIES,volume=5);self.assertEqual(rp['scenario_boundary'],'COUNTERFACTUAL_SCENARIO_ONLY');self.assertTrue(tr['steps'])
 def test_ingest_json(self):
  temp=ROOT/'tests'/'tmp_events.json';temp.write_text(json.dumps([{'case_id':'C1','concept:name':'Submit','time':'2026-01-01T00:00:00Z','org:resource':'Applicant'}]),encoding='utf8')
  try:self.assertEqual(len(load(temp)),1)
  finally:temp.unlink(missing_ok=True)

if __name__=='__main__':unittest.main()
