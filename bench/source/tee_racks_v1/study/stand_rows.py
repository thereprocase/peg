"""Bounded HX05 two-tier study; no FreeCAD required. Run one set per process.
SHORT_TEE_SET=tee_13190.json python stand_rows.py --seconds 90 --output hx05c_stand.json
"""
import argparse, hashlib, json, math, os, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import short as S


def vector(p):
    gy, lower_y, dz, grade, stagger, tilt, pad0, pad1 = p
    pitch = math.sqrt(S.TEE_EQUAL**2-grade**2)
    count = len(S.TEE)//2
    x = np.zeros(45)
    # Centre the combined two-row footprint about the fixed plate centre.
    gx = (count-1)*pitch/2-stagger/2
    x[26:38] = [gx, gy, 0, pitch, stagger, lower_y-gy, -dz, tilt, 0, 90, count, grade]
    x[38:40] = [pad0, pad1]
    x[35]=65.;x[40]=90. # large upper grips angled 25 degrees; small lower grips fore-aft
    return x


def record(v):
    _, depth, body, pen, rep, lo = S.evaluate(v, True)
    bp = np.vstack([b[0] for b in lo.bosses]); br = np.concatenate([b[1] for b in lo.bosses])
    # CAD plate limits from build_short.build (before final shape/peg bounds).
    cad_h = max(t['mouth'][2] for t in lo.tools)+12-min(t['tip'][2] for t in lo.tools)+25
    return dict(x=v.tolist(), rep=rep, depth=depth, body_h=body, cad_plate_height_mm=cad_h,
                pen={k: float(q) for k,q in pen.items()},
                stage='sampled layout study; native CAD, FEA, slicing and physical tests pending',
                build_env={k:v for k,v in os.environ.items() if k.startswith(('SHORT_', 'XENV'))},
                dependencies={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest()
                              for n in ('stand_rows.py','short.py','socket_policy.py','sunray.py','comb.py',os.environ['SHORT_TEE_SET'],'tee_sets_note.json')})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();start=time.monotonic();best=[float('inf'),None];bounds=[(115,123),(85,95),(85,115),(0,8),(-25,25),(16,21),(0,8),(0,8)]
    class Done(Exception):pass
    def cost(p):
        if time.monotonic()-start>a.seconds:raise Done
        v=vector(p);_,d,b,pen,rep,lo=S.evaluate(v,True)
        cad_h=max(t['mouth'][2] for t in lo.tools)+12-min(t['tip'][2] for t in lo.tools)+25
        val=d+.05*b+10000*(sum(pen.values())+max(0,d-178)+max(0,cad_h-242))
        if val<best[0]:
            best[:]=[val,np.array(p)]
            print(round(time.monotonic()-start,1),round(val,2),round(d,2),{k:round(float(q),3) for k,q in pen.items()},flush=True)
        return val
    grade = 18 if os.environ['SHORT_TEE_SET'] == 'tee_13189.json' else 12
    seed=[122,87,100,0,-24,20,0,0]
    try:
        minimize(cost,seed,method='Powell',bounds=bounds,options={'maxiter':100,'xtol':.02,'ftol':1e-7})
    except Done:pass
    if best[1] is None:raise RuntimeError('no evaluation')
    r=record(vector(best[1]));r['search_seconds']=round(time.monotonic()-start,2);r['search_parameters']=best[1].tolist()
    a.output.write_text(json.dumps(r,indent=1)+'\n',encoding='utf-8',newline='\n')
    print('saved',a.output,r['depth'],r['pen'],flush=True)

if __name__=='__main__':main()
