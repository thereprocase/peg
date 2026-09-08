"""Independent OpenCascade collision check of exported geometry and pair bridge."""
from pathlib import Path
import json
import cadquery as cq
import numpy as np
from anchor import make_anchor,pair
from render_study import load_study
ROOT=Path(__file__).resolve().parent

def make_board(p,columns=1):
    b=cq.Workplane('XY').box((columns-1)*p['pitch']+32,p['board_thickness'],62).translate(((columns-1)*p['pitch']/2,-p['board_thickness']/2,-12))
    for col in range(columns):
        for z in [0,-p['pitch']]:
            hole=cq.Solid.makeCylinder(p['hole_diameter']/2,p['board_thickness']+2,cq.Vector(col*p['pitch'],-p['board_thickness']-1,z),cq.Vector(0,1,0))
            b=b.cut(hole)
    return b

def main():
    data,p,parts,z0,poses=load_study(ROOT/'motion_results.json')
    # Ten interior samples per segment, including the bearing-contact transition.
    poses=np.vstack([a+(b-a)*u for a,b in zip(poses[:-1],poses[1:]) for u in np.linspace(0,1,11)])
    records=[]
    for cols in [1,2]:
        part=make_anchor(**p) if cols==1 else pair(p)
        board=make_board(p,cols)
        ids=np.unique(np.linspace(0,len(poses)-1,min(100,len(poses))).astype(int))
        vols=[]
        for i in ids:
            y,z,a=poses[i]
            sh=part.rotate((0,0,0),(1,0,0),float(a)).translate((0,float(y),float(z)))
            inter=sh.intersect(board)
            vols.append(sum(s.Volume() for s in inter.vals()))
        records.append({'columns':cols,'poses_checked':len(ids),'maximum_interference_mm3':max(vols),'pass':max(vols)<1e-7})
        if cols==1:
            cq.exporters.export(board,str(ROOT/'cad/reference_board.step'))
    (ROOT/'occ_motion_check.json').write_text(json.dumps(records,indent=2))
    print(json.dumps(records,indent=2))
    assert all(r['pass'] for r in records),'CAD motion interference found'
if __name__=='__main__':main()
