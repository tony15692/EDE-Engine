from collections import Counter
from .observatory import by_unit
def actor_map(events):
 edges=Counter();counts=Counter()
 for e in events:counts[e.actor]+=1
 for ev in by_unit(events).values():
  for a,b in zip(ev,ev[1:]):
   if a.actor!=b.actor:edges[(a.actor,b.actor)]+=1
 return {'nodes':[{'actor':a,'events':n} for a,n in counts.most_common()],'edges':[{'from':a,'to':b,'count':c} for (a,b),c in edges.most_common()]}
def boundary_discovery(events,declared):
 declared=set(declared);observed=set(e.actor for e in events);undeclared=sorted(observed-declared);gaps=[]
 for ev in by_unit(events).values():
  for a,b in zip(ev,ev[1:]):
   gap=max(0,b.timestamp-a.timestamp)/3600
   if gap>=24:gaps.append({'unit_id':b.unit_id,'from_activity':a.activity,'to_activity':b.activity,'gap_hours':round(gap,1),'candidate':'unobserved_work_or_queue'})
 return {'declared':sorted(declared),'observed':sorted(observed),'undeclared_observed':undeclared,'boundary_candidates':gaps[:25],'candidate_count':len(gaps),'note':'Candidates are explanations to investigate, not inferred actors.'}
