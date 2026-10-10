"""Independent exported native, socket, vent and nominal-tool checks. No inherited FEA rating."""
from pathlib import Path
import argparse,json,sys,math,hashlib
import FreeCAD as A,Part,Mesh
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import build_short as H
V=A.Vector

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args();out=a.out
 shape=Part.Shape();shape.read(str(out/'installed.step'));assert shape.isValid() and len(shape.Solids)==1
 g=json.loads((out/'build-geometry.json').read_text());lo=H.SH.Layout(H.LAYOUT['x']);tools=H.ref_tool_list(lo);rows=[]
 for i,t in enumerate(lo.tools):
  ax=H.v(t['u']);tip=H.v(t['tip']);mouth=H.v(t['mouth']);guide=t['guide_mm'];hexed=t['set'] in ('tee','hex')
  if hexed:
   size=t.get('af',float(t['name']) if t['set']=='hex' else 0);bar=H.v(t.get('bar',t.get('arm')))
   clean=H.hex_rod(tip+ax*.1,mouth-ax*3.001,size+.36,bar)
   # Complete 2 mm material wall around six flats, beyond the tiny floor vent channel.
   outer=H.hex_rod(tip,mouth-ax*3.,size+.38+4,bar)
   inner=H.hex_rod(tip,mouth-ax*3.,size+.38+.001,bar)
   wall=outer.cut(inner)
  else:
   size=2*t['bore']-.38
   clean=Part.makeCylinder(t['bore']-.01,guide-.2,tip+ax*.1,ax)
   wall=Part.makeCylinder(t['bore']+2,guide,tip,ax).cut(Part.makeCylinder(t['bore']+.001,guide,tip,ax))
  obstruction=shape.common(clean).Volume;missing=wall.cut(shape).Volume
  vent=Part.makeCylinder(.49,3.55,tip+ax*.025,ax*-1)
  outlet=Part.makeCylinder(.49,490.,tip-ax*3.5,V(1,0,0) if (out/'owner-refinement.json').exists() else V(0,1,0))
  vent_hit=shape.common(vent).Volume+shape.common(outlet).Volume
  stored=shape.common(tools[i]).Volume
  other=max((tools[i].common(q).Volume for k,q in enumerate(tools) if k!=i and q.BoundBox.intersect(tools[i].BoundBox)),default=0)
  # Offset stop shoulders retain 3 mm floor despite the centre vent.
  side=ax.cross(V(1,0,0) if abs(ax.x)<.9 else V(0,1,0));side.normalize()
  floor_missing=min(Part.makeCylinder(.1,2.95,tip+side*(sgn*.85)-ax*2.975,ax).cut(shape).Volume for sgn in (-1,1))
  rows.append(dict(set=t['set'],size=t['name'],guide_mm=guide,bore_across_flats_mm=size+.38 if hexed else None,bore_diameter_mm=2*t['bore'] if not hexed else None,straight_guide_obstruction_mm3=obstruction,guide_wall_missing_mm3=missing,vent_obstruction_mm3=vent_hit,floor_shoulder_missing_mm3=floor_missing,stored_body_overlap_mm3=stored,stored_neighbor_overlap_mm3=other))
  print(t['set'],t['name'],rows[-1],flush=True)
 rear_delta=0.
 if (out/'base-installed.step').exists():
  original=Part.Shape();original.read(str(out/'base-installed.step'));rear=H.B.box(-300,-40,-400,600,40.15,800)
  old=original.common(rear);new=shape.common(rear);rear_delta=old.cut(new).Volume+new.cut(old).Volume;assert rear_delta<1e-6
 meshes={}
 for name in ('installed.stl','print.stl'):
  m=Mesh.Mesh(str(out/name));assert m.isSolid() and not m.hasNonManifolds()
  meshes[name]=dict(closed=True,volume_relative_error=abs(m.Volume-shape.Volume)/shape.Volume,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest())
 doc=A.openDocument(str(out/'model.FCStd'));assert len(doc.Objects)==1 and doc.Objects[0].Shape.isValid();A.closeDocument(doc.Name)
 passed=all(max(q[k] for k in ('straight_guide_obstruction_mm3','guide_wall_missing_mm3','vent_obstruction_mm3','floor_shoulder_missing_mm3','stored_body_overlap_mm3','stored_neighbor_overlap_mm3'))<1e-3 for q in rows)
 report=dict(refinement_rear_delta_mm3=rear_delta,passed=passed,native_valid=True,native_solids=1,freecad=A.Version(),occ=Part.OCC_VERSION,step_sha256=hashlib.sha256((out/'installed.step').read_bytes()).hexdigest(),meshes=meshes,sockets=rows,scope='Exported native geometry, 2 mm six-flat guide wall, vent routes, stop shoulders and nominal stored tools. No continuous withdrawal, installation, printed loads or other-size fit qualification.')
 (out/'native-check.json').write_text(json.dumps(report,indent=2)+'\n');print('native check',passed,flush=True)
if __name__=='__main__':main()
