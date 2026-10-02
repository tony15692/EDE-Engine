from .observatory import system_overview,trajectory,review_signal
from .evidence import profile,trace
from .system_map import actor_map,boundary_discovery
from .design import search,score
from .simulation import simulate,sensitivity
from .pilot import real_benchmark,pilot_status,make_pilot_template
from .burden import incidence,transfer
from .replay import replay
from .discovery import discover_system
from .mechanism_trace import trace as mechanism_trace
from .counterfactual import estimate
from .models import Topology,Stage
class EDE:
 def __init__(self,events):self.events=list(events)
 def overview(self):return {'system':system_overview(self.events),'evidence':profile(self.events),'actor_map':actor_map(self.events)}
 def trajectory(self,unit_id):
  t=trajectory(self.events,unit_id);t['signal']=review_signal(t);t['evidence']=profile([e for e in self.events if e.unit_id==unit_id]);t['trace']=trace(self.events,unit_id);return t
 def boundaries(self,declared):return boundary_discovery(self.events,declared)
 def discover(self):return discover_system(self.events)
 def design_search(self,actors,req,capacities,volume,max_util,max_handoffs,method='structural',pilot=None,analogues=None):
  result=search(actors,req,capacities,volume,max_util,max_handoffs,method,pilot,analogues)
  baseline=score(Topology('BASELINE','Current: Agency verification','Current baseline.',(Stage('Verification','Agency',1.0),)),req,capacities,volume,'structural')
  b={a['actor']:{d:a.get(d,0) for d in ('handling_minutes','actions','rework','waiting_minutes','financial_cost','cognitive_load','uncertainty_minutes','temporal_span_days')} for a in baseline['actors']}
  result['baseline']=baseline;result['incidence']=incidence(result['candidates'],b);result['transfer']=transfer(result['incidence']);return result
 def simulate(self,topology,req,capacities,**kwargs):return simulate(topology,req,capacities,**kwargs)
 def sensitivity(self,topology,req,capacities,**kwargs):return sensitivity(topology,req,capacities,**kwargs)
 def benchmark(self):return real_benchmark()
 def pilot_status(self,predictions,observations):return pilot_status(predictions,observations)
 def pilot_template(self):return make_pilot_template()
 def replay(self,*args):return replay(self.events,*args)
 def mechanism_trace(self,topology,req,capacities,**kwargs):return mechanism_trace(topology,req,capacities,**kwargs)
 def estimate(self,*args,**kwargs):return estimate(*args,**kwargs)
