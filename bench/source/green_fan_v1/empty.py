"""Render mesh of the checked native green holder without reference tools."""
from pathlib import Path
import sys,importlib.util
source=Path(__file__).resolve().parent.parent/'stacked_fans_v1'/'build.py'
sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('hx05_native_helpers',source)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
body=h.Part.Shape();body.read(str(Path(sys.argv[1])/'HX05C/body.brep'))
scene=h.trimesh.Scene();h.add(scene,body,[50,146,133,255],'holder');h.write(scene,'HX05C-empty')
