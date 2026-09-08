"""Measure the bore-matching faces in the exported STEP, independently of mesh."""
from pathlib import Path
import hashlib
import json
import math

import cadquery as cq

ROOT = Path(__file__).resolve().parent


def check(step=None, contract_path=None, output=None):
    step = Path(step or ROOT/'cad/conformal/conformal_120.step')
    contract_path = Path(contract_path or step.with_name(step.stem+'_geometry.json'))
    output = Path(output or step.with_name(step.stem+'_bearing_check.json'))
    g = json.loads(contract_path.read_text())
    p = g['parameters']; b = g['conformal_bearing']
    shape = cq.importers.importStep(str(step)).val()
    faces = []
    for f in shape.Faces():
        if f.geomType() != 'CYLINDER':
            continue
        cylinder = f._geomAdaptor().Cylinder()
        radius = cylinder.Radius()
        if abs(radius-b['radius_mm'])>1e-8:
            continue
        bounds = f.BoundingBox()
        length = bounds.ymax-bounds.ymin
        faces.append({'radius_mm':radius,'surface_area_mm2':f.Area(),
                      'axial_length_mm':length,
                      'angular_coverage_deg':math.degrees(f.Area()/(radius*length)),
                      'design_y_bounds_mm':[bounds.ymin,bounds.ymax],
                      'design_z_bounds_mm':[bounds.zmin,bounds.zmax]})
    faces.sort(key=lambda f:f['design_z_bounds_mm'][0],reverse=True)
    checks = []
    for land,face in zip(b['lands'],faces):
        checks.append({'land':land['name'],**face,
                       'passed':abs(face['angular_coverage_deg']-b['angle_deg'])<1e-5
                       and abs(face['axial_length_mm']-land['axial_bearing_length_mm'])<1e-6})
    report = {'passed':len(checks)==2 and all(c['passed'] for c in checks),
              'scope':'Exact exported STEP cylindrical-face radius, area and axial extent; no contact-pressure or load prediction.',
              'bearing_faces':checks,
              'source_sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in [step,contract_path,Path(__file__)]}}
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not report['passed']:
        raise ValueError('Exported bearing geometry does not match requested arc/land')
    return report


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
