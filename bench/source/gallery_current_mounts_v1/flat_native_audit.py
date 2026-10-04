"""Read-back STEP validity and explicit v10 legacy-interface comparison."""
from pathlib import Path
import json,hashlib,sys
import FreeCAD as A,Part
R=Path('/home/repro/code/peg-gallery-current-mounts');D=R/'bench/reviews/gallery-current-mounts-flat-top-v2'
for p in sorted(D.glob('*/report.json')):
 d=json.loads(p.read_text());out=p.parent;check={}
 if len(sys.argv)>1 and d['id'] not in sys.argv[1:]:continue
 for pose in ['installed','print']:
  q=out/(pose+'.step');s=Part.read(str(q));check[pose]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
 if d['id']=='tweezers-v10':
  old=Part.read(d['source']['input']);new=Part.read(str(out/'installed.step'));regions={'upper_hook_rear':Part.makeBox(100,40.15,22.5,A.Vector(-50,-40,-12.5)),'all_rear':Part.makeBox(100,40.15,400,A.Vector(-50,-40,-300))}
  check['legacy_v10_difference_mm3']={}
  for key,region in regions.items():
   a=old.common(region);b=new.common(region);check['legacy_v10_difference_mm3'][key]=a.cut(b).Volume+b.cut(a).Volume
 check['pass']=all(check[k]['valid'] and check[k]['solids']==1 for k in ['installed','print']);check['scope']='Basic native STEP round-trip validity, not exhaustive BOP qualification.'
 (out/'native-checks.json').write_text(json.dumps(check,indent=2)+'\n');print(out.name,check['pass'],flush=True)
