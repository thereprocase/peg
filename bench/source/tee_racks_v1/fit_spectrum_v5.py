"""Three five-slot clearance spectra, in HX05 left-end print orientation.
FreeCAD Python is required for build; --plan uses ordinary Python.
"""
import argparse,hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
CLEARANCES=(.10,.15,.19,.23,.28)  # per flat; C is owner's latest requested fit
DEFAULT_ANGLES={3.:90.,5.:65.,7.:65.}  # grip turn about shaft, from HX05B tiers
VENT=1.;WALL=3.;FLOOR=3.;LEAD=.8

def plan(angles,heading):
 return [dict(size_mm=size,guide_mm=max(40.,8*size),grip_turn_deg=angles[size],bed_heading_deg=heading,
              slots=[dict(letter=letter,clearance_per_flat_mm=c,total_af_clearance_mm=2*c,bore_af_mm=size+2*c) for letter,c in zip('ABCDE',CLEARANCES)]) for size in angles]

def build(out,angles,heading):
 import FreeCAD as A,Part,MeshPart,Mesh
 V=A.Vector;out.mkdir(parents=True,exist_ok=True);doc=A.newDocument('HX05FitSpectrumV5');parts=[];reports=[];yoff=0.
 def polygon(x,cy,cz,af,turn):
  psi=math.radians(turn);bar=V(0,-math.sin(psi),math.cos(psi));side=V(1,0,0).cross(bar);r=af/math.sqrt(3)
  pts=[V(x,cy,cz)+bar*(r*math.cos(math.pi/6+k*math.pi/3))+side*(r*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
  return Part.makePolygon(pts+[pts[0]])
 for q in plan(angles,heading):
  size=q['size_mm'];guide=q['guide_mm'];length=guide+LEAD+FLOOR;radius=(size+2*max(CLEARANCES))/math.sqrt(3)
  pitch=2*radius+WALL;height=2*radius+2*WALL;width=5*pitch+WALL;z=height/2
  shape=Part.makeBox(length,width,height);cuts=[];checks=[]
  for i,s in enumerate(q['slots']):
   cy=WALL+radius+i*pitch;af=s['bore_af_mm'];turn=q['grip_turn_deg']
   bore=Part.Face(polygon(FLOOR,cy,z,af,turn)).extrude(V(length-FLOOR+1,0,0))
   lead=Part.makeLoft([polygon(length-LEAD,cy,z,af,turn),polygon(length+.001,cy,z,af+2*LEAD,turn)],True,True)
   vent=Part.makeCylinder(VENT/2,FLOOR+.2,V(-.1,cy,z),V(1,0,0));cuts.extend([bore,lead,vent])
   checks.append((cy,s))
  for cutter in cuts:shape=shape.cut(cutter)
  shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1
  for cy,s in checks:
   vent=Part.makeCylinder(.49,FLOOR,V(0,cy,z),V(1,0,0));assert shape.common(vent).Volume<1e-7
   stop=Part.makeCylinder(.2,FLOOR,V(0,cy+.75,z),V(1,0,0));assert abs(shape.common(stop).Volume-stop.Volume)<1e-7
   tool=Part.Face(polygon(FLOOR+.1,cy,z,size,q['grip_turn_deg'])).extrude(V(guide-.2,0,0));assert shape.common(tool).Volume<1e-7
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
  # Rack shaft is horizontal in the left-end print. Its 20-degree board tilt becomes bed heading.
  shape.rotate(V(0,0,0),V(0,0,1),heading);bb=shape.BoundBox;shape.translate(V(-bb.XMin,-bb.YMin,0))
  name=f'HX05-fit-v5-{size:g}mm__rack-angle__print';shape.exportStep(str(out/(name+'.step')))
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);mesh.write(str(out/(name+'.stl')))
  reload=Part.Shape();reload.read(str(out/(name+'.step')));assert reload.isValid() and len(reload.Solids)==1
  assert mesh.isSolid() and mesh.countComponents()==1 and not mesh.hasInvalidPoints() and not mesh.hasInvalidNeighbourhood()
  assert abs(mesh.Volume-reload.Volume)/reload.Volume<.005
  obj=doc.addObject('Part::Feature',f'Hex{size:g}');obj.Label=f'{size:g} mm spectrum A-E';docshape=shape.copy();docshape.translate(V(0,yoff,0));obj.Shape=docshape
  for key,val in [('GripTurn',q['grip_turn_deg']),('BedHeading',heading)]:obj.addProperty('App::PropertyAngle',key,'Build metadata');setattr(obj,key,val)
  bb=shape.BoundBox;q.update(files=[name+'.stl',name+'.step'],native_valid=True,native_solids=1,mesh_closed=True,mesh_components=1,mesh_step_relative_volume_error=abs(mesh.Volume-reload.Volume)/reload.Volume,print_extents_mm=[bb.XLength,bb.YLength,bb.ZLength],vent_diameter_mm=VENT,floor_mm=FLOOR)
  reports.append(q);placed=shape.copy();placed.translate(V(0,yoff,0));parts.append(placed);yoff+=bb.YLength+8
 packed=Part.makeCompound(parts);assert packed.BoundBox.YLength<230 and packed.BoundBox.XLength<230
 mesh=MeshPart.meshFromShape(Shape=packed,LinearDeflection=.03,AngularDeflection=.12,Relative=False);mesh.write(str(out/'HX05-fit-v5__three-spectra__print.stl'));assert mesh.isSolid() and mesh.countComponents()==3
 packed.exportStep(str(out/'HX05-fit-v5__three-spectra__print.step'));doc.recompute();doc.saveAs(str(out/'HX05-fit-v5.FCStd'));A.closeDocument(doc.Name)
 doc=A.openDocument(str(out/'HX05-fit-v5.FCStd'));assert len(doc.Objects)==3 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in doc.Objects);A.closeDocument(doc.Name)
 r=dict(version=5,status='Native/export checks pass; owner-profile slicing and physical fit pending',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),freecad=A.Version(),occ=Part.OCC_VERSION,print_extents_mm=[packed.BoundBox.XLength,packed.BoundBox.YLength,packed.BoundBox.ZLength],coupons=reports,orientation='HX05 left-end print; horizontal shafts, original six hex flats, flat-to-flat grip axis. 3 mm lower tier 90 degree grip turn; 5 mm upper tier 65 degrees. 7 mm uses upper-tier orientation as a trial: not a tool in Bondhus 13189.',files={p.name:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in out.iterdir() if p.suffix in ('.stl','.step','.FCStd')})
 (out/'fit-v5-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=HERE/'runs/fit-v5');p.add_argument('--heading',type=float,default=20.)
 for size,angle in DEFAULT_ANGLES.items():p.add_argument(f'--angle-{size:g}',type=float,default=angle)
 p.add_argument('--plan',action='store_true');a=p.parse_args();angles={size:getattr(a,f'angle_{size:g}') for size in DEFAULT_ANGLES}
 if a.plan:print(json.dumps(plan(angles,a.heading),indent=2))
 else:build(a.out.resolve(),angles,a.heading)
if __name__=='__main__':main()
