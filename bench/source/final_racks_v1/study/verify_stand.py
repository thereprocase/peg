"""Recheck fixed forward withdrawal at five turn-play poses with dense tool/motion samples.
Run per rack with the environment in its selected layout. This is not an OCC check or continuous proof.
"""
import argparse, hashlib, json, math, os
from pathlib import Path
import numpy as np
import short as S


def verify(layout):
    j=json.loads(layout.read_text()); v=j['x']; original_step=S.STEP
    original_escape=S.ESC;original_env={k:os.environ.get(k) for k in ('SHORT_POINT_STEP','SHORT_ESCAPE_STEP')}
    # Preserve the same planned lift and force the actual selected route in all play poses.
    if any(r['escape']!='forward' for r in j['rep']):raise ValueError('verifier expects selected forward routes')
    S.STEP=.75;os.environ.update(SHORT_POINT_STEP='.75',SHORT_ESCAPE_STEP='1.25')
    S.ESC={'forward':np.array([0.,1.,0.])}
    play=np.array([S.tee_play_deg(t[0]) for t in S.TEE]);alt=np.array([(-1)**k for k in range(len(S.TEE))])
    poses=[]
    try:
        for label,turn in [('nominal',np.zeros(len(play))),('plus',play),('minus',-play),('alternating-plus',play*alt),('alternating-minus',-play*alt)]:
            S.TPSI_OFF=turn
            _,d,h,pen,rep,lo=S._evaluate(v,True)
            if max(pen.values())>1e-7:raise AssertionError((layout.name,label,pen))
            poses.append(dict(pose=label,turn_deg=turn.tolist(),depth_mm=d,pen={k:float(q) for k,q in pen.items()},routes=rep))
    finally:
        S.TPSI_OFF=np.zeros(len(play));S.STEP=original_step;S.ESC=original_escape
        for k,value in original_env.items():
            if value is None:os.environ.pop(k,None)
            else:os.environ[k]=value
    return dict(layout=layout.name,layout_sha256=hashlib.sha256(layout.read_bytes()).hexdigest(),
                verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                passed=True,tool_point_step_mm=.75,lift_step_mm=.75,escape_step_mm=1.25,
                worst_loaded_depth_mm=max(p['depth_mm'] for p in poses),poses=poses,
                scope='Dense sampled capsule/cloud layout and fixed forward routes at five clock-play poses; not continuous collision proof, native CAD or physical qualification.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('layout',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    result=verify(a.layout);a.output.write_text(json.dumps(result,indent=1)+'\n',encoding='utf-8',newline='\n')
    print(a.layout,result['worst_loaded_depth_mm'],'five fixed-route poses passed')
