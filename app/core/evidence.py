from collections import Counter
def profile(events):
 if not events:return {'mean_confidence':0,'min_confidence':0,'source_count':0,'verified_share':0}
 conf=[e.confidence for e in events]
 return {'mean_confidence':round(sum(conf)/len(conf),4),'min_confidence':round(min(conf),4),'source_count':len(set(e.source_id for e in events if e.source_id)),'verified_share':round(sum(1 for e in events if e.confidence>=.9)/len(events),4),'confidence_band':Counter('HIGH' if c>=.9 else 'MEDIUM' if c>=.7 else 'LOW' for c in conf)}
def trace(events,unit_id):
 ev=sorted([e for e in events if e.unit_id==unit_id],key=lambda e:e.timestamp)
 return [{'event_id':e.event_id,'source_id':e.source_id,'confidence':e.confidence,'activity':e.activity,'actor':e.actor} for e in ev]
