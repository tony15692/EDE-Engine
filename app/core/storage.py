import json,sqlite3
from pathlib import Path
from .models import Event
SCHEMA='''CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,unit_id TEXT,timestamp REAL,actor TEXT,activity TEXT,state_before TEXT,state_after TEXT,source_id TEXT,confidence REAL,completion INTEGER,rework INTEGER,attributes TEXT);CREATE INDEX IF NOT EXISTS idx_events_unit_time ON events(unit_id,timestamp,event_id);CREATE INDEX IF NOT EXISTS idx_events_activity ON events(activity);CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor);CREATE TABLE IF NOT EXISTS pilot_observations(id INTEGER PRIMARY KEY AUTOINCREMENT,design_id TEXT,actor TEXT,dimension TEXT,observed REAL,source_id TEXT,period TEXT,notes TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);'''
def init(path):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(p);c.executescript(SCHEMA);c.commit();return c
def replace_events(path,events):
 c=init(path);c.execute('DELETE FROM events');c.executemany('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',[(e.event_id,e.unit_id,e.timestamp,e.actor,e.activity,e.state_before,e.state_after,e.source_id,e.confidence,e.completion,e.rework,json.dumps(e.attributes,separators=(',',':'))) for e in events]);c.commit();c.close()
def load_events(path):
 c=init(path);rows=c.execute('SELECT event_id,unit_id,timestamp,actor,activity,state_before,state_after,source_id,confidence,completion,rework,attributes FROM events ORDER BY timestamp,event_id').fetchall();c.close();return [Event(*r[:11],json.loads(r[11] or '{}')) for r in rows]
def insert_pilot_observations(path,observations):
 c=init(path);c.executemany('INSERT INTO pilot_observations(design_id,actor,dimension,observed,source_id,period,notes) VALUES(?,?,?,?,?,?,?)',[(o.get('design_id',''),o.get('actor',''),o.get('dimension',''),float(o.get('observed',0)),o.get('source_id',''),o.get('period',''),o.get('notes','')) for o in observations]);c.commit();c.close()
def load_pilot_observations(path):
 c=init(path);rows=c.execute('SELECT design_id,actor,dimension,observed,source_id,period,notes FROM pilot_observations ORDER BY id').fetchall();c.close();return [dict(zip(['design_id','actor','dimension','observed','source_id','period','notes'],r)) for r in rows]
