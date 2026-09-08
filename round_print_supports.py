"""Parametric removable cradles for the true-round anchor. Functional CAD stays intact.

Side cradles support the negative-X hemisphere. Upright cradles use two ramp
webs each, rooted into the spine; cut those roots, then lift off the cradle.
A vertical 0.20 mm air gap separates every cradle from the round bearing.
Inspect the sliced interface; a geometric gap is not a physical tolerance test.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
from round_anchor import geometry,make_round_anchor,print_pose
ROOT=Path(__file__).resolve().parent
SUPPORT_DEFAULTS=dict(interface_gap=.20,web_thickness=.50,cradle_floor=.60,
                     support_half_angle_deg=45.,root_embed=.25,side_root_gap=.20,bed_relief_width=.12,side_lift=.40)


def extrude_yz(poly,x0,width):
    if poly.geom_type!='Polygon':raise ValueError('Expected one cradle profile')
    return cq.Workplane('YZ',origin=(x0,0,0)).polyline(list(poly.exterior.coords[:-1])).close().extrude(width)


def lower_at(poly,y):
    cut=poly.intersection(LineString([(y,-1000),(y,1000)]))
    if cut.is_empty:raise ValueError('No projected section')
    return cut.bounds[1]


def support_radii(g):
    upper=g['upper_capsule'];radii=upper.get('segment_radii',[upper['radius']]*2)
    if max(radii)-min(radii)<1e-8:return {'upper':radii[0],'lower':g['locator']['radius']}
    return {'upper_neck':radii[0],'upper_tongue':radii[1],'lower':g['locator']['radius']}


def projections(g,radius_scale=1.):
    upper=g['upper_capsule'];centers=upper['centers_xyz'];radii=support_radii(g);result={}
    if 'upper' in radii:
        result['upper']=LineString([(p[1],p[2]) for p in centers]).buffer(radii['upper']*radius_scale,quad_segs=48)
    else:
        # Separate exact segment capsules preserve the small tongue radius and
        # the large spherical junction owned by the neck capsule. Final CAD
        # subtraction below uses the complete exact variable-radius shape.
        for name,pair in [('upper_neck',centers[:2]),('upper_tongue',centers[1:])]:
            result[name]=LineString([(p[1],p[2]) for p in pair]).buffer(radii[name]*radius_scale,quad_segs=48)
    loc=g['locator'];lr=loc['radius']*radius_scale
    result['lower']=box(loc['tip_y'],loc['center_z']-lr,loc['root_y'],loc['center_z']+lr)
    return result


def support_parts(params=None,support_params=None,orientation='side'):
    g=geometry(params);p=g['parameters'];s=SUPPORT_DEFAULTS|(support_params or {})
    if not 0<s['interface_gap']<.5:raise ValueError('Use a positive, sub-0.5 mm interface gap')
    if not 0<s['web_thickness']<1.5:raise ValueError('Invalid support web thickness')
    clean=make_round_anchor(**p);parts=[]
    factor=math.sin(math.radians(s['support_half_angle_deg']))
    narrow=projections(g,factor);full=projections(g)
    if orientation=='side':
        # Build direction +X. Keep these cradles entirely on the side-facing
        # hemisphere, away from the installed gravity-bearing bottom crown.
        shifted=clean.translate((-s['interface_gap'],0,0))
        bed_x=g['spine']['x_min']-s['side_lift']
        for name,projection in narrow.items():
            radius=support_radii(g)[name]
            footprint=projection.intersection(box(-1000,-1000,p['front_gap']-s['side_root_gap'],1000))
            top_x=-radius*math.cos(math.radians(s['support_half_angle_deg']))
            if top_x<=bed_x:raise ValueError('Spine too narrow for this side cradle')
            cradle=extrude_yz(footprint,bed_x,top_x-bed_x).cut(shifted)
            if radius+s['interface_gap']>=-bed_x-1e-7:
                # Avoid a zero-thickness bed tangency where two cradle wings
                # meet. Relieve only sacrificial material along that line.
                c=g['upper_capsule']['centers_xyz']
                if name=='lower':
                    loc=g['locator'];line=LineString([(loc['tip_y'],loc['center_z']),(loc['root_y'],loc['center_z'])])
                else:
                    points=c if name=='upper' else (c[:2] if name=='upper_neck' else c[1:])
                    line=LineString([(v[1],v[2]) for v in points])
                relief=line.buffer(s['bed_relief_width']/2,quad_segs=12)
                cradle=cradle.cut(extrude_yz(relief,bed_x-.05,top_x-bed_x+.1))
            parts.append((f'{name}_side_cradle',cradle))
        # A shallow sacrificial pad lifts the spine too, leaving enough room
        # for a real one-layer air interface below the nearest round surface.
        spine=g['spine'];profile=box(spine['y_min'],spine['z_min'],spine['y_max'],spine['z_max'])
        corner=spine['yz_corner_radius']
        if corner:profile=profile.buffer(-corner,quad_segs=12).buffer(corner,quad_segs=12)
        pad_height=s['side_lift']-s['interface_gap']
        if pad_height<=0:raise ValueError('Side lift must exceed interface gap')
        parts.append(('spine_lift_pad',extrude_yz(profile,bed_x,pad_height)))
        # A narrow tongue cradle can overlap the larger neck's bed tangency.
        # Apply all tangent-line reliefs to every side support, not only its
        # own primitive, to prevent shared zero-thickness mesh edges.
        c=g['upper_capsule']['centers_xyz'];near_bed=[]
        for a,b,r in zip(c[:-1],c[1:],g['upper_capsule'].get('segment_radii',[g['upper_capsule']['radius']]*2)):
            if r+s['interface_gap']>=-bed_x-1e-7:near_bed.append(LineString([(a[1],a[2]),(b[1],b[2])]))
        loc=g['locator']
        if loc['radius']+s['interface_gap']>=-bed_x-1e-7:near_bed.append(LineString([(loc['tip_y'],loc['center_z']),(loc['root_y'],loc['center_z'])]))
        for line in near_bed:
            relief=extrude_yz(line.buffer(s['bed_relief_width']/2,quad_segs=12),bed_x-.05,-bed_x+.1)
            parts=[(label,part.cut(relief)) for label,part in parts]
    elif orientation=='upright':
        shifted=clean.translate((0,0,-s['interface_gap']))
        # Keep spine-root attachment, but subtract round-body material from
        # ramp webs too when a large neck sphere overlaps a smaller tongue.
        front_clip=cq.Workplane('XY').box(100,100,200).translate((0,p['front_gap']-50,-50))
        round_only_shifted=shifted.intersect(front_clip)
        for name,projection in narrow.items():
            radius=support_radii(g)[name]
            half=radius*factor;rear=projection.bounds[0]+.015
            front=min(p['front_gap']-s['side_root_gap'],projection.bounds[2]-.015)
            ys=np.linspace(rear,front,max(50,int((front-rear)/.075)))
            bottoms=[lower_at(full[name],float(y))-s['interface_gap']-s['cradle_floor'] for y in ys]
            tops=[lower_at(projection,float(y))-s['interface_gap']+.02 for y in ys]
            band=Polygon(list(zip(ys,bottoms))+list(zip(ys[::-1],tops[::-1])))
            cradle=extrude_yz(band,-half,2*half).cut(shifted)
            parts.append((f'{name}_upright_cradle',cradle))
            root_y=p['front_gap']+s['root_embed'];rear_base=bottoms[0]
            ramp_root_z=rear_base-(root_y-rear)
            # Two thin 45-degree ramp walls carry the cradle's first bridge.
            roof=list(zip(ys,bottoms));roof=[(float(y),float(z)+.12) for y,z in roof]
            roof.append((root_y,roof[-1][1]))
            web=Polygon([(root_y,ramp_root_z),(rear,rear_base)]+roof+[(root_y,ramp_root_z)])
            web=web.intersection(box(-1000,g['spine']['z_min'],1000,1000)).buffer(0)
            for side,x0 in [('left',-half),('right',half-s['web_thickness'])]:
                parts.append((f'{name}_{side}_ramp',extrude_yz(web,x0,s['web_thickness']).cut(round_only_shifted)))
    else:raise ValueError('Orientation must be side or upright')
    return clean,parts,g,s


def make_supported(params=None,support_params=None,orientation='side'):
    clean,parts,g,s=support_parts(params,support_params,orientation)
    # Keep all disconnected support solids as separate shells within one STL.
    # Upright ramp roots intentionally intersect the spine and union there.
    combined=clean
    for _,part in parts:combined=combined.union(part)
    if not combined.val().isValid():raise ValueError('Invalid support combination')
    return combined,parts,g,s


def export_supported(params=None,support_params=None,name='round',output=None):
    out=Path(output or ROOT/'cad');out.mkdir(parents=True,exist_ok=True);reports=[]
    for orientation in ('side','upright'):
        combined,parts,g,s=make_supported(params,support_params,orientation)
        posed=print_pose(combined,orientation)
        stl=out/f'{name}_{orientation}_supported.stl'
        cq.exporters.export(posed,str(stl),tolerance=.008,angularTolerance=.05)
        mesh=trimesh.load(stl,force='mesh');valid=mesh.nondegenerate_faces(height=1e-10)
        if not valid.all():mesh.update_faces(valid);mesh.remove_unreferenced_vertices();mesh.export(stl)
        if not mesh.is_watertight or not mesh.is_volume:raise ValueError(f'Non-manifold support mesh: {stl.name}')
        cq.exporters.export(combined,str(out/f'{name}_{orientation}_supported.step'))
        assembly=cq.Assembly(name=f'Round_anchor_{orientation}_cutaway')
        assembly.add(make_round_anchor(**g['parameters']),name='KEEP_functional_round_anchor',color=cq.Color(.07,.48,.5))
        for label,part in parts:assembly.add(part,name='REMOVE_'+label,color=cq.Color(.95,.40,.12))
        assembly.export(str(out/f'{name}_{orientation}_support_reference.step'))
        reports.append(dict(orientation=orientation,file=stl.name,valid_brep=combined.val().isValid(),
                            watertight=bool(mesh.is_watertight),positive_volume=bool(mesh.is_volume),
                            solids=len(combined.val().Solids()),bounds_mm=mesh.bounds.tolist(),
                            support_parts=[label for label,_ in parts],support_parameters=s,
                            functional_geometry_unchanged=True,functional_print_z_offset_mm=s['side_lift'] if orientation=='side' else 0,physical_print_tested=False))
    (out/f'{name}_support_validation.json').write_text(json.dumps(reports,indent=2))
    return reports


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--geometry',type=Path);ap.add_argument('--name',default='round');args=ap.parse_args()
    params=json.loads(args.geometry.read_text())['parameters'] if args.geometry else None
    print(json.dumps(export_supported(params,name=args.name),indent=2))
