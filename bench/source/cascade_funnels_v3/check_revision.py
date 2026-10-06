"""Measure the removed side fins against the immutable CF01 v2 STEP."""
from pathlib import Path
import json,hashlib
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[3];D=R/'bench/reviews/cascade-funnels-v3/CF01';old=R/'bench/reviews/cascade-funnels-v2/CF01'
r=json.loads((D/'report.json').read_text());prior=json.loads((old/'report.json').read_text())
a=old/prior['assets']['installed_step'];b=D/r['assets']['installed_step'];before=Part.read(str(a));after=Part.read(str(b))
removed=before.cut(after).Volume;added=after.cut(before).Volume
assert 1000<removed<65000 and added<1e-5,(removed,added)
# At the common tube bases, the two 6 mm gaps must be clear through the web depth.
# The old 30 mm webs bridged both of these spaces into projecting fins.
boxes=[Part.makeBox(5.8,24,20,A.Vector(x,5.6,-114.7)) for x in [-15.4,9.6]]
remaining=[after.common(q).Volume for q in boxes];previous=[before.common(q).Volume for q in boxes]
assert max(remaining)<1e-5 and min(previous)>1000,(remaining,previous)
record=dict(passed=True,removed_volume_mm3=removed,added_volume_mm3=added,web_width_before_mm=30,web_width_after_mm=18,lower_gap_probe_volumes_mm3=remaining,previous_gap_probe_volumes_mm3=previous,inputs={'previous_step':hashlib.sha256(a.read_bytes()).hexdigest(),'installed_step':hashlib.sha256(b.read_bytes()).hexdigest()},previous_release='https://github.com/thereprocase/peg/releases/tag/cascade-funnels-v2-2026-10-06')
(D/'fin-removal.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
