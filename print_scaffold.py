"""Optional sacrificial supports for upright printing. Remove completely before use.
All CAD stays in the anchor's common design coordinates; only STL shifts onto bed.
"""
from pathlib import Path
import json
import cadquery as cq
import trimesh
from shapely.geometry import Polygon
from anchor import make_anchor
from motion_design import get_parts
from upright_supports_design import support_profile
ROOT=Path(__file__).resolve().parent

def extrude_polygon(poly,x0,thickness):
    return cq.Workplane('YZ',origin=(x0,0,0)).polyline(list(poly.exterior.coords)[:-1]).close().extrude(thickness)

def make_upright_supports(web_thickness=.5,web_inset=.15,**params):
    p,parts,z0=get_parts(params)
    profiles=support_profile(p)
    ribs=[]
    for x0 in [-p['width']/2+web_inset,p['width']/2-web_inset-web_thickness]:
        for name,points in profiles.items():
            poly=Polygon(points)
            ribs.append((name,x0,extrude_polygon(poly,x0,web_thickness)))
    return ribs

def make_printable_upright(web_thickness=.5,web_inset=.15,**params):
    part=make_anchor(**params)
    for name,x0,rib in make_upright_supports(web_thickness,web_inset,**params):part=part.union(rib)
    return part

def main():
    out=ROOT/'cad';out.mkdir(exist_ok=True)
    part=make_printable_upright()
    shape=part.val()
    assert shape.isValid() and len(shape.Solids())==1
    cq.exporters.export(part,str(out/'anchor_upright_supported.step'))
    bb=shape.BoundingBox();printpart=part.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    cq.exporters.export(printpart,str(out/'anchor_upright_supported.stl'),tolerance=.008,angularTolerance=.06)
    mesh=trimesh.load(out/'anchor_upright_supported.stl',force='mesh')
    assert mesh.is_watertight and mesh.is_volume
    clean=make_anchor()
    assembly=cq.Assembly(name='Upright_anchor_with_cutaway_webs')
    assembly.add(clean,name='KEEP_anchor',color=cq.Color(.09,.49,.50))
    for i,(name,x0,web) in enumerate(make_upright_supports()):
        assembly.add(web,name=f'CUT_{name}_{i+1}',color=cq.Color(.90,.39,.13))
    assembly.export(str(out/'upright_cutaway_reference.step'))
    report={'valid_brep':True,'solid_count':1,'stl_watertight':True,'web_count':4,'web_thickness_mm':.5,'web_inset_mm':.15,'inter_web_bridge_mm':2.7,'upright_bounds_mm':mesh.extents.tolist(),'anchor_volume_mm3':clean.val().Volume(),'supported_volume_mm3':shape.Volume(),'sacrificial_volume_mm3':shape.Volume()-clean.val().Volume(),'physical_print_tested':False}
    (ROOT/'upright_cad_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
