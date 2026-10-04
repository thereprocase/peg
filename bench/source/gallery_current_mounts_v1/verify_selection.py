"""Read-only exact-byte validation for the selected gallery modeling collection."""
import argparse,ast,base64,hashlib,json
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('selection',type=Path);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);p.add_argument('--exclude',action='append',default=[]);a=p.parse_args();root=a.repo.resolve();selection=json.loads(a.selection.read_text());fail=[];done=[]
 for product in selection['products']:
  id=product['id']
  if id in a.exclude:continue
  try:
   d=json.loads((root/product['report']).read_text());out=(root/product['report']).parent
   assert d['checks']['pass'] and d['print_review']['within_machine'];assert d['print_review']['hoop_flex_out_of_layer_component']<1e-9
   for path,h in d['input_hashes'].items():assert digest(Path(path))==h,('source hash',path)
   for name,path in product['assets'].items():assert digest(root/path)==product['hashes'][name],('selected hash',path)
   native=json.loads((out/'native-checks.json').read_text());assert native['pass']
   for pose in ['installed','print']:
    assert digest(out/(pose+'.stl'))==d['checks']['mesh'][pose]['sha256'];assert digest(out/(pose+'.step'))==native[pose]['sha256']
   if 'source_normalization' in d:
    n=json.loads((root/d['source_normalization']['record']).read_text());old=base64.b64decode(n['original_execution_source_base64']);assert hashlib.sha256(old).hexdigest()==n['before_sha256'];current=(root/'bench/source/gallery_current_mounts_v1/flat_top.py').read_bytes();assert hashlib.sha256(current).hexdigest()==n['after_sha256'];assert ast.dump(ast.parse(old))==ast.dump(ast.parse(current))
   if d['version']=='current-mounts-flat-top-v2':
    assert json.loads((out/'seat-checks.json').read_text())['pass'];q=d['print_review'];assert q['forward_body_bed_contact_area_mm2']>100 and abs(q['forward_body_lowest_print_z_mm'])<1e-5 and q['body_top_to_hook_crown_clearance_mm']>.1
   done.append(id)
  except (AssertionError,KeyError,FileNotFoundError) as e:fail.append({'id':id,'error':str(e)})
 print(json.dumps({'pass':not fail,'checked':len(done),'excluded':a.exclude,'failures':fail},indent=2))
 return 2 if fail else 0
if __name__=='__main__':raise SystemExit(main())
