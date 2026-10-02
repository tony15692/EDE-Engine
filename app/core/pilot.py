from dataclasses import dataclass,asdict
from typing import Any
REAL_BENCHMARK={'name':'EDE real event-log benchmark — Sepsis Cases','dataset':'Sepsis Cases - Event Log','source':'4TU.ResearchData','doi':'10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460','source_url':'https://data.4tu.nl/articles/_/12707639/1','status':'ARCHIVED_REAL_BENCHMARK','rows':15214,'cases':1050,'activities':16,'holdout_points':4081,'split':'chronological 70/30 by first-event timestamp','metrics':[{'model':'B0','features':'current/global smoothed next distribution','log_loss':2.1649040972,'accuracy':.2308257780},{'model':'B1','features':'current + previous activity','log_loss':1.2689860573,'accuracy':.5606469003},{'model':'B2','features':'B1 + inter-event time bucket','log_loss':1.2540197708,'accuracy':.5704484195},{'model':'B3','features':'B2 + org:group','log_loss':1.2964784992,'accuracy':.5692232296}]}
DIMENSIONS=('actions','handling_minutes','rework','waiting_minutes','financial_cost','cognitive_load','uncertainty_minutes','temporal_span_days')
@dataclass(frozen=True)
class PilotObservation:
 design_id:str;actor:str;dimension:str;observed:float;source_id:str;period:str='';notes:str=''
def real_benchmark():return REAL_BENCHMARK
def pilot_status(predictions:list[dict[str,Any]],observations:list[dict[str,Any]]):
 obs=[o for o in observations if o.get('observed') is not None and o.get('source_id')];pred=[p for p in predictions if p.get('estimate') is not None]
 return {'prediction_records':len(pred),'pilot_observations':len(obs),'calibration_ready':bool(obs and pred),'observed_dimensions':sorted({str(o.get('dimension')) for o in obs}),'observed_designs':sorted({str(o.get('design_id')) for o in obs}),'observed_actors':sorted({str(o.get('actor')) for o in obs}),'status':'READY_FOR_CALIBRATION' if obs and pred else 'AWAITING_POST_INTERVENTION_OBSERVATIONS'}
def make_pilot_template():return [asdict(PilotObservation('DESIGN_ID','ACTOR','handling_minutes',0.0,'PILOT_SOURCE','2026-09-30','replace placeholder'))]
