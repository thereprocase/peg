"""Check the matched-fan release scope, source receipts and public links."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
for name,row in json.loads((R/'publication/matched-fans-v1.json').read_text()).items():
 p=R/name;assert p.stat().st_size==row['bytes'],name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
D=R/'docs/gallery/key-fan/stacked/matched';review=json.loads((D/'review.json').read_text());B=R/'bench/reviews/matched-fans-v1'
assert {m['set'] for m in review['models']}=={'13189','33034'}
for name in ('access.json','sweep-check.json','pinch-check.json'):
 result=json.loads((B/name).read_text());assert result['passed']
 assert len(result.get('rows',result.get('records')))==26
layout=json.loads((B/'layout.json').read_text())
original=json.loads((R/'bench/reviews/green-fan-v1/layout.json').read_text())
assert layout['racks'][0]['tools']==original['racks'][0]['tools']
for rack in layout['racks']:
 for t in rack['tools']:assert math.degrees(math.asin(t['axis'][2]))>=10-1e-8
for m in review['models']:
 p=m['print_check'];assert p['passed'] and p['board_side_symmetric_difference_mm3']<1e-6
 assert m['edit_check']['fresh_process_reopen_and_execute_passed']
 assert m['guide_range_mm'][0]>=60
 assert all(max(c['vent_probe_overlap_mm3'],c['entrance_clearance_probe_overlap_mm3'])<1e-5 for c in p['cavity_checks'])
assets=json.loads((R/'publication/release-assets.json').read_text());links=json.loads((R/'publication/release-downloads.json').read_text())
for name,row in review['assets'].items():
 assert assets[name]==row
 assert links['key-fan/stacked/matched/'+name].endswith('/'+review['release']+'/'+name)
page=(D/'index.html').read_text()
assert 'do not lock handle rotation' in page and 'have not been sliced' in page
assert sum(p.stat().st_size for p in (R/'docs').rglob('*') if p.is_file())<1024**3
print('Matched fans: native/source receipts, unchanged green, 26 access/pinch checks, vents, edits, downloads and scope PASS')
