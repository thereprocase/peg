"""v9 tool mating == v8: identical solid left of X=0.5 in front of the board,
and every reference tool (rest and lift-then-left path) stays left of all new
material. Run with FreeCAD's Python: mating_check.py <v9-build> <v8-regen>"""
import sys, json
from pathlib import Path
import FreeCAD as A, Part, Mesh
V = A.Vector
v9, v8 = Path(sys.argv[1]), Path(sys.argv[2])
P8 = 'part-solder-modules-tweezers__v8__long-body-cradle__fit-e586ab4ff6'
N9 = 'part-solder-modules-tweezers__v9__cheek-cradle__fit-pf02c9-latch'
a = Part.read(str(v8/f'{P8}__installed.step')); b = Part.read(str(v9/f'{N9}__installed.step'))
region = Part.makeBox(120, 300, 400, V(-119.5, 0.15, -300))      # X <= 0.5, in front of the board face
ra, rb = a.common(region), b.common(region)
diff = ra.cut(rb).Volume+rb.cut(ra).Volume
new = b.cut(a)                                                   # everything v9 added
new_front = new.common(Part.makeBox(200, 300, 400, V(-100, 0.15, -300)))
real = [so for so in new_front.Solids if so.Volume > 1e-6]      # ignore zero-volume Boolean slivers
xmin_new = min(so.BoundBox.XMin for so in real)
tools_xmax = max(Mesh.Mesh(str(v8/f'{P8}__reference-tool-{i+1}.stl')).BoundBox.XMax for i in range(4))
gap = xmin_new-tools_xmax      # removal moves only +Z then -X, so this gap never shrinks
r = dict(symmetric_difference_left_of_x0p5_mm3=diff, new_material_min_x_mm=xmin_new,
         tools_max_x_at_rest_mm=tools_xmax, min_clearance_tool_to_new_material_mm=gap,
         passed=diff < 1e-6 and gap > 0)
(v9/'mating-check.json').write_text(json.dumps(r, indent=2)+'\n'); print(json.dumps(r))
