import csv,json,os,xml.etree.ElementTree as ET
from datetime import datetime, timezone
from .models import Event

FIELD_ALIASES={'event_id':['event_id','event','id'],'unit_id':['unit_id','case_id','case','application_id','process_id'],'timestamp':['timestamp','time','datetime','date','complete_timestamp','start_timestamp'],'actor':['actor','org:resource','resource','role','responsible'],'activity':['activity','concept:name','task','event_type','name'],'state_before':['state_before','from_state'],'state_after':['state_after','to_state'],'source_id':['source_id','source','document_id'],'confidence':['confidence','evidence_confidence'],'completion':['completion','complete','completed'],'rework':['rework','is_rework']}

def pick(row,key):
    for alias in FIELD_ALIASES[key]:
        if alias in row and row[alias] not in (None,''): return row[alias]
    return ''
def parse_time(v):
    if v is None or v=='': return 0.0
    try:return float(v)
    except ValueError:pass
    s=str(v).replace('Z','+00:00')
    try:
        dt=datetime.fromisoformat(s)
        return dt.timestamp() if dt.tzinfo else dt.replace(tzinfo=timezone.utc).timestamp()
    except Exception:return 0.0
def to_float(v,default=1.0):
    try:return float(v)
    except Exception:return default
def _event_from_row(row,i):
    return Event(str(pick(row,'event_id') or f'e{i:06d}'),str(pick(row,'unit_id') or 'unit-unknown'),parse_time(pick(row,'timestamp')),str(pick(row,'actor') or 'Unknown'),str(pick(row,'activity') or 'Unknown'),str(pick(row,'state_before')),str(pick(row,'state_after')),str(pick(row,'source_id') or f'row-{i}'),max(0,min(1,to_float(pick(row,'confidence'),1))),int(to_float(pick(row,'completion'),1)),int(to_float(pick(row,'rework'),0)),{k:v for k,v in row.items() if k and k not in sum(FIELD_ALIASES.values(),[])})
def load_csv(path):
    with open(path,newline='',encoding='utf-8-sig') as f:return [_event_from_row(r,i) for i,r in enumerate(csv.DictReader(f),1)]
def load_json(path):
    with open(path,encoding='utf-8') as f:data=json.load(f)
    rows=data if isinstance(data,list) else data.get('events',[])
    return [_event_from_row(r,i) for i,r in enumerate(rows,1)]
def load_xes(path):
    root=ET.parse(path).getroot(); out=[]; idx=0
    for trace in root.findall('.//{*}trace'):
        attrs={x.attrib.get('key'):x.attrib.get('value','') for x in trace.findall('./{*}string')}
        uid=attrs.get('concept:name') or attrs.get('case:concept:name') or f'case-{len(out)+1}'
        for ev in trace.findall('./{*}event'):
            row={x.attrib.get('key'):x.attrib.get('value','') for x in ev}; row['unit_id']=uid; idx+=1; out.append(_event_from_row(row,idx))
    return out
def load(path):
    ext=os.path.splitext(path)[1].lower()
    if ext=='.csv':return load_csv(path)
    if ext=='.json':return load_json(path)
    if ext=='.xes':return load_xes(path)
    raise ValueError(f'Unsupported file type: {ext}')
def readiness(events):
    n=len(events); units={e.unit_id for e in events}; actors={e.actor for e in events}; acts={e.activity for e in events}
    fields={'unit_id':sum(bool(e.unit_id and e.unit_id!='unit-unknown') for e in events)/max(1,n),'timestamp':sum(e.timestamp>0 for e in events)/max(1,n),'actor':sum(bool(e.actor and e.actor!='Unknown') for e in events)/max(1,n),'activity':sum(bool(e.activity and e.activity!='Unknown') for e in events)/max(1,n),'source_id':sum(bool(e.source_id) for e in events)/max(1,n),'confidence':sum(e.confidence<1 for e in events)/max(1,n)}
    trajectory=fields['unit_id']>=.95 and fields['timestamp']>=.95 and fields['activity']>=.95
    work=trajectory and fields['actor']>=.90
    return {'rows':n,'units':len(units),'actors':len(actors),'activities':len(acts),'field_coverage':fields,'trajectory_observation':'READY' if trajectory else 'NOT READY','measured_actor_work':'READY' if work else 'NOT READY','evidence_traceability':'READY' if fields['source_id']>=.90 else 'PARTIAL','counterfactual_calibration':'NOT READY','notes':['Calibration requires measured post-intervention observations.','Low-granularity logs can support trajectory observation even when work measurement is unavailable.']}
