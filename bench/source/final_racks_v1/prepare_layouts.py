"""Recompute selected final layouts with the straight-socket policy; bounded searches."""
import json,os,sys,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent

def env_for(part):
 if part=='HX04':
  env=json.loads((HERE.parents[2]/'bench/reviews/key-fan-v2/HX04/report.json').read_text())['build_env']
  env.update(SHORT_DEEP_BACK='0',SHORT_DEEP_TEE='0',SHORT_HAND='0',SHORT_COCK='0',HX4S_TBAR='flats',HX4S_LAYOUT='hx04_final.json')
 else:
  env=json.loads((HERE/'study'/f'{part.lower()}_stand.json').read_text())['build_env']
  env.update(HX4S_LAYOUT=f'{part.lower()}_final.json',HX4S_TBAR='flats',HX4S_GUSSET='cheek',SHORT_COCK='0',SHORT_ROBUST='0',SHORT_ROBUST_ALT='0')
 env.update(HX4S_SOFT_WEB='0')
 return os.environ|env

def main():
 if len(sys.argv)==1:
  for part in ('HX04','HX05A','HX05B','HX05C'):
   subprocess.run([sys.executable,__file__,part],cwd=HERE/'study',env=env_for(part),check=True,timeout=1000)
  return
 import numpy as np
 from scipy.optimize import minimize
 import time
 import short as S
 part=sys.argv[1];study=HERE/'study';src='short_dt_c2.json' if part=='HX04' else part.lower()+'_stand.json'
 j=json.loads((study/src).read_text());x=np.array(j['x']);x[38:40]=0 if part=='HX04' else x[38:40];x[43:45]=0
 t0=time.monotonic();best=[float('inf'),x.copy()]
 class Done(Exception):pass
 if part=='HX04':
  # Preserve the T3/T5 print/clocking frame that the coupons physically tested.
  free=[0,1,2,3,4,5,13,14,15,16,17,18]
  bounds=[(x[i]-30,x[i]+30) if i in (0,1,2,13,14,15) else (x[i]-3,x[i]+3) for i in free]
 else:free=[];bounds=[]
 def cost(p):
  if time.monotonic()-t0>600:raise Done
  v=x.copy();v[free]=p
  r=S.evaluate(v,True);val=10000*sum(r[3].values())+r[1]+.05*r[2]
  if val<best[0]:
   best[:]=val,v.copy();print(part,round(time.monotonic()-t0,1),round(val,3),r[3],flush=True)
  if free and sum(r[3].values())<1e-8:raise Done
  return val
 try:cost(x[free])
 except Done:pass
 if free and best[0]>1000:
  try:minimize(cost,x[free],method='Powell',bounds=bounds,options={'maxiter':20,'xtol':.02,'ftol':1e-8})
  except Done:pass
 r=S.evaluate(best[1],True)
 record=dict(x=best[1].tolist(),rep=r[4],depth=r[1],body_h=r[2],pen=r[3],build_env={k:v for k,v in os.environ.items() if k.startswith(('SHORT_','HX4S_')) or k=='XENV'},scope='Nominal sampled layout; clock play, native CAD and physical complete-rack checks separate.')
 (study/(part.lower()+'_final.json')).write_text(json.dumps(record,indent=2)+'\n')
 print(part,'selected',r[1],r[3],flush=True)
if __name__=='__main__':
 sys.path.insert(0,str(HERE/'study'));main()
