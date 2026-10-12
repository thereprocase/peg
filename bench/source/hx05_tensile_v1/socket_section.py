"""Isolated straight-sleeve direct-tension calculation, not whole-rack FOS.

Use only the 1.2 mm solid socket band. No sparse bulk or surrounding wall
material is credited. Axial load, uniform net-section stress, no concentration,
bending, attachment or layer-interface model is implied by this calculation.
"""
from pathlib import Path
import json, math, hashlib

def section_area(opening, thickness, round_socket=False):
    factor=math.pi/4 if round_socket else math.sqrt(3)/2
    return factor*((opening+2*thickness)**2-opening**2)

def main():
    root=Path(__file__).resolve().parents[3]
    source=root/'bench/source/hx05_anisotropy_v1/config.json'
    cfg=json.loads(source.read_text()); out=[]
    for rack in cfg['racks']:
        tools=[]
        for tool in rack['tools']:
            opening=tool.get('af',tool.get('p2p'))+.38
            area=section_area(opening,1.2,rack['id']=='HX05A')
            stress=100/area
            tools.append(dict(tool=tool['name'],opening_mm=opening,solid_band_mm=1.2,area_mm2=area,axial_force_N=100,nominal_tensile_MPa=stress,reference_30MPa_factor=30/stress,assumed_15MPa_factor=15/stress))
        out.append(dict(id=rack['id'],tools=tools,minimum_reference_factor=min(t['reference_30MPa_factor'] for t in tools),minimum_assumed_factor=min(t['assumed_15MPa_factor'] for t in tools)))
    result=dict(scope='Uniform axial tensile stress in an isolated intact straight-sleeve band only. Not a whole-holder factor of safety; load sharing, stress concentration, bending, torsion, vents, lead-in, roots, pegs and installation stress omitted.',geometry_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),material_reference_url='https://polymaker.com/product/polylite-asa',reference_strength_MPa=30,assumed_derated_strength_MPa=15,derating_is_unmeasured_sensitivity=True,racks=out)
    target=root/'bench/reviews/hx05-tensile-v1/socket-axial-section.json'; target.write_text(json.dumps(result,indent=2)+'\n')
    print(target)

if __name__=='__main__':
    assert abs(section_area(4,1)-10*math.sqrt(3))<1e-12
    assert abs(section_area(4,1,True)-5*math.pi)<1e-12
    main()
