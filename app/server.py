import argparse,csv,io,json,threading,webbrowser
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from pathlib import Path
from .core.ingest import load,_event_from_row,readiness
from .core.storage import init,replace_events,load_events,load_pilot_observations,insert_pilot_observations
from .core.engine import EDE
from .core.models import Requirement,Topology,Stage
from .core.requirements import DEFAULT_REQUIREMENT
from .core.config import ACTORS,CAPACITIES
from .core.design import generate_topologies
from .core.observatory import by_unit
from .core.validation import compare
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data';DB=DATA/'ede.sqlite3';DEMO=DATA/'demo_caseflow.csv';FRONTEND=ROOT/'frontend'
def ensure_seed():
 c=init(DB);n=c.execute('SELECT COUNT(*) FROM events').fetchone()[0];c.close()
 if n==0 and DEMO.exists():replace_events(DB,load(str(DEMO)))
def req_from(values):
 def num(k,d):
  x=values.get(k,d);x=x[0] if isinstance(x,(list,tuple)) and x else x
  try:return float(x)
  except:return float(d)
 return Requirement(DEFAULT_REQUIREMENT.requirement_id,str(values.get('name',DEFAULT_REQUIREMENT.name)),str(values.get('trigger',DEFAULT_REQUIREMENT.trigger_activity)),num('actions',DEFAULT_REQUIREMENT.actions_per_unit),num('minutes',DEFAULT_REQUIREMENT.minutes_per_unit),num('rework',DEFAULT_REQUIREMENT.rework_per_unit),num('waiting',DEFAULT_REQUIREMENT.waiting_minutes_per_unit),num('financial',DEFAULT_REQUIREMENT.financial_cost_per_unit),num('cognitive',DEFAULT_REQUIREMENT.cognitive_load_per_unit),num('uncertainty',DEFAULT_REQUIREMENT.uncertainty_minutes_per_unit),num('span',DEFAULT_REQUIREMENT.temporal_span_days_per_unit))
def topology_for(tid,req):
 tops=generate_topologies(ACTORS,req);return next((t for t in tops if t.topology_id==tid),tops[0])
def public_config():
 return {'product':{'name':'EDE','full_name':'Evidence-aware Dynamics & Design Engine','version':'1.0.0'},'actors':[a.__dict__ for a in ACTORS],'capacities':{k:v.__dict__ for k,v in CAPACITIES.items()},'default_requirement':req_from({}).__dict__,'burden_dimensions':['actions','handling_minutes','rework','waiting_minutes','financial_cost','cognitive_load','uncertainty_minutes','temporal_span_days'],'estimation_modes':['structural','analogue','pilot_calibrated','expert','hybrid']}
class Handler(BaseHTTPRequestHandler):
 server_version='EDE/1.0'
 def log_message(self,*a):pass
 def send_json(self,c,obj):
  b=json.dumps(obj,ensure_ascii=False,default=str).encode();self.send_response(c);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def send_file(self,p,ct):
  b=p.read_bytes();self.send_response(200);self.send_header('Content-Type',ct);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def read_json(self):
  n=int(self.headers.get('Content-Length','0'));return json.loads(self.rfile.read(n).decode() or '{}')
 def events(self):return load_events(DB)
 def do_GET(self):
  ensure_seed();parsed=urlparse(self.path);path=parsed.path;q=parse_qs(parsed.query);events=self.events();eng=EDE(events)
  try:
   if path=='/api/health':return self.send_json(200,{'ok':True,'events':len(events),'units':len({e.unit_id for e in events})})
   if path=='/api/config':return self.send_json(200,public_config())
   if path=='/api/overview':return self.send_json(200,eng.overview())
   if path=='/api/readiness':return self.send_json(200,readiness(events))
   if path=='/api/evidence':return self.send_json(200,eng.overview()['evidence'])
   if path=='/api/actor-map':return self.send_json(200,eng.overview()['actor_map'])
   if path=='/api/discover':return self.send_json(200,eng.discover())
   if path=='/api/boundaries':return self.send_json(200,eng.boundaries([a.actor_id for a in ACTORS[:3]]))
   if path=='/api/benchmark/real':return self.send_json(200,eng.benchmark())
   if path=='/api/units':return self.send_json(200,{'units':sorted({e.unit_id for e in events})})
   if path=='/api/trajectory':
    units=sorted({e.unit_id for e in events});return self.send_json(200,eng.trajectory(q.get('unit_id',[units[0]])[0]))
   if path in {'/api/designs','/api/design-search'}:
    req=req_from(q);res=eng.design_search(ACTORS,req,CAPACITIES,float(q.get('volume',[5])[0]),float(q.get('max_util',[.85])[0]),int(q.get('max_handoffs',[2])[0]),q.get('method',['structural'])[0],pilot=load_pilot_observations(DB));return self.send_json(200,res)
   if path=='/api/replay':
    req=req_from(q);uid=q.get('unit_id',[sorted({e.unit_id for e in events})[0]])[0];return self.send_json(200,eng.replay(uid,topology_for(q.get('topology_id',['T001'])[0],req),req,CAPACITIES))
   if path=='/api/mechanism-trace':
    req=req_from(q);return self.send_json(200,eng.mechanism_trace(topology_for(q.get('topology_id',['T001'])[0],req),req,CAPACITIES,volume=float(q.get('volume',[5])[0]),method=q.get('method',['structural'])[0],pilot=load_pilot_observations(DB)))
   if path=='/api/simulate':
    req=req_from(q);return self.send_json(200,eng.simulate(topology_for(q.get('topology_id',['T001'])[0],req),req,CAPACITIES,volume=float(q.get('volume',[5])[0]),days=int(q.get('days',[21])[0]),growth=float(q.get('growth',[.03])[0]),shock_day=int(q.get('shock_day',[8])[0]),shock=float(q.get('shock',[3])[0])))
   if path=='/api/robustness':
    req=req_from(q);sc=eng.sensitivity(topology_for(q.get('topology_id',['T001'])[0],req),req,CAPACITIES,base_volume=float(q.get('volume',[5])[0]));return self.send_json(200,{'scenario_count':len(sc),'robustness':sum(s['peak_utilisation']<=float(q.get('max_util',[.85])[0]) for s in sc)/max(1,len(sc)),'scenarios':sc})
   if path=='/api/pilot/status':return self.send_json(200,eng.pilot_status([],load_pilot_observations(DB)))
   if path=='/api/events':
    size=min(500,max(1,int(q.get('size',[100])[0])));page=max(1,int(q.get('page',[1])[0]));term=q.get('q',[''])[0].lower();rows=[e.to_dict() for e in events if not term or term in e.activity.lower() or term in e.actor.lower() or term in e.unit_id.lower()];i=(page-1)*size;return self.send_json(200,{'page':page,'size':size,'total':len(rows),'events':rows[i:i+size]})
   if path=='/api/export/events':
    o=io.StringIO();w=csv.writer(o);w.writerow(['event_id','unit_id','timestamp','actor','activity','state_before','state_after','source_id','confidence','completion','rework']);[w.writerow([e.event_id,e.unit_id,e.timestamp,e.actor,e.activity,e.state_before,e.state_after,e.source_id,e.confidence,e.completion,e.rework]) for e in events];self.send_response(200);b=o.getvalue().encode();self.send_header('Content-Type','text/csv');self.send_header('Content-Disposition','attachment; filename="ede_events.csv"');self.end_headers();self.wfile.write(b);return
   if path=='/':return self.send_file(FRONTEND/'index.html','text/html')
   if path.startswith('/static/'):
    p=FRONTEND/Path(path[8:]);return self.send_file(p,{'.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.svg':'image/svg+xml; charset=utf-8'}.get(p.suffix,'text/plain; charset=utf-8')) if p.exists() else self.send_json(404,{'error':'not found'})
   return self.send_json(404,{'error':'not found'})
  except Exception as e:return self.send_json(500,{'error':str(e),'path':path})
 def do_POST(self):
  ensure_seed();path=urlparse(self.path).path;p=self.read_json();events=self.events();eng=EDE(events)
  try:
   if path=='/api/import':
    ev=[_event_from_row(r,i) for i,r in enumerate(p.get('events',[]),1)];replace_events(DB,ev);return self.send_json(200,{'ok':True,'events':len(ev),'readiness':readiness(ev)})
   if path=='/api/import-text':
    fmt=str(p.get('format','csv')).lower();tmp=DATA/('_upload.'+fmt);tmp.write_text(str(p.get('text','')),encoding='utf8')
    try:ev=load(str(tmp))
    finally:tmp.unlink(missing_ok=True)
    replace_events(DB,ev);return self.send_json(200,{'ok':True,'events':len(ev),'readiness':readiness(ev)})
   if path=='/api/pilot/observations':
    obs=p.get('observations',[]);insert_pilot_observations(DB,obs);return self.send_json(200,{'ok':True,'added':len(obs)})
   if path=='/api/pilot/clear':
    c=init(DB);c.execute('DELETE FROM pilot_observations');c.commit();c.close();return self.send_json(200,{'ok':True})
   if path=='/api/validate':return self.send_json(200,compare(p.get('predictions',[]),p.get('observations',[])))
   if path=='/api/design-search':
    x=p;req=req_from(x.get('params',{}));return self.send_json(200,eng.design_search(ACTORS,req,CAPACITIES,float(x.get('volume',5)),float(x.get('max_util',.85)),int(x.get('max_handoffs',2)),str(x.get('method','structural')),pilot=load_pilot_observations(DB),analogues=x.get('analogues',[])))
   return self.send_json(404,{'error':'not found'})
  except Exception as e:return self.send_json(500,{'error':str(e),'path':path})
def serve(host='127.0.0.1',port=8899,open_browser=True):
 ensure_seed();h=ThreadingHTTPServer((host,port),Handler);print(f'EDE running at http://{host}:{port}/')
 if open_browser:threading.Timer(.6,lambda:webbrowser.open(f'http://{host}:{port}/')).start()
 h.serve_forever()
def main():
 p=argparse.ArgumentParser();p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8899);p.add_argument('--no-browser',action='store_true');a=p.parse_args();serve(a.host,a.port,not a.no_browser)
if __name__=='__main__':main()
