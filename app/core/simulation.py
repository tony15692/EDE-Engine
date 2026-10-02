from dataclasses import replace
from .models import Capacity
def simulate(topology,req,capacities,volume=5.0,days=14,growth=.05,shock_day=None,shock=1.0,rework_gain=.25):
    queues={s.actor:0.0 for s in topology.stages}; prev_rework=0.0; rows=[]
    for day in range(1,days+1):
        demand=volume*((1+growth)**(day-1))
        if shock_day and day>=shock_day:demand*=shock
        demand+=prev_rework*rework_gain; stage_util=[]
        for stage in topology.stages:
            cap=capacities.get(stage.actor,Capacity(stage.actor,240,.85)); incoming=demand*stage.share+queues.get(stage.actor,0.0); mins=incoming*req.minutes_per_unit*stage.share; util=mins/max(1,cap.minutes_per_day); throughput=min(incoming,cap.minutes_per_day/max(1,req.minutes_per_unit*stage.share)); queues[stage.actor]=max(0,incoming-throughput); stage_util.append(util)
        completed=min(demand,max(0,demand-sum(queues.values()))); prev_rework=completed*req.rework_per_unit
        rows.append({'day':day,'demand':round(demand,3),'completed':round(completed,3),'completion_ratio':round(completed/max(1,demand),4),'queue':round(sum(queues.values()),3),'peak_utilisation':round(max(stage_util,default=0),4),'rework':round(prev_rework,3)})
    return {'topology_id':topology.topology_id,'daily':rows,'max_queue':max(r['queue'] for r in rows),'peak_utilisation':max(r['peak_utilisation'] for r in rows),'final_queue':rows[-1]['queue'],'mean_completion':sum(r['completion_ratio'] for r in rows)/len(rows),'recovery':next((r['day'] for r in rows[(shock_day or 1)-1:] if r['queue']<=.1 and r['peak_utilisation']<=.85),None)}
def sensitivity(topology,req,capacities,base_volume=5):
    factors=[.75,1,1.25,1.5]; out=[]
    for mf in factors:
        rq=replace(req,minutes_per_unit=req.minutes_per_unit*mf)
        for vf in factors:
            r=simulate(topology,rq,capacities,base_volume*vf,14,growth=.03);r['minutes_factor']=mf;r['volume_factor']=vf;out.append(r)
    return out
