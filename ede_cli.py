import argparse, csv, json, sys
from pathlib import Path

from app.server import ensure_seed, DB
from app.core.ingest import load, readiness
from app.core.storage import replace_events, load_events
from app.core.engine import EDE


def main():
    p = argparse.ArgumentParser(prog='ede')
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    imp = sub.add_parser('import'); imp.add_argument('file')
    rep = sub.add_parser('report'); rep.add_argument('--unit', dest='unit', default=None)
    exp = sub.add_parser('export-events'); exp.add_argument('output')
    sub.add_parser('test')
    a = p.parse_args()
    ensure_seed()

    if a.cmd == 'status':
        events = load_events(DB)
        eng = EDE(events)
        print(json.dumps({'overview': eng.overview(), 'readiness': readiness(events)}, indent=2, default=str))
        return
    if a.cmd == 'import':
        ev = load(a.file)
        replace_events(DB, ev)
        print(json.dumps({'events': len(ev), 'units': len({x.unit_id for x in ev}), 'readiness': readiness(ev)}, indent=2))
        return
    if a.cmd == 'report':
        events = load_events(DB)
        uid = a.unit or sorted({x.unit_id for x in events})[0]
        print(json.dumps(EDE(events).trajectory(uid), indent=2, default=str))
        return
    if a.cmd == 'export-events':
        events = load_events(DB)
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['event_id','unit_id','timestamp','actor','activity','state_before','state_after','source_id','confidence','completion','rework'])
            for x in events:
                w.writerow([x.event_id,x.unit_id,x.timestamp,x.actor,x.activity,x.state_before,x.state_after,x.source_id,x.confidence,x.completion,x.rework])
        print(out)
        return
    if a.cmd == 'test':
        import subprocess
        r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], check=False)
        sys.exit(r.returncode)


if __name__ == '__main__':
    main()
