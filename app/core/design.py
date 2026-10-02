from itertools import permutations
from .models import Requirement, Capacity, Stage, Topology, BURDEN_DIMS
from .counterfactual import estimate,aggregate,conservation
def generate_topologies(actors,req,max_stages=3):
    eligible=[a.actor_id for a in actors if a.eligible]; tops=[]; idx=0
    for depth in range(1,max_stages+1):
        for seq in permutations(eligible,depth):
            idx+=1; share=1/depth; stages=tuple(Stage(f'Stage {i+1}',a,share) for i,a in enumerate(seq))
            tops.append(Topology(f'T{idx:03d}',' → '.join(seq),f'{depth}-stage architecture using '+', '.join(seq),stages))
    return tops
def score(topology,req,capacities,volume,method='structural',pilot=None,analogues=None):
    est=estimate(topology,req,method,pilot=pilot,analogues=analogues); agg=aggregate(est); rows=[]; util={}
    for actor,vals in agg.items():
        cap=capacities.get(actor,Capacity(actor,240,.85)); mins=vals.get('handling_minutes',0)*volume; util[actor]=mins/max(1,cap.minutes_per_day)
        rows.append({'actor':actor,**{d:round(vals.get(d,0),4) for d in BURDEN_DIMS},'daily_minutes':round(mins,2),'utilisation':round(util[actor],3)})
    return {'topology_id':topology.topology_id,'name':topology.name,'description':topology.description,'stages':[s.__dict__ for s in topology.stages],'actors':rows,'handoffs':max(0,len(topology.stages)-1),'total_handling_minutes_per_unit':round(sum(v.get('handling_minutes',0) for v in agg.values()),4),'peak_utilisation':round(max(util.values(),default=0),4),'bottleneck':max(util,key=util.get) if util else None,'conservation':conservation(est,req),'prediction_method':method,'prediction_records':[e.to_dict() for e in est],'prediction_summary':{'source_types':sorted(set(e.source_type for e in est)),'min_estimate':min((e.estimate for e in est),default=0),'max_estimate':max((e.estimate for e in est),default=0),'mean_interval_width':sum(e.upper-e.lower for e in est)/max(1,len(est)),'mean_evidence_adjustment':sum(abs(e.increment_over_base) for e in est)/max(1,len(est))}}
def dominated(a,b):
    dims=['peak_utilisation','handoffs','total_handling_minutes_per_unit']; le=all(a[d]<=b[d] for d in dims); lt=any(a[d]<b[d] for d in dims); return le and lt
def frontier(rows): return [a for a in rows if not any(dominated(b,a) for b in rows if b is not a)]
def apply_constraints(rows,max_util=.85,max_handoffs=2):
    for r in rows:r['feasible']=r['peak_utilisation']<=max_util and r['handoffs']<=max_handoffs
    return rows
def search(actors,req,capacities,volume=0,max_util=.85,max_handoffs=2,method='structural',pilot=None,analogues=None):
    rows=apply_constraints([score(t,req,capacities,volume,method,pilot,analogues) for t in generate_topologies(actors,req)],max_util,max_handoffs)
    feasible=[r for r in rows if r['feasible']]; return {'candidates':rows,'candidate_count':len(rows),'feasible_count':len(feasible),'frontier':[r['topology_id'] for r in frontier(feasible or rows)]}
