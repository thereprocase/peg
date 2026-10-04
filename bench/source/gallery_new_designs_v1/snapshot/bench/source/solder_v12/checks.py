"""Standard pre-print checks for a v12 solder module (run with cadpy: trimesh + numpy).

    cadpy checks.py BUILD_DIR NAME

Reads NAME__checks-spec.json (written by the module builder) and writes NAME__checks.json.
Every check is a number with a pass flag; the build is not printable unless all pass.

1. mesh: one watertight body.
2. overhangs in the print pose (and islands: features whose lowest point starts on air;
   and the same two checks on glued parts' own print STLs listed as 'glued_print'): faces steeper than 45 deg (normal z < -0.7071) above the
   bed, grouped into connected features. Pegs (installed Y < 0.15) are exempt. Any other
   feature fails unless the spec declares it as a bridge (flat, both ends anchored, span
   <= 10 mm) with a reason; declared bridges are re-measured here.
3. tool fit: sampled tool vertices inside the holder or glued parts (depth), so contacts
   read as ~0 and real clashes as millimetres.
4. seat: contacts within 0.2 mm, their spread, and whether the tool's centre of mass sits
   over the contact hull (gravity seat) when the spec says it rests by gravity.
5. removal: the spec's motion sequence (lift, slide, ...) sampled every <= 2 mm; minimum
   clearance to the holder and glued parts. Sliding contact (>= -0.15 mm) passes.
6. massing: volume and solid ASA grams.
"""
from pathlib import Path
import json
import sys

import numpy as np
import trimesh
from scipy.spatial import ConvexHull, Delaunay

PEG_Y = 0.15
CONTACT_MM = 0.2
CLASH_MM = -0.15          # deeper than this into the holder is a clash, not a contact


def load(p):
    m = trimesh.load(p, force='mesh')
    return m


def overhangs(pr, inv, exceptions):
    n, c, a = pr.face_normals, pr.triangles_center, pr.area_faces
    down = (n[:, 2] < -0.7071) & (c[:, 2] > 0.3)
    if inv is None:                                      # a glued part: nothing is exempt
        ci = c.copy(); peg = np.zeros(len(c), bool)
    else:
        ci = trimesh.transform_points(c, inv)           # back to installed coordinates
        peg = ci[:, 1] < PEG_Y
    idx = np.where(down & ~peg)[0]
    feats = []
    if len(idx):
        adj = pr.face_adjacency
        keep = np.isin(adj, idx).all(axis=1)
        groups = trimesh.graph.connected_components(adj[keep], nodes=idx, min_len=1)
        for g in groups:
            g = np.asarray(g)
            area = float(a[g].sum())
            if area < 0.5:                                  # tessellation slivers
                continue
            lo, hi = c[g].min(0), c[g].max(0)
            flat = float((n[g, 2]*a[g]).sum()/area)
            span = float(min(hi[0]-lo[0], hi[1]-lo[1]))
            lo_i, hi_i = ci[g].min(0), ci[g].max(0)
            f = dict(area_mm2=round(area, 2), print_bbox=[lo.round(1).tolist(), hi.round(1).tolist()],
                     installed_bbox=[lo_i.round(1).tolist(), hi_i.round(1).tolist()],
                     mean_normal_z=round(flat, 3), short_span_mm=round(span, 1))
            f['declared'] = None
            for e in exceptions:
                el, eh = np.array(e['installed_bbox'][0]), np.array(e['installed_bbox'][1])
                if (lo_i >= el-0.5).all() and (hi_i <= eh+0.5).all():
                    f['declared'] = e['why']
            f['ok'] = bool(f['declared'] and flat < -0.98 and span <= 10.0)
            feats.append(f)
    return dict(features=feats, peg_area_mm2=round(float(a[down & peg].sum()), 1),
                other_area_mm2=round(float(sum(f['area_mm2'] for f in feats)), 2),
                passed=all(f['ok'] for f in feats))


def islands(pr, inv):
    """Features whose lowest point starts in mid-air: vertices above the bed that are local
    minima (no neighbour lower) with air just below them (0.2 mm down is outside the part).
    A V-shaped underside of two 50 deg faces passes the face test but still starts on air
    along its bottom edge; this catches it. Pegs (installed Y < 0.15) are exempt."""
    v = pr.vertices; z = v[:, 2]
    nb = pr.vertex_neighbors
    cand = [i for i in range(len(v)) if z[i] > 0.3 and nb[i] and min(z[j] for j in nb[i]) >= z[i]-1e-4]
    if not cand:
        return dict(points=[], passed=True)
    cand = np.array(cand)
    below = v[cand]-[0, 0, 0.2]
    air = ~pr.contains(below)
    ci = trimesh.transform_points(v[cand], inv) if inv is not None else None
    keep = air & ((ci[:, 1] >= PEG_Y) if ci is not None else True)
    pts = cand[keep]
    groups = []
    if len(pts):
        sub = set(pts.tolist())
        edges = [(a, b) for a in pts.tolist() for b in nb[a] if b in sub]
        for g in trimesh.graph.connected_components(np.array(edges) if edges else np.zeros((0, 2), int), nodes=pts, min_len=1):
            g = np.asarray(g)
            q = v[g]
            groups.append(dict(print_xyz=q.mean(0).round(1).tolist(), vertices=int(len(g)),
                               installed_xyz=(trimesh.transform_points(q, inv).mean(0).round(1).tolist() if inv is not None else None)))
    return dict(points=groups, passed=not groups)


def sd(solids, p):
    """Max signed distance (positive inside) of points p over all solids."""
    return np.max([trimesh.proximity.signed_distance(s, p) for s in solids], axis=0)


def com(tool):
    hull = tool.convex_hull
    return hull.center_mass


def main(d, name):
    spec = json.loads((d/f'{name}__checks-spec.json').read_text())
    holder = load(d/spec['installed'])
    pr = load(d/spec['print'])
    M = np.array(spec['pose_matrix'], dtype=float).reshape(4, 4)
    inv = np.linalg.inv(M)
    glued = [load(d/g) for g in spec.get('glued', [])]
    solids = [holder]+glued
    rep = dict(name=name)
    bodies = holder.split(only_watertight=False)
    rep['mesh'] = dict(watertight=bool(holder.is_watertight), bodies=len(bodies),
                       volume_cm3=round(holder.volume/1000, 2), passed=bool(holder.is_watertight and len(bodies) == 1))
    moved = trimesh.transform_points(holder.vertices, M)
    err = float(np.abs(np.r_[moved.min(0)-pr.bounds[0], moved.max(0)-pr.bounds[1]]).max())
    rep['pose_matrix_error_mm'] = round(err, 4)
    assert err < 0.05, ('pose_matrix does not map the installed part onto the print STL', err)
    rep['overhangs'] = overhangs(pr, inv, spec.get('overhang_exceptions', []))
    rep['islands'] = islands(pr, inv)
    gp = []
    for g in spec.get('glued_print', []):             # glued parts' own print poses: no peg exemption
        gm = load(d/g)
        gp.append(dict(file=g, overhangs=overhangs(gm, None, []), islands=islands(gm, None)))
    rep['glued_print'] = gp
    rep['mass'] = dict(solid_asa_g=round(holder.volume/1000*1.07, 1),
                       glued_asa_g=round(sum(g.volume for g in glued)/1000*1.07, 1))
    tools = []
    for t in spec.get('tools', []):
        tm = load(d/t['stl'])
        v = tm.vertices
        stride = max(1, len(v)//int(t.get('samples', 2500)))
        vs = v[::stride]                                   # removal sweep only
        dist = sd(solids, v)                               # +inside; every vertex, so no contact line aliases away
        r = dict(id=t['id'], sampled=len(v), deepest_mm=round(float(dist.max()), 3))
        r['fit_passed'] = bool(dist.max() <= -CLASH_MM)
        near = v[np.abs(dist) <= CONTACT_MM]
        r['contacts'] = int(len(near))
        if len(near):
            r['contact_bbox'] = [near.min(0).round(1).tolist(), near.max(0).round(1).tolist()]
        seat = t.get('seat', {})
        if seat.get('gravity'):
            cm = com(tm)
            ok = False
            if len(near) >= 3:
                try:
                    hull = Delaunay(near[:, :2])
                    ok = bool(hull.find_simplex(cm[:2]) >= 0)
                except Exception:
                    ok = False
            r['com'] = cm.round(1).tolist()
            r['com_over_contacts'] = ok
            r['seat_passed'] = ok or bool(seat.get('captured'))
        else:
            r['seat_passed'] = r['contacts'] >= seat.get('min_contacts', 1)
        # Removal: piecewise-linear moves from the rest pose.
        if t.get('removal'):
            pos = np.zeros(3); worst, at = 1e9, None
            for move in t['removal']:
                vec = np.array(move, dtype=float); L = np.linalg.norm(vec)
                steps = max(1, int(np.ceil(L/2.0)))
                for i in range(1, steps+1):
                    p = pos+vec*i/steps
                    dd = sd(solids, vs+p)
                    clr = -float(dd.max())
                    if clr < worst:
                        worst, at = clr, p.round(1).tolist()
                pos = pos+vec
            r['removal'] = dict(moves=t['removal'], min_clearance_mm=round(worst, 3), at_offset=at,
                                passed=bool(worst >= CLASH_MM))
        tools.append(r)
    rep['tools'] = tools
    rep['passed'] = bool(rep['mesh']['passed'] and rep['overhangs']['passed'] and rep['islands']['passed'] and
                         all(g['overhangs']['passed'] and g['islands']['passed'] for g in gp) and
                         all(t['fit_passed'] and t['seat_passed'] and t.get('removal', {}).get('passed', True) for t in tools))
    (d/f'{name}__checks.json').write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
    return rep


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2])
