from collections import defaultdict,Counter
from statistics import median
def _per_unit(events):
 d=defaultdict(list)
 for e in events:d[e.unit_id].append(e)
 for k in d:d[k]=sorted(d[k],key=lambda x:(x.timestamp,x.event_id))
 return d
def discover_system(events,min_support=.02):
 units=_per_unit(events); total=max(1,len(units)); act_cases=defaultdict(set);actor_cases=defaultdict(set);trans=Counter();dur=defaultdict(list);act_actor=Counter();loops=Counter();branches=Counter();starts=Counter();terms=Counter();gaps=[];ain=Counter();aout=Counter();freq=Counter()
 for uid,seq in units.items():
  seen=set()
  for i,e in enumerate(seq):
   freq[e.activity]+=1;act_cases[e.activity].add(uid);actor_cases[e.actor].add(uid);act_actor[(e.activity,e.actor)]+=1
   if i==0:starts[e.activity]+=1
   if i==len(seq)-1:terms[e.activity]+=1
   if e.activity in seen:loops[e.activity]+=1
   seen.add(e.activity)
   if i+1<len(seq):
    n=seq[i+1];k=(e.activity,n.activity);trans[k]+=1; aout[e.activity]+=1;ain[n.activity]+=1
    dur[k].append(max(0,n.timestamp-e.timestamp)/60)
    if e.actor!=n.actor:branches[(e.actor,n.actor)]+=1
    gap=max(0,n.timestamp-e.timestamp)/3600
    if gap>=24:gaps.append({'unit_id':uid,'from_activity':e.activity,'to_activity':n.activity,'gap_hours':round(gap,2),'from_actor':e.actor,'to_actor':n.actor})
 edges=[{'from':a,'to':b,'count':c,'support':round(sum(1 for seq in units.values() if any(x.activity==a for x in seq) and any(x.activity==b for x in seq))/total,4),'median_gap_minutes':round(median(dur[(a,b)]),2) if dur[(a,b)] else None} for (a,b),c in trans.most_common()]
 nodes=[]
 for a in sorted(freq,key=lambda x:(-freq[x],x)):
  roles=[]; 
  if starts[a]:roles.append('ENTRY')
  if terms[a]:roles.append('TERMINAL')
  if ain[a]>1 and aout[a]>1:roles.append('GATE/BRANCH')
  elif ain[a]>1:roles.append('MERGE')
  elif aout[a]>1:roles.append('BRANCH')
  if loops[a]:roles.append('LOOP-CANDIDATE')
  if not roles:roles.append('TRANSIT')
  actors=sorted([{'actor':aa,'count':c} for (act,aa),c in act_actor.items() if act==a],key=lambda x:-x['count'])
  nodes.append({'activity':a,'event_count':freq[a],'unit_count':len(act_cases[a]),'roles':roles,'actors':actors[:5]})
 paths=Counter(' > '.join(e.activity for e in seq) for seq in units.values())
 bottlenecks=[]
 for a in freq:
  waits=[x for k,vals in dur.items() if k[1]==a for x in vals]
  if waits:bottlenecks.append({'activity':a,'frequency':freq[a],'median_incoming_gap_minutes':round(median(waits),2),'bottleneck_score':round(median(waits)*(1+max(0,ain[a]-aout[a])*.1),2),'incoming_transitions':ain[a],'outgoing_transitions':aout[a]})
 return {'status':'INFERRED_FROM_OBSERVED_EVENTS','event_count':len(events),'unit_count':len(units),'activity_count':len(freq),'actor_count':len(actor_cases),'nodes':nodes,'transitions':edges[:30],'paths':[{'path':p,'units':c,'share':round(c/total,4)} for p,c in paths.most_common(12)],'loops':[{'activity':a,'units_with_repeat':c,'rate':round(c/total,4)} for a,c in loops.most_common(15)],'bottlenecks':sorted(bottlenecks,key=lambda x:x['bottleneck_score'],reverse=True)[:10],'actor_coupling':[{'from_actor':a,'to_actor':b,'handoffs':c} for (a,b),c in branches.most_common(15)],'boundary_gaps':sorted(gaps,key=lambda x:x['gap_hours'],reverse=True)[:20],'method':{'transition_graph':'Observed consecutive activity transitions within units.','role_inference':'Roles inferred from graph structure.','bottleneck_proxy':'Median observed incoming dwell time; not causal.','boundary_gap_rule':'Long gaps are surfaced as candidates; no hidden actor is invented.'},'limits':['Inferred structure is descriptive, not proof of causation.','Unlogged work remains unknown unless declared or externally measured.']}
