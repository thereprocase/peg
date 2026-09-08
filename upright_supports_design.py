"""Sacrificial thin webs for Z-up printing of the unchanged pegboard anchor.

The default print orientation keeps the installed Z direction vertical. Two
0.5 mm webs support each projection; each web sits 0.15 mm inside an outside
X face. The resulting roof bridges 2.7 mm across X. Cut all webs flush before
installation. This geometric construction does not establish slicer settings
or an upright FDM load rating.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from motion_design import get_parts

SUPPORT_DEFAULTS=dict(web_thickness=.50,web_inset=.15,spine_overlap=.25,
                      roof_overlap=.12,ramp_drop=.20,layer_height=.20)

def _lower_envelope(poly,ymax):
    ys=sorted(set([float(poly.bounds[0]),float(ymax)]+[
        float(v[0]) for v in poly.exterior.coords if poly.bounds[0]<=v[0]<ymax]))
    out=[]
    for y in ys:
        seg=poly.intersection(LineString([(y,poly.bounds[1]-1),(y,poly.bounds[3]+1)]))
        if seg.is_empty:raise ValueError('Cannot locate underside at profile boundary')
        out.append((y,float(seg.bounds[1])))
    return out

def support_profile(params=None,support_params=None):
    """Return {'upper': [(y,z),...], 'lower': [(y,z),...]} support exteriors.

    Extrude each polygon in both X intervals supplied by support_data().
    Roofs enter the functional solid by roof_overlap for a reliable union.
    These roofs and roots are cut edges; they are not permanent gussets.
    """
    p,parts,_=get_parts(params);s=SUPPORT_DEFAULTS|(support_params or {})
    root_y=p['front_gap']+s['spine_overlap'];out={}
    for name,part in [('upper',parts['hook']),('lower',parts['locator'])]:
        roof=_lower_envelope(part,root_y)
        # Every underside point satisfies y+z >= intercept+ramp_drop.
        # Therefore the lower boundary z=intercept-y remains below the roof.
        intercept=min(y+z for y,z in roof)-s['ramp_drop']
        ymin=roof[0][0]
        pts=[(root_y,intercept-root_y),(ymin,intercept-ymin)]
        pts += [(y,z+s['roof_overlap']) for y,z in roof]
        shape=Polygon(pts)
        if not shape.is_valid or shape.area<=0:raise ValueError('Invalid support membrane')
        # The foot must meet an already established section of the spine.
        foot=LineString([(root_y-.01,intercept-root_y),(root_y+.01,intercept-root_y)])
        if not parts['spine'].intersects(foot):
            raise ValueError(f'{name} support foot misses spine; lengthen spine_height or revise locator dimensions')
        out[name]=np.asarray(shape.exterior.coords[:-1]).tolist()
    return out

def _intervals(geom):
    if geom.is_empty:return []
    if geom.geom_type in ('LineString','Point'):return [(geom.bounds[0],geom.bounds[2])]
    return [v for g in geom.geoms for v in _intervals(g)]

def check_layer_growth(params=None,support_params=None):
    """Check web-only deposition against the preceding composite layer.

    Geometry already provides an exact 45-degree rearward ramp. This checks
    roof/root transitions at four layer phases in addition to that arithmetic.
    Horizontal reach is expanded by one layer height: a 45-degree allowance.
    """
    p,parts,_=get_parts(params);s=SUPPORT_DEFAULTS|(support_params or {})
    profiles=support_profile(p,s);webs={k:Polygon(v) for k,v in profiles.items()}
    composite=unary_union([parts['complete']]+list(webs.values()))
    h=s['layer_height'];checks=0;failures=[]
    for phase in [0,.25,.5,.75]:
        zstart=parts['complete'].bounds[1]+phase*h
        for z in np.arange(zstart,composite.bounds[3]+h,h):
            prev=composite.intersection(LineString([(-50,z-h),(50,z-h)]))
            supported=[(a-h,b+h) for a,b in _intervals(prev)]
            for name,web in webs.items():
                now=web.intersection(LineString([(-50,z),(50,z)]))
                for a,b in _intervals(now):
                    checks+=1
                    if not any(a>=pa-1e-8 and b<=pb+1e-8 for pa,pb in supported):
                        failures.append({'web':name,'z':float(z),'interval':[a,b],'previous_expanded_intervals':supported})
    return {'passed':not failures,'checked_web_sections':checks,'layer_height_mm':h,
      'layer_phases':[0,.25,.5,.75],'maximum_geometric_ramp_angle_from_vertical_deg':45,
      'rearward_growth_per_layer_mm':h,'failures':failures,
      'scope':'Web deposition supported by previous composite layer within 45 degrees horizontal reach; exact polygon geometry. Does not simulate extrusion or slicer bridging.'}

def support_data(params=None,support_params=None):
    p,parts,_=get_parts(params);s=SUPPORT_DEFAULTS|(support_params or {})
    if s['web_thickness']<=0 or s['web_inset']<0 or 2*(s['web_thickness']+s['web_inset'])>=p['width']:
        raise ValueError('Web thickness/inset must leave a positive central roof bridge')
    profiles=support_profile(p,s)
    outer=p['width']/2-s['web_inset'];inner=outer-s['web_thickness']
    bands=[[-outer,-inner],[inner,outer]]
    polys={k:Polygon(v) for k,v in profiles.items()}
    pure_support={k:v.difference(parts['complete']) for k,v in polys.items()}
    metrics={}
    for name,poly in polys.items():
        pts=np.asarray(profiles[name]);root=pts[0];rampend=pts[1]
        metrics[name]={'root_yz':root.tolist(),'rear_ramp_end_yz':rampend.tolist(),
           'ramp_rearward_run_mm':float(root[0]-rampend[0]),
           'ramp_vertical_rise_mm':float(rampend[1]-root[1]),
           'support_area_per_web_mm2':pure_support[name].area,
           'sacrificial_volume_two_webs_mm3':pure_support[name].area*2*s['web_thickness'],
           'spine_root_embed_mm':s['spine_overlap'],'roof_embed_mm':s['roof_overlap']}
    return {'parameters':p,'support_parameters':s,'profiles_yz':profiles,'web_x_bands':bands,
        'metrics':metrics,'bridge_span_x_mm':2*inner,'outside_roof_overhang_x_mm':s['web_inset'],
        'verification':check_layer_growth(p,s),
        'removal':['Use flush cutters from both outside X faces; remove upper and lower membranes on both sides.',
          'Trim each roof attachment flush with the original neck/tongue or locator underside, and each root flush with the spine.',
          'The 0.15 mm web inset preserves the outermost bearing corners during cutting; remove any remaining material inside those corners.',
          'Check the board-fit sample after trimming. Removed-web geometry is the previously motion-validated functional anchor.'],
        'printing':['Print installed Z direction upward, using a brim for a standalone anchor or the integrated holder base.',
          'Orient roof bridge lines across X between the two membranes; the default clear span is 2.7 mm.',
          'The membranes require a slicer path for 0.5 mm thin walls. Inspect the layer preview; automatic generic supports are not part of this geometry.',
          'The main anchor has a stronger continuous filament path when printed flat on its side; the upright option prioritizes integration and needs separate load qualification.']}

if __name__=='__main__':
    out=Path(__file__).parent
    data=support_data()
    (out/'upright_supports_geometry.json').write_text(json.dumps(data,indent=2))
    print(json.dumps({k:data[k] for k in ['web_x_bands','bridge_span_x_mm','metrics','verification']},indent=2))
