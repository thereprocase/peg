"""Three five-slot clearance spectra, in the HX04 fan print orientation.
Angle authority is fan_orientation_v6.json: both shaft vector and hex-flat clocking.
FreeCAD Python is required for build; --plan uses ordinary Python.
"""
import argparse,hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
CLEARANCES=(.10,.15,.19,.23,.28)  # per flat; C is owner's latest requested fit
ORIENTATION=HERE/'fan_orientation_v6.json'
FAN=json.loads(ORIENTATION.read_text())
VENT=1.;WALL=3.;FLOOR=3.;LEAD=.8

def plan():
 return [dict(q,guide_mm=max(40.,8*q['size_mm']),slots=[dict(letter=letter,clearance_per_flat_mm=c,total_af_clearance_mm=2*c,bore_af_mm=q['size_mm']+2*c) for letter,c in zip('ABCDE',CLEARANCES)]) for q in FAN['coupons']]

def build(out):
 import FreeCAD as A,Part,MeshPart,Mesh
 V=A.Vector;out.mkdir(parents=True,exist_ok=True);doc=A.newDocument('HX05FitSpectrumV6');parts=[];reports=[];yoff=0.
 def polygon(x,cy,cz,af,bar):
  side=V(1,0,0).cross(bar);r=af/math.sqrt(3)
  pts=[V(x,cy,cz)+bar*(r*math.cos(math.pi/6+k*math.pi/3))+side*(r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
  return Part.makePolygon(pts+[pts[0]])
 for q in plan():
  axis=V(*q["shaft_print"]);row=V(-axis.y,axis.x,0);row.normalize();up=axis.cross(row)
  bp=V(*q["bar_print"]);bar=V(bp.dot(axis),bp.dot(row),bp.dot(up))
  assert abs(bar.x)<1e-8
  transform=A.Matrix(axis.x,row.x,up.x,0,axis.y,row.y,up.y,0,axis.z,row.z,up.z,0,0,0,0,1)
  size=q['size_mm'];guide=q['guide_mm'];length=guide+LEAD+FLOOR;radius=(size+2*max(CLEARANCES))/math.sqrt(3)
  pitch=2*radius+WALL;height=2*radius+2*WALL;width=5*pitch+WALL;z=height/2
  shape=Part.makeBox(length,width,height);cuts=[];checks=[]
  for i,s in enumerate(q['slots']):
   cy=WALL+radius+i*pitch;af=s['bore_af_mm'];turn=bar
   bore=Part.Face(polygon(FLOOR,cy,z,af,turn)).extrude(V(length-FLOOR+1,0,0))
   lead=Part.makeLoft([polygon(length-LEAD,cy,z,af,turn),polygon(length+.001,cy,z,af+2*LEAD,turn)],True,True)
   vent=Part.makeCylinder(VENT/2,FLOOR+.2,V(-.1,cy,z),V(1,0,0));cuts.extend([bore,lead,vent])
   checks.append((cy,s))
  for cutter in cuts:shape=shape.cut(cutter)
  shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1
  for cy,s in checks:
   vent=Part.makeCylinder(.49,FLOOR,V(0,cy,z),V(1,0,0));assert shape.common(vent).Volume<1e-7
   stop=Part.makeCylinder(.2,FLOOR,V(0,cy+.75,z),V(1,0,0));assert abs(shape.common(stop).Volume-stop.Volume)<1e-7
   tool=Part.Face(polygon(FLOOR+.1,cy,z,size,bar)).extrude(V(guide-.2,0,0));assert shape.common(tool).Volume<1e-7
   moved=tool.copy();moved.rotate(V(0,cy,z),V(1,0,0),30);collision=shape.common(moved).Volume
   qratio=(size/2+s['clearance_per_flat_mm'])/(size/math.sqrt(3));s['free_full_rotation']=qratio>=1
   if qratio>=1: assert collision<1e-7
   else: assert collision>1e-4,'30 degree hex stop missing'
   s['ideal_one_sided_play_deg']=None if qratio>=1 else 30-math.degrees(math.acos(qratio));s['collision_at_30_deg_mm3']=collision
   # Size and letter engraved on the flat print top; no labels inside guides.
   wires=Part.makeWireString(f'{size:g}{s["letter"]}',str(HERE/'fonts/Fillaprint-Regular.ttf'),3.)
   glyph=Part.makeCompound([Part.Face(w,'Part::FaceMakerBullseye') for w in wires if w]);bb=glyph.BoundBox
   glyph.translate(V(length/2-(bb.XMin+bb.XMax)/2,cy-(bb.YMin+bb.YMax)/2,height+.1))
   shape=shape.cut(Part.makeCompound([f.extrude(V(0,0,-.7)) for f in glyph.Faces])).removeSplitter()
  assert shape.isValid() and len(shape.Solids)==1
  # Apply the fan's complete shaft and hex-flat frame before forming a flat foot.
  shape.transformShape(transform);bb=shape.BoundBox
  shift=V(-bb.XMin,-bb.YMin,1.2-bb.ZMin);shape.translate(shift);bb=shape.BoundBox
  foot=Part.makeBox(bb.XLength,bb.YLength,2.,V(0,0,0))
  shape=shape.fuse(foot).removeSplitter();assert shape.isValid() and len(shape.Solids)==1
  for cy,slot in checks:
   floorpoint=transform.multVec(V(0,cy,z))+shift
   vent=Part.makeCylinder(.49,FLOOR,floorpoint,axis)
   assert shape.common(vent).Volume<1e-7,'foot blocks vent'
   slot['vent_outer_point_print_mm']=[floorpoint.x,floorpoint.y,floorpoint.z]
  # Congruence of all six directions with the flat-to-flat fan frame.
  for k in range(6):
   ang=math.pi/6+k*math.pi/3
   local=bar*math.cos(ang)+V(1,0,0).cross(bar)*math.sin(ang)
   expected=bp*math.cos(ang)+axis.cross(bp)*math.sin(ang)
   assert (transform.multVec(local)-expected).Length<1e-8
  q['fan_frame_match']=True
  name=f'HX05-fit-v6-{size:g}mm__fan-angle__print';shape.exportStep(str(out/(name+'.step')))
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);mesh.write(str(out/(name+'.stl')))
  reload=Part.Shape();reload.read(str(out/(name+'.step')));assert reload.isValid() and len(reload.Solids)==1
  assert mesh.isSolid() and mesh.countComponents()==1 and not mesh.hasInvalidPoints() and not mesh.hasInvalidNeighbourhood()
  assert abs(mesh.Volume-reload.Volume)/reload.Volume<.005
  obj=doc.addObject('Part::Feature',f'Hex{size:g}');obj.Label=f'{size:g} mm spectrum A-E';docshape=shape.copy();docshape.translate(V(0,yoff,0));obj.Shape=docshape
  for key,val in [('ShaftElevation',q['elevation_deg']),('BedHeading',q['heading_deg'])]:obj.addProperty('App::PropertyAngle',key,'Build metadata');setattr(obj,key,val)
  bb=shape.BoundBox;q.update(files=[name+'.stl',name+'.step'],native_valid=True,native_solids=1,mesh_closed=True,mesh_components=1,mesh_step_relative_volume_error=abs(mesh.Volume-reload.Volume)/reload.Volume,print_extents_mm=[bb.XLength,bb.YLength,bb.ZLength],vent_diameter_mm=VENT,floor_mm=FLOOR)
  reports.append(q);placed=shape.copy();placed.translate(V(0,yoff,0));parts.append(placed);yoff+=bb.YLength+8
 packed=Part.makeCompound(parts);assert packed.BoundBox.YLength<230 and packed.BoundBox.XLength<230
 mesh=MeshPart.meshFromShape(Shape=packed,LinearDeflection=.03,AngularDeflection=.12,Relative=False);mesh.write(str(out/'HX05-fit-v6__three-spectra__print.stl'));assert mesh.isSolid() and mesh.countComponents()==3
 packed.exportStep(str(out/'HX05-fit-v6__three-spectra__print.step'));doc.recompute();doc.saveAs(str(out/'HX05-fit-v6.FCStd'));A.closeDocument(doc.Name)
 doc=A.openDocument(str(out/'HX05-fit-v6.FCStd'));assert len(doc.Objects)==3 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in doc.Objects);A.closeDocument(doc.Name)
 r=dict(version=6,status='Native/export checks pass; owner-profile slicing and physical fit pending',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),freecad=A.Version(),occ=Part.OCC_VERSION,print_extents_mm=[packed.BoundBox.XLength,packed.BoundBox.YLength,packed.BoundBox.ZLength],coupons=reports,orientation='Exact HX04 fan print frame for T3 and T5; normalized T6/T8 interpolation for 7 mm. Revised flat-to-flat hex clocking.',orientation_source_sha256=hashlib.sha256(ORIENTATION.read_bytes()).hexdigest(),files={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in out.iterdir() if p.suffix in ('.stl','.step','.FCStd')})
 (out/'fit-v6-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=HERE/'runs/fit-v6');p.add_argument('--plan',action='store_true');a=p.parse_args()
 if a.plan:print(json.dumps(plan(),indent=2))
 else:build(a.out.resolve())
if __name__=='__main__':main()
