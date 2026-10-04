"""Read-only exact-STEP check of the aligned guide/front-floor termination planes.

This addresses the former 0.187 mm recessed guide end/triangular ledge; it is
not a general aesthetic or minimum-wall-thickness certificate.
"""
from pathlib import Path
import argparse,json,math,hashlib
import FreeCAD as A
import Part

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);d=p.parse_args().build.resolve();c=json.loads((d/'candidate.json').read_text())['cases'][0]
    bodypath=d/f"{c['name']}__installed.step";body=Part.read(str(bodypath));u=A.Vector(0,math.cos(math.radians(20)),math.sin(math.radians(20)))
    rows=[];files=[d/'candidate.json',bodypath,Path(__file__)]
    for k in range(4):
        gp=d/f'guide-{k+1}.step';g=Part.read(str(gp));files.append(gp)
        target=c['guide']['U_band_mm'][1]-u.z*c['tray_pitch_vertical_mm']*k
        guide_end=max(u.dot(v.Point) for v in g.Vertexes)
        faces=[]
        for f in body.Faces:
            if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).dot(u)>.999999:
                here=u.dot(f.CenterOfMass)
                if abs(here-target)<1e-7:faces.append(dict(area_mm2=f.Area,centre_mm=list(f.CenterOfMass),plane_offset_mm=here-target))
        row=dict(station=k+1,guide_end_U_mm=guide_end,target_front_plane_U_mm=target,guide_end_offset_mm=guide_end-target,
            matching_body_front_faces=faces,lower_guide_joins_preceding_floor=k>0,passed=abs(guide_end-target)<1e-7 and bool(faces))
        rows.append(row)
    report=dict(passed=all(r['passed'] for r in rows),method=__doc__,stations=rows,
        earlier_fixed_U_end_mm=134.0,selected_top_guide_U_end_mm=c['guide']['U_band_mm'][1],
        former_step_removed_mm=c['guide']['U_band_mm'][1]-134.0,inputs={str(f):sha(f) for f in files},
        limits=['Exact coplanar termination proves removal of this offset ledge; inspect complete-body render for remaining joins','Peg seams and receiving geometry have separate generator comparisons'])
    (d/'guide-junctions.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
