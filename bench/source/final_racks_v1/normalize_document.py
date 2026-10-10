"""Save a stable one-feature FreeCAD document from the delivered STEP solid."""
from pathlib import Path
import argparse,json,hashlib
import FreeCAD as A,Part

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args();out=a.out
 s=Part.Shape();s.read(str(out/'installed.step'));assert s.isValid() and len(s.Solids)==1
 doc=A.newDocument('FinalRackNative');obj=doc.addObject('Part::Feature','Holder');obj.Label='Final straight-socket rack';obj.Shape=s;doc.recompute();doc.saveAs(str(out/'model.FCStd'));A.closeDocument(doc.Name)
 doc=A.openDocument(str(out/'model.FCStd'));print('Native document objects',len(doc.Objects),[(o.Name,o.Shape.isValid()) for o in doc.Objects],flush=True);assert len(doc.Objects)==1 and doc.Objects[0].Shape.isValid()
 read=doc.Objects[0].Shape
 assert (len(read.Faces),len(read.Edges),len(read.Vertexes))==(len(s.Faces),len(s.Edges),len(s.Vertexes))
 left=sorted(tuple(v.Point) for v in s.Vertexes);right=sorted(tuple(v.Point) for v in read.Vertexes)
 vertex_delta=max(abs(a-b) for p,q in zip(left,right) for a,b in zip(p,q));assert vertex_delta<1e-6
 volume_delta=abs(read.Volume-s.Volume);area_delta=abs(read.Area-s.Area);assert volume_delta/max(s.Volume,1)<1e-8 and area_delta/max(s.Area,1)<1e-8
 A.closeDocument(doc.Name)
 (out/'document-roundtrip.json').write_text(json.dumps(dict(valid=True,solid_count=1,max_vertex_difference_mm=vertex_delta,volume_difference_mm3=volume_delta,area_difference_mm2=area_delta,topology_counts_equal=True,step_sha256=hashlib.sha256((out/'installed.step').read_bytes()).hexdigest(),fcstd_sha256=hashlib.sha256((out/'model.FCStd').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print('Native FreeCAD roundtrip PASS',flush=True)
if __name__=='__main__':main()
