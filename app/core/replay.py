from .counterfactual import estimate,aggregate
def _ts(x): return float(x) if not isinstance(x,str) else __import__('datetime').datetime.fromisoformat(x.replace('Z','+00:00')).timestamp()
def replay(events,unit_id,topology,req,capacities):
 original=sorted([e for e in events if e.unit_id==unit_id],key=lambda e:_ts(e.timestamp))
 if not original:raise ValueError(f'Unknown unit_id: {unit_id}')
 estimates=estimate(topology,req,'structural');stage_minutes={s.name:req.minutes_per_unit*s.share for s in topology.stages};stage_wait=req.waiting_minutes_per_unit/max(1,len(topology.stages));trigger_idx=next((i for i,e in enumerate(original) if e.activity==req.trigger_activity),0);out=[]
 for i,e in enumerate(original):
  out.append({'kind':'observed','scenario_only':False,'event_id':e.event_id,'activity':e.activity,'actor':e.actor,'timestamp':_ts(e.timestamp),'state_before':e.state_before,'state_after':e.state_after,'confidence':e.confidence,'source_id':e.source_id})
  if i==trigger_idx:
   cursor=_ts(e.timestamp)
   for j,s in enumerate(topology.stages,1):
    cursor+=stage_wait*60;out.append({'kind':'counterfactual','scenario_only':True,'event_id':f'CF-{topology.topology_id}-{j}','activity':req.name,'actor':s.actor,'timestamp':cursor,'state_before':e.state_after,'state_after':f'{req.requirement_id}:{s.name}','confidence':None,'source_id':f'scenario:{topology.topology_id}','duration_minutes':stage_minutes[s.name],'assumption':'Structural replay; not observed and not causal.'});cursor+=stage_minutes[s.name]*60
 out.sort(key=lambda r:(r['timestamp'],0 if r['kind']=='observed' else 1))
 return {'unit_id':unit_id,'topology':{'id':topology.topology_id,'name':topology.name,'stages':[s.__dict__ for s in topology.stages]},'requirement':req.__dict__,'observed_event_count':len(original),'counterfactual_event_count':sum(x['kind']=='counterfactual' for x in out),'scenario_boundary':'COUNTERFACTUAL_SCENARIO_ONLY','events':out,'actor_summary':aggregate(estimates)}
