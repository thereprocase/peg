"""Exact (OCC) checks on an HX04 build: every tool's way out against the holder, the other stored tools
and the shelf keep-out; floors under every socket. Run with FreeCAD's Python:
    python check.py <outdir>
"""
from pathlib import Path
import json, math, sys, time
import importlib.util
_sp = importlib.util.spec_from_file_location('hx04_build', Path(__file__).with_name(__import__('os').environ.get('HX4_BUILD', 'build_short.py')))
H = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(H)
import FreeCAD as A
import Part
V = A.Vector
INCH = 25.4


def floors(shape, seats):
    """Thinnest material under each socket: probed along the axis at the centre and at 8 points around the
    floor rim (the floor is slanted for the print, the bore flares and pinched tools get a corner seat)."""
    out = []
    for st in seats:
        axis = V(*st['axis']); base = V(*st['mouth'])-axis*st['depth']
        a = axis.cross(V(1, 0, 0)) if abs(axis.x) < .9 else axis.cross(V(0, 1, 0)); a.normalize(); b = axis.cross(a)
        rf = .9*st.get('radius_floor', st['radius'])
        best = None
        for k in range(9):
            off = V(0, 0, 0) if k == 0 else (a*math.cos(k*math.pi/4)+b*math.sin(k*math.pi/4))*rf
            q = base+off
            seg = shape.common(Part.makeLine(q+axis*25, q-axis*80))      # material along -axis past the bore
            # first solid run that starts past the bore's own depth: skip runs that end above the floor
            runs = []
            for e in seg.Edges:
                ds = sorted(((vx.Point-(q+axis*25)).dot(axis*-1)) for vx in e.Vertexes)
                runs.append(ds)
            runs = [r for r in runs if r[-1] > 25.5]
            first = min(runs, key=lambda r: r[0]) if runs else None
            th = round(first[-1]-max(first[0], 25.), 2) if first else 0.
            best = th if best is None else min(best, th)
        out.append(best)
    return out


def path_of(st):
    """List of displacement vectors (piecewise straight) for the tool's way out."""
    axis = V(*st['axis'])
    ex = st['exit']
    if ex['kind'] == 'axis':
        return [axis*ex['distance_mm'], axis*120.]
    lift = axis*ex['lift_mm']
    tail = ex['kind'].split('-then-')[1]
    d = {'forward': V(0, 1, 0), 'axis': axis, 'up-forward': V(0, 1, .4)}[tail]
    d.normalize()
    return [lift, d*160.]


def sweep_check(shape, tools, seats, shelf, step=float(__import__('os').environ.get('CHECK_STEP', 3.)), movers=None):
    """tools: every tool as stored (the obstacles); movers: the shape each one is drawn out as (default: as stored)."""
    rows = []
    for i, (tool, st) in enumerate(zip(movers or tools, seats)):
        if st['exit']['kind'] != 'axis':
            lo, hi = min(st['depth']+3., st['exit']['lift_mm']), st['exit']['lift_mm']
            tries = sorted({round(lo, 2), round((lo+hi)/2, 2), round(hi, 2)})
            res = None
            for lf in tries:
                st2 = dict(st, exit=dict(st['exit'], lift_mm=lf))
                r = one(shape, tools, i, tool, st2, shelf, step)
                if res is None or r['ok']:
                    res = r
                if r['ok']:
                    break
            res['lift_mm'] = lf
            if not res['ok']:                       # the user can take it out any of the three ways
                for alt in ('forward', 'up-forward', 'axis'):
                    st2 = dict(st, exit=dict(st['exit'], kind='lift-then-'+alt))
                    for lf in tries:
                        st2['exit']['lift_mm'] = lf
                        r = one(shape, tools, i, tool, st2, shelf, step)
                        if r['ok']:
                            res = r; res['lift_mm'] = lf; break
                    if res['ok']:
                        break
            rows.append(res); print(res, flush=True)
            continue
        rows.append(one(shape, tools, i, tool, st, shelf, step)); print(rows[-1], flush=True)
    return rows


def one(shape, tools, i, tool, st, shelf, step):
    if True:
        legs = path_of(st)
        pos = [V(0, 0, 0)]
        for leg in legs:
            n = max(1, math.ceil(leg.Length/step))
            base = pos[-1]
            pos += [base+leg*(k/n) for k in range(1, n+1)]
        bb = tool.BoundBox
        for p in pos[::max(1, len(pos)//6)]+[pos[-1]]:
            m = tool.copy(); m.translate(p); bb.add(m.BoundBox)
        bb.enlarge(3)
        clip = shape.common(H.B.box(bb.XMin, bb.YMin, bb.ZMin, bb.XLength, bb.YLength, bb.ZLength))
        near = [j for j, o in enumerate(tools) if j != i and o.BoundBox.intersect(bb)]
        body = nb = sh = 0.; first = None
        for p in pos[1:]:
            m = tool.copy(); m.translate(p)
            vb = clip.common(m).Volume if clip.BoundBox.intersect(m.BoundBox) else 0.
            vn = 0.
            for j in near:
                if tools[j].BoundBox.intersect(m.BoundBox):
                    vn = max(vn, tools[j].common(m).Volume)
            vs = shelf.common(m).Volume if shelf.BoundBox.intersect(m.BoundBox) else 0.
            if (vb > 1e-4 or vn > 1e-4 or vs > 1e-4) and first is None:
                first = [round(c, 1) for c in p]
            body, nb, sh = max(body, vb), max(nb, vn), max(sh, vs)
        return dict(set=st['set'], size=st['size'], exit=st['exit']['kind'], body_mm3=round(body, 4), tools_mm3=round(nb, 4),
                    shelf_mm3=round(sh, 4), first_hit_offset=first, ok=body < 1e-3 and nb < 1e-3 and sh < 1e-3)


if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    g = H.build()
    shape, tools, seats = g['shape'], g['tools'], g['seats']
    movers = None; settle = []
    if 'Lo' in g:                                   # short-socket build: study tool envelopes and planned exits
        tools = H.ref_tool_list(g['Lo'])            # stored: each tool in its gravity rest pose (leaning)
        # drawing a tool out starts by straightening it: it swings from its rest lean back to the socket axis
        # (its tip leaves the seat and the flare), then lifts. Checked as poses part-way and fully upright,
        # against the holder and every other tool at rest; the lift and the way out start from upright.
        cock = H.SH.COCK; H.SH.COCK = False
        try:
            Ln = H.SH.Layout(H.LAYOUT['x'])
        finally:
            H.SH.COCK = cock
        movers = H.ref_tool_list(Ln)
        for f in (1/3, 2/3, 1.):
            class _L: pass
            Lm = _L(); Lm.tools = [dict(tr, pts=tr['pts']+f*(tn['pts']-tr['pts'])) for tr, tn in zip(g['Lo'].tools, Ln.tools)]
            settle.append(H.ref_tool_list(Lm))
        rep = H.LAYOUT.get('rep') or H.SH.evaluate(H.LAYOUT['x'], True)[4]
        for st, r_, t in zip(seats, rep, g['Lo'].tools):
            esc = r_['escape']
            st['exit'] = dict(kind='lift-then-'+esc, lift_mm=t['D']+3.)
            st['depth'] = t['D']
    top = max(t.BoundBox.ZMax for t in tools)
    shelf = H.B.box(-400, -50, top+2*INCH, 800, 50+3*INCH, 200)      # 3" deep, its underside 2" above the loaded rack
    stored = []
    for i, t in enumerate(tools):
        hit = shape.common(t).Volume
        others = max((t.common(o).Volume for j, o in enumerate(tools) if j != i and t.BoundBox.intersect(o.BoundBox)), default=0.)
        stored.append(dict(set=seats[i]['set'], size=seats[i]['size'], body_mm3=round(hit, 4), tools_mm3=round(others, 4)))
    for k, pose in enumerate(settle):
        for i, t in enumerate(pose):
            hit = shape.common(t).Volume
            others = max((t.common(o).Volume for j, o in enumerate(tools) if j != i and t.BoundBox.intersect(o.BoundBox)), default=0.)
            if hit > 1e-3 or others > 1e-3:
                stored[i].setdefault('straighten', []).append(dict(step=k+1, body_mm3=round(hit, 4), tools_mm3=round(others, 4)))
    fl = floors(shape, seats)
    rows = sweep_check(shape, tools, seats, shelf, movers=movers)
    rep = dict(stored_top_z=round(top, 2), body_top_z=round(shape.BoundBox.ZMax, 2), depth_mm=round(max(shape.BoundBox.YMax, max(t.BoundBox.YMax for t in tools)), 2),
               floors_mm=fl, stored=stored, routes=rows, all_routes_ok=all(r['ok'] for r in rows),
               stored_ok=all(s['body_mm3'] < 1e-3 and s['tools_mm3'] < 1e-3 for s in stored),
               straighten_ok=not any('straighten' in s for s in stored), seconds=round(time.time()-t0))
    (out/'checks.json').write_text(json.dumps(rep, indent=1), encoding='utf-8', newline='\n')
    print(json.dumps({k: rep[k] for k in ('stored_top_z', 'body_top_z', 'depth_mm', 'floors_mm', 'all_routes_ok', 'stored_ok', 'straighten_ok', 'seconds')}), flush=True)
