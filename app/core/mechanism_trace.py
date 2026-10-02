from .counterfactual import estimate
from .models import BURDEN_DIMS,Capacity
def trace(topology,req,capacities,volume=1.0,method='structural',pilot=None,analogues=None):
 est=estimate(topology,req,method,pilot=pilot,analogues=analogues);by={(e.actor,e.dimension):e for e in est};steps=[];n=0
 attrs={'actions':'actions_per_unit','handling_minutes':'minutes_per_unit','rework':'rework_per_unit','waiting_minutes':'waiting_minutes_per_unit','financial_cost':'financial_cost_per_unit','cognitive_load':'cognitive_load_per_unit','uncertainty_minutes':'uncertainty_minutes_per_unit','temporal_span_days':'temporal_span_days_per_unit'}
 for stage in topology.stages:
  for dim in BURDEN_DIMS:
   e=by.get((stage.actor,dim))
   if not e:continue
   n+=1;steps.append({'step':n,'stage':stage.name,'actor':stage.actor,'dimension':dim,'operation':'ALLOCATE','input':round(getattr(req,attrs[dim]),6),'multiplier':round(stage.share,6),'output':round(e.base_estimate,6),'reason':f'{stage.actor} receives {stage.share:.3f} of declared requirement workload.'})
   if e.source_type!='structural':
    n+=1;steps.append({'step':n,'stage':stage.name,'actor':stage.actor,'dimension':dim,'operation':'EVIDENCE_ADJUST','input':round(e.base_estimate,6),'observed_or_supplied':round(e.estimate,6),'adjustment':round(e.increment_over_base,6),'output':round(e.estimate,6),'source_type':e.source_type,'source_refs':list(e.source_refs),'reason':e.assumption})
 utils=[]
 for stage in topology.stages:
  e=by.get((stage.actor,'handling_minutes'));mins=(e.estimate if e else 0)*volume;cap=capacities.get(stage.actor,Capacity(stage.actor,240,.85));u=mins/max(1,cap.minutes_per_day);utils.append((stage.actor,u));n+=1;steps.append({'step':n,'stage':stage.name,'actor':stage.actor,'dimension':'system_pressure','operation':'CAPACITY_TEST','daily_minutes':round(mins,6),'capacity_minutes_per_day':cap.minutes_per_day,'utilisation':round(u,6),'target':cap.utilisation_target})
 b=max(utils,key=lambda x:x[1]) if utils else (None,0)
 return {'topology_id':topology.topology_id,'topology_name':topology.name,'method':method,'scenario_boundary':'MODELED_MECHANISM_TRACE_NOT_CAUSAL','steps':steps,'bottleneck':{'actor':b[0],'utilisation':round(b[1],6)},'actor_dimension_estimates':[e.to_dict() for e in est]}
