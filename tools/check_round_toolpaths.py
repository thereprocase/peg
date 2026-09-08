"""Actual extrusion-path screening, including unsupported portions of connected paths.
The reach tests are conservative geometric screens, not sag or thermal simulations.
"""
import argparse,json,sys,pathlib
from shapely.geometry import LineString
from shapely.ops import polygonize
import trimesh,numpy as np
from shapely.ops import unary_union
# Reuse the generic absolute-extrusion parser from the repository's tools.
for parent in pathlib.Path(__file__).resolve().parents:
 candidate=parent/'tools'/'analyze_toolpaths.py'
 if candidate.exists():sys.path.insert(0,str(candidate.parent));break
else:raise FileNotFoundError('Cannot locate repository tools/analyze_toolpaths.py')
from analyze_toolpaths import parse
p=argparse.ArgumentParser();p.add_argument('gcode',type=pathlib.Path);p.add_argument('--layer',type=float,default=.2);p.add_argument('--output',type=pathlib.Path);p.add_argument('--functional-mesh',type=pathlib.Path);p.add_argument('--functional-z-offset',type=float,default=0.);a=p.parse_args()
cleanmesh=trimesh.load(a.functional_mesh,force='mesh') if a.functional_mesh else None
if cleanmesh is not None:cleanmesh.apply_translation([0,0,a.functional_z_offset])
layers=parse(a.gcode,layer_height=a.layer);footprints=[];supportprints=[];records=[];support_layers=[]
for idx,segs in layers.items():
 model=[s for s in segs if s['type'] not in ('SKIRT','SUPPORT','SUPPORT-INTERFACE')]
 support=[s for s in segs if s['type'] in ('SUPPORT','SUPPORT-INTERFACE')]
 if cleanmesh is not None and segs:
  cross=trimesh.intersections.mesh_plane(cleanmesh,[0,0,1],[0,0,segs[0]['z']-a.layer/2])
  polygon=unary_union(list(polygonize([LineString(np.round(l[:,:2],5)) for l in cross]))).buffer(.05)
  separated=[]
  for seg in model:
   line=LineString([seg['p'],seg['q']])
   for target,shape in [(separated,line.intersection(polygon)),(support,line.difference(polygon))]:
    for piece in (list(shape.geoms) if hasattr(shape,'geoms') else [shape]):
     if piece.geom_type=='LineString' and piece.length>.001:
      item=seg.copy();item.update(p=list(piece.coords[0]),q=list(piece.coords[-1]),length=piece.length);target.append(item)
  model=separated
 support_layers.extend([idx] if support else [])
 def envelope(ss):return unary_union([LineString([s['p'],s['q']]).buffer(s['width']/2) for s in ss if .1<s['width']<1])
 now=envelope(model);supp=envelope(support)
 if idx and footprints:
  # Prior model is one layer down. A 0.2 mm support-air gap places the roof two layers down.
  old=footprints[-1]
  if len(supportprints)>1:old=unary_union([old,supportprints[-2]])
  allowed=old.buffer(a.layer)
  exposed=[]
  for s in model:
   if s['type'] not in ('WALL-OUTER','WALL-INNER'):continue
   cut=LineString([s['p'],s['q']]).difference(allowed)
   if cut.length>.05:exposed.append(dict(type=s['type'],p=s['p'],q=s['q'],length_mm=s['length'],unsupported_centerline_mm=cut.length))
  if exposed:records.append(dict(layer=idx,z=segs[0]['z'],total_exposed_centerline_mm=sum(s['unsupported_centerline_mm'] for s in exposed),max_exposed_single_segment_mm=max(s['unsupported_centerline_mm'] for s in exposed),segments=exposed))
 footprints.append(now);supportprints.append(supp)
result=dict(gcode=a.gcode.name,layers=len(layers),support_layers=len(support_layers),screen_reach_mm=a.layer,support_airgap_mm=.2,flagged_layers=len(records),worst_layers=sorted(records,key=lambda r:r['max_exposed_single_segment_mm'],reverse=True)[:12],all_flagged_layers=records,functional_mesh=a.functional_mesh.name if a.functional_mesh else None,scope='Portions of perimeter centerlines outside previous model envelope or two-layer-earlier support envelope expanded by one layer height. Flags may include intended bridges and supported-overhang flow differences; not a printability pass/fail.')
out=a.output or a.gcode.with_suffix('.paths.json');out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('worst_layers','all_flagged_layers')},indent=2));print('worst',[(r['layer'],round(r['max_exposed_single_segment_mm'],2)) for r in result['worst_layers']])
