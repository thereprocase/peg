"""Reusable pegboard anchor CAD. All dimensions mm; X width, Y toward user, Z up.

  from anchor import make_anchor
  part = make_anchor(board_thickness=3.94)
  result = your_mount.union(part)  # overlap the fusion face, Y=4.5 mm

The parametric source is this file plus motion_design.py. STEP is an interchange
solid, not a native parametric feature tree. Run this script to rebuild exports.
"""
from pathlib import Path
import argparse,json,math
import cadquery as cq
import numpy as np
import trimesh
from motion_design import DEFAULTS,make_profile,get_parts,transformed

ROOT=Path(__file__).resolve().parent

def make_anchor(**params):
    p=DEFAULTS|params
    if not 0 < p['width'] < p['hole_diameter']:
        raise ValueError('width must be positive and smaller than hole diameter')
    if p['board_thickness']<=0 or p['pitch']<=p['hole_diameter']:
        raise ValueError('Board thickness must be positive; pitch must exceed bore')
    if p['neck_height']>=math.sqrt(p['hole_diameter']**2-p['width']**2):
        raise ValueError('Neck section cannot fit the full-width chord of this bore')
    pts=make_profile(p)
    return cq.Workplane('YZ',origin=(-p['width']/2,0,0)).polyline(pts).close().extrude(p['width'])

def in_print_orientation(part):
    """X extrusion/layer stacking becomes printer Z; full side profile lies flat."""
    part=part.rotate((0,0,0),(0,1,0),-90)
    bb=part.val().BoundingBox()
    return part.translate((-bb.xmin,-bb.ymin,-bb.zmin))

def pair(p=None,columns=2):
    """Two anchor columns joined at the front; use for broader mounted objects.
    Includes only a small fusion bridge. Full attached-mount motion must be checked.
    """
    p=DEFAULTS|(p or {})
    unit=make_anchor(**p)
    part=unit
    for i in range(1,columns):part=part.union(unit.translate((i*p['pitch'],0,0)))
    if columns>1:
        # Root-side bridge never extends behind original front spine.
        bridge=cq.Workplane('XY').box((columns-1)*p['pitch']+p['width'],3.0,6.0).translate(((columns-1)*p['pitch']/2,p['spine_depth']+.9,-p['pitch']/2))
        part=part.union(bridge)
    return part

def export_part(name,part,folder,print_stl=True):
    folder.mkdir(exist_ok=True,parents=True)
    shape=part.val()
    if not shape.isValid() or len(shape.Solids())!=1:
        raise ValueError(f'{name}: invalid solid or disconnected geometry')
    cq.exporters.export(part,str(folder/(name+'.step')))
    printable=in_print_orientation(part) if print_stl else part
    cq.exporters.export(printable,str(folder/(name+'.stl')),tolerance=.008,angularTolerance=.06)
    mesh=trimesh.load(folder/(name+'.stl'),force='mesh')
    if not mesh.is_watertight or not mesh.is_volume:
        raise ValueError(f'{name}: mesh is not a watertight outward solid')
    return {'name':name,'valid_brep':shape.isValid(),'solid_count':len(shape.Solids()),'stl_watertight':bool(mesh.is_watertight),'stl_volume_positive':bool(mesh.is_volume),'volume_mm3':round(shape.Volume(),3),'print_bounds_mm':np.round(mesh.extents,3).tolist()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--thickness',type=float)
    parser.add_argument('--hole-diameter',type=float)
    args=parser.parse_args()
    records=[];out=ROOT/'cad'
    if args.thickness is not None or args.hole_diameter is not None:
        p=DEFAULTS.copy()
        if args.thickness is not None:p['board_thickness']=args.thickness
        if args.hole_diameter is not None:p['hole_diameter']=args.hole_diameter
        records.append(export_part('anchor_custom',make_anchor(**p),out))
        (out/'custom_parameters.json').write_text(json.dumps(p,indent=2))
    else:
        records.append(export_part('anchor_default_3p94mm',make_anchor(),out))
        for t in [4.19,4.7625,6.35]:
            name='anchor_'+str(t).replace('.','p')+'mm'
            records.append(export_part(name,make_anchor(board_thickness=t),out))
        records.append(export_part('anchor_3p94mm_9over32_holes',make_anchor(hole_diameter=25.4*9/32),out))
        # Assembly reference only: a complete host determines support/print orientation.
        pair_part=pair()
        assert pair_part.val().isValid() and len(pair_part.val().Solids())==1
        cq.exporters.export(pair_part,str(out/'two_column_example.step'))
        stale=out/'two_column_example.stl'
        if stale.exists():stale.unlink()
    (ROOT/'cad_validation.json').write_text(json.dumps(records,indent=2))
    (ROOT/'parameters.json').write_text(json.dumps(DEFAULTS,indent=2))
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
