"""Opt-in print-face variants, always derived from freshly loaded canonical fit."""
import hashlib,json,math
import FreeCAD as A,Part
from peg_profile import build as canonical_build,FIT_SOURCE,parse,ROOT
V=A.Vector
SOURCE=ROOT/'reference/peg-print-variants.json'
def build(name):
    raw=SOURCE.read_bytes();cfg=json.loads(raw)[name]
    base,info=canonical_build();p=parse(FIT_SOURCE.read_bytes())
    angle=cfg.get('seat_slope_deg',0.0);assert 0<=angle<=10
    a=math.radians(angle);normal=V(0,-math.sin(a),math.cos(a))
    cz=-(p['PEG_HOLE_DIAMETER']-p['PEG_DIAMETER'])/2+p['PEG_SEAT_DROP']+p['PEG_TONGUE_RISE']
    cy=info['elbow_center_y_mm']-p['PEG_TONGUE_RUN']
    top=normal.dot(V(0,cy,cz))+p['PEG_TONGUE_DIAMETER']/2
    depth=cfg['cap_removal_mm'];assert 0<depth<p['PEG_TONGUE_DIAMETER']/2
    distance=top-depth;plane=distance/normal.z
    half=Part.makeBox(80,140,100,V(-40,-70,-100))
    half.rotate(V(),V(1,0,0),angle);half.translate(V(0,0,plane))
    shape=base.common(half).removeSplitter();removed=base.cut(shape)
    assert shape.isValid() and len(shape.Solids)==2
    assert shape.cut(base).Volume<1e-7 # Removal cannot add insertion interference.
    boardband=Part.makeBox(80,p['PEG_BOARD_GRIP']+p['PEG_FACE_Y'],100,V(-40,-p['PEG_BOARD_GRIP'],-50))
    bearing_change=removed.common(boardband).Volume
    assert bearing_change<1e-7
    flats=[f for f in shape.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).dot(normal)>.99999 and abs(f.CenterOfMass.dot(normal)-distance)<1e-7]
    assert len(flats)==1 and flats[0].Area>8
    f=flats[0];bounds=f.optimalBoundingBox()
    info.update(print_variant=name,print_variant_source='reference/peg-print-variants.json',
        print_variant_sha256=hashlib.sha256(raw).hexdigest(),cap_removal_mm=depth,
        cut_plane_z_mm=plane,cut_plane_normal=list(normal),cut_plane_normal_distance_mm=distance,seat_slope_deg=angle,bed_flat_area_mm2=f.Area,bed_flat_width_mm=bounds.XLength,
        removed_volume_mm3=removed.Volume,removed_nearest_y_mm=removed.optimalBoundingBox().YMax,
        assumed_board_back_y_mm=-p['PEG_BOARD_GRIP'],seated_board_band_change_mm3=bearing_change,
        peg_subset_of_canonical=True,scope='Top-cap subtraction only. Seated assumed board band unchanged; same prescribed insertion poses cannot gain peg collisions. Removal path, hold force and adhesion remain unmeasured.')
    return shape,info
