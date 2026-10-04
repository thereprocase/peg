"""v14 external-perimeter and lift-clearance review using existing physics Python.

Material projections retain windows; occupied external perimeters fill internal holes
only. No convex hull or bounding rectangle is substituted for an external outline.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import trimesh
from shapely.geometry import LineString,Polygon,mapping
from shapely.ops import polygonize,unary_union

NAME='part-solder-spool-storage__v14__right-cheek__fit-pf02c9-hoop5'


def project(mesh):
    t=mesh.triangles[:,:,[0,2]];a=t[:,1]-t[:,0];b=t[:,2]-t[:,0]
    return unary_union([Polygon(q) for q in t[np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-8]])


def perimeter(shape):
    if shape.geom_type=='Polygon':return Polygon(shape.exterior)
    return unary_union([Polygon(p.exterior) for p in shape.geoms])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    d=parser.parse_args().output.resolve()
    design=json.loads((d/f'{NAME}__design.json').read_text())
    checks=json.loads((d/f'{NAME}__checks.json').read_text())
    body=trimesh.load(d/f'{NAME}__installed.stl',force='mesh')
    material=project(body);external=perimeter(material)
    floor=design['trough']['bottom_z_mm']
    geometry={'body_material_projection':mapping(material),'body_external_perimeter':mapping(external)}
    reports=[]
    for c in design['payload_cases']:
        tool=trimesh.load(d/f"payload__{c['id']}.stl",force='mesh')
        installed=project(tool); occupied=perimeter(unary_union([material,installed]))
        w=c['width_mm']/2; top=c['lifted_top_z_mm']
        swept=Polygon([(-w,floor),(w,floor),(w,top),(-w,top)])
        extra=swept.difference(occupied)
        geometry[c['id']]=dict(installed_payload=mapping(installed),
            installed_occupied_external_perimeter=mapping(occupied),
            conservative_up_out_sweep_projection=mapping(swept),extra_lift_envelope=mapping(extra))
        reports.append(dict(id=c['id'],outside_installed_occupied_perimeter_mm2=float(extra.area),
            extra_z_above_installed_perimeter_mm=max(0,top-occupied.bounds[3]),
            extra_z_above_flat_plate_edge_mm=max(0,top-5.12),
            extra_x_mm=0,required_lift_mm=8,front_translation_mm=65))
    (d/'projected-outlines.json').write_text(json.dumps(geometry,indent=2)+'\n')
    sections={}
    for label,mesh,x in [('body',body,0),('nominal',trimesh.load(d/'payload__nominal-55x30.stl',force='mesh'),14),
                         ('large',trimesh.load(d/'payload__large-65x34.stl',force='mesh'),16)]:
        segments=trimesh.intersections.mesh_plane(mesh,plane_origin=[x,0,0],plane_normal=[1,0,0])
        polygons=list(polygonize(unary_union(
            [LineString(np.round(s[:,[1,2]],5)) for s in segments])))
        samples=[[x,p.representative_point().x,p.representative_point().y] for p in polygons]
        inside=mesh.contains(samples) if samples else []
        sections[label]=[mapping(p) for p,keep in zip(polygons,inside) if keep]
    (d/'side-sections.json').write_text(json.dumps(sections,indent=2)+'\n')
    contained=all(c['outside_installed_occupied_perimeter_mm2']<1e-4 for c in reports)
    report=dict(passed=bool(checks['passed']) and contained,
        shared_checks_passed=bool(checks['passed']),sweeps_contained=contained,
        projection_method='Orthographic union of STL triangles. External occupied perimeter fills internal holes only; no convex hull or bounding-box replacement.',
        cases=reports,body_bounds=body.bounds.tolist(),
        body_growth_from_braid_mm=dict(downward=float(-body.bounds[0,2]-37.5082),
                                      forward=float(body.bounds[1,1]-55.1356),lateral=0),
        reduction_from_v13=dict(volume_fraction=1-design['volume_mm3']/59805.323239311896,
                               bottom_height_mm=float(body.bounds[0,2]+70.5),
                               front_depth_mm=float(80-body.bounds[1,1])),
        hand_clearance='Additional to spool sweep. Open top and front allow a direct grasp; no qualified hand envelope.',
        inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [d/f'{NAME}__installed.stl',d/f'{NAME}__design.json',d/f'{NAME}__checks.json',
                 *sorted(d.glob('payload__*.stl'))]},
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (d/'storage-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
