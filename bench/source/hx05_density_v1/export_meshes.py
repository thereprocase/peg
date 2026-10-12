"""Retessellate the checked native print solids at the declared mesh tolerance."""
from pathlib import Path
import FreeCAD as App, Part, MeshPart
ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / '.local-runtime/hx05-density-v1'
for ident in ['HX05C', 'HX05B', 'HX05A']:
    for name in ['print-body', 'print-solid-core']:
        shape = Part.Shape()
        shape.read(str(WORK / ident / (name + '.brep')))
        assert shape.isValid()
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.025,
                                     AngularDeflection=.1, Relative=False)
        mesh.write(str(WORK / ident / (name + '-fine.stl')))
        print(ident, name, 'fine mesh exported', flush=True)
