"""Compact sunburst under a shelf ("sunray" study).

Owner requirement (2026-10-07): a 3" (76.2 mm) deep object may sit 2" (50.8 mm) above the top of the
loaded rack, and every tool must still come out. Keep-out box K: y <= 76.2, z >= Z_TOP + 50.8, all x.
Goal: the least depth off the board (max y of the rack and stored tools).

Installed frame: x = user's left, y = out from the board, z = up, mm. Z_TOP = 0 is the highest stored
point; nothing stored may rise above it.

L-keys have to slide out by their whole socket depth, so each axis is a ray passing just under the
keep-out's front edge (Q). Each key is tilted only as far as it must be for its tip to sit at the board
wall. The rays fan up toward Q: a sunburst in side view. Torx and hex alternate in x (comb.py), so a hex
key's path runs past the Torx tubes and Torx short arms in the gaps. T-handles stand in front of the lower
comb; they lift out of their sockets, then leave forward. Their sockets aim at one hub (sunburst from the
front).
"""
import math, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import comb

INCH = 25.4
SHELF_DEPTH, SHELF_GAP = 3*INCH, 2*INCH
Z_TOP = 0.
Z_K = Z_TOP+SHELF_GAP
STEP = 5.
C_SWEEP = 3.          # tool to tool / body while moving
C_STORE = 1.5
C_SHELF = 4.          # tool to the keep-out while moving
BAR_R = 9.            # T-handle grip radius (ASSUMED 18 mm grip)
BOSS_WALL = 3.
WALL = 3.
BOARD = .15           # board face of the receiver
HEIGHT_MAX = 248.     # P1S bed (right-cheek print puts the rack's height on the bed)
Z_BOT = Z_TOP-HEIGHT_MAX
HALF = 25.4*8/2-1
import os
FRONT_MODE = os.environ.get('SUNRAY_FRONT', '0') == '1'
TEE = [(t['across_flats'], t['overall'], t['handle_length']) for t in comb.TEES]


def unit(v): v = np.asarray(v, float); return v/np.linalg.norm(v)


def seg(p0, p1, r, step=STEP):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    n = max(2, int(math.ceil(np.linalg.norm(p1-p0)/step))+1)
    t = np.linspace(0, 1, n)[:, None]
    return p0+(p1-p0)*t, np.full(n, float(r))


def cat(parts):
    return np.vstack([p for p, _ in parts]), np.concatenate([r for _, r in parts])


def sweep(pts, rr, d, n):
    ts = np.linspace(0, 1, n)
    return np.vstack([pts+d*t for t in ts]), np.tile(rr, n)


def shelf_pen(pts, rr, c=C_SHELF):
    a = SHELF_DEPTH+c-(pts[:, 1]-rr)
    b = pts[:, 2]+rr-(Z_K-c)
    m = np.minimum(a, b)
    return float(np.sum(m[m > 0]))


def hit_tree(tree, rr_tree, rmax_tree, pts, rr, c):
    if len(pts) == 0:
        return 0.
    d, idx = tree.query(pts, k=4, distance_upper_bound=rr.max()+rmax_tree+c)
    ok = np.isfinite(d)
    if not ok.any():
        return 0.
    idx2 = np.where(ok, idx, 0)
    pen = rr[:, None]+rr_tree[idx2]+c-d
    return float(np.sum(np.where(ok & (pen > 0), pen, 0)))


# ------------------------------------------------------------------ L-keys on rays under the shelf edge
def q_point(r):
    """Corner of the keep-out grown by clearance + key radius: the key axis must pass in front of it."""
    return SHELF_DEPTH+C_SHELF+r+.5, Z_K-C_SHELF-r


def solve_tilt(z_m, L, r, bore):
    """Tilt from vertical so the axis passes y_Q at Z_K and the tip (mouth - L along the axis) sits at the
    board wall. Returns theta (rad)."""
    yq, zq = q_point(r)
    yb = BOARD+WALL+bore
    f = lambda th: yq-(zq-z_m)*math.tan(th)-L*math.sin(th)-yb
    lo, hi = 0., math.radians(80)
    for _ in range(60):
        mid = (lo+hi)/2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return (lo+hi)/2


def lkey(x, z_m, th, L, short, r):
    u = np.array([0, math.sin(th), math.cos(th)]); n = np.array([0, math.cos(th), -math.sin(th)])
    rb = max(2*r, 3.)
    yq, zq = q_point(r)
    m = np.array([x, yq-(zq-z_m)*math.tan(th), z_m])
    tip = m-u*L; top = m+u*rb
    bend = top+n*rb*.3
    pts = cat([seg(tip, top, r), seg(bend, bend+n*(short-r), r)])
    return dict(mouth=m, tip=tip, u=u, n=n, pts=pts, L=L, r=r)


def l_layout(z_t, z_h, extra=0.):
    xs, kind, _ = comb.layout(extra)
    s = (HALF-4.)/max(abs(v) for v in xs)
    xs = [v*s for v in xs]
    keys = []
    for x, (kd, i) in zip(xs, kind):
        if kd == 'hex':
            h = comb.HEX[i]; L = h['straight_length']; r = comb.hex_key_r(i); bore = comb.hex_bore(i); z = z_h; sh = h['short_arm_assumed']
        else:
            t = comb.TORX[i]; L = t['socket_depth']; r = comb.torx_key_r(i); bore = comb.torx_bore(i); z = z_t; sh = t['short_arm_assumed']
        th = solve_tilt(z, L, r, bore)
        k = lkey(x, z, th, L, sh, r)
        k.update(kind=kd, i=i, bore=bore, theta=math.degrees(th), short=sh)
        keys.append(k)
    if FRONT_MODE:
        # every key except the depth-setting one stands as upright as the common depth allows:
        # its tip leaves the board, so the wedge behind it can be hollowed
        front = lambda k: float(np.max(k['pts'][0][:, 1]+k['pts'][1]))
        dmax = max(front(k) for k in keys)-1.
        out = []
        for k in keys:
            if front(k) >= dmax:
                out.append(k); continue
            lo, hi = 0., math.radians(k['theta'])
            for _ in range(40):
                mid = (lo+hi)/2
                kk = lkey(k['mouth'][0], k['mouth'][2], mid, k['L'], k['short'], k['r'])
                if front(kk) > dmax: lo = mid
                else: hi = mid
            kk = lkey(k['mouth'][0], k['mouth'][2], hi, k['L'], k['short'], k['r'])
            kk.update(kind=k['kind'], i=k['i'], bore=k['bore'], theta=math.degrees(hi), short=k['short'])
            out.append(kk)
        keys = out
    return keys


def segdist(p1, q1, p2, q2):
    d1 = q1-p1; d2 = q2-p2; r = p1-p2; a = d1@d1; e = d2@d2; f = d2@r
    c = d1@r; b = d1@d2; den = a*e-b*b
    s = np.clip((b*f-c*e)/den, 0, 1) if den > 1e-12 else 0.
    t = (b*s+f)/e
    if t < 0: t = 0; s = np.clip(-c/a, 0, 1)
    elif t > 1: t = 1; s = np.clip((b-c)/a, 0, 1)
    return float(np.linalg.norm(p1+d1*s-(p2+d2*t)))


SWEEP40 = math.radians(40)


def prism_halfplanes(k, w):
    """The CAD pipe section (build.pipe_profile): lens arc +/-40 deg plus its tangents, as half-planes
    (unit normal, offset) in the section's (s = x, t = outward normal) coordinates."""
    c = k['bore']+WALL; R = max(c, w/math.sin(SWEEP40))
    arc = [(R*math.sin(math.radians(40*i/8)), (c-R)+R*math.cos(math.radians(40*i/8))) for i in range(-8, 9)]
    ext = 260.
    hi = (arc[-1][0]+ext*math.cos(SWEEP40), arc[-1][1]-ext*math.sin(SWEEP40))
    lo = (arc[0][0]-ext*math.cos(SWEEP40), arc[0][1]-ext*math.sin(SWEEP40))
    poly = np.array([lo]+arc+[hi, (hi[0], -ext*1.5), (lo[0], -ext*1.5)])
    cen = poly.mean(axis=0); N, O = [], []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]; e = b-a; L = np.linalg.norm(e)
        if L < 1e-9: continue
        nrm = np.array([e[1], -e[0]])/L
        if (cen-a)@nrm > 0: nrm = -nrm          # outward
        N.append(nrm); O.append(nrm@a)
    return np.array(N), np.array(O)


def pipe_cloud(k, tube=None):
    """Pipe (bore + wall) from the floor to the mouth, plus the web straight back to the board."""
    R = k['bore']+(WALL if tube is None else tube)
    a = k['tip']-k['u']*comb.FLOOR; b = k['mouth']
    parts = []
    for f in np.linspace(0, 1, 6):
        sh = np.array([0, -1., 0])*f
        parts.append(seg(a+sh*max(0, a[1]-BOARD-R), b+sh*max(0, b[1]-BOARD-R), R, step=max(2., R*.6)))
    return cat(parts)


# ------------------------------------------------------------------ T-handle fan
def tee_geom(params):
    hub = np.asarray(params.get('hub', (0, 0, 0)), float)
    out = []
    for k, (af, over, bar) in enumerate(TEE):
        a, ph = math.radians(params['a'][k]), math.radians(params['phi'][k])
        axis = unit([math.sin(a)*math.cos(ph), math.sin(ph), math.cos(a)*math.cos(ph)])
        tip = np.asarray(params['tips'][k], float) if 'tips' in params else hub+axis*params['rho']
        d = params['d'][k]
        mouth = tip+axis*d
        r = af/math.sqrt(3)
        top = tip+axis*(over-BAR_R)
        b0 = unit(np.cross(axis, [0, 1, 0]))          # grip flat to the board
        psi = math.radians(params.get('psi', [0]*8)[k])  # 'prom portrait' turn about the shaft
        bdir = unit(b0*math.cos(psi)+np.cross(axis, b0)*math.sin(psi))
        pts, rr = cat([seg(tip, top, r), seg(top-bdir*(bar/2-BAR_R), top+bdir*(bar/2-BAR_R), BAR_R)])
        out.append(dict(k=k, axis=axis, tip=tip, mouth=mouth, d=d, top=top, bdir=bdir, pts=pts, rr=rr,
                        bore=r+comb.CLEAR+.15, bar=bar))
    return out


def boss_cloud(t):
    R = t['bore']+BOSS_WALL
    a = t['tip']-t['axis']*comb.FLOOR; b = t['mouth']
    parts = []
    for f in np.linspace(0, 1, 6):
        sh = np.array([0, -1., 0])*f
        parts.append(seg(a+sh*max(0, a[1]-BOARD-R), b+sh*max(0, b[1]-BOARD-R), R, step=max(2., R*.6)))
    return cat(parts)


ESCAPES = [np.array([0, 1., 0]), None, unit([0, 1, .4])]


class Scene:
    def __init__(self, z_t, z_h, extra=0.):
        self.keys = l_layout(z_t, z_h, extra)
        self.z_t, self.z_h = z_t, z_h
        self.L_STORED = cat([k['pts'] for k in self.keys])
        self.pipes = [pipe_cloud(k) for k in self.keys]
        sw = []
        for k in self.keys:
            sw.append(sweep(*k['pts'], k['u']*(k['L']+6.), int((k['L']+6)/STEP)+1))
        self.sweeps = sw
        self.L_SWEPT = cat(sw)
        self.tree_L = cKDTree(self.L_STORED[0]); self.tree_LS = cKDTree(self.L_SWEPT[0])
        self.body = cat(self.pipes); self.tree_B = cKDTree(self.body[0])
        xs = [k['mouth'][0] for k in self.keys]; self.prisms = []
        for j, k in enumerate(self.keys):
            left = (xs[j-1]-xs[j])/2 if j > 0 else HALF-xs[j]
            right = (xs[j]-xs[j+1])/2 if j < len(xs)-1 else xs[j]+HALF
            N, O = prism_halfplanes(k, min(max(left, right), 12.))
            self.prisms.append((k['tip']-k['u']*comb.FLOOR, k['n'], k['u'], k['L']+comb.FLOOR, N, O))
        self.rmax = max(self.L_STORED[1].max(), 1.)

    def body_sdf(self, p):
        """Signed distance (conservative outside) to the CAD comb body: union of pipe prisms inside the envelope."""
        d = np.full(len(p), 1e9)
        X1 = np.array([1., 0, 0])
        for a0, n, u, Lk, N, O in self.prisms:
            q = p-a0
            st = np.stack([q@X1, q@n], 1)
            d2 = (st@N.T-O).max(axis=1)
            ax = q@u
            d = np.minimum(d, np.maximum(d2, np.maximum(-ax, ax-Lk)))
        env = np.maximum.reduce([BOARD+.05-p[:, 1], p[:, 2]-(Z_TOP-.6), np.abs(p[:, 0])-HALF, Z_BOT-p[:, 2]])
        return np.maximum(d, env)

    def body_pen(self, p, r, c):
        if len(p) == 0:
            return 0.
        return float(np.sum(np.maximum(0, r+c-self.body_sdf(p))))

    def l_report(self):
        """L-key checks: each sweep vs the shelf, vs other stored keys, vs other pipes (with webs)."""
        rows = []
        for j, (k, (sp, sr)) in enumerate(zip(self.keys, self.sweeps)):
            others = cat([self.keys[i]['pts'] for i in range(len(self.keys)) if i != j])
            ob = cat([self.pipes[i] for i in range(len(self.keys)) if i != j])
            t1 = cKDTree(others[0]); t2 = cKDTree(ob[0])
            out = (sp-k['mouth'])@k['u'] > 0          # below its own mouth a key is inside its own bore
            wall = min(segdist(k['tip'], k['mouth'], o['tip'], o['mouth'])-k['bore']-o['bore']
                       for i, o in enumerate(self.keys) if i != j)
            rows.append(dict(kind=k['kind'], i=k['i'], theta=round(k['theta'], 1),
                             mouth=k['mouth'].round(1).tolist(), tip=k['tip'].round(1).tolist(),
                             shelf=round(shelf_pen(sp, sr), 1),
                             tools=round(hit_tree(t1, others[1], others[1].max(), sp, sr, C_SWEEP), 1),
                             body=round(hit_tree(t2, ob[1], ob[1].max(), sp[out], sr[out], C_SWEEP), 1),
                             bore_wall=round(wall, 2)))
        return rows

    def l_depth(self):
        p, r = self.L_STORED
        bp, br = self.body
        return float(max(np.max(p[:, 1]+r), np.max(bp[:, 1]+br)))

    def evaluate(self, params, detail=False):
        T = tee_geom(params)
        clouds = [boss_cloud(t) for t in T]
        pen = dict(store=0., sweep=0., body=0., order=0., env=0., shelf=0.)
        rep = []
        n = len(T)
        obs = []
        for t in T:
            op, orr = cat([(o['pts'], o['rr']) for o in T if o['k'] != t['k']]+[clouds[j] for j in range(n) if j != t['k']])
            obs.append((cKDTree(op), orr, orr.max()))
        bp, br = self.body
        for t in T:
            tree, orr, rmax = obs[t['k']]
            p = self.body_pen(t['pts'], t['rr'], C_STORE)
            p += hit_tree(self.tree_LS, self.L_SWEPT[1], self.rmax, t['pts'], t['rr'], C_STORE)
            p += .5*hit_tree(tree, orr, rmax, t['pts'], t['rr'], C_STORE)
            pen['store'] += p
        for cp, cr in clouds:
            pen['body'] += hit_tree(self.tree_LS, self.L_SWEPT[1], self.rmax, cp, cr, C_SWEEP)

        def cost(tree, orr, rmax, p, r):
            c = hit_tree(tree, orr, rmax, p, r, C_SWEEP)+hit_tree(self.tree_L, self.L_STORED[1], self.rmax, p, r, C_SWEEP)
            c += float(np.sum(np.maximum(0, BOARD+C_SWEEP-(p[:, 1]-r))))       # the board is solid
            return c+self.body_pen(p, r, C_SWEEP)+shelf_pen(p, r)
        for t in T:
            tree, orr, rmax = obs[t['k']]
            lift = t['axis']*(t['d']+4.)
            sp, sr = sweep(t['pts'], t['rr'], lift, max(2, int((t['d']+4)/STEP)+1))
            base = cost(tree, orr, rmax, sp, sr)
            best, which = 1e9, None
            for e_i, e in enumerate(ESCAPES):
                dvec = (t['axis'] if e is None else e)*260.
                ep, er = sweep(t['pts']+lift, t['rr'], dvec, 27)
                c = cost(tree, orr, rmax, ep, er)
                if c < best:
                    best, which = c, e_i
                if c == 0:
                    break
            pen['sweep'] += base+best
            rep.append(dict(tool=TEE[t['k']][0], lift_pen=round(base, 2), escape=['forward', 'axis', 'up-forward'][which], escape_pen=round(best, 2)))
        xs = [t['top'][0] for t in T]
        for i in range(n-1):
            pen['order'] += max(0., xs[i+1]-xs[i]+8.)
        allp = np.vstack([t['pts'] for t in T]); allr = np.concatenate([t['rr'] for t in T])
        pen['env'] += float(np.sum(np.maximum(0, np.abs(allp[:, 0])+allr-params.get('xenv', 130.))))
        pen['env'] += float(np.sum(np.maximum(0, Z_BOT-(allp[:, 2]-allr))))
        pen['env'] += float(np.sum(np.maximum(0, allp[:, 2]+allr-Z_TOP)))
        pen['env'] += float(np.sum(np.maximum(0, BOARD+C_STORE-(allp[:, 1]-allr))))
        for t in T:                                        # every handle points at least 5 deg above horizontal
            pen['env'] += 200*max(0., math.sin(math.radians(5))-t['axis'][2])
        for t in T:                                        # sockets attach inside the rack width, in front of the board
            for q in (t['tip'], t['mouth']):
                pen['env'] += 5*max(0., abs(q[0])-(HALF-2))+5*max(0., BOARD+WALL+t['bore']-q[1])
        for cp, cr in clouds:
            pen['env'] += float(np.sum(np.maximum(0, Z_BOT-(cp[:, 2]-cr))))
            pen['env'] += float(np.sum(np.maximum(0, BOARD-.01-(cp[:, 1]-cr))))
        cy = max(float(np.max(cp[:, 1]+cr)) for cp, cr in clouds)
        depth = max(float(np.max(allp[:, 1]+allr)), cy, self.l_depth())
        xspan = float(np.max(allp[:, 0]+allr)-np.min(allp[:, 0]-allr))
        total = depth+.05*xspan+10*sum(pen.values())
        if detail:
            return total, depth, pen, rep, T
        return total


if __name__ == '__main__':
    for z_t, z_h in [(-10, -30), (-10, -36), (-12, -40)]:
        S = Scene(z_t, z_h)
        bp = S.body[0]; zmin = float(bp[:, 2].min()); zmax = float(np.max(S.L_STORED[0][:, 2]+S.L_STORED[1]))
        print('z_t %g z_h %g  L depth %.1f  body z %.1f..  stored top %.1f' % (z_t, z_h, S.l_depth(), zmin, zmax))
        bad = [r for r in S.l_report() if r['shelf'] or r['tools'] or r['body']]
        for r in S.l_report():
            print('  ', r['kind'], r['i'], r['theta'], r['mouth'][1:], r['tip'][1:], r['shelf'], r['tools'], r['body'], r['bore_wall'])
