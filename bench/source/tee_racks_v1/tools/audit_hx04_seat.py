import json,os,sys,math
from pathlib import Path
import argparse,hashlib
ROOT=Path(__file__).resolve().parents[4];src=ROOT/'bench/source/key_fan_v1'
ap=argparse.ArgumentParser();ap.add_argument('--coupon',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
r=json.loads((ROOT/'bench/reviews/key-fan-v2/HX04/report.json').read_text());os.environ.update(r['build_env']);sys.path.insert(0,str(src));import build_short as B
import FreeCAD as A,Part
V=A.Vector
shape=Part.Shape();shape.read(str(args.coupon))
lo=B.SH.Layout(B.LAYOUT['x']);t=next(t for t in lo.tools if t['set']=='tee' and t['name']=='5')
axis=V(*t['u']);tip=V(*t['tip']);bar=V(*t['bar']);results=[]
print('solids',[(s.Volume,[s.BoundBox.XMin,s.BoundBox.XMax,s.BoundBox.YMin,s.BoundBox.YMax]) for s in shape.Solids],flush=True)
for name,target in [('T5 C',43519),('T5 F',43517)]:
 s=min(shape.Solids,key=lambda q:abs(q.Volume-target));assert abs(s.Volume-target)<1
 B.TBAR='corners' if name.endswith('C') else 'flats'
 tool=B.hex_rod(tip+axis*.1,tip+axis*(t['D']-.1),5,bar)
 samples=[]
 for ang in [0,5,10,15,20,25,30,45,60]:
  q=tool.copy();q.rotate(tip,axis,ang);samples.append(dict(deg=ang,intersection_mm3=s.common(q).Volume))
 disk=[]
 for depth in [0,.5,1,1.5,2,3,4,5,6,8,12,16,19]:
  cyl=Part.makeCylinder(5/math.sqrt(3),.2,V(*t['mouth'])-axis*(depth+.2),axis)
  disk.append(dict(depth_from_mouth_mm=depth,full_spin_disc_intersection_mm3=s.common(cyl).Volume))
 results.append(dict(piece=name,volume=s.Volume,rotation=samples,sections=disk))
 print(name,samples,flush=True)
out=args.out
out.write_text(json.dumps(dict(source='published HX04 v2 native coupon STEP',coupon_step_sha256=hashlib.sha256(args.coupon.read_bytes()).hexdigest(),audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),release_sha256='bebcbc2008efa8984a0a2375e097a3535c95727c3f631c0d384b469b4c1f5945',freecad=A.Version(),seat_depth_mm=t['D'],neck_mm=B.SH.land(t['D']),hex_funnel_depth_mm=4/math.tan(math.radians(50)),pieces=results),indent=2)+'\n')
