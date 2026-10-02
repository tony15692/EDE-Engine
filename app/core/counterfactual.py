from statistics import mean
from .models import BURDEN_DIMS, Requirement, Topology, Estimate

REL={'actions':.08,'handling_minutes':.15,'rework':.25,'waiting_minutes':.40,'financial_cost':.40,'cognitive_load':.20,'uncertainty_minutes':.40,'temporal_span_days':.35}
def source_interval(value,dim):
    rel=REL.get(dim,.30); half=abs(value)*rel; return max(0,value-half),value+half
def _structural(st,req):
    s=st.share
    return {'actions':req.actions_per_unit*s,'handling_minutes':req.minutes_per_unit*s,'rework':req.rework_per_unit*s,'waiting_minutes':req.waiting_minutes_per_unit*s,'financial_cost':req.financial_cost_per_unit*s,'cognitive_load':req.cognitive_load_per_unit*s,'uncertainty_minutes':req.uncertainty_minutes_per_unit*s,'temporal_span_days':req.temporal_span_days_per_unit*s}
def _matches(records,actor,dim): return [r for r in (records or []) if r.get('actor')==actor and r.get('dimension')==dim and r.get('observed') is not None]
def estimate(topology,req,method='structural',analogues=None,pilot=None,expert=None):
    method=str(method or 'structural').lower()
    if method not in {'structural','analogue','pilot_calibrated','expert','hybrid'}: method='structural'
    vals=[]
    for st in topology.stages:
        for dim,base in _structural(st,req).items():
            v=base; lo,hi=source_interval(v,dim); stype='structural'; refs=['requirement','topology']; assumption='Allocated declared requirement workload by topology share.'
            pm=_matches(pilot,st.actor,dim); am=_matches(analogues,st.actor,dim); em=[x for x in (expert or []) if x.get('actor')==st.actor and x.get('dimension')==dim and x.get('estimate') is not None]
            if method in {'pilot_calibrated','hybrid'} and pm:
                v=mean(float(p['observed']) for p in pm); lo=float(pm[0].get('lower',v)); hi=float(pm[0].get('upper',v)); stype='pilot_calibrated'; refs=sorted(set(str(p.get('source_id','pilot')) for p in pm)); assumption='Measured post-intervention burden increment.'
            elif method in {'analogue','hybrid'} and am:
                av=mean(float(a['observed']) for a in am); v=.45*v+.55*av; lo,hi=source_interval(v,dim); stype='analogue'; refs=sorted(set(str(a.get('source_id','analogue')) for a in am)); assumption='Blended structural estimate with supplied structurally similar observations.'
            elif method in {'expert','hybrid'} and em:
                ex=em[0]; v=float(ex['estimate']); lo=float(ex.get('lower',v)); hi=float(ex.get('upper',v)); stype='expert'; refs=[str(ex.get('source_id','expert'))]; assumption=str(ex.get('assumption','Explicit expert-supplied assumption.'))
            role='pilot_observation' if stype=='pilot_calibrated' else 'analogue_evidence' if stype=='analogue' else 'expert_assumption' if stype=='expert' else 'requirement_allocation'
            vals.append(Estimate(st.actor,dim,v,lo,hi,stype,tuple(refs),assumption,base_estimate=base,increment_over_base=v-base,evidence_role=role))
    return vals
def aggregate(estimates):
    out={}
    for e in estimates: out.setdefault(e.actor,{})[e.dimension]=e.estimate
    return out
def conservation(estimates,req):
    expected={'actions':req.actions_per_unit,'handling_minutes':req.minutes_per_unit,'rework':req.rework_per_unit,'waiting_minutes':req.waiting_minutes_per_unit,'financial_cost':req.financial_cost_per_unit,'cognitive_load':req.cognitive_load_per_unit,'uncertainty_minutes':req.uncertainty_minutes_per_unit,'temporal_span_days':req.temporal_span_days_per_unit}
    totals={d:sum(e.base_estimate for e in estimates if e.dimension==d) for d in BURDEN_DIMS}
    return {d:{'allocated_requirement_workload':round(totals[d],6),'declared':round(expected[d],6),'error':round(totals[d]-expected[d],6),'evidence_adjustment':round(sum(e.estimate-e.base_estimate for e in estimates if e.dimension==d),6)} for d in BURDEN_DIMS}
