"""Broad printable stock and additive root blends, ahead of bore/vent cuts."""
import math
import numpy as np
import FreeCAD as A,Part

def make_stock(ts,half,bottom,ring,hull,v):
    # A constant rounded bed-plane section gives a large flat X-min face.
    # All subsequent entrance-plane clips have positive X normals, so the
    # stock's outer section can only shrink as printing advances along +X.
    front=max(float(np.max(ring(np.array(t['mouth']),np.array(t['axis']),t['outer_radius'])[:,1])) for t in ts)
    y0=5.;stock=Part.makeBox(2*half,front-y0,-bottom,A.Vector(-half,y0,bottom))
    edges=[e for e in stock.Edges if e.BoundBox.XLength>2*half-.01]
    stock=stock.makeFillet(8.,edges)
    for t in ts:
        u,b,m=map(np.array,(t['axis'],t['bar_axis'],t['mouth']));side=np.cross(u,b)
        assert u[0]>0
        # Keep the stock face 0.05 mm below the sleeve cap to avoid
        # coincident Boolean/tessellation surfaces at the lowest entrance.
        cap=m-u*.05
        pts=[v(cap+1000*(sx*b+sy*side)) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        cut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(v(u*2000))
        stock=stock.cut(cut).removeSplitter()
    assert stock.isValid() and len(stock.Solids)==1
    record=dict(recipe='rounded solid tip stock clipped below every entrance plane',print_direction=[1,0,0],bed_plane_x_mm=-half,bed_plane_corner_radius_mm=8.,uncut_stock_volume_mm3=stock.Volume,stock_front_y_mm=front,all_entrance_normals_positive_x=True,vent_direction='toward front, perpendicular to each shaft; extended through added stock')
    print('Strength stock',record,flush=True)
    return stock,record

def blend_roots(body,half):
    # Only host-front junctions; board-side peg geometry is never selected.
    edges=[e for e in body.Edges if e.Length>15 and abs(e.BoundBox.YMin-5.55)<.002 and abs(e.BoundBox.YMax-5.55)<.002 and e.BoundBox.XMin>-half+8 and e.BoundBox.XMax<half-8 and e.BoundBox.ZMax<.001]
    log=dict(requested_radius_mm=6.,candidate_edges=len(edges),applied_edges=0)
    if edges:
        try:
            out=body.makeFillet(6.,edges)
            if out.isValid() and len(out.Solids)==1:
                log['applied_edges']=len(edges);print('Root blends',log,flush=True);return out.removeSplitter(),log
        except Part.OCCError:pass
        # One bounded fallback at the longest root. No radius search campaign.
        try:
            out=body.makeFillet(6.,[max(edges,key=lambda e:e.Length)])
            if out.isValid() and len(out.Solids)==1:
                log['applied_edges']=1;print('Root blends',log,flush=True);return out.removeSplitter(),log
        except Part.OCCError:pass
    print('Root blends',log,flush=True)
    return body,log


def fin_gusset(t,half,bottom,ring,hull,v):
    """Broaden each fin in the bed plane and extend its root toward the bed."""
    p,u,b,m=map(np.array,(t['tip'],t['axis'],t['bar_axis'],t['mouth']))
    ends=np.vstack([ring(p-u*3,u,t['outer_radius']),ring(m,u,t['outer_radius'])])
    root=ends.copy();root[:,1]=5.;root[:,0]-=16.
    left=root.copy();right=root.copy();left[:,2]-=12.;right[:,2]+=12.
    gusset=hull(np.vstack([ends,left,right]))
    side=np.cross(u,b)
    cap=m-u*.10
    pts=[v(cap+1000*(sx*b+sy*side)) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    beyond=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(v(u*2000))
    envelope=Part.makeBox(2*half,1000.,-bottom,A.Vector(-half,5.,bottom))
    gusset=gusset.common(envelope).cut(beyond).removeSplitter()
    assert gusset.isValid() and len(gusset.Solids)==1
    return gusset
