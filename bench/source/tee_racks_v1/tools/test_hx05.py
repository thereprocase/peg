"""Geometry-study regression and Windows-runner failure handling; no FreeCAD claims."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
sp=importlib.util.spec_from_file_location('hx05_build',HERE/'tools/hx05_build.py')
runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner)


def study_environment():
    return {k:v for k,v in os.environ.items() if not k.startswith(('SHORT_','HX4S_')) and k!='XENV'}


def run_study(code,env):
    return subprocess.run([sys.executable,'-c',code],cwd=HERE/'study',env=env,capture_output=True,text=True,check=True,timeout=90)


class HX05Tests(unittest.TestCase):
    def test_hx04_layout_unchanged(self):
        # Compare the exact published HX04 study implementation to the edited module.
        source=subprocess.run(['git','show','2d509de:bench/source/key_fan_v1/study/short.py'],cwd=ROOT,capture_output=True,text=True,check=True,timeout=30).stdout
        env=study_environment()
        env.update(json.loads((ROOT/'bench/reviews/key-fan-v2/HX04/report.json').read_text())['build_env'])
        code='''import json, types, pathlib, numpy as np
import sys
sys.path.insert(0,OLD_STUDY)
import short as current
old=types.ModuleType('old_short');old.__file__=str(pathlib.Path('short.py').resolve())
exec(SOURCE,old.__dict__)
v=json.load(open('short_dt_c2.json'))['x']
a=old.evaluate(v,True);b=current.evaluate(v,True)
np.testing.assert_allclose(a[:3],b[:3],rtol=0,atol=1e-10)
assert a[3]==b[3] and a[4]==b[4]
assert len(a[5].tools)==len(b[5].tools)==26
for t,u in zip(a[5].tools,b[5].tools):
 assert t['name']==u['name'] and t['D']==u['D']
 for k in ('tip','mouth','u','bar' if t['set']=='tee' else 'arm','pts','rr','floor_p','floor_n'):
  np.testing.assert_allclose(t[k],u[k],rtol=0,atol=1e-10)
for x,y in zip(a[5].rails,b[5].rails):
 for p,q in zip(x,y):np.testing.assert_allclose(p,q,rtol=0,atol=1e-10)
print('published HX04 study identical')
'''
        run_study('SOURCE='+repr(source)+'\nOLD_STUDY='+repr(str(ROOT/'bench/source/key_fan_v1/study'))+'\n'+code,env)

    def test_three_layout_contracts(self):
        for part in runner.SETS:
            with self.subTest(part=part):
                env=runner.environment(part)
                code='''import json, numpy as np
import short as S
j=json.load(open(LAYOUT));_,d,h,pen,rep,lo=S.evaluate(j['x'],True)
assert max(pen.values())<1e-7,pen
assert d<=178 and j['cad_plate_height_mm']<=242
assert len(lo.tools)==len(S.TEE) and len(lo.rail_groups)==2
assert [t['name'] for t in lo.tools]==S.TEE_NAMES
assert len(set(S.TEE_NAMES))==len(S.TEE_NAMES)
for k,t in enumerate(lo.tools):assert t['D']>=4*S.TEE_SEAT_SIZE[k]-1e-9
for name,tools in lo.rail_groups:
 np.testing.assert_allclose(np.linalg.norm(np.diff([t['top'] for t in tools],axis=0),axis=1),48,rtol=0,atol=1e-8)
assert all(r['lift_pen']==0 and r['esc_pen']==0 for r in rep)
print(d,pen)
'''
                run_study('LAYOUT='+repr(env['HX4S_LAYOUT'])+'\n'+code,env)

    def test_owner_clearance_and_handle_axis(self):
        env=runner.environment('HX05B')
        self.assertEqual(env['HX4S_TBAR'],'flats')
        run_study("import short as S; assert S.TEE_HEX_C==.10; assert abs(5+2*S.TEE_HEX_C-5.20)<1e-12",env)
        spec=importlib.util.spec_from_file_location('fit_coupon',HERE/'fit_coupon_v2.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        trial=next(q for q in module.specs() if q['tool']=='T5')
        self.assertEqual(trial['bore_af_mm'],5.20)
        self.assertEqual(trial['clearance_per_flat_mm'],.10)
        self.assertAlmostEqual(trial['straight_guide_mm'],19.2)
        self.assertAlmostEqual(module.hex_play(5,.10),4.245803894404268,places=6)

    def test_child_failure_reaches_caller(self):
        with tempfile.TemporaryDirectory() as d:
            log=Path(d)/'child.log'
            with self.assertRaisesRegex(RuntimeError,'exit 7'):
                runner.command('failed check',[sys.executable,'-c',"print('failed check evidence');raise SystemExit(7)"],log,os.environ.copy(),5)
            self.assertIn('failed check evidence',log.read_text())

    def test_child_timeout_reaches_caller(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(subprocess.TimeoutExpired):
                runner.command('timeout check',[sys.executable,'-c','import time;time.sleep(10)'],Path(d)/'log',os.environ.copy(),.1)

    def test_stale_layout_rejected(self):
        original=runner.digest
        def stale(path):
            return '0'*64 if Path(path).name=='short.py' else original(path)
        with patch.object(runner,'digest',side_effect=stale):
            with self.assertRaisesRegex(RuntimeError,'stale study dependency short.py'):
                runner.environment('HX05A')

    def test_missing_freecad_is_explicit(self):
        with self.assertRaisesRegex(RuntimeError,'owner Windows machine'):
            runner.preflight(None,Path('/missing'))

if __name__=='__main__':unittest.main()
