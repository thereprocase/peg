"""Inward20 v3: four vertical trays, retained v2 seating, continuous clean frame.

FreeCAD Python: inward20_v3.py NEW_OUTPUT_DIRECTORY
Y is away from the board, Z up. Positive X-axis rotation makes +Y uphill.
Original contact geometry is rigidly transformed; shared receiver remains unrotated.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import FreeCAD as A
import Part

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
saved_argv = sys.argv[:]
sys.argv = ['holder.py', 'unused', 'v11p3']
import holder as H
sys.argv = saved_argv
sys.path.insert(0, str(HERE.parent / 'solder_v12'))
import common as K

V = A.Vector
NAME = 'part-tweezers__inward20-v3-A4p0__right-cheek__fit-pf02c9-hoop5'
ANGLE = 20.0
PITCH = 23.0
HEIGHT = -37.0
EXTRA_Y = 19.05
V2 = HERE.parents[1] / 'reviews/tweezer-inward20-v2'
TRAYS = 4
HOOP_ROW = 4
BEARING_ROWS = [2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moved(shape, placement):
    result = shape.copy()
    result.transformShape(placement.toMatrix())
    return result


def difference(a, b):
    return a.cut(b).Volume + b.cut(a).Volume


def round_outline(points, x0, thickness, radius):
    """Round only the extruded outline's X-directed edges; never a bearing seam."""
    shape = K.poly_prism(points, 'x', x0, x0 + thickness)
    edges = [e for e in shape.Edges if len(e.Vertexes) == 2 and
             abs(abs(e.Vertexes[1].Point.x-e.Vertexes[0].Point.x)-thickness) < 1e-7]
    return shape.makeFillet(radius, edges)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        parser.error('Output must be empty: preserve existing build evidence.')
    H.LEAN = H.RIB = 4.0
    H.RIBS = False
    H.TRAYS = TRAYS
    H.TOP_FLOOR_Z = 0.0
    mesh, pts = H.tool_points()
    pl, yaw = H.placement(pts)
    reference = H.tray(0, pl, pts)
    rotation = A.Rotation(V(1, 0, 0), ANGLE)
    pivot = V(0, 10, 0)
    pitch = A.Placement(pivot-rotation.multVec(pivot)+V(0, 0, HEIGHT), rotation)
    tool_pose = pitch.multiply(pl)
    # First reproduce v1, then translate globally without changing Z or orientation.
    tip_y = min(tool_pose.multVec(V(*p)).y for p in pts)
    pitch.move(V(0, max(0.0, 9.55-tip_y), 0))
    pitch.move(V(0, EXTRA_Y, 0))
    tool_pose = pitch.multiply(pl)
    v2 = json.loads((V2/'candidate.json').read_text())['cases'][0]
    translation = [a-b for a, b in zip(list(tool_pose.Base), v2['tool_pose']['base'])]
    assert max(abs(a-b) for a,b in zip(translation, [0, 0, 0])) < 1e-9
    assert max(abs(a-b) for a,b in zip(tool_pose.Rotation.Q, v2['tool_pose']['quaternion'])) < 1e-9
    host, receiver = K.receiver(2, HOOP_ROW, 'right-cheek', bearing_rows=BEARING_ROWS)
    floors, slots, wedges = [], [], []
    for k in range(TRAYS):
        transform = A.Placement(pitch)
        transform.move(V(0, 0, -PITCH*k))
        floors.append(moved(reference[0][0], transform))
        slots.append(moved(reference[1], transform))
        wedges.append(moved(reference[2], transform))
    # The cheek follows the receiving pitch; exposed heels overhang the open end.
    yf = max(f.optimalBoundingBox().YMax for f in floors)
    slope = math.tan(math.radians(ANGLE))
    valley_point = pitch.multVec(V(H.INNER, 70, 0))
    def valley(y):
        return valley_point.z + (y-valley_point.y)*slope
    top = lambda y: valley(y) + 26.0
    bottom = lambda y: valley(y) - PITCH*(TRAYS-1) - 9.0
    # One rounded silhouette controls shell, reinforcement and web boundaries.
    # No individually terminated diagonal strips or rail shards are added.
    outline = [(5.25, -107.48), (5.25, 5.12), (32, 5.12),
               (yf, top(yf)), (yf, bottom(yf)), (75, -106), (25, -111.7)]
    outer = round_outline(outline, H.CHEEK_X, 3.0, 3.0)
    envelope = round_outline(outline, H.CHEEK_X, 48.8, 3.0)
    rear_limit = min(f.optimalBoundingBox().YMin for f in floors)-5.0
    # Rounded openings leave a continuous mount spine, middle cross-member and
    # shelf-root spine. Their through-depth boundaries are shared by the cheek
    # and its shallow reinforcement, so no sliver remains at a strip junction.
    windows = [ [(18,-43),(18,-7),(rear_limit-5,-7),(rear_limit-5,-43)],
                [(18,-98),(18,-54),(rear_limit-5,-54),(rear_limit-5,-98)] ]
    for k in range(TRAYS):
        ya, yb = rear_limit+5, yf-7
        low, high = 3.5-PITCH*k, 12.0-PITCH*k
        windows.append([(ya,valley(ya)+low),(yb,valley(yb)+low),
                        (yb,valley(yb)+high),(ya,valley(ya)+high)])
    cheek = outer
    rear_profile=[(H.CHEEK_X,0),(H.CHEEK_X+5,0),
                  (H.CHEEK_X+5,rear_limit-3),(H.INNER,rear_limit+1),
                  (H.CHEEK_X,rear_limit+1)]
    rear_frame=envelope.common(K.poly_prism(rear_profile,'z',-150,50))
    for poly in windows:
        cutter = round_outline(poly,H.CHEEK_X-1,51,2.5)
        cheek = cheek.cut(cutter)
        rear_frame = rear_frame.cut(cutter)
    # Continuous top/bottom flanges share the outer contour and rounded inner
    # boundaries; both run into the mount spine, without an acute free strip end.
    top_inner = [(4,-140),(yf+2,-140),(yf+2,top(yf)-2.4),
                 (32,2.72),(4,2.72)]
    bottom_inner = [(4,40),(yf+2,40),(yf+2,bottom(yf)+6),
                    (74,-100),(25,-105.7),(4,-101.48)]
    flange_blank = round_outline(outline,H.CHEEK_X,15.0,3.0)
    top_rail = flange_blank.cut(round_outline(top_inner,H.CHEEK_X-1,18,2.5))
    bottom_rail = flange_blank.cut(round_outline(bottom_inner,H.CHEEK_X-1,18,2.5))
    shell = cheek.multiFuse([rear_frame,top_rail,bottom_rail]).removeSplitter()
    # Broad end webs merge into those same flanges and are clipped to their
    # silhouette, removing the former stepped/pointed web-to-rail overhangs.
    webs = []
    # A shared silhouette-derived skin gives each end web the same roof/floor
    # planes as its adjacent rail, eliminating intersecting triangular surface
    # shards. Only the broad footprint tapers toward the cheek.
    upper_web_inner=top_inner
    skins=[envelope.cut(round_outline(upper_web_inner,H.CHEEK_X-1,51,2.5)),
           envelope.cut(round_outline(bottom_inner,H.CHEEK_X-1,51,2.5))]
    for ye,skin in zip([45,75],skins):
        footprint=K.poly_prism([(H.CHEEK_X,4),(24.1,4),(H.CHEEK_X,ye)],'z',-150,50)
        webs.append(skin.common(footprint))
    root = K.poly_prism([(H.INNER-.05,5.4),(H.INNER+4.5,5.4),
                         (H.INNER-.05,10.0)],'z',-105,3.0)
    body = host.multiFuse([shell, root]+webs+floors).cut(slots).removeSplitter()
    # Pointed (+X print-up) plate opening; protect the complete shared peg roots.
    for offset in [0,50.8]:
        window = K.pointed_window(-17,17,-39-offset,-14-offset,'+X')
        body = body.cut(window.cut(K.peg_keepout(2,HOOP_ROW,bearing_rows=BEARING_ROWS))).removeSplitter()
    assert body.isValid() and len(body.Solids) == 1
    rear = K.box(-60, -40, -160, 120, 40.15, 240)
    peg_delta = difference(body.common(rear), host.common(rear))
    assert peg_delta < 1e-6, peg_delta
    record = K.export(body, out, NAME, 'right-cheek', dict(receiver=receiver))
    K.write(body.common(K.box(-100, .15, -150, 200, 250, 300)),
            out/f'{NAME}__front-material.stl')
    clearance_meshes = {}
    for label, shape in [('plate-region', body.common(K.box(-50, .15, -150, 100, 5.4, 240))),
                         ('root-corner', root.common(body))]+[
                             (f'root-web-{k+1}', web.common(body)) for k,web in enumerate(webs)]:
        filename = f'{NAME}__clearance-{label}.stl'
        K.write(shape, out/filename)
        clearance_meshes[label] = filename
    tools, wedge_files, equivalence = [], [], []
    for k in range(TRAYS):
        transform = A.Placement(pitch)
        transform.move(V(0, 0, -PITCH*k))
        equivalence.append(dict(tray=k+1, floor_mm3=difference(moved(floors[k], transform.inverse()), reference[0][0]),
            pocket_mm3=difference(moved(slots[k], transform.inverse()), reference[1]),
            wedge_mm3=difference(moved(wedges[k], transform.inverse()), reference[2])))
        wp = f'{NAME}__wedge-{k+1}__installed.stl'
        K.write(wedges[k], out/wp)
        wedges[k].exportStep(str(out/wp.replace('.stl', '.step')))
        wedge_files.append(wp)
        m = mesh.copy()
        m.Placement = transform.multiply(pl)
        tp = f'{NAME}__tool-{k+1}.stl'
        m.write(str(out/tp))
        tools.append(tp)
    # Normal wedge is unchanged in its own frame. Print on its tapered broad face.
    w = moved(reference[2], pl.inverse())
    h0, h1 = reference[3]['wedge_front_mm']/2, reference[3]['wedge_back_mm']/2
    normal = V(0, -(h1-h0), -20)
    normal.normalize()
    w = moved(w, A.Placement(V(), A.Rotation(normal, V(0, 0, -1))))
    bb = w.optimalBoundingBox()
    w.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    wp = f'{NAME}__wedge__print.stl'
    K.write(w, out/wp)
    w.exportStep(str(out/wp.replace('.stl', '.step')))
    up_out = [0.0, math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE))]
    record.update(id='inward20-v3-A4p0', lean_mm=4.0,
        lean_definition='Reference right-arm outer edge to cheek in receiving frame; not universal slot width',
        fore_aft_pitch_deg=ANGLE, lateral_cant_in_receiving_frame_deg=15,
        global_lateral_plane_angle_deg=math.degrees(math.atan(math.tan(H.CANT)/math.cos(math.radians(ANGLE)))),
        receiving_transform=dict(base=list(pitch.Base), quaternion=list(pitch.Rotation.Q)),
        tool_pose=dict(base=list(tool_pose.Base), quaternion=list(tool_pose.Rotation.Q)),
        tray_pitch_vertical_mm=PITCH, receiving_equivalence=equivalence,
        tools=tools, wedges=wedge_files, wedge_print=wp, wedge_count=TRAYS,
        wedge_volume_mm3=w.Volume, peg_symmetric_difference_mm3=peg_delta,
        removal=dict(lift_mm=6.5, lift_direction=[0, 0, 1], out_distance_mm=135,
                     out_direction=up_out, reverse_for_insertion=True),
        added_tip_clearance_global_y_mm=EXTRA_Y,
        top_translation_from_v2_mm=translation,
        v2_comparison=dict(candidate=str(V2/'candidate.json'),sha256=sha(V2/'candidate.json'),
                           top_two_positions_unchanged=True,orientation_unchanged=True,plate_gap_mm=23.05),
        clearance_meshes=clearance_meshes,
        cheek=dict(thickness_mm=3, perimeter_rise_mm=12, outer_radius_mm=3.0,
                   window_radius_mm=2.5, outline_yz_mm=outline, windows_yz_mm=windows),
        sources={str(p.resolve()): sha(p) for p in [Path(__file__), HERE/'holder.py', K.HERE/'common.py', H.TOOL]})
    load_x = reference[3]['xmax']-2.5
    load = pitch.multVec(V(load_x, reference[3]['y_front']-4, H.floor_top(load_x, 0)-1.0))
    loads=[]
    for k in range(TRAYS):
        point=list(load+V(0,0,-PITCH*k))
        for axis,force,target in [('side',[5,0,0],1.0),('down',[0,0,-5],.5)]:
            loads.append(dict(id=f'tray-{k+1}-{axis}-5N',point=point,radius=3,force=force,
                              target_load_point_mm=target,what=f'Tray {k+1}, {axis} handling load'))
    (out/f'{NAME}__fea-spec.json').write_text(json.dumps(dict(
        step=f'{NAME}__installed.step',h=2.0,supports=['pegs'],loads=loads),indent=2)+'\n')
    assert all(max(v for key, v in eq.items() if key!='tray') < 1e-5 for eq in equivalence)
    K.save_design(out, NAME, record)
    (out/'candidate.json').write_text(json.dumps(dict(cases=[record], runtime=dict(
        FreeCAD=A.Version(), OpenCascade=Part.OCC_VERSION)), indent=2)+'\n')
    print(json.dumps(dict(volume_cm3=body.Volume/1000, bounds=record['bounds_installed'],
                         print_bounds=record['print_bounds'], receiving_equivalence=equivalence), indent=2))


if __name__ == '__main__':
    main()
