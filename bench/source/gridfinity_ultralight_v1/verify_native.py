"""Reopen exported native solids and check roots, bin withdrawal and fit-ring crop."""
from pathlib import Path
import json
import sys
import FreeCAD as A
import Part
import MeshPart

root=Path(sys.argv[1]);V=A.Vector
report=[]
for n,cells in [(1,2),(2,4)]:
    name=f'GF{n}1-v1-shelf-pf02c9-hoop5'
    shelf=Part.read(str(root/(name+'-installed.step')))
    if n==2:
        core=Part.makeBox(76.2,1.9,10,V(-38.1,49.65,-4.28))
        missing=core.cut(shelf).Volume
        assert missing<1e-6,('front beam continuity',missing)
        (root/'BEAM-CONTINUITY.json').write_text(json.dumps({'bounds_mm':[[-38.1,49.65,-4.28],[38.1,51.55,5.72]],'expected_core_volume_mm3':core.Volume,'missing_volume_mm3':missing,'pass':True},indent=2)+'\n')
    binshape=Part.read(str(root/(name+'-reference-bin.step')))
    columns=[-(cells-1)*25.4/2,(cells-1)*25.4/2]
    roots=[]
    for x in columns:
        for z,diam in [(.12,6.72),(-25.28,7.62)]:
            full=Part.makeBox(diam,5.4,diam,V(x-diam/2,.15,z-diam/2))
            missing=full.cut(shelf).Volume
            assert missing<1e-6,(n,x,z,missing)
            roots.append({'x':x,'z':z,'full_wall_depth_mm':5.4,'nub_diameter_mm':diam,'missing_volume_mm3':missing})
    overlaps=[]
    for dz in [0,.01,.05,.1,.2,.5,1,2,3,4,5,7,10]:
        b=binshape.copy();b.translate(V(0,0,dz));overlap=b.common(shelf).Volume
        assert overlap<1e-6,(n,dz,overlap)
        overlaps.append({'lift_mm':dz,'overlap_mm3':overlap})
    report.append({'name':name,'roots':roots,'sampled_vertical_bin_withdrawal':overlaps})
    if n==1:
        ring=shelf.common(Part.makeBox(46,46,5,V(-23,5.55,.72))).removeSplitter()
        assert ring.isValid() and len(ring.Solids)==1
        ring.rotate(V(0,0,0),V(1,0,0),180)
        ring.translate(V(0,0,-ring.BoundBox.ZMin))
        ring.exportStep(str(root/'GF11-v1-seat-fit-ring-print-inverted.step'))
        mesh=MeshPart.meshFromShape(Shape=ring,LinearDeflection=.005,AngularDeflection=.087,Relative=False)
        mesh.write(str(root/'GF11-v1-seat-fit-ring-print-inverted.stl'))
(root/'NATIVE-REOPEN-CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print('Root blocks and sampled vertical withdrawal pass; isolated seat-fit ring exported')
