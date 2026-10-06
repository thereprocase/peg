"""Verify physical overlap of adjoining funnel shells and the cascade direction."""
from pathlib import Path
import sys,json
import FreeCAD
import Part
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
import importlib.util
module=importlib.util.spec_from_file_location('cascade_build',Path(__file__).with_name('build.py'))
C=importlib.util.module_from_spec(module);module.loader.exec_module(C)
original=C.B.union;captured={}
def capture(items):
    if len(items)==7:captured['outer']=[items[i] for i in [1,3,5]]
    if len(items)==9:captured['void']=original(items)
    return original(items)
C.B.union=capture
shape,receiver,info,tools,spec=C.cascade()
shells=[s.cut(captured['void']) for s in captured['outer']]
joints=[shells[i].common(shells[i+1]).Volume for i in range(2)]
assert all(v>1e-5 for v in joints),joints
seats=spec['tool_spec']['seats']
assert [s['position'] for s in seats]==['right','middle','left']
assert seats[0]['mouth_z_mm']>seats[1]['mouth_z_mm']>seats[2]['mouth_z_mm']
record=dict(passed=True,adjacent_funnel_overlap_mm3=joints,centres_mm=25,height_steps_mm=25.4,order='right highest, middle, left lowest',source_sha256=C.B.sha(Path(C.__file__)))
(R/'bench/reviews/cascade-funnels-v2/CF01/junctions.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
