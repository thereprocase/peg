"""Versioned installed-body remount. Run with FreeCAD's Python; no slicing or printing.
The historical body is trimmed only behind its mounting face, then rigidly placed.
Functional seats and cavities are retained; additions are confined to the back wall.
"""
from pathlib import Path
import argparse, hashlib, json, math, sys
import FreeCAD as A
import Part
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'station_snapshot/source/solder_v12'))
import common as K
V = A.Vector

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(s):
 b=s.optimalBoundingBox(); return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def matrix(m): return [getattr(m,'A%d%d'%(i,j)) for i in range(1,5) for j in range(1,5)]
def screen(s):
 # Tessellated front surface, sampled bounded-step rigid motion. NOT a new fit proof.
 verts,_=s.tessellate(.005); yz=np.array([[v.y,v.z] for v in verts]);rho=np.linalg.norm(yz,axis=1).max()
 poses=json.loads((HERE/'station_snapshot/reference/conformal_motion_results.json').read_text())['removal_poses']
 minimum=1e9; worst=None; count=0
 for a,b in zip(poses,poses[1:]):
  n=max(1,math.ceil((math.hypot(b['y']-a['y'],b['z']-a['z'])+math.radians(abs(b['theta_deg']-a['theta_deg']))*rho)/.05))
  for f in np.linspace(0,1,n+1):
   y=a['y']+(b['y']-a['y'])*f;t=math.radians(a['theta_deg']+(b['theta_deg']-a['theta_deg'])*f)
   ys=y+yz[:,0]*math.cos(t)-yz[:,1]*math.sin(t); k=int(ys.argmin()); m=float(ys[k]);count+=1
   if m<minimum:minimum=m;worst={'point_yz':yz[k].tolist(),'translation_y':y,'angle_deg':math.degrees(t)}
 return {'pass':minimum>=-.006,'minimum_front_board_y_mm':minimum,'poses':count,'max_point_step_mm':.05,'mesh_deflection_mm':.005,'worst':worst,'scope':'Front material vs board plane only; sampled nominal reference route, not certification of changed interference pegs or physical installation.'}
def build(spec,out):
 out.mkdir(parents=True,exist_ok=True)
 src=Path(spec['input']);assert sha(src)==spec['input_sha256']

 if src.suffix.lower()=='.stl':
  import Mesh
  mesh=Mesh.Mesh(str(src));shell=Part.Shape();shell.makeShapeFromMesh(mesh.Topology,.0001);original=Part.makeSolid(shell).removeSplitter()
 else: original=Part.read(str(src))
 assert original.isValid() and len(original.Solids)==1
 body=original.common(box(-500,.15,-500,500,500,500)).removeSplitter()
 original_forward=body.copy()
 level=spec['level_at_original_z_mm']
 body=body.common(box(-500,-50,-500,500,500,level)).removeSplitter()
 removed_top=original_forward.cut(body).Volume
 body.translate(V(*spec.get('body_translation_mm',[0,0,0])))
 back=body.common(box(-500,-50,-500,500,5.55,500));bb=back.optimalBoundingBox()
 z0=spec.get('plate_bottom',bb.ZMin);cols=spec['columns']; hoop=spec.get('hoop_row',max(1,int((.12-z0-6)/25.4)));pose=spec['pose']
 old_columns=K.columns
 try:
  K.columns=lambda cells:cols
  receiver, mount=K.receiver(2,hoop,'right-cheek' if pose=='right-cheek' else 'upright',x0=bb.XMin,x1=bb.XMax,z0=z0,z1=spec['flat_top_installed_z_mm'])
 finally: K.columns=old_columns
 shape=body.fuse(receiver).removeSplitter()
 assert shape.isValid() and len(shape.Solids)==1,(shape.isValid(),len(shape.Solids))
 rear=box(-500,-50,-500,500,.15,500)
 diff=shape.common(rear).cut(receiver).Volume+receiver.common(rear).cut(shape).Volume
 lost=body.cut(shape).Volume
 added=shape.cut(body).common(box(-500,5.55001,-500,500,500,500)).Volume
 front=shape.common(box(-500,.15,-500,500,500,500)); motion=screen(front)
 if pose=='inverted-flat-top':
  m=A.Matrix();m.rotateX(math.radians(180));pp=shape.copy();pp.transformShape(m);b=pp.optimalBoundingBox();t=A.Matrix();t.move(V(-b.XMin,-b.YMin,-b.ZMin));pp.transformShape(t);pm=t.multiply(m)
 else: pp,pm=K.pose_transform(shape,pose)
 meshes={}
 for label,s in [('installed',shape),('print',pp)]:
  s.exportStep(str(out/f'{label}.step'));meshes[label]=K.write(s,out/f'{label}.stl')
  doc=A.newDocument('Mount_'+label);o=doc.addObject('PartDesign::Feature','Body');o.Shape=s;doc.recompute();doc.saveAs(str(out/f'{label}.FCStd'));A.closeDocument(doc.Name)
 # Independent tessellation at print bed; area of truly coplanar triangles.
 vv,ff=pp.tessellate(.005);v=np.array([[q.x,q.y,q.z] for q in vv]);f=np.array(ff);tri=v[f];bed=tri[np.max(np.abs(tri[:,:,2]),axis=1)<.0001];area=float(np.linalg.norm(np.cross(bed[:,1]-bed[:,0],bed[:,2]-bed[:,0]),axis=1).sum()/2)
 checks={'valid_one_solid':True,'authorized_top_planing_removed_mm3':removed_top,'top_planing_z_range_mm':[level,original_forward.BoundBox.ZMax],'rear_interface_symmetric_difference_mm3':diff,'preserved_body_missing_mm3':lost,'new_material_beyond_back_wall_mm3':added,'upper_body_motion':motion,'bed_contact_area_mm2':area,'mesh':meshes}
 checks['pass']=bool(diff<1e-6 and lost<1e-6 and added<1e-6 and motion['pass'] and area>1)
 report={'schema_version':1,'id':spec['id'],'name':spec.get('name',spec['id']),'family':spec['family'],'version':'current-mounts-flat-top-v2','fit_label':'PF02 #9 / PF07 #5, clipped root; physical fit pending','pose':pose,'print_bounds_mm':np.subtract(bounds(pp)[3:],bounds(pp)[:3]).tolist(),'installed_bounds_mm':bounds(shape),'print_matrix':matrix(pm),'mount':mount,'body_translation_mm':spec.get('body_translation_mm',[0,0,0]),'source':spec,'checks':checks,'assets':{f'{label}_{ext.lower()}':f'{label}.{ext}' for label in ['installed','print'] for ext in ['stl','step','FCStd']},'notes':['Authorized top planing removes at most 0.12 mm of the nearly flat top; remaining body is translated +0.60 mm in Z. All seat openings must pass the separate section audit.','Pegs require local support planning; bare print pose is not sliced or support-qualified.','Changed interference-fit peg motion, physical fit and load testing remain pending.'],'input_hashes':{str(src):sha(src),str(Path(__file__)):sha(__file__)}}
 for p in (HERE/'station_snapshot').rglob('*'):
  if p.is_file() and p.suffix in ['.py','.json','.step','.scad']:report['input_hashes'][str(p)]=sha(p)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'id':spec['id'],'pass':checks['pass'],'motion':motion,'bed_area':area,'rear_difference':diff}),flush=True)
 if not checks['pass']:raise SystemExit(2)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('spec');p.add_argument('out');a=p.parse_args();build(json.loads(Path(a.spec).read_text()),Path(a.out))
