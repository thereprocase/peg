"""Reuse nominal tool/path checks; add exact flat-bed and upright geometry evidence."""
import json,sys
from pathlib import Path
import numpy as np
import trimesh
from shapely.ops import unary_union
from shapely.geometry import Polygon
import rectangular_funnel_check_v1 as base

def review(d):
 c=json.loads((d/'candidate.json').read_text());out=json.loads((d/'checks.json').read_text());m=trimesh.load_mesh(d/c['print_file']);tri=m.triangles
 flat=(np.max(np.abs(tri[:,:,2]),axis=1)<1e-5)&(m.face_normals[:,2]<-.999)
 contact=unary_union([Polygon(t[:,:2]) for t in tri[flat]])
 bodybase=trimesh.load_mesh(d/'bed-contact.stl');cadarea=c['bed_contact']['cad_face_area_mm2']
 # CAD section at the bed is open: preserve the full rectangular lower passage.
 hole_area=14*48
 holes=sum(Polygon(r).area for g in ([contact] if contact.geom_type=='Polygon' else contact.geoms) for r in g.interiors)
 # Quantify downward-facing body facets separately from rear-facing pegs.
 inv=np.linalg.inv(np.array(c['pose_matrix']).reshape(4,4));centres=trimesh.transform_points(m.triangles_center,inv)
 elevated=(m.face_normals[:,2]<-np.cos(np.radians(44.9)))&(tri[:,:,2].min(axis=1)>.01)
 front=elevated&(centres[:,1]>.151);rear=elevated&~(centres[:,1]>.151)
 near45=(np.abs(m.face_normals[:,2]+np.sqrt(.5))<.002)&(tri[:,:,2].min(axis=1)>.01)&(centres[:,1]>.151)
 evidence=dict(body_45deg_transition_area_mm2=float(m.area_faces[near45].sum()),facet_angle_tolerance_deg=.1,print_z_min_mm=float(m.bounds[0,2]),contact_area_mm2=float(contact.area),exact_CAD_contact_area_mm2=cadarea,contact_area_error_mm2=abs(contact.area-cadarea),contact_regions=1 if contact.geom_type=='Polygon' else len(contact.geoms),through_hole_area_mm2=float(holes),expected_bottom_hole_area_mm2=hole_area,body_downward_area_steeper_than_45deg_mm2=float(m.area_faces[front].sum()),peg_downward_area_steeper_than_45deg_mm2=float(m.area_faces[rear].sum()),scope='Complete print-mesh bed triangles at Z0; ordinary facet orientation screen, not layer/toolpath support qualification')
 evidence['passed']=bool(abs(m.bounds[0,2])<1e-5 and abs(contact.area-cadarea)<.02 and abs(holes-hole_area)<.02 and evidence['contact_regions']==1)
 out['bed_contact']=evidence;out['printing']['supports']='Upright. Sleeve/web/plate share the bed; rounded exterior; nominal taper23.63deg and existing lower internal transition45deg. Rear pegs still require support review. Unsliced; no support/toolpath qualification.'
 out['upright_interface']=dict(reference='common.receiver(2,2,upright,z0=-64)',symmetric_difference_mm3=c['peg_symmetric_difference_mm3'],v2_styling_symmetric_difference_mm3=c['v2_styling_symmetric_difference_mm3'],hoop='Shared upright horizontal hoop, flex in X within XY print layers; unchanged from v2 upright hoop, physical installation/release test remains pending')
 section_mesh=trimesh.load_mesh(d/(c['name']+'__installed.stl'))
 sections={}
 for label,normal,axes in [('X-Z',[0,1,0],[0,2]),('Y-Z',[1,0,0],[1,2])]:
  sec=trimesh.intersections.mesh_plane(section_mesh,plane_origin=[0,48,0],plane_normal=normal);sections[label]=[q[:,axes].tolist() for q in sec]
 (d/'sections.json').write_text(json.dumps(sections,indent=2)+'\n')
 out['inputs'].update({str(p):base.sha(p) for p in [Path(__file__),d/'bed-contact.stl']});out['passed']=bool(out['passed'] and evidence['passed']);(d/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print('UPRIGHT/BED',evidence,flush=True)
 if not out['passed']:raise SystemExit(1)
def main():
 base.main()
 review(Path(sys.argv[1]))
if __name__=='__main__':main()
