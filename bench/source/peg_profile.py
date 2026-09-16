"""Canonical peg construction. Re-read fit on every call; cache by content hash."""
from pathlib import Path
from functools import lru_cache
import json,math,hashlib,re
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];V=A.Vector
FIT_SOURCE=ROOT/'reference/peg-fit.scad'
def parse(raw):
    values={}
    for name,value in re.findall(r'^\s*(PEG_[A-Z_]+)\s*=\s*("[^"\n]*"|-?[0-9]+(?:\.[0-9]+)?)\s*;',raw.decode(),re.M):
        values[name]=json.loads(value)
    required={'PEG_BOARD_GRIP','PEG_PULL_CLEARANCE','PEG_TONGUE_RUN','PEG_TONGUE_RISE','PEG_FIT_REVISION','PEG_DIAMETER','PEG_HOLE_DIAMETER','PEG_TONGUE_DIAMETER','PEG_FACE_Y','PEG_ROOT_Y','PEG_SEAT_DROP','PEG_PITCH'}
    assert required<=values.keys(),required-values.keys()
    assert values['PEG_TONGUE_RUN']>0 and values['PEG_TONGUE_RISE']>0
    assert values['PEG_BOARD_GRIP']>0 and values['PEG_ROOT_Y']>values['PEG_FACE_Y']
    return values
def box(x,y,z,w,d,h):return Part.makeBox(w,d,h,V(x,y,z))

@lru_cache(maxsize=8)
def _build(raw):
    cfg=parse(raw)
    BOARD_GRIP_ASSUMPTION=cfg["PEG_BOARD_GRIP"]; PULL_CLEARANCE=cfg["PEG_PULL_CLEARANCE"]
    TONGUE_RUN=cfg["PEG_TONGUE_RUN"]; TONGUE_RISE=cfg["PEG_TONGUE_RISE"]; VARIANT=cfg["PEG_FIT_REVISION"]
    g=json.loads((ROOT/'reference/conformal_120_geometry.json').read_text())
    p=dict(g['parameters'])
    for key,field in {'hole_diameter':'PEG_HOLE_DIAMETER','peg_diameter':'PEG_DIAMETER','tongue_diameter':'PEG_TONGUE_DIAMETER','front_gap':'PEG_FACE_Y','root_y':'PEG_ROOT_Y','seat_drop':'PEG_SEAT_DROP','pitch':'PEG_PITCH'}.items():p[key]=cfg[field]
    r=p['peg_diameter']/2;tr=p['tongue_diameter']/2
    slope=TONGUE_RISE/TONGUE_RUN
    elbow_offset=PULL_CLEARANCE-p['front_gap']-(p['hole_diameter']-r)/slope+tr*math.sqrt(1+1/slope**2)
    z=-(p['hole_diameter']-p['peg_diameter'])/2+p['seat_drop']
    elbow_y=-BOARD_GRIP_ASSUMPTION-elbow_offset
    a,b,c=V(0,p['root_y'],z),V(0,elbow_y,z),V(0,elbow_y-TONGUE_RUN,z+TONGUE_RISE)
    parts=[Part.makeSphere(r,a),Part.makeSphere(r,b),Part.makeSphere(tr,c)]
    for start,end,radius in [(a,b,r),(b,c,tr)]:
        direction=end-start;parts.append(Part.makeCylinder(radius,direction.Length,start,direction))
    # Exact existing 120-degree lower bore-bearing arc. Land stops at the elbow.
    R=p['hole_diameter']/2;cutoff=p['seat_drop']-R*math.cos(math.radians(60))
    land=Part.makeCylinder(R,p['root_y']-elbow_y,V(0,elbow_y,p['seat_drop']),V(0,1,0))
    land=land.common(box(-R-1,elbow_y-1,p['seat_drop']-R-1,2*R+2,p['root_y']-elbow_y+2,cutoff-(p['seat_drop']-R-1)))
    upper=parts[0].multiFuse(parts[1:]+[land]).removeSplitter()
    baseline=Part.read(str(ROOT/'reference/conformal_120.step'))
    lower=baseline.common(box(-10,-30,-45,20,60,35))
    result=Part.makeCompound([upper,lower])
    assert result.isValid()
    return result,dict(config_sha256=hashlib.sha256(raw).hexdigest(),canonical_source="reference/peg-fit.scad",variant=VARIANT,board_grip_assumption_mm=BOARD_GRIP_ASSUMPTION,
        source_board_assumption_mm=3.94,clearance_at_assumed_board_mm=PULL_CLEARANCE,
        predicted_clearance_at_3p94_board_mm=PULL_CLEARANCE-(3.94-BOARD_GRIP_ASSUMPTION),
        tongue_run_mm=TONGUE_RUN,tongue_rise_mm=TONGUE_RISE,
        tongue_angle_deg=math.degrees(math.atan(slope)),previous_tongue_angle_deg=math.degrees(math.atan(3/5)),
        elbow_center_y_mm=elbow_y,lower_locator='Exact baseline lower locator, unchanged; designed for 3.94 mm board',
        construction='Canonical cylinder/sphere upper core and exact 120-degree cylindrical lower bearing segment. User-authorized parameter revision.',
        scope='Intentional interference: negative clearance requires plastic/board compliance. Assumed board grip, not measured thickness. No force or recoverable deformation claim.',
        baseline_sha256=hashlib.sha256((ROOT/'reference/conformal_120.step').read_bytes()).hexdigest())


def build():
    shape,info=_build(FIT_SOURCE.read_bytes())
    return shape.copy(),dict(info)
def load_reference():return build()[0]
def parameters():return build()[1]
