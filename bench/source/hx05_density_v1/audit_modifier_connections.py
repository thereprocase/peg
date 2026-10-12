from pathlib import Path
import sys,json,os
ROOT=Path(__file__).resolve().parents[3];WORK=Path(os.environ.get('HX05_BUILD_DIR',str(ROOT/'.local-runtime/hx05-connected-v3')))
sys.path[:0]=[str(ROOT/'bench/source/hx05_density_v1'),str(ROOT/'bench/source/matched_fans_v1'),str(ROOT/'bench/source/hx05_parametric_v1')]
import FreeCAD as A,Part
import hx05_density as H,hx05_family,hx05_parametric
ident=sys.argv[1];doc=A.openDocument(str(next((WORK/ident).glob('*_density_v1.FCStd'))));body=doc.DraftedHolder.Shape;p=doc.DensityParameters;rows=[]
for key in doc.DenseRibs.Keys:
 objects=[]
 for role in ['Ribs','Sockets']:
  obj=doc.addObject('Part::FeaturePython','Audit'+role)
  for kind,name in [('App::PropertyString','DensityRole'),('App::PropertyLink','DensityParameters'),('App::PropertyLink','Holder'),('App::PropertyLinkList','Keys')]:obj.addProperty(kind,name)
  obj.DensityRole=role;obj.DensityParameters=p;obj.Holder=doc.DraftedHolder;obj.Keys=[key];H.DensityZone(obj);obj.Proxy.build(obj);objects.append(obj)
 rib,socket=[o.Shape.common(body) for o in objects];tip,axis,bar,mouth=H.frame(key);length=(mouth-tip).Length
 row=dict(tool=key.Label,stations=[])
 for fraction in [.15,.5,.85]:
  slab=Part.makeCylinder(1000,1.,tip+axis*(length*fraction-.5),axis)
  a=rib.common(slab);b=socket.common(slab)
  distance=None if a.isNull() or b.isNull() or a.Volume<1e-7 or b.Volume<1e-7 else a.distToShape(b)[0]
  overlap=0. if distance is None else a.common(b).Volume
  row['stations'].append(dict(fraction=fraction,gap_mm=distance,overlap_mm3=overlap))
 rows.append(row);print(row,flush=True)
 for o in objects:doc.removeObject(o.Name)
(WORK/ident/'modifier-connectivity-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
