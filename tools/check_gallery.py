"""Check gallery local links, curation, release maps and unchanged CAD/media."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,posixpath
R=Path(__file__).resolve().parents[1];D=R/'docs/gallery'
source=json.loads((R/'publication/gallery-source-manifest.json').read_text())['files'];moves=json.loads((R/'publication/release-downloads.json').read_text());assets=json.loads((R/'publication/release-assets.json').read_text());errors=[];links=0
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  global links
  for k,v in attrs:
   if k not in {'href','src','data-src','data-model','poster'} or not v:continue
   u=urlsplit(v)
   if u.scheme or u.netloc or not u.path:continue
   links+=1
   if u.path.startswith('/peg/'):target=R/'docs'/unquote(u.path[len('/peg/'):])
   elif u.path.startswith('/'):errors.append((self.name,v,'root-relative'));continue
   else:target=self.path.parent/unquote(u.path)
   if target.is_dir():target=target/'index.html'
   if not target.exists():errors.append((self.name,v,'missing'))
for p in D.rglob('*.html'):
 parser=Links();parser.name=p.relative_to(D).as_posix();parser.path=p;parser.feed(p.read_text(encoding='utf-8'))
for n,v in source.items():
 if n in moves:
  a=assets[moves[n].split('/')[-1]];assert a==v,(n,a,v)
 elif Path(n).suffix not in {'.html'}:assert hashlib.sha256((D/n).read_bytes()).hexdigest()==v['sha256'],n
assert (D/'index.html').read_text(encoding='utf-8').count('<article>')==4
assert '1 mm nominal clearance' in (D/'shaft-sampler/index.html').read_text(encoding='utf-8')
additions=R/'publication/ms01-v3-recoverable-additions.json'
if additions.exists():
 for n,v in json.loads(additions.read_text()).items():
  route='shaft-sampler/recoverable/'+n
  if route in moves:assert assets[moves[route].split('/')[-1]]==v,route
  else:assert hashlib.sha256((D/route).read_bytes()).hexdigest()==v['sha256'],route
 assert 'No pause, no permanent cap' in (D/'shaft-sampler/recoverable/index.html').read_text(encoding='utf-8')
additions=R/'publication/mh01-mh04-shaft-holders-v1-additions.json'
if additions.exists():
 for n,v in json.loads(additions.read_text()).items():
  route='shaft-holders/'+n
  if route in moves:assert assets[moves[route].split('/')[-1]]==v,route
  else:assert hashlib.sha256((D/route).read_bytes()).hexdigest()==v['sha256'],route
 assert 'Not sliced, not printed' in (D/'shaft-holders/index.html').read_text(encoding='utf-8')
assert len(list(D.rglob('*.sqlite*')))==0
report={'source_files':len(source),'release_assets':len(assets),'html_links':links,'errors':errors,'site_bytes':sum(p.stat().st_size for p in (R/'docs').rglob('*') if p.is_file())}
print(json.dumps(report,indent=2));assert not errors
