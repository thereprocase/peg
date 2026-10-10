"""Rigid straightening and finer withdrawal screens on the exact published fan STEP.
Prescribed kinematics; neither a continuous collision certificate nor dynamic simulation.
"""
import argparse,json,os,hashlib,sys,time,math,importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import multiprocessing as mp
import numpy as np
from scipy.spatial.transform import Rotation,Slerp

G={}
def initialise(repo,step):
 import FreeCAD as A,Part,MeshPart
 r=json.loads((Path(repo)/'bench/reviews/key-fan-v2/HX04/report.json').read_text());os.environ.update(r['build_env']);file=Path(repo)/'bench/source/key_fan_v1/build_short.py'
 # Extract the unchanged native reference-tool functions, avoiding unrelated mount imports.
 import ast,types
 sys.path.insert(0,str(file.parent/'study'));import short as S
 wanted={'v','hex_rod','ref_tools','ref_tool_list'};tree=ast.parse(file.read_text());definitions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in wanted];assert len(definitions)==4
 ns=dict(A=A,Part=Part,V=A.Vector,np=np,math=math,TBAR='corners',TEE_KEYED_MIN=S.TEE_KEYED_MIN)
 exec(compile(ast.Module(body=definitions,type_ignores=[]),str(file),'exec'),ns)
 H=types.SimpleNamespace(SH=S,LAYOUT=json.loads((file.parent/'study'/r['layout']).read_text()),ref_tool_list=ns['ref_tool_list'])
 Lo=H.SH.Layout(H.LAYOUT['x']);old=H.SH.COCK;H.SH.COCK=False
 try:Ln=H.SH.Layout(H.LAYOUT['x'])
 finally:H.SH.COCK=old
 tools=H.ref_tool_list(Lo);upright=H.ref_tool_list(Ln);shape=Part.read(str(step));assert shape.isValid() and len(shape.Solids)==1
 top=max(t.BoundBox.ZMax for t in tools);shelf=Part.makeBox(800,126.2,200,A.Vector(-400,-50,top+50.8));routes=json.loads((Path(repo)/'bench/reviews/key-fan-v2/HX04/exact-check.json').read_text())['routes']
 G.update(A=A,Part=Part,MeshPart=MeshPart,H=H,Lo=Lo,Ln=Ln,tools=tools,upright=upright,shape=shape,shelf=shelf,routes=routes)

def rigid_frame(up,rest):
 cu=up.mean(0);cr=rest.mean(0);U,S,Vt=np.linalg.svd((up-cu).T@(rest-cr));R=Vt.T@U.T
 if np.linalg.det(R)<0:Vt[-1]*=-1;R=Vt.T@U.T
 t=cr-R@cu;error=float(np.max(np.linalg.norm(up@R.T+t-rest,axis=1)));assert error<1e-6,error
 return R,t,error

def transform(shape,R,t):
 A=G['A'];m=A.Matrix(*[float(x) for row in np.c_[R,t] for x in row],0,0,0,1);s=shape.copy();s.transformShape(m);return s

def worker(i,out,step_mm):
 A=G['A'];V=A.Vector;tool=G['Lo'].tools[i];up=G['Ln'].tools[i];rest=G['tools'][i];upright=G['upright'][i];shape=G['shape'];route=G['routes'][i];start=time.monotonic()
 R,t,error=rigid_frame(up['pts'],tool['pts']);slerp=Slerp([0,1],Rotation.from_matrix([R,np.eye(3)]));tipup=up['pts'][0];tiprest=tool['pts'][0]
 unit=np.array(up['u']);lift=unit*route.get('lift_mm',up['D']+3);tail=route['exit'].split('-then-')[-1];direction={'axis':unit,'forward':np.array([0,1,0]),'up-forward':np.array([0,1,.4])}[tail];direction=direction/np.linalg.norm(direction);exitvec=direction*160
 bb=A.BoundBox(upright.BoundBox);bb.add(rest.BoundBox)
 for delta in [lift,lift+exitvec]:q=upright.copy();q.translate(V(*delta));bb.add(q.BoundBox)
 bb.enlarge(3);clip=shape.common(G['Part'].makeBox(bb.XLength,bb.YLength,bb.ZLength,V(bb.XMin,bb.YMin,bb.ZMin)))
 peers=[j for j,q in enumerate(G['tools']) if j!=i and q.BoundBox.intersect(bb)];poses=[]
 def check(m,phase,parameter):
  body=clip.common(m).Volume if clip.BoundBox.intersect(m.BoundBox) else 0.;other=0.;who=None
  for j in peers:
   q=G['tools'][j]
   if q.BoundBox.intersect(m.BoundBox):
    volume=q.common(m).Volume
    if volume>other:other=volume;who={'set':G['Lo'].tools[j]['set'],'size':G['Lo'].tools[j]['name']}
  shelf=G['shelf'].common(m).Volume if G['shelf'].BoundBox.intersect(m.BoundBox) else 0.
  poses.append(dict(phase=phase,parameter=parameter,body_intersection_mm3=float(body),peer_intersection_mm3=float(other),shelf_intersection_mm3=float(shelf),peer=who))
 for f in np.linspace(0,1,13):
  rot=slerp([f]).as_matrix()[0];anchor=tiprest*(1-f)+tipup*f;delta=anchor-rot@tipup;check(transform(upright,rot,delta),'rigid-straighten',float(f))
 offset=np.zeros(3)
 for label,leg in [('lift',lift),('escape',exitvec)]:
  n=max(1,math.ceil(np.linalg.norm(leg)/step_mm))
  for k in range(1,n+1):
   delta=offset+leg*k/n;m=upright.copy();m.translate(V(*delta));check(m,label,float(np.linalg.norm(leg)*k/n))
  offset+=leg
 name=f'{tool["set"]}-{tool["name"].replace("/","_")}';path=Path(out);path.mkdir(exist_ok=True)
 mesh=G['MeshPart'].meshFromShape(Shape=upright,LinearDeflection=.16,AngularDeflection=.18,Relative=False);mesh.write(str(path/(name+'__reference.stl')))
 thresholds=dict(body=.001,peers=.001,shelf=.001);fails=[p for p in poses if p['body_intersection_mm3']>.001 or p['peer_intersection_mm3']>.001 or p['shelf_intersection_mm3']>.001]
 row=dict(index=i,set=tool['set'],size=tool['name'],mesh=name+'__reference.stl',rest_rotation=R.tolist(),rigid_fit_max_error_mm=error,tip_up_mm=tipup.tolist(),tip_rest_mm=tiprest.tolist(),axis_up=unit.tolist(),lift_vector_mm=lift.tolist(),escape_vector_mm=exitvec.tolist(),mouth_mm=up['mouth'].tolist(),grip_mm=up.get('top',up['pts'][~up['main']].mean(0)).tolist(),sample_count=len(poses),step_mm=step_mm,rigid_straighten_samples=13,passed=not fails,max_body_intersection_mm3=max(p['body_intersection_mm3'] for p in poses),max_peer_intersection_mm3=max(p['peer_intersection_mm3'] for p in poses),max_shelf_intersection_mm3=max(p['shelf_intersection_mm3'] for p in poses),first_failure=fails[0] if fails else None,seconds=time.monotonic()-start)
 (path/(name+'__screen.json')).write_text(json.dumps(dict(summary=row,poses=poses),indent=2)+'\n');return row

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--step',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--step-mm',type=float,default=1.);p.add_argument('--tool',type=int,action='append');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);start=time.monotonic();rows=[]
 assert hashlib.sha256(a.step.read_bytes()).hexdigest()=='62a8acee8145f11967618944d6b4e0e2a54f3d96c428f3a197c91fc82f86798a'
 with ProcessPoolExecutor(max_workers=a.workers,mp_context=mp.get_context('spawn'),initializer=initialise,initargs=(a.repo.resolve(),a.step.resolve())) as pool:
  fs=[pool.submit(worker,i,str(a.out.resolve()),a.step_mm) for i in (a.tool or range(26))]
  for f in as_completed(fs):row=f.result();rows.append(row);print(row['set'],row['size'],'pass',row['passed'],'poses',row['sample_count'],'seconds',round(row['seconds'],1),flush=True)
 rows.sort(key=lambda q:q['index']);r=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),step_sha256=hashlib.sha256(a.step.read_bytes()).hexdigest(),tools=rows,all_sampled_routes_pass=all(q['passed'] for q in rows),seconds=time.monotonic()-start,scope='Original HX04 v2 tool proxies and seats; rigid straightening with linearly interpolated tip and 1 mm translation samples. Finer sampling is not a continuous certificate. Does not certify revised straight-guide seats or physical tool dimensions.')
 (a.out/'motion-audit.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
