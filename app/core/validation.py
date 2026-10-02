from math import sqrt
def compare(predictions,observations):
 bykey={(str(x.get('design_id')),str(x.get('actor')),str(x.get('dimension'))):x for x in observations};err=[]
 for p in predictions:
  o=bykey.get((str(p.get('design_id')),str(p.get('actor')),str(p.get('dimension'))))
  if o and p.get('estimate') is not None and o.get('observed') is not None:err.append((float(p['estimate']),float(o['observed']),float(p.get('lower',p['estimate'])),float(p.get('upper',p['estimate']))))
 if not err:return {'n':0,'status':'NO_VALIDATION_OBSERVATIONS'}
 ae=[abs(p-o) for p,o,_,_ in err];se=[(p-o)**2 for p,o,_,_ in err]
 return {'n':len(err),'mae':round(sum(ae)/len(ae),4),'rmse':round(sqrt(sum(se)/len(se)),4),'bias':round(sum(p-o for p,o,_,_ in err)/len(err),4),'interval_coverage':round(sum(lo<=o<=hi for _,o,lo,hi in err)/len(err),4),'status':'VALIDATED'}
