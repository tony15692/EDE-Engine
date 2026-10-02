from .models import BURDEN_DIMS
def incidence(rows,baseline):
    out=[]
    for r in rows:
        for a in r['actors']:
            base=baseline.get(a['actor'],{})
            out.append({'topology_id':r['topology_id'],'actor':a['actor'],'incremental':{d:round(a.get(d,0)-base.get(d,0),4) for d in BURDEN_DIMS},'utilisation':a.get('utilisation',0)})
    return out
def transfer(incidence_rows):
    out=[]; actors=sorted({x['actor'] for x in incidence_rows}); by={(x['topology_id'],x['actor']):x for x in incidence_rows}
    for tid in sorted({x['topology_id'] for x in incidence_rows}):
        for d in BURDEN_DIMS:
            neg=[];pos=[]
            for a in actors:
                v=by.get((tid,a),{}).get('incremental',{}).get(d,0)
                (pos if v>0 else neg).append((a,v))
            for i,vi in neg:
                for j,vj in pos: out.append({'topology_id':tid,'dimension':d,'from':i,'to':j,'amount':round(min(abs(vi),vj),4)})
    return out
