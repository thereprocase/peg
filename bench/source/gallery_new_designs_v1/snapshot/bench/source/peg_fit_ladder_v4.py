"""PF04: five lower-peg retention concepts, each at minus / base / plus.

PF03/BX01 feedback (2026-09-30): friction ribs made the box's lower pegs hard
to push in yet it still fell out; +0.65/+0.80 single coupons felt okay, +0.95
not. The user asked for distinct concepts that use the 3/4 in space behind the
board rather than more squeeze. Every coupon: PF02 coupon 9's top, in-hole
lower ribs at +0.30 (anti-rattle only), a feature past the board's rear face.

  BARB  split tail; two halves flex sideways; barbs hook the rear face with a
        55 deg reverse-wedge catch that cams out under a firm pull. Var: barb height.
  PIN   split tail with small 45 deg barbs (easy in); a 1.75 mm filament pin
        pushed through a 1.9 mm bore from the holder front spreads the halves.
        Var: slot width (narrower = more spread).
  HOOP  split closed into a ring at the tip; barbed like BARB. Var: arm thickness.
  LATCH one long spring arm on one side, rooted at the tail's far end, free end
        hooking the rear face like a zip-tie pawl; the long arm carries a bigger
        hook for the same push. Var: hook height.
  (HEEL, a rigid gravity bump under the tail, was rejected: heel_window.py
        found no lift that clears both it and the hole top; reviews/pf04-heel-*.)
  FIN   two rows of thin fins raked back like a push clip; the second row
        catches thicker boards. Var: fin reach past the hole wall.

Side features (BARB/PIN/HOOP/FIN) act in X only and keep the PF02 tail's Z
extent, which cleared a sampled sweep of the removal path. HEEL HEEL geometry is
kept for the rejection record only. Run with FreeCAD's Python.
Snap, release and pull-out forces, and fatigue, are unmeasured.
"""
from pathlib import Path
import argparse, hashlib, json, math
import FreeCAD as A, Part
import peg_profile as P
import peg_print_variant as PV
import peg_fit_ladder_v2 as G
from peg_fit_ladder import box, label, print_pose, write_stl
from peg_interface import receive_pegs
V = A.Vector
ROOT = P.ROOT
OUT = ROOT.parent/'docs/gallery/fit-ladder-v4'
NAME, VERSION = 'part-pf04-peg-retention-concepts', 'v1'
TOP = dict(upper_ribs_mm=0.50, clamp_mm=0.49)
BODY_RIBS = 0.30
R = 6.35/2
TAIL_LEN = 7.0
TIP_HALF = 1.9
CATCH_X0 = 2.95
SLOT_ROOT = 1.0
BORE = 1.9
CONCEPTS = [
    ('BARB', 'barb_height_mm', [0.3, 0.5, 0.7]),
    ('PIN', 'slot_mm', [1.00, 1.25, 1.50]),
    ('HOOP', 'arm_mm', [0.9, 1.2, 1.5]),
    ('LATCH', 'hook_mm', [0.6, 0.9, 1.2]),
    ('FIN', 'fin_reach_mm', [0.4, 0.7, 1.0]),
]


def coupons():
    out = []
    for name, key, values in CONCEPTS:
        for v in values:
            text = f'{v:.2f}'.rstrip('0').rstrip('.') if v >= 1 else f'{v:.2f}'.rstrip('0').lstrip('0')
            out.append({'coupon': len(out)+1, 'concept': name, key: v, 'label': f'{name} {text}'})
    return out


def prism_xy(points, z0, z1):
    vs = [V(x, y, z0) for x, y in points]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0, 0, z1-z0))


def barb_profile(rear, h, angle, tip_half=TIP_HALF, x0=CATCH_X0):
    """Half outline (x >= 0) of a barbed tail behind the rear face, root to tip."""
    peak = R+h
    catch = (peak-x0)/math.tan(math.radians(angle))
    y0 = rear-0.05-catch
    y1 = y0-0.3
    tip = rear-TAIL_LEN
    pts = [(x0, rear+0.6), (x0, rear-0.05), (peak, y0), (peak, y1), (tip_half, tip)]
    ramp = math.degrees(math.atan((peak-tip_half)/(y1-tip)))
    return pts, dict(width_across_barbs_mm=2*peak, catch_angle_deg=angle, catch_length_mm=catch,
                     ramp_angle_deg=ramp, crest_y_mm=[y0, y1], catch_bearing_per_side_mm=peak-R)


def mirrored(half):
    """Closed outline from a half outline listed root-to-tip."""
    return [(x, y) for x, y in half] + [(-x, y) for x, y in reversed(half)]


def slot_cut(zl, face, width, rear):
    return box(-width/2, rear-TAIL_LEN-1, zl-6, width, (face-SLOT_ROOT)-(rear-TAIL_LEN-1), 12)


def concept_geometry(e, zl, face):
    rear = face-G.BOARD
    add, cut, info = [], [], {}
    band = 0.8
    if e['concept'] in ('BARB', 'PIN'):
        h, ang, w = (e['barb_height_mm'], 55, 1.4) if e['concept'] == 'BARB' else (0.25, 45, e['slot_mm'])
        half, info = barb_profile(rear, h, ang)
        add += G.tail(zl, face) + [prism_xy(mirrored(half), zl-band, zl+band)]
        cut.append(slot_cut(zl, face, w, rear))
        info.update(slot_mm=w, slot_root_from_face_mm=SLOT_ROOT)
        if e['concept'] == 'PIN':
            cut.append(Part.makeCylinder(BORE/2, G.WALL+SLOT_ROOT+1.5, V(0, face-SLOT_ROOT-0.5, zl), V(0, 1, 0)))
            info.update(pin_bore_mm=BORE, pin='1.75 mm filament, about 17 mm long',
                        pin_spread_total_mm=1.75-w)
    elif e['concept'] == 'HOOP':
        t = e['arm_mm']
        band = 1.4
        # Taller band: the hole is only 2.85 wide at +-1.4, so start the catch inside that.
        half, info = barb_profile(rear, 0.5, 55, tip_half=e.get('tip_half', 1.6), x0=2.75)
        add.append(prism_xy(mirrored(half), zl-band, zl+band))
        y0, y1 = info['crest_y_mm']
        tip = rear-TAIL_LEN
        void = [(0.7, face-SLOT_ROOT), (0.7, rear), (R+0.5-t, y0), (R+0.5-t, y1), (0.5, tip+1.2)]
        assert R+0.5-t > 0.7
        if e.get('even_catch_wall'):
            # PF07 review: the corner (R+0.5-t, y0) left only 0.574 t between the void and
            # the 55 deg catch face, a notch thinner than one 0.42 bead at t = 0.7. Run the
            # void along the catch face offset inward by t instead, from the offset of the
            # vertical root face down to the old ramp-side void edge; the rest is unchanged.
            (bx, by), (cx, cy) = half[1], half[2]
            L = math.hypot(cx-bx, cy-by); ux, uy = (cx-bx)/L, (cy-by)/L
            nx, ny = uy, -ux                                  # inward normal of the catch face
            ox, oy = bx+nx*t, by+ny*t                         # a point on the offset catch line
            v0 = (bx-t, oy+uy*((bx-t)-ox)/ux)                 # meets the offset root face x = x0 - t
            (px, py), (qx, qy) = (R+0.5-t, y1), (0.5, tip+1.2)
            wx, wy = qx-px, qy-py
            det = -ux*wy+wx*uy
            sx = ((px-ox)*(-wy)+wx*(py-oy))/det
            r = (ux*(py-oy)-uy*(px-ox))/det
            assert 0 <= r <= 1, r
            meet = (ox+ux*sx, oy+uy*sx)
            void = [(0.7, face-SLOT_ROOT), (0.7, rear), v0, meet, (0.5, tip+1.2)]
            if e.get('ramp_wall'):
                # v11 (owner, after PF07): "make the pointy end a little thinner so it's
                # less stiff there". The ramp-side wall is the ramp offset inward by t (it
                # used to thicken toward the nose) and the closed nose is nose_mm. The
                # outer profile, catch and crest are unchanged.
                (dx, dy), (ex, ey) = half[3], half[4]
                L2 = math.hypot(ex-dx, ey-dy); vx, vy = (ex-dx)/L2, (ey-dy)/L2
                mx, my = (vy, -vx) if vy < 0 else (-vy, vx)
                if mx > 0:
                    mx, my = -mx, -my                         # inward: toward the peg axis
                rx, ry = dx+mx*t, dy+my*t                     # a point on the offset ramp line
                det2 = -ux*vy+vx*uy
                s2 = ((rx-ox)*(-vy)+vx*(ry-oy))/det2
                corner = (ox+ux*s2, oy+uy*s2)                 # offset catch meets offset ramp
                nose = e.get('nose_mm', 1.2)
                ny_ = tip+nose
                nose_pt = (rx+vx*(ny_-ry)/vy, ny_)            # offset ramp meets the nose line
                assert nose_pt[0] > 0.3, nose_pt
                void = [(0.7, face-SLOT_ROOT), (0.7, rear), v0, corner, nose_pt]
                info.update(nose_mm=nose, ramp_wall_mm=t)
            wall = Part.makePolygon([V(x, y, 0) for x, y in half[1:]])
            inner = Part.makePolygon([V(x, y, 0) for x, y in void[2:]])
            info['min_wall_mm'] = round(wall.distToShape(inner)[0], 3)
            assert info['min_wall_mm'] >= 0.95*t, (info['min_wall_mm'], t)
        g = e.get('root_gusset_mm', 0.0)
        if g:
            # v11 (owner): "reinforce the gusset to the peg just a hair" after PF07 #2 tore
            # off at the root. The band grows g taller where it leaves the peg, tapering to
            # nothing 1.5 mm back, clipped to the board hole (r 3.175, 0.05 margin) so it
            # adds no install interference; the void cut below keeps the arms free.
            lg = 1.5
            tall = prism_xy(mirrored(half), zl-band-g, zl+band+g)
            slab = box(-5, rear-lg, zl-5, 10, lg+0.6, 10)
            hole = Part.makeCylinder(R-0.05, lg+2, V(0, rear-lg-0.5, zl), V(0, 1, 0))
            ramp = [(rear-lg, zl+band), (rear, zl+band+g), (rear+0.6, zl+band+g),
                    (rear+0.6, zl-band-g), (rear, zl-band-g), (rear-lg, zl-band)]
            taper = Part.Face(Part.makePolygon([V(-5, y, z) for y, z in ramp+[ramp[0]]])).extrude(V(10, 0, 0))
            add.append(tall.common(slab).common(hole).common(taper))
            info.update(root_gusset_mm=g, root_gusset_length_mm=lg)
        cut.append(prism_xy(mirrored(void), zl-6, zl+6))
        info.update(arm_mm=t, closed_nose_mm=e.get('nose_mm', 1.2), band_half_height_mm=band)
    elif e['concept'] == 'HEEL':
        hb = e['heel_mm']
        add += G.tail(zl, face)
        top = zl-1.9                     # inside the raised tail
        bottom = zl-R-hb
        ramp = (top-bottom)/math.tan(math.radians(30))
        pts = [(rear-0.05, top), (rear-0.05, bottom), (rear-1.05, bottom), (rear-1.05-ramp, top)]
        vs = [V(-1.5, y, z) for y, z in pts]
        add.append(Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(3.0, 0, 0)))
        info.update(heel_below_hole_bottom_mm=hb, heel_width_mm=3.0, catch_face='vertical',
                    lead_ramp_deg_from_axis=30, required_lift_mm=hb)
    elif e['concept'] == 'LATCH':
        h, ang = e['hook_mm'], 60
        add += G.tail(zl, face)
        catch = (R+h-2.9)/math.tan(math.radians(ang))
        y0 = rear-0.05-catch
        root = rear-6.2
        arm = [(1.4, rear-0.05), (2.9, rear-0.05), (R+h, y0), (R+h, y0-0.3), (2.25, root), (1.4, root)]
        add.append(prism_xy(arm, zl-band, zl+band))
        cut.append(box(0.2, root, zl-6, 1.2, rear+0.2-root, 12))          # flex gap beside the arm
        cut.append(box(0.2, rear-0.05, zl-6, 4.0, 0.25, 12))             # frees the arm's end from the peg
        info.update(hook_per_side_mm=h, catch_angle_deg=ang, catch_length_mm=catch, crest_y_mm=[y0, y0-0.3],
                    arm_length_mm=rear-0.05-root, arm_root_thickness_mm=2.25-1.4, flex_gap_mm=1.2,
                    ramp_angle_deg=math.degrees(math.atan((R+h-2.25)/(y0-0.3-root))), one_sided=True)
    elif e['concept'] == 'LATCH2':
        # PF05: meatier head and a flex gap sized to the hook. User: tip needs
        # more meat; tune interference and the return (catch) slope.
        h, ang = e['hook_mm'], e['catch_deg']
        add += G.tail(zl, face)
        gap = e.get('gap_mm', h+0.3)      # the arm must fold in by about h+0.2 to pass
        x_in = -0.6+gap                   # gap runs from x=-0.6 on the solid side
        crest = e.get('crest_mm', 0.8)
        root = rear-6.2
        ref = e.get('contact_ref_deg')
        if ref:
            # PF06: pivot the return face about the point where PF04 #12's 60 deg
            # face crosses the hole wall (x=R), so the board edge still bears
            # at the same place; only the slope changes.
            yc = rear-0.05-(R-2.9)/math.tan(math.radians(ref))
            xs = R-(rear-0.05-yc)*math.tan(math.radians(ang))
            y0 = yc-h/math.tan(math.radians(ang))
            info['contact_point_mm'] = dict(x=R, y_from_rear=yc-rear)
        else:
            xs = 2.9
            y0 = rear-0.05-(R+h-2.9)/math.tan(math.radians(ang))
        assert xs < R
        catch = rear-0.05-y0
        arm = [(x_in, rear-0.05), (xs, rear-0.05), (R+h, y0), (R+h, y0-crest), (2.25, root), (x_in, root)]
        add.append(prism_xy(arm, zl-band, zl+band))
        cut.append(box(-0.6, root, zl-6, gap, rear+0.2-root, 12))
        cut.append(box(-0.6, rear-0.05, zl-6, 4.8, 0.25, 12))
        info.update(hook_per_side_mm=h, catch_angle_deg=ang, catch_length_mm=catch, crest_y_mm=[y0, y0-crest],
                    arm_length_mm=rear-0.05-root, arm_root_thickness_mm=2.25-x_in, head_thickness_mm=R+h-x_in,
                    flex_gap_mm=gap, crest_length_mm=crest,
                    ramp_angle_deg=math.degrees(math.atan((R+h-2.25)/(y0-crest-root))), one_sided=True)
    elif e['concept'] == 'FIN':
        o = e['fin_reach_mm']
        band = 1.0
        tail = Part.makeCylinder(2.4, TAIL_LEN+1.2, V(0, rear-TAIL_LEN, zl+0.4), V(0, 1, 0))
        add.append(tail.common(box(-1.2, rear-TAIL_LEN-1, zl-5, 2.4, TAIL_LEN+3, 10)))
        rake, thick = math.radians(40), 0.8
        dy = (R+o-1.0)/math.tan(rake)     # fin at 40 deg to the peg axis, root buried in the spine
        ty = thick/math.sin(rake)         # Y extent giving 0.8 mm normal thickness
        for tip_y in (rear-0.1, rear-2.3):
            for s in (1, -1):
                pts = [(s*1.0, tip_y-dy), (s*(R+o), tip_y), (s*(R+o), tip_y-ty), (s*1.0, tip_y-dy-ty)]
                add.append(prism_xy(pts, zl-band, zl+band))
        info.update(fin_reach_past_hole_mm=o, fin_thickness_mm=thick, fin_rake_deg=40,
                    fin_rows_tip_y_from_rear_mm=[-0.1, -2.3], spine_half_width_mm=1.2)
    info['band_half_height_mm'] = band
    return add, cut, info


def coupon(entry):
    path = G.fit_file(TOP['clamp_mm'])
    P.FIT_SOURCE = PV.FIT_SOURCE = path
    fit = P.parse(path.read_bytes())
    _, vinfo = PV.build(G.PRINT_VARIANT)
    top, face = vinfo['cut_plane_z_mm'], fit['PEG_FACE_Y']
    zu, zl = fit['PEG_SEAT_DROP'], fit['PEG_SEAT_DROP']-fit['PEG_PITCH']
    host = box(-G.WIDTH/2, face, zl-G.BELOW_LOWER, G.WIDTH, G.WALL, top-(zl-G.BELOW_LOWER))
    base, report = receive_pegs(P.load_reference(), host, print_variant=G.PRINT_VARIANT)
    elbow = report['peg_profile']['elbow_center_y_mm']
    common = (G.side_ribs(zu, TOP['upper_ribs_mm'], max(elbow, face-G.BOARD)+0.3, face+1.0, lead=G.UPPER_LEAD)[0]
              + G.side_ribs(zl, BODY_RIBS, face-G.BOARD+0.2, face+1.0, lead=1.0)[0])
    base = base.multiFuse(common).removeSplitter()
    add, cut, cinfo = concept_geometry(entry, zl, face)
    shape = base.multiFuse(add).removeSplitter()
    if cut:
        shape = shape.cut(cut).removeSplitter()
    text = [label(str(entry['coupon']), 11, 0, top-8.5, face+G.WALL),
            label(entry['label'], 3.2, 0, zl+10.5, face+G.WALL)]
    shape = shape.multiFuse(text).removeSplitter()
    base = base.multiFuse(text).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1, entry
    # Measured: top and in-hole widths unchanged by the concept.
    uw = shape.common(box(-10, face-.505, zu-.005, 20, .01, .01)).BoundBox.XLength
    assert abs(uw-(6.35+TOP['upper_ribs_mm'])) < 1e-4, uw
    lw = shape.common(box(-10, face-.505, zl-.005, 20, .01, .01)).BoundBox.XLength
    assert abs(lw-(6.35+BODY_RIBS)) < 1e-4, lw
    # Seated: the concept adds no board overlap beyond the common ribs/clamp.
    board = box(-15, -G.BOARD, -60, 30, G.BOARD, 80)   # installed: front Y=0, holes Z=0/-25.4
    for zc in (0.0, -fit['PEG_PITCH']):
        board = board.cut(Part.makeCylinder(R, G.BOARD+2, V(0, -G.BOARD-1, zc), V(0, 1, 0)))
    board.translate(V(0, 0.15, 0.12))    # into design coordinates (seated pose inverted)
    extra = shape.common(board).Volume-base.common(board).Volume
    assert extra < 1e-6, f'{entry["label"]}: concept intrudes into the seated board by {extra} mm3'
    # Concept-specific measurements of the built part.
    rear = face-G.BOARD
    if entry['concept'] == 'LATCH2':
        yc = sum(cinfo['crest_y_mm'])/2
        cr = shape.common(box(-10, yc-.005, zl-.005, 20, .01, .01))
        assert len(cr.Solids) == 2, 'arm must be free of the body'
        assert abs(cr.BoundBox.XMax-(R+entry['hook_mm'])) < 1e-4, cr.BoundBox.XMax
        cinfo['measured_hook_reach_past_hole_mm'] = cr.BoundBox.XMax-R
        g = cinfo['flex_gap_mm']
        assert shape.common(box(-0.59, rear-6.19, zl-.005, g-.02, 6.38, .01)).Volume < 1e-9, 'flex gap must be open'
        assert g >= entry['hook_mm']+0.25, 'gap must let the hook fold inside the hole'
    if entry['concept'] == 'LATCH':
        yc = sum(cinfo['crest_y_mm'])/2
        cr = shape.common(box(-10, yc-.005, zl-.005, 20, .01, .01))
        assert len(cr.Solids) == 2, 'arm must be free of the body'
        assert abs(cr.BoundBox.XMax-(R+entry['hook_mm'])) < 1e-4, cr.BoundBox.XMax
        cinfo['measured_hook_reach_past_hole_mm'] = cr.BoundBox.XMax-R
        gap = shape.common(box(0.21, rear-6.19, zl-.005, 1.18, 6.38, .01)).Volume
        assert gap < 1e-9, 'flex gap must be open'
    if entry['concept'] in ('BARB', 'PIN', 'HOOP'):
        yc = sum(cinfo['crest_y_mm'])/2
        cr = shape.common(box(-10, yc-.005, zl-.005, 20, .01, .01))
        assert len(cr.Solids) == 2, 'crest must be split'
        assert abs(cr.BoundBox.XLength-cinfo['width_across_barbs_mm']) < 1e-4, cr.BoundBox.XLength
        cinfo['measured_width_across_barbs_mm'] = cr.BoundBox.XLength
    if entry['concept'] == 'HEEL':
        zmin = shape.common(box(-3, rear-2, zl-6, 6, 2, 6)).BoundBox.ZMin
        assert abs(zmin-(zl-R-entry['heel_mm'])) < 1e-4, zmin
        cinfo['measured_heel_bottom_below_hole_mm'] = (zl-R)-zmin
    if entry['concept'] == 'FIN':
        fx = shape.common(box(-10, rear-0.15, zl-.005, 20, .01, .01)).BoundBox
        cinfo['measured_fin_span_mm'] = fx.XLength
    info = dict(entry, top=TOP, body_ribs_mm=BODY_RIBS, fit_file=str(path.relative_to(ROOT)),
                measured_upper_width_mm=uw, measured_lower_body_width_mm=lw,
                seated_extra_board_overlap_mm3=extra, concept_detail=cinfo)
    return shape, info


def main(output, entries=None, name=NAME, part='PF04 lower-peg retention concepts'):
    output.mkdir(parents=True, exist_ok=True)
    canonical = P.FIT_SOURCE
    fit = hashlib.sha256(canonical.read_bytes()).hexdigest()[:10]
    catalog = dict(part=part, version=VERSION, top=TOP, body_ribs_mm=BODY_RIBS,
                   concepts={n: dict(varies=k, values=v) for n, k, v in CONCEPTS},
                   scope='CAD geometry only. Snap, release and pull-out forces, fatigue and board wear are unmeasured. HEEL rejected by heel_window.py.',
                   coupons=[])
    printed = []
    try:
        for i, entry in enumerate(entries or coupons()):
            shape, info = coupon(entry)
            stem = f"{name}__{VERSION}__coupon-{entry['coupon']}"
            shape.exportStep(str(output/f'{stem}__installed__fit-{fit}.step'))
            info['files'] = [write_stl(shape, output/f'{stem}__installed__fit-{fit}.stl')]
            catalog['coupons'].append(info)
            p = print_pose(shape); p.translate(V((i % 5)*(G.WIDTH+8), (i//5)*30, 0)); printed.append(p)
            print(entry['label'], json.dumps({k: round(v, 3) for k, v in info['concept_detail'].items() if isinstance(v, float)}), flush=True)
    finally:
        P.FIT_SOURCE = PV.FIT_SOURCE = canonical
    catalog['plate'] = write_stl(Part.makeCompound(printed), output/f'{name}__{VERSION}__all-{len(printed)}__print-flat-top__fit-{fit}.stl')
    (output/f'{name}__{VERSION}__catalog.json').write_text(json.dumps(catalog, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    main(parser.parse_args().output)
