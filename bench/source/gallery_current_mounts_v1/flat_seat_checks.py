"""Compare opening cross-sections against the exact released mesh after +.6 Z.
Top planing only occurs above original Z=5; compare below that authorized band.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np,trimesh,manifold3d as M
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path('/home/repro/code/peg-gallery-current-mounts');D=R/'bench/reviews/gallery-current-mounts-flat-top-v2'
def solid(p):
 m=trimesh.load(p);a=M.Manifold(M.Mesh(np.float32(m.vertices),np.uint32(m.faces)));assert a.status()==M.Error.NoError;return a
def holes(a,z):
 out=[]
 for q in a.slice(z).to_polygons():
  area=np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))/2
  if area<0 and q[:,1].mean()>5.55:out.append(Polygon(q))
 return out
for p in sorted(D.glob('*/report.json')):
 d=json.loads(p.read_text());id=d['id']
 if id=='P09-36' or (len(sys.argv)>1 and id not in sys.argv[1:]):continue
 old=R/f"docs/gallery/{d['family']}/{id}/model.stl";new=p.parent/'installed.stl';a,b=solid(old),solid(new);sections=[]
 for z in [4.0,2.0,0.0]:
  h,k=holes(a,z),holes(b,z+.6);delta=unary_union(h).symmetric_difference(unary_union(k)).area;sections.append({'original_z_mm':z,'new_z_mm':z+.6,'original_openings':len(h),'new_openings':len(k),'opening_symmetric_difference_mm2':float(delta)})
 spec=json.loads((R/f"docs/gallery/{d['family']}/{id}/spec.json").read_text());expected=spec.get('hole_count');passed=all(q['original_openings']==q['new_openings'] and q['opening_symmetric_difference_mm2']<.01 for q in sections)
 if expected:passed=passed and all(q['new_openings']==expected for q in sections)
 result={'pass':passed,'expected_array_seats':expected,'sections':sections,'tolerance_mm2':.01,'scope':'Cross-section preservation below authorized planing band. Closed section void counts can include structural gaps; only declared array seat counts are treated as capacity. Does not establish physical tool fit; open-sided seats may not form closed loops. Exact remaining-body preservation is checked independently in CAD.','input_hashes':{str(old):hashlib.sha256(old.read_bytes()).hexdigest(),str(new):hashlib.sha256(new.read_bytes()).hexdigest(),str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}};(p.parent/'seat-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(id,passed,[(q['new_openings'],round(q['opening_symmetric_difference_mm2'],6)) for q in sections],flush=True)
