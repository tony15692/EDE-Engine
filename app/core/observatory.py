from collections import Counter,defaultdict
from statistics import mean,median
def by_unit(events):
 d=defaultdict(list)
 for e in events:d[e.unit_id].append(e)
 for k in d:d[k].sort(key=lambda e:(e.timestamp,e.event_id))
 return d
def trajectory(events,unit_id):
 ev=sorted([e for e in events if e.unit_id==unit_id],key=lambda e:(e.timestamp,e.event_id))
 if not ev:return {'unit_id':unit_id,'events':[]}
 gaps=[max(0,e2.timestamp-e1.timestamp)/86400 for e1,e2 in zip(ev,ev[1:])]
 states=[e.state_after or e.activity for e in ev]
 changes=sum(a!=b for a,b in zip(states,states[1:]));repeats=len(states)-len(set(states));vel=[1/g if g>0 else 0 for g in gaps];accel=[v2-v1 for v1,v2 in zip(vel,vel[1:])]
 return {'unit_id':unit_id,'event_count':len(ev),'activities':len(set(e.activity for e in ev)),'start':ev[0].timestamp,'end':ev[-1].timestamp,'span_days':max(0,(ev[-1].timestamp-ev[0].timestamp)/86400),'median_gap_days':median(gaps) if gaps else 0,'repeated_states':repeats,'state_changes':changes,'velocity':mean(vel) if vel else 0,'acceleration':mean(accel) if accel else 0,'coherence':changes/max(1,len(states)-1),'recurrence':sum(1 for x,c in Counter(states).items() if c>1),'events':[e.to_dict() for e in ev],'actors':sorted(set(e.actor for e in ev))}
def system_overview(events):
 units=by_unit(events);transitions=Counter();actor_edges=Counter();activities=Counter()
 for e in events:activities[e.activity]+=1
 for ev in units.values():
  for a,b in zip(ev,ev[1:]):transitions[(a.activity,b.activity)]+=1;actor_edges[(a.actor,b.actor)]+=int(a.actor!=b.actor)
 terminal=Counter((ev[-1].state_after or ev[-1].activity) for ev in units.values() if ev);mean_conf=mean([e.confidence for e in events]) if events else 0
 return {'events':len(events),'units':len(units),'actors':len(set(e.actor for e in events)),'activities':len(activities),'mean_confidence':round(mean_conf,4),'terminal_states':terminal.most_common(8),'top_transitions':[{'from':a,'to':b,'count':c} for (a,b),c in transitions.most_common(12)],'actor_handoffs':[{'from':a,'to':b,'count':c} for (a,b),c in actor_edges.most_common(12)],'activity_volume':activities.most_common(12)}
def review_signal(t):
 if t['acceleration']>0 and t['recurrence']>0:return 'REVIEW'
 if t['recurrence']>0 or t['span_days']>7:return 'WATCH'
 return 'NORMAL'
