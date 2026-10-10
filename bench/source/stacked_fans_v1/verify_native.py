"""Native body checks for socket release and grasp approach, not free-hand removal.
Shaft sweeps are exact hex/round extrusions. Grip and hand capsule sweeps use
circumscribed icospheres, never inscribed ones.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import FreeCAD as A,Part
import trimesh
import importlib.util
spec=importlib.util.spec_from_file_location('hx05_native_helpers',Path(__file__).with_name('build.py'))
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
hexwire,v,H=helpers.hexwire,helpers.v,helpers.H
OUT=Path(sys.argv[1]);rs=json.loads((OUT.parent/'layout.json').read_text())['racks']
S=trimesh.creation.icosphere(subdivisions=1,radius=1)
from scipy.spatial import ConvexHull
ch=ConvexHull(S.vertices);inradius=min(-ch.equations[:,3]);sphere=S.vertices/inradius

def read(p):q=Part.Shape();q.read(str(p));return q

def swept_capsule(a,b,r,translation):
    centres=np.array([a,b,a+translation,b+translation])
    return H.hull_solid((centres[:,None,:]+sphere[None,:,:]*r).reshape(-1,3))

def overlap(a,b):
    if not a.BoundBox.intersect(b.BoundBox):return 0.
    return float(a.common(b).Volume)

bodies=[]
for rack in rs:
    body=read(OUT/rack['id']/'body.brep');body.translate(v([0,0,rack['z']]));bodies.append(body)
body_contacts=[dict(a=rs[i]['id'],b=rs[j]['id'],volume_mm3=overlap(body,other)) for i,body in enumerate(bodies) for j,other in enumerate(bodies[:i])]
rows=[]
for rack in rs:
    for t in rack['tools']:
        p,u,b,c=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['top']));p+=np.array([0,0,rack['z']]);c+=np.array([0,0,rack['z']])
        length=t['overall']-9+t['burial']+5
        axis_shaft=Part.makeCylinder(t['p2p']/2,length,v(p),v(u)) if 'p2p' in t else Part.Face(hexwire(p,u,b,t['af'])).extrude(v(u*length))
        d=u*(t['burial']+5)
        a=c-b*(t['bar']/2-9);z=c+b*(t['bar']/2-9)
        grip_axis=swept_capsule(a,z,9,d)
        ha=c+b*(t['bar']/2-18);hb=c+b*(t['bar']/2-3)
        hands=[swept_capsule(ha,hb,25,np.array([0,180,0])),swept_capsule(ha,hb,25,d)]
        tool_over=max(overlap(shape,holder) for shape in (axis_shaft,grip_axis) for holder in bodies)
        hand_over=max(overlap(shape,holder) for shape in hands for holder in bodies)
        row=dict(rack=rack['id'],tool=t['name'],tool_release_body_overlap_mm3=tool_over,hand_body_overlap_mm3=hand_over)
        rows.append(row);print(row,flush=True)
record=dict(passed=all(max(x['tool_release_body_overlap_mm3'],x['hand_body_overlap_mm3'])<1e-5 for x in rows) and all(x['volume_mm3']<1e-5 for x in body_contacts),rows=rows,body_contacts=body_contacts,sphere_bound_scale=1/inradius,scope='Represented tools and 50 mm hand envelopes; axial stroke = burial plus 5 mm, plus front grasp approach. Subsequent free-hand removal, physical fit, whole-holder installation and loads not qualified.')
record['freecad']=A.Version()
record['occ']=Part.OCC_VERSION
record['native_artifacts']={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.suffix in ('.step','.FCStd','.brep','.stl','.gz')}
record['construction_sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}
(OUT/'sweep-check.json').write_text(json.dumps(record,indent=2)+'\n')
assert record['passed']
