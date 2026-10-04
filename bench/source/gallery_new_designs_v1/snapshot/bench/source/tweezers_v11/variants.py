"""Tactile tray variants of the v11.3 tweezer rack (holder.py), for the capture simulation.

The owner's rule (2026-10-02): people look at the rack, reach toward it, touch the tool to the
cradle and let go. Features the hand can feel (the wedge in the tweezer's crotch, an entry lip on
the shelf) should steer the tool home while it is still held, and never force it into an awkward
pose.

Every variant keeps the owner's concept: the tool stands on edge, points toward the board, heel
toward the user, and slides down the cant until its crotch hangs on the glued wedge. No lean
ribs except the v11p2 baseline. Each variant imports holder.py, overrides its module constants
or wraps holder.tray()/holder.cheek(), and calls holder.main(out). holder.py's own defaults
('v11p3') are never changed.

Families ('+' joins ids, e.g. ch5p0+lip2. An optional JSON object after the id adds or
overrides parameters, and then the id may also be a new name, e.g.
variants.py OUT lip1p5 '{"lip": {"h": 1.5}}'. The id is the build directory and the file tag):
  channel   ch3p0 ch5p0 ch6p5   right arm's outer edge off the cheek face (v11p3: 4.0 mm)
  cant      cant10 cant20       floor cant, left side up (v11p3: 15 deg)
  wedge     wedge-long          V-matching wedge over stations 26-56 (v11p3: 31-51)
            wedge-snug          flanks follow the V station by station, relief 0 -> 0.1 mm at the
                                back (v11p3: straight flank, 0.4 mm), on holder's pocket and foot
            wedge-nose          pointed ogive nose reaching ~2.5 mm further into the crotch
                                (tip at station 28.5), printed on the wedge's flat top
            wedge-tall          fin 2.4 mm taller with a 40 deg ridge roof the arms ride onto
  shelf     lip1 lip2           entry lip across the floor 0.6 mm behind the heel, 1.0 / 2.0 mm
                                tall: the heel rides up its 30 deg ramp and drops behind its
                                75 deg stop face (floor extended under the heel to carry it)
            mouth               lead-in at the tray mouth: 30 deg down-ramp off the floor's front
                                edge, floor flared 4 mm wider on the left over the last 15 mm,
                                2 mm 45 deg chamfer on the cheek's front inner edge
  baselines v11p3 (lean 4.0, no ribs), v11p2 (as printed, lean ribs), v11p2-noribs

Run with FreeCAD's Python:
  python.exe variants.py OUT_ROOT VARIANT_ID [JSON_PARAMS]       build OUT_ROOT/VARIANT_ID/
  python.exe variants.py OUT_ROOT VARIANT_ID [JSON_PARAMS] --dry  trays and cheek only, no files
Files are holder.py's, named part-solder-modules-tweezers__<id>__edge-trays-right-cheek__fit-pf02c9-hoop5__*,
plus variant.json (parameters and the tactile features' geometry) and checks-spec.json.
Coordinates as holder.py: X lateral (+X the user's left facing the board, right cheek at -X),
Y out of the board, Z up. Tool frame: x width, y heel->tips, z opening.
"""
from pathlib import Path
import json
import math
import sys

sys.dont_write_bytecode = True               # leave no caches next to the sources
HERE = Path(__file__).resolve().parent
NAME_FMT = 'part-solder-modules-tweezers__%s__edge-trays-right-cheek__fit-pf02c9-hoop5'

FAMILIES = {
    # baselines (holder.VARIANTS)
    'v11p3': dict(base='v11p3'),
    'v11p2': dict(base='v11p2'),
    'v11p2-noribs': dict(base='v11p2-noribs'),
    # channel: right arm's outer edge off the cheek face
    'ch3p0': dict(lean=3.0),
    'ch5p0': dict(lean=5.0),
    'ch6p5': dict(lean=6.5),
    # floor cant
    'cant10': dict(cant=10.0),
    'cant20': dict(cant=20.0),
    # wedge
    'wedge-long': dict(wedge_s=[26.0, 56.0]),
    'wedge-snug': dict(snug=dict(relief=0.1)),
    'wedge-nose': dict(nose=dict(length=3.0, tip_r=0.25)),
    'wedge-tall': dict(tall=dict(ridge_tx=3.4, roof_deg=40.0)),
    # shelf entry
    'lip1': dict(lip=dict(h=1.0)),
    'lip2': dict(lip=dict(h=2.0)),
    'mouth': dict(mouth=dict(ramp_deg=30.0, ramp_len=5.0, flare_w=4.0, flare_len=15.0, cheek_chamfer=2.0)),
}

TACTILE = {
    'base': 'none beyond the baseline',
    'lean': 'channel between the cheek face and the right arm',
    'cant': 'how hard the floor pushes the tool toward the cheek and onto the wedge',
    'wedge_s': 'longer wedge flanks: the V meets the wedge earlier on the way in and locates over more length',
    'relief': 'straight wedge flank with a different back relief (holder allows >= ~0.32 mm)',
    'snug': 'wedge flanks follow the V station by station, relief 0 at the nose to 0.1 mm at the back: contact along the whole flank, less yaw play when seated',
    'nose': 'pointed ogive nose that runs into the crotch and centres the V',
    'tall': 'taller ridge-roofed fin: an arm landing on it rides off the 40 deg roof, and the V rides onto more fin',
    'lip': 'entry lip behind the heel: the heel rides up the 30 deg ramp and drops behind the stop face (felt click, no walk-out)',
    'mouth': 'tray-mouth lead-in: front down-ramp lifts a low tool onto the floor, left flare widens the landing, cheek chamfer turns an edge strike inward',
}


def resolve(vid, extra=None):
    """Parameters for an id ('+' joins family ids) plus an optional JSON override."""
    params = {}
    for part in vid.split('+'):
        if part not in FAMILIES:
            if extra is None:
                raise KeyError('unknown variant %r (known: %s)' % (part, ', '.join(FAMILIES)))
            continue
        for k, v in FAMILIES[part].items():
            if isinstance(v, dict) and isinstance(params.get(k), dict):
                params[k] = dict(params[k], **v)
            else:
                params[k] = v
    if extra:
        for k, v in json.loads(extra).items():
            params[k] = dict(params.get(k, {}), **v) if isinstance(v, dict) and isinstance(params.get(k), dict) else v
    base = params.get('base', 'v11p3')
    if base != 'v11p3' and set(params) - {'base'}:
        raise ValueError('tactile parameters go on the v11p3 base only (no lean ribs): %r' % params)
    return params


def build(out_root, vid, extra=None, dry=False):
    p = resolve(vid, extra)
    base = p.get('base', 'v11p3')
    out = Path(out_root)/vid
    # holder.py reads its variant from argv[2] at import time.
    sys.argv = [sys.argv[0], str(out), base]
    sys.path.insert(0, str(HERE))
    import FreeCAD as A
    import Part
    import holder as H
    V = A.Vector

    H.NAME = NAME_FMT % vid
    if 'lean' in p:
        H.LEAN = H.RIB = float(p['lean'])
    if 'cant' in p:
        H.CANT = math.radians(float(p['cant']))
    if 'wedge_s' in p:
        H.WEDGE_S = tuple(float(s) for s in p['wedge_s'])
    if 'relief' in p:
        H.WEDGE_BACK_RELIEF = float(p['relief'])
    tv = H.FLOOR_T/math.cos(H.CANT)              # vertical floor thickness
    state = dict(pl=None, wedges={}, heel_y=None, notes={})

    # ---------------------------------------------------------------- helpers
    def below(k, depth):
        """Half-space under a plane parallel to the floor top of tray k, depth below it (normal)."""
        z0 = H.floor_top(H.INNER, k)-depth/math.cos(H.CANT)
        b = H.box(H.INNER-200, -200, z0-400, 400, 600, 400)
        b.rotate(V(H.INNER, 0, z0), V(0, 1, 0), -math.degrees(H.CANT))
        return b

    def tool_frame_prism(outline, tx0, tx1):
        """Prism in the tool frame: outline [(tz, ty)] extruded along the tool width tx0..tx1."""
        vs = [V(tx0, ty, tz) for tz, ty in outline]
        return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(tx1-tx0, 0, 0))

    def to_tray(solid, pl, k):
        s = solid.transformGeometry(pl.toMatrix())
        s.translate(V(0, 0, -k*H.TRAY_PITCH))
        return s

    def along_floor(k, profile, x0, x1):
        """Solid from a (Y, dz) profile, dz measured vertically from tray k's floor top,
        carried across X from x0 to x1 so it follows the cant."""
        vs = [V(x0, y, H.floor_top(x0, k)+dz) for y, dz in profile]
        L = x1-x0
        return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(L, 0, L*math.tan(H.CANT)))

    # ---------------------------------------------------------------- wedge features
    def snug_outline(pts, h0, spec):
        """Plan outline [(tz, ty)] whose flanks follow the V itself, station by station, with
        relief growing linearly from 0 at the front to `relief` at the back. A straight flank
        cannot go below ~0.32 mm back relief: the V opens slower just behind station 31."""
        S0, S1 = H.WEDGE_S
        rel = float(spec.get('relief', 0.1))
        n = int(round((S1-S0)/1.0))
        st = [S0+(S1-S0)*i/n for i in range(n+1)]
        h1 = H.gap(pts, S1)/2-H.WEDGE_BACK_RELIEF                 # holder's straight flank (the foot)
        trap = [h0+(h1-h0)*(s-S0)/(S1-S0) for s in st]
        hw = [h0]+[max(H.gap(pts, s)/2-rel*(s-S0)/(S1-S0), w) for s, w in zip(st[1:], trap[1:])]  # never under the foot
        for i in range(n):                              # chords stay inside the V between stations
            sm = (st[i]+st[i+1])/2
            assert (hw[i]+hw[i+1])/2 <= H.gap(pts, sm)/2+1e-6, ('snug chord wider than the V', sm)
        return [(w, s) for w, s in zip(hw, st)]+[(-w, s) for w, s in reversed(list(zip(hw, st)))]

    def add_snug(wedge, k, pl, outline):
        """Replace the wedge above the floor with the V-following body; keep holder's foot
        (in its pocket). The body may overhang the pocket's edge by a few tenths and sits on
        the floor top there."""
        foot = wedge.common(below(k, 0.0))
        body = to_tray(tool_frame_prism(outline, -30.0, 1.0), pl, k).cut(below(k, 0.0))
        return body.fuse(foot).removeSplitter()

    def add_nose(wedge, k, pl, pts, h0, h1, spec):
        """Pointed ogive nose ahead of the wedge's front (crotch-side) end. Its half-width
        closes 0.06 mm/mm faster than the V from the wedge's V-matched front, then
        quadratically to a rounded tip, so it stays inside the V everywhere and its point
        leads into the crotch."""
        S0, S1 = H.WEDGE_S
        L, rt = float(spec.get('length', 3.0)), float(spec.get('tip_r', 0.25))
        s = (H.gap(pts, S0)-H.gap(pts, S0-2.0))/4.0+0.06  # V half-width per mm at the nose, plus clearance
        L = min(L, 0.85*h0/s)                             # a narrow front gets a shorter nose
        rt = min(rt, 0.5*h0)
        c = (h0-s*L)/L**2
        assert c > 0, ('nose shorter than the V allows', h0, s, L)
        d_end = (-s+math.sqrt(s*s-4*c*(rt-h0)))/(2*c)     # where the half-width is rt
        n = 10
        side = [(h0-s*d-c*d*d, S0-d) for d in [d_end*i/n for i in range(n+1)]]
        tip = [(rt*math.cos(a), S0-d_end-rt*math.sin(a)) for a in [math.pi*i/6 for i in range(1, 6)]]
        back = h0+(h1-h0)*0.3/(S1-S0)
        outline = [(back-0.02, S0+0.3)]+side+tip+[(-tz, ty) for tz, ty in reversed(side)]+[(-back+0.02, S0+0.3)]
        for tz, ty in outline:
            if ty < S0-1e-9:
                margin = min(0.03, 0.03*(S0-ty))
                assert abs(tz) <= H.gap(pts, ty)/2-margin, ('nose wider than the V', ty, tz, H.gap(pts, ty))
        nose = to_tray(tool_frame_prism(outline, -30.0, 1.0), pl, k).cut(below(k, 0.0))
        state['notes']['nose'] = dict(length_mm=d_end+rt, tip_station_mm=S0-d_end-rt, tip_radius_mm=rt,
                                      v_half_slope_per_mm=s)
        return wedge.fuse(nose).removeSplitter()

    def add_tall(wedge, k, pl, outline, spec):
        """The same flanks (plan outline) carried up to a ridge at tool x = ridge_tx, roofed
        at roof_deg either side. The roof stays under 45 deg so the wedge still prints on its
        tool-right flank."""
        h0, h1 = outline[0][0], max(abs(tz) for tz, _ in outline)
        R, th = float(spec.get('ridge_tx', 3.4)), math.radians(float(spec.get('roof_deg', 40.0)))
        assert th <= math.radians(44.0), 'roof steeper than the side print allows'
        assert R-h1*math.tan(th) >= 1.0, 'roof would cut the v11p3 wedge'
        body = tool_frame_prism(outline, -30.0, R+5.0)
        for sgn in (1, -1):
            cutter = Part.makeBox(200, 200, 200, V(0, -100, -100))       # x >= 0
            cutter.rotate(V(0, 0, 0), V(0, 1, 0), -sgn*math.degrees(th))  # +x -> (cos, 0, sgn*sin)
            cutter.translate(V(R, 0, 0))
            body = body.cut(cutter)
        body = to_tray(body, pl, k).cut(below(k, 0.0))
        state['notes']['tall'] = dict(ridge_tool_x_mm=R, roof_deg=math.degrees(th),
                                      shoulder_tool_x_mm=[R-h0*math.tan(th), R-h1*math.tan(th)])
        return wedge.fuse(body).removeSplitter()

    # ---------------------------------------------------------------- shelf features
    def add_lip(parts, t, k, spec):
        """Extend the floor under the heel and stand a lip across it just behind the heel."""
        floor = parts[0]
        yf, yb0 = t['y_front'], t['y_back']
        h, gap = float(spec['h']), float(spec.get('gap', 0.6))
        back, ramp = math.radians(float(spec.get('back_deg', 75.0))), math.radians(float(spec.get('ramp_deg', 30.0)))
        top, ff = float(spec.get('top', 1.2)), float(spec.get('front_face', 0.8))
        yb = state['heel_y']+gap                       # foot of the stop face
        ext_len = yb+0.5-(yf-0.01)
        assert 0 < ext_len < yf-yb0
        ext = floor.common(H.box(-200, yb0, -400, 400, ext_len, 800))
        ext.translate(V(0, yf-0.01-yb0, 0))
        y_top0 = yb+h/math.tan(back)
        y_top1 = y_top0+top
        ye = y_top1+(h+tv-ff)/math.tan(ramp)
        prof = [(yb-0.5, -tv), (ye, -tv), (ye, -tv+ff), (y_top1, h), (y_top0, h), (yb, 0.0), (yb-0.5, 0.0)]
        lip = along_floor(k, prof, H.CHEEK_X+0.01, t['xmax'])
        parts += [ext, lip]
        t['y_front'] = ye
        t['lip'] = dict(height_mm=h, heel_y=state['heel_y'], stop_face_y=yb, stop_face_deg=math.degrees(back),
                        top_y=[y_top0, y_top1], ramp_deg=math.degrees(ramp), front_y=ye)

    def add_mouth(parts, t, k, spec):
        yf, xm = t['y_front'], t['xmax']
        r, L = math.radians(float(spec.get('ramp_deg', 30.0))), float(spec.get('ramp_len', 5.0))
        W, Lf = float(spec.get('flare_w', 4.0)), float(spec.get('flare_len', 15.0))
        if W > 0:
            sec = [(xm-0.01, 0.0), (xm+W, 0.0), (xm+W, -tv), (xm-0.01, -tv)]
            vs = [V(x, yf-Lf, H.floor_top(x, k)+dz) for x, dz in sec]
            slab = Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0, Lf+0.01, 0))
            tri = [V(xm-0.01, yf-Lf, -400), V(xm+W, yf+0.01, -400), V(xm-0.01, yf+0.01, -400)]
            slab = slab.common(Part.Face(Part.makePolygon(tri+[tri[0]])).extrude(V(0, 0, 800)))
            parts.append(slab)
        if 'lip' in t:
            L = 0.0                                    # the lip's own 30 deg ramp is the lead-in
        else:
            prof = [(yf-0.5, 0.0), (yf, 0.0), (yf+L, -L*math.tan(r)), (yf+L, -L*math.tan(r)-tv), (yf-0.5, -tv)]
            parts.append(along_floor(k, prof, H.CHEEK_X+0.01, xm+W))
        t['y_front'] = yf+L
        t['mouth'] = dict(floor_edge_y=yf, ramp_deg=math.degrees(r), ramp_front_y=yf+L, ramp_drop_mm=L*math.tan(r),
                          flare_w_mm=W, flare_from_y=yf-Lf, cheek_chamfer_mm=float(spec.get('cheek_chamfer', 0.0)))

    # ---------------------------------------------------------------- wrappers
    orig_tray, orig_cheek = H.tray, H.cheek

    def tray(k, pl, pts):
        parts, slot, wedge, t = orig_tray(k, pl, pts)
        state['pl'] = pl
        if state['heel_y'] is None:
            state['heel_y'] = max(pl.multVec(V(*q)).y for q in pts)
        h0, h1 = t['wedge_front_mm']/2, t['wedge_back_mm']/2
        S0, S1 = H.WEDGE_S
        outline = [(h0, S0), (h1, S1), (-h1, S1), (-h0, S0)]
        if 'snug' in p:
            outline = snug_outline(pts, h0, p['snug'])
            wedge = add_snug(wedge, k, pl, outline)
            state['notes']['snug'] = dict(relief_back_mm=float(p['snug'].get('relief', 0.1)),
                                          back_width_mm=2*max(abs(tz) for tz, _ in outline),
                                          holder_back_width_mm=2*h1)
        if 'nose' in p:
            wedge = add_nose(wedge, k, pl, pts, h0, h1, p['nose'])
        if 'tall' in p:
            wedge = add_tall(wedge, k, pl, outline, p['tall'])
        if 'lip' in p:
            add_lip(parts, t, k, p['lip'])
        if 'mouth' in p:
            add_mouth(parts, t, k, p['mouth'])
        assert wedge.isValid() and len(wedge.Solids) == 1, ('wedge', k)
        state['wedges'][k] = wedge
        return parts, slot, wedge, t

    def cheek(trays):
        shape = orig_cheek(trays)
        c = float(p.get('mouth', {}).get('cheek_chamfer', 0.0))
        if c > 0:
            # 45 deg chamfer on the cheek face's front edge, kept clear of the edge flanges.
            y1 = max(t['y_front'] for t in trays)
            z_hi = H.TOP_FLOOR_Z+24.0-5.0
            z_lo = H.floor_top(H.INNER, H.TRAYS-1)-tv-4.0-H.FLANGE_W-2.0+5.0
            tri = [V(H.INNER+0.01, y1+0.01, z_lo), V(H.INNER-c, y1+0.01, z_lo), V(H.INNER+0.01, y1-c-0.01, z_lo)]
            shape = shape.cut(Part.Face(Part.makePolygon(tri+[tri[0]])).extrude(V(0, 0, z_hi-z_lo)))
        return shape

    H.tray, H.cheek = tray, cheek

    if dry:
        _, pts = H.tool_points()
        pl, yaw = H.placement(pts)
        trays, extras = [], []
        for k in range(H.TRAYS):
            parts, slot, wedge, t = tray(k, pl, pts)
            extras += parts; trays.append(t)
            for s in parts+[slot, wedge]:
                assert s.isValid(), ('invalid', k)
        ch = cheek(trays)
        assert ch.isValid()
        print(json.dumps(dict(id=vid, params=p, yaw=yaw, heel_y=state['heel_y'], notes=state['notes'],
                              tray0=trays[0], wedge_volume=state['wedges'][0].Volume,
                              extras_volume=sum(s.Volume for s in extras), cheek_volume=ch.Volume), indent=1, default=str))
        return

    H.main(out)

    # ---------------------------------------------------------------- post: record the variant
    name = H.NAME
    dj = out/f'{name}__design.json'
    info = json.loads(dj.read_text())
    info['cant_deg'] = math.degrees(H.CANT)       # holder.main records 15.0 whatever CANT is
    info['lean_mm'] = H.LEAN
    info['wedge_back_relief_mm'] = H.WEDGE_BACK_RELIEF
    wedge_pose = 'tool-right flank on the bed (holder.main)'
    if 'nose' in p or 'snug' in p:
        # A nose or V-following flank is not one plane, so lying on the right flank would leave
        # facets hanging over the bed; lay this wedge on its flat top instead (every other face
        # then faces up or is vertical).
        w = state['wedges'][0].copy().transformGeometry(state['pl'].inverse().toMatrix())
        w = w.transformGeometry(A.Placement(V(), A.Rotation(V(1, 0, 0), V(0, 0, -1))).toMatrix())
        b = w.BoundBox
        w.translate(V(-b.XMin, -b.YMin, -b.ZMin))
        entry = H.write(w, out/f'{name}__wedge__print.stl', lin=0.005)
        info['files'] = [entry if f['file'] == entry['file'] else f for f in info['files']]
        wedge_pose = 'flat top on the bed (nose / V-following flank)'
    variant = dict(id=vid, base=base, params=p, name=name,
                   tactile=[TACTILE[k] for k in p if k in TACTILE] or [TACTILE['base']],
                   lean_mm=H.LEAN, ribs=H.RIBS, cant_deg=math.degrees(H.CANT), wedge_stations_mm=list(H.WEDGE_S),
                   wedge_back_relief_mm=H.WEDGE_BACK_RELIEF, wedge_print_pose=wedge_pose,
                   heel_y_mm=state['heel_y'], features=state['notes'],
                   trays=[{k: v for k, v in t.items()} for t in info['trays']])
    info['variant'] = variant
    dj.write_text(json.dumps(info, indent=1))
    (out/'variant.json').write_text(json.dumps(variant, indent=1))
    spec = dict(name=name, title='Tweezers v11.3 tactile variant %s' % vid, pose='right-cheek',
                installed=f'{name}__installed.stl', print=f'{name}__print-right-cheek.stl',
                glued=[f'{name}__wedge-{k}__installed.stl' for k in range(1, H.TRAYS+1)],
                tools=[dict(id='tweezers-%d' % k, stl=f'{name}__tool-{k}.stl', removal=[[0.3, 0, 6.5], [0, 130, 0]])
                       for k in range(1, H.TRAYS+1)])
    (out/f'{name}__checks-spec.json').write_text(json.dumps(spec, indent=1))
    print(json.dumps(dict(id=vid, name=name, params=p, out=str(out)), indent=1))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    build(args[0], args[1], args[2] if len(args) > 2 else None, dry='--dry' in sys.argv[1:])
