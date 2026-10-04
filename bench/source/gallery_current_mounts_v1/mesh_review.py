"""Independent mesh/export review; FreeCAD not required. GLB positions are metres."""
import json,hashlib,argparse
from pathlib import Path
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def review(out):
 report=json.loads((out/'report.json').read_text());checks={}
 for pose in ['installed','print']:
  p=out/(pose+'.stl');m=trimesh.load(p,force='mesh',process=True)
  checks[pose]={'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist(),'components':int(connected_components(coo_matrix((np.ones(len(m.edges)),(m.edges[:,0],m.edges[:,1])),shape=(len(m.vertices),len(m.vertices))),directed=False,return_labels=False)),'input_sha256':sha(p)}
  n,labels=connected_components(coo_matrix((np.ones(len(m.edges)),(m.edges[:,0],m.edges[:,1])),shape=(len(m.vertices),len(m.vertices))),directed=False)
  shell_volumes=np.bincount(labels[m.faces[:,0]],weights=np.einsum('ij,ij->i',m.triangles[:,0],np.cross(m.triangles[:,1],m.triangles[:,2]))/6,minlength=n)
  checks[pose]['shell_signed_volumes_mm3']=shell_volumes.tolist()
  checks[pose]['positive_material_shells']=int(np.count_nonzero(shell_volumes>1e-6))
  checks[pose]['internal_cavity_shells']=int(np.count_nonzero(shell_volumes<-1e-6))
  display=m.copy();display.apply_scale(.001);display.visual.face_colors=[82,174,198,255];target=out/(pose+'.glb');display.export(target);roundtrip=trimesh.load(target,force='mesh');checks[pose]['glb_span_error_mm']=float(np.abs(roundtrip.extents*1000-m.extents).max());report['assets'][pose+'_glb']=target.name
  if pose=='print':
   nz=m.face_normals[:,2];nonbed=m.triangles[:,:,2].max(axis=1)>.01;steep=(nz<-2**-.5)&nonbed
   checks[pose]['downfacing_over45deg_area_mm2']=float(m.area_faces[steep].sum());checks[pose]['overhang_scope']='Geometric face-normal screen; not toolpaths or a support-removal qualification.'
 installed=trimesh.load(out/'installed.stl',force='mesh'); front=installed.vertices[installed.vertices[:,1]>=.1499]
 pose=report['pose'];shift=report['body_translation_mm'];extent=report['print_bounds_mm']
 report['upper_material']={'highest_front_material_z_mm':float(front[:,2].max()),'above_nominal_lip_mm':max(0,float(front[:,2].max())-5.12),'approach':('Original functional body shifted 3 mm forward / 2 mm up, overlapping the 5.4 mm receiver by 2.4 mm; no hook shortening or separate crown pad.' if pose=='flat-top' else 'Original forward body retained and fused into full-thickness integral receiver; no separate crown pad.'),'root_continuity':'Single valid fused solid; exact shared rear interface; front motion includes all upper body material.'}
 flex=[0,0,1] if pose=='right-cheek' else [1,0,0];pm=np.array(report['print_matrix']).reshape(4,4);print_flex=pm[:3,:3]@flex
 placements=[]
 for rotate in [False,True]:
  x,y=extent[:2][::-1] if rotate else extent[:2]
  for dx,dy in [(18,0),(0,28)]:
   if x+dx<=256 and y+dy<=256 and extent[2]<=250:placements.append({'rotate_z_90':rotate,'offset_xy_mm':[dx,dy],'placed_bounds_mm':[x+dx,y+dy,extent[2]]})
 report['print_review']={'hoop_flex_installed_direction':flex,'hoop_flex_print_direction':print_flex.tolist(),'hoop_flex_out_of_layer_component':float(abs(print_flex[2])),'machine_envelope_mm':[256,256,250],'excluded_front_left_rectangle_mm':[18,28],'machine_source':'Released MS01 v3 used Repro P1S - 0.4 nozzle -> Bambu Lab P1S 0.4 nozzle -> fdm_bbl_3dp_001_common -> fdm_machine_common. Height 250 mm; machine-specific exclusion overrides parent.','bare_body_aabb_placement_options':placements,'within_machine':bool(placements),'bed_contact_note':('Original planar top and any coplanar receiver; hook material does not set the bed plane.' if pose=='flat-top' else 'Coplanar triangles on selected body cheek / bottom and integral receiver; bed contact is geometric, not adhesion qualification.'),'support_and_brim_scope':'Bare body only; local peg supports, body bridges and brim need a new plate/toolpath review. No prior print job applies.'}
 report['input_hashes'][str(Path(__file__))]=sha(Path(__file__))
 checks['pass']=all(c['watertight'] and c['consistent_winding'] and c['positive_material_shells']==1 and c['glb_span_error_mm']<.001 for c in checks.values())
 (out/'mesh-checks.json').write_text(json.dumps(checks,indent=2)+'\n');report['checks']['independent_mesh']=checks;report['checks']['pass']=bool(report['checks']['valid_one_solid'] and report['checks']['rear_interface_symmetric_difference_mm3']<1e-6 and report['checks']['preserved_body_missing_mm3']<1e-6 and report['checks']['new_material_beyond_back_wall_mm3']<1e-6 and report['checks']['upper_body_motion']['pass'] and report['checks']['bed_contact_area_mm2']>1 and checks['pass'] and bool(placements) and abs(print_flex[2])<1e-9);report['assets']['mesh_checks']='mesh-checks.json';report['export_hashes']={p.name:sha(p) for p in out.iterdir() if p.suffix in ['.stl','.glb','.step','.FCStd']};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(out.name,checks['pass'],flush=True)
 if not checks['pass']:raise SystemExit(2)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();review(a.out)
