"""Nominal bending stress in each key's own two dense root ribs.

Use the connected-v3 hull construction and exact polygon section integrals.
This is an idealized beam load allocation, not a complete-holder FOS: surrounding
skins, adjacent helpers and bulk are omitted; plane-section compatibility is
assumed, and torsion/local contact/stress concentrations are not assessed.
"""
from pathlib import Path
import json, numpy as np
from scipy.spatial import ConvexHull

def hulls(tool,rack):
    u=np.array(tool['axis']);tip=np.array(tool['tip']);mouth=np.array(tool['mouth']);bar=np.array(tool['bar_axis'])
    rad=np.array([0.,0.,1.])-u*u[2];rad/=np.linalg.norm(rad)
    size=tool.get('af',tool.get('p2p'))+.38
    radius=size/2+.6
    if rack['id']!='HX05A':
        normals=np.array([bar*np.cos(k*np.pi/3)+np.cross(u,bar)*np.sin(k*np.pi/3) for k in range(6)])
        radius/=max(normals@rad)
    parts=[]
    for sign in [-1,1]:
        pts=[]
        for q in [tip-u*3,mouth-u*3]:
            shell=q+rad*sign*radius; rz=np.clip(shell[2]+sign*4,rack['parameters']['PlateBottom']+1.5,-1.5)
            root=np.array([shell[0],.8,rz])
            for sx in [-1,1]:
                for sz in [-1,1]:
                    pts.extend([shell+[sx*.6,0,sz*.6],root+[sx*.6,0,sz*1.25]])
        parts.append(np.asarray(pts))
    return parts

def section(points,y):
    h=ConvexHull(points);edges=set(tuple(sorted((int(a),int(b)))) for f in h.simplices for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]);cuts=[]
    for a,b in edges:
        p,q=points[a],points[b]
        if (p[1]-y)*(q[1]-y)<=0 and abs(q[1]-p[1])>1e-12:
            v=p+(q-p)*(y-p[1])/(q[1]-p[1]);cuts.append(v[[0,2]])
    c=np.unique(np.round(cuts,10),axis=0);return c[ConvexHull(c).vertices]

def clip(poly,bound):
    result=poly.copy()
    for a,b in zip(bound,np.roll(bound,-1,axis=0)):
        points=[];n=np.array([-(b-a)[1],(b-a)[0]])
        for p,q in zip(result,np.roll(result,-1,axis=0)):
            dp=(p-a)@n;dq=(q-a)@n
            if dp>=-1e-10:points.append(p)
            if (dp>=0)!=(dq>=0):points.append(p+(q-p)*dp/(dp-dq))
        if len(points)<3:return np.empty((0,2))
        result=np.asarray(points)
    return result

def moments(p):
    if len(p)<3:return np.zeros(6)
    q=np.roll(p,-1,axis=0);x,z=p.T;X,Z=q.T;c=x*Z-X*z
    return np.array([c.sum()/2,((x+X)*c).sum()/6,((z+Z)*c).sum()/6,((x*x+x*X+X*X)*c).sum()/12,((z*z+z*Z+Z*Z)*c).sum()/12,((2*x*z+x*Z+X*z+2*X*Z)*c).sum()/24])

def stress(polys,force,grip,y):
    a,b=polys; m=moments(a)+moments(b)-moments(clip(a,b));A=m[0];cent=m[1:3]/A
    Q=np.array([[m[3],m[5]],[m[5],m[4]]])-A*np.outer(cent,cent)
    F=np.asarray(force);g=np.asarray(grip);point=np.array([cent[0],y,cent[1]]);M=np.cross(g-point,F)
    slope=np.linalg.solve(Q,np.array([M[2],-M[0]]));sigma=F[1]/A+(np.vstack(polys)-cent)@slope
    assert np.linalg.norm(Q@slope-np.array([M[2],-M[0]]))<1e-5,'Section bending equilibrium'
    return dict(area_mm2=float(A),centroid_xz_mm=cent.tolist(),normal_tension_gradient_xz_MPa_per_mm=slope.tolist(),normal_mean_stress_MPa=float(F[1]/A),nominal_peak_normal_tension_MPa=float(max(0,sigma.max())),nominal_peak_compression_MPa=float(max(0,-sigma.min())),section_moment_Nmm=M.tolist(),unassessed_torsion_Nm=float(abs(M[1])/1000),average_interlayer_shear_MPa=float(abs(F[0])/A),average_inplane_shear_MPa=float(abs(F[2])/A),nominal_15MPa_bending_margin=float(15/max(sigma.max(),1e-20)))

def main():
    root=Path(__file__).resolve().parents[3];cfg=json.loads((root/'bench/source/hx05_anisotropy_v1/config.json').read_text());out=[]
    for rack in cfg['racks']:
        cases=[]
        for tool in rack['tools']:
            parts=hulls(tool,rack)
            for y in [1.3,2,3,4,5]:
                polys=[section(p,y) for p in parts]
                for name,F in [('down20N',[0,0,-25]),('across_layers20N',[20,0,-5]),('outboard20N',[0,20,-5])]:
                    result=stress(polys,F,tool['top'],y);cases.append(dict(tool=tool['name'],plane_y_mm=y,case=name,**result))
        out.append(dict(id=rack['id'],cases=cases));worst=max(cases,key=lambda c:c['nominal_peak_normal_tension_MPa']);print(rack['id'],worst)
    record=dict(scope='Idealized own-two-dense-root-ribs beam section screen. 20 N directional force plus 5 N own-key downward weight. Connected-v3 analytic hulls, 1.3-5 mm front-of-board sections. No surrounding skins/other dense masks/bulk credited. Plane-section compatibility assumed. Torsion, local contact, root stress concentrations, pegs, buckling and true interlayer stresses unassessed. Not a complete-holder safety factor or a guaranteed conservative bound.',racks=out)
    (root/'bench/reviews/hx05-tensile-v1/rib-bending-sections.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':
    p=np.array([[0.,0.],[2,0],[2,4],[0,4]])
    assert np.allclose(moments(p),[8,8,16,32/3,128/3,16])
    assert abs(moments(clip(p,p))[0]-8)<1e-10
    # Two 1x4 bars centered at x=-2,+2 have Qxx = 2*(4/12+4*4).
    polys=[np.array([[-2.5,-2],[-1.5,-2],[-1.5,2],[-2.5,2]]),np.array([[1.5,-2],[2.5,-2],[2.5,2],[1.5,2]])]
    q=stress(polys,[1,0,0],[0,10,0],0)
    assert abs(q['nominal_peak_normal_tension_MPa']-25/(2*(4/12+16)))<1e-10
    main()
