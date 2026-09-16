"""Optional dense straight-locator mount. Read canonical fit on every build."""
import hashlib
import FreeCAD as A, Part
import peg_profile as P
from peg_interface import receive_pegs
V=A.Vector

def configuration():
    raw=P.FIT_SOURCE.read_bytes();cfg=P.parse(raw)
    for key in ['PEG_ARRAY_DIAMETRAL_INTERFERENCE','PEG_ARRAY_DEPTH','PEG_ARRAY_TIP_DIAMETER','PEG_ARRAY_LEAD_LENGTH']:
        assert key in cfg,key
    return cfg,hashlib.sha256(raw).hexdigest()

def straight(x,row,cfg):
    radius=(cfg['PEG_HOLE_DIAMETER']+cfg['PEG_ARRAY_DIAMETRAL_INTERFERENCE'])/2
    face=cfg['PEG_FACE_Y'];root=cfg['PEG_ROOT_Y'];end=face-cfg['PEG_ARRAY_DEPTH']
    shoulder=end+cfg['PEG_ARRAY_LEAD_LENGTH'];z=cfg['PEG_SEAT_DROP']-row*cfg['PEG_PITCH']
    land=Part.makeCylinder(radius,root-shoulder,V(x,shoulder,z),V(0,1,0))
    lead=Part.makeCone(cfg['PEG_ARRAY_TIP_DIAMETER']/2,radius,shoulder-end,V(x,end,z),V(0,1,0))
    return land.fuse(lead).removeSplitter()

def mount(host,columns,rows):
    cfg,sha=configuration();result=host;reports=[];reference=P.load_reference()
    # Fetch canonical upper hooks without also importing the loose old locator.
    for x in columns:
        q=reference.copy();q.translate(V(x,0,0))
        result,r=receive_pegs(q,result,include_lower=False);reports.append(r)
    locators=[]
    for row in rows:
        assert row>0
        for x in columns:
            q=straight(x,row,cfg);result=result.fuse(q).removeSplitter();locators.append(q)
    assert result.isValid() and len(result.Solids)==1
    return result,dict(canonical_source='reference/peg-fit.scad',config_sha256=sha,
        hooks=reports,columns_x_mm=columns,straight_rows=rows,straight_count=len(locators),
        locator_diameter_mm=cfg['PEG_HOLE_DIAMETER']+cfg['PEG_ARRAY_DIAMETRAL_INTERFERENCE'],
        diametral_interference_mm=cfg['PEG_ARRAY_DIAMETRAL_INTERFERENCE'],
        locator_depth_from_board_face_mm=cfg['PEG_ARRAY_DEPTH'],configuration=cfg,
        scope='Optional array; upper hook geometry unchanged. Deliberate bore contact needs board/plastic compliance; retention force and wear unmeasured.')
