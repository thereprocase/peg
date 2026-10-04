"""Check connector provenance, native/mesh receipts and front-page routes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,math
R=Path(__file__).resolve().parents[1];D=R/'docs'
def receipt(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def main():
 catalog=json.loads((D/'pegs/catalog.json').read_text());build=json.loads((R/'bench/reviews/peg-connectors-v1/BUILD.json').read_text());checks=json.loads((R/'bench/reviews/peg-connectors-v1/MESH-CHECKS.json').read_text());assets=json.loads((R/'publication/release-assets.json').read_text());moves=json.loads((R/'publication/release-downloads.json').read_text());additions=json.loads((R/'publication/peg-connectors-v1-additions.json').read_text())
 assert len(catalog['parts'])==len(build['parts'])==len(checks)==6
 assert set(catalog['formats'])=={'step','freecad','iges','brep','stl','obj','3mf'}
 assert build['mesh_tessellation']['native_solid_source'] and not build['mesh_tessellation']['mesh_repairs']
 for path,sha in build['source_hashes'].items():assert receipt(R/path)['sha256']==sha,path
 for part,record,check in zip(catalog['parts'],build['parts'],checks):
  assert part['id']==record['id']==check['id'];assert record['analytical_cylindrical_faces']>0
  assert check['watertight'] and check['mesh_solids']==record['solids']
  info=part['interface'];assert info['embed_mm']==2 and info['holder_plane_y_mm']==.15
  if record['solids']==1:
   assert math.isclose(info['nub_diameter_mm']/info['shaft_reference_diameter_mm'],1.2)
   assert info['board_side_symmetric_difference_mm3']<1e-7 and info['sample_union_one_solid'] and info['sample_holder_overlap_mm3']>1
  else:assert info['pitch_mm']==25.4 and info['separate_solids']==2
  assert set(part['links'])==set(catalog['formats'])
  for fmt,url in part['links'].items():
   name=unquote(url.rsplit('/',1)[-1]);assert moves['pegs/'+name]==url
   assert assets[name]==additions[name]
   if fmt in record['hashes']:assert assets[name]['sha256']==record['hashes'][fmt]
  assert receipt(D/'pegs'/part['preview'])==additions['pegs/'+part['preview']]
 for name,metadata in additions.items():
  if name.startswith('pegs/'):assert receipt(D/name)==metadata,name
  else:assert assets[name]==metadata,name
 class Links(HTMLParser):
  def handle_starttag(self,tag,attrs):
   for key,value in attrs:
    if key not in {'href','src'} or not value:continue
    u=urlsplit(value)
    if u.scheme or u.netloc or not u.path:continue
    target=self.path.parent/unquote(u.path)
    if target.is_dir():target=target/'index.html'
    assert target.is_file(),(self.path,value)
 for p in [D/'index.html',D/'anchor-study/index.html']:
  parser=Links();parser.path=p;parser.feed(p.read_text())
 root=(D/'index.html').read_text();assert root.count('<h1>')==1 and 'projects/peg/' not in root
 print(json.dumps({'peg_parts':6,'formats':7,'release_assets':sum(not k.startswith('pegs/') for k in additions),'native_geometry':True,'routes':'PASS'},indent=2))
if __name__=='__main__':main()
