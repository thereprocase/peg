"""Protect every owner-fan guide wall and route its vents toward the print-bed end.
Run with the owner's final build environment and FreeCAD Python after build_all.py.
The original base STEP is retained; other three rack geometries are unchanged.
"""
from pathlib import Path
import argparse,json,hashlib,math,shutil
import FreeCAD as A,Part
import build_short as H
V=A.Vector

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args();out=a.out
 base=out/'base-installed.step'
 if not base.exists():shutil.copyfile(out/'installed.step',base)
 original=Part.Shape();original.read(str(base));shape=original.copy();lo=H.SH.Layout(H.LAYOUT['x']);walls=[];patches=[]
 for t in lo.tools:
  ax=H.v(t['u']);tip=H.v(t['tip']);mouth=H.v(t['mouth']);length=t['guide_mm']-1.15
  if t['set'] in ('tee','hex'):
   size=t.get('af',float(t['name']) if t['set']=='hex' else 0);bar=H.v(t.get('bar',t.get('arm')))
   outer=H.hex_rod(tip+ax*1.1,mouth-ax*3.05,size+.38+4,bar);inner=H.hex_rod(tip+ax*1.1,mouth-ax*3.05,size+.381,bar);wall=outer.cut(inner)
  else:wall=Part.makeCylinder(t['bore']+2,length,tip+ax*1.1,ax).cut(Part.makeCylinder(t['bore']+.001,length,tip+ax*1.1,ax))
  walls.append(wall);missing=wall.cut(shape).Volume
  if missing>1e-5:
   shape=shape.fuse(wall).removeSplitter();assert shape.isValid() and len(shape.Solids)==1
   patches.append(dict(set=t['set'],size=t['name'],restored_wall_mm3=missing))
 # Positive installed X is the print-bed end. Every opening stays below its floor;
 # the full exported check verifies it crosses no other guide.
 cutters=[Part.makeCylinder(.5,500.2,H.v(t['tip'])-H.v(t['u'])*3.5-V(.2,0,0),V(1,0,0)) for t in lo.tools]
 for i in range(0,len(cutters),6):
  raw=shape.cut(cutters[i:i+6]);reduced=raw.removeSplitter();candidate=reduced if reduced.isValid() else raw
  if not candidate.isValid() or len(candidate.Solids)!=1:
   candidate=shape
   for cutter in cutters[i:i+6]:
    raw=candidate.cut(cutter);reduced=raw.removeSplitter();candidate=reduced if reduced.isValid() else raw
    assert candidate.isValid() and len(candidate.Solids)==1, ('lateral vent cut invalid',i)
  shape=candidate;print('Lateral vent batch',i,'of',len(cutters),flush=True)
 assert shape.isValid() and len(shape.Solids)==1
 added=shape.cut(original).removeSplitter();tools=H.ref_tool_list(lo);routes=H.LAYOUT['rep'];screen=[]
 for tool,t,route in zip(tools,lo.tools,routes):
  lift=H.v(t['u'])*H.SH.lift_distance(t);direction={'axis':H.v(t['u']),'forward':V(0,1,0),'up-forward':V(0,1,.4)}[route['escape']];direction.normalize();legs=[lift,direction*160];basepos=V();maximum=0.;poses=0
  for leg in legs:
   n=math.ceil(leg.Length/1.)
   for k in range(n+1):
    moved=tool.copy();moved.translate(basepos+leg*(k/n));poses+=1
    if moved.BoundBox.intersect(added.BoundBox):maximum=max(maximum,moved.common(added).Volume)
   basepos+=leg
  screen.append(dict(set=t['set'],size=t['name'],poses=poses,added_material_overlap_mm3=maximum))
  print('Restored-wall withdrawal',t['set'],t['name'],maximum,flush=True)
 assert all(r['added_material_overlap_mm3']<1e-3 for r in screen), 'restored guide wall obstructs withdrawal'
 shape.exportStep(str(out/'installed.step'));H.B.mesh(shape,out/'installed.stl');pp,m=H.print_pose(shape);H.B.mesh(pp,out/'print.stl')
 geom=json.loads((out/'build-geometry.json').read_text());bb=shape.BoundBox
 env=H.B.box(-H.HALF,H.Y_BACK,bb.ZMin,2*H.HALF,300,bb.ZLength)
 rails=[H.rail(ts,env,name,[]) for name,ts in lo.rail_groups];zones=H.solid_zones(lo,rails,geom['mount'],shape);zp=zones.copy();zp.transformShape(m);H.B.mesh(zones,out/'installed_solid.stl');H.B.mesh(zp,out/'print_solid.stl')
 doc=A.newDocument('FinalOwnerFan');obj=doc.addObject('Part::Feature','Holder');obj.Shape=shape;obj.Label='Owner fan — protected straight guides';doc.recompute();doc.saveAs(str(out/'model.FCStd'));A.closeDocument(doc.Name)
 geom.update(volume_mm3=shape.Volume,installed_bounds_mm=[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax]);geom['socket_policy']['vent_outlet']='positive installed X, below floor';(out/'build-geometry.json').write_text(json.dumps(geom,indent=2)+'\n')
 pose=[[m.A11,m.A12,m.A13,m.A14],[m.A21,m.A22,m.A23,m.A24],[m.A31,m.A32,m.A33,m.A34],[0,0,0,1]];(out/'pose.json').write_text(json.dumps([c for row in pose for c in row]))
 receipt=dict(base_step_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),step_sha256=hashlib.sha256((out/'installed.step').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_restorations=patches,added_material_withdrawal_screen=screen,step_mm=1,scope='Native guide-wall restoration and vent reroute; added material sampled along all nominal tool withdrawals. Original complete-rack sampled layout remains separate; installation and physical printing are unqualified.')
 (out/'owner-refinement.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Owner guide walls refined',flush=True)
if __name__=='__main__':main()
