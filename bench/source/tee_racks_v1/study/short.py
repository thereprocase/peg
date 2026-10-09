"""HX05 shaft-guiding layout study.
Owner rule: at least 40 mm straight guide, increasing to 8x shaft size for larger tools,
plus a separate 0.8 mm entrance chamfer. Full hex sections, 0.10 mm per-flat clearance,
flat-to-flat T-bars and square floors replace the short flared seating chamber.
Stored tools and sampled removal paths are checked against neighbors, the holder and
an overhead shelf (76.2 mm deep, 50.8 mm above the highest stored point).
"""
import math, os, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import comb
from socket_policy import burial_depth, ENTRY_LEAD_MM, HEX_CLEARANCE_PER_FLAT_MM
from sunray import seg as _segment, cat, sweep, unit, TEE, BAR_R, BOARD, HALF


def seg(p0, p1, r, step=None):
    # Keep HX04's 5 mm tool cloud; HX05 can request denser stored envelopes.
    return _segment(p0, p1, r, step=float(os.environ.get('SHORT_POINT_STEP', 5.)) if step is None else step)


def hit_tree(tree, rr_tree, rmax_tree, pts, rr, c):
    """Sum of penetrations, checking every pair within reach (vectorized; mixed radii safe)."""
    if len(pts) == 0:
        return 0.
    mt = cKDTree(pts)
    pairs = mt.sparse_distance_matrix(tree, float(rr.max()+rmax_tree+c), output_type='ndarray')
    if len(pairs) == 0:
        return 0.
    pen = rr[pairs['i']]+rr_tree[pairs['j']]+c-pairs['v']
    return float(pen[pen > 0].sum())


INCH = 25.4
CELLS = int(os.environ.get('SHORT_CELLS', 8))
HALF = 25.4*CELLS/2-1                                   # owner, 2026-10-08: footprint as wide as the T fan
HALF = float(os.environ.get('SHORT_PLATE_HALF', HALF))  # ... shaved 5-10 mm a side, the fan a little over
SPREAD = float(os.environ.get('SHORT_SPREAD', 0))      # Torx and hex rows: mouths spread at least this far in x
SHELF_DEPTH, SHELF_GAP = 3*INCH, 2*INCH
STEP = float(os.environ.get('SHORT_STEP', 2.5))
C_SWEEP, C_STORE, C_SHELF = 3., 1.5, 3.
WALL, FLOOR = 3., 3.
DV, SF, G, MU = .20, 2., 9.81, .25
H_MAX = float(os.environ.get('SHORT_HMAX', 248))


KD = float(os.environ.get('SHORT_KD', 4.))      # owner, 2026-10-08: 'minimum seat depth is 4x key'
# T-handle grip turn (owner, 2026-10-08: 'socket shapes to encourage ideal positions at rest'). A T-handle has no
# preferred turn under gravity (the bar is symmetric about the shaft), so a hex-keyed bore clocks it; it still
# turns by the bore's play. TEE_HEX_C = clearance per flat; TPSI_OFF = per-handle turn used by evaluate().
TEE_HEX_C = HEX_CLEARANCE_PER_FLAT_MM
TEE_KEYED_MIN = 0.                                      # full-depth hex guidance includes small keys
# HX05 (owner, 2026-10-08): single-set T-handle racks. SHORT_TEE_SET = a JSON list of dict(name, af, overall, bar)
# replaces the T fan's tools (af: hex across flats; a Torx shaft enters as 0.866 x point-to-point, the hex whose
# corners hold its lobes); SHORT_TONLY=1 drops the two L-key rows.
TONLY = os.environ.get('SHORT_TONLY', '0') == '1'
SETS = ('tee',) if TONLY else ('torx', 'hex', 'tee')
TEE_NAMES = ['%g' % t[0] for t in TEE]
TEE_SEAT_SIZE = [t[0] for t in TEE]
if os.environ.get('SHORT_TEE_SET'):
    _ts = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ['SHORT_TEE_SET'])).read())
    TEE[:] = [(t['af'], t['overall'], t['bar']) for t in _ts]; TEE_NAMES = [t['name'] for t in _ts]
    TEE_SEAT_SIZE = [t.get('p2p', t['af']) for t in _ts]
TPSI_OFF = np.zeros(len(TEE))
TEE_STAND = os.environ.get('SHORT_TEE_STAND', '0') == '1'
if TEE_STAND and not TONLY:
    raise ValueError('SHORT_TEE_STAND requires SHORT_TONLY=1')


def tee_play_deg(af, c=TEE_HEX_C, eyeball=10.):        # unclocked T2, T2.5: set by eye
    """Turn a hex shaft can make in a hex bore with clearance c per flat before a corner bears on a flat."""
    q = (af/2+c)/(af/math.sqrt(3))
    return eyeball if q >= 1 else 30.-math.degrees(math.acos(q))


def socket_depth(d_key, axial):
    """Actual burial = straight shaft hug plus the additional shallow entrance."""
    return burial_depth(d_key)


def lkey_cloud(mouth, u, D, L, short, r, arm):
    """Long arm from the socket floor (mouth - D u) up to the bend (L - D above the mouth), short arm along `arm`."""
    tip = mouth-u*D
    top = tip+u*(L+max(2*r, 3.))
    return cat([seg(tip, top, r), seg(top+arm*r*.3, top+arm*(short-r), r)])


def arm_dir(u, psi):
    n = np.array([0, 1., 0])-u*u[1]; n /= np.linalg.norm(n)       # 'out', perpendicular to the key
    b = np.cross(u, n)
    return n*math.cos(psi)+b*math.sin(psi)


def boss_cloud(tip, mouth, u, R):
    a = tip-u*FLOOR; b = mouth
    parts = []
    for f in np.linspace(0, 1, 5):
        sh = np.array([0, -1., 0])*f
        parts.append(seg(a+sh*max(0, a[1]-BOARD-R), b+sh*max(0, b[1]-BOARD-R), R, step=max(2., R*.6)))
    return cat(parts)


PLATE_T = 3.5
EDGE_R = 1.6


def ring_pts(c, axis, r, n=24):
    axis = np.asarray(axis, float); axis = axis/np.linalg.norm(axis)
    a = np.cross(axis, [1, 0, 0]) if abs(axis[0]) < .9 else np.cross(axis, [0, 1, 0]); a /= np.linalg.norm(a)
    b = np.cross(axis, a); t = np.linspace(0, 2*math.pi, n, endpoint=False)
    return np.asarray(c)+r*(np.outer(np.cos(t), a)+np.outer(np.sin(t), b))


def row(p, n):
    """p: m0(3), dm(3), th0, dth, a0, da, psi0, dpsi (degrees) -> per item (mouth, u, psi)."""
    m0, dm = np.array(p[0:3]), np.array(p[3:6]); th0, dth, a0, da, s0, ds = p[6:12]
    grade = p[12] if len(p) > 12 else 0.         # graded spacing: wider toward the big end
    out = []
    for k in range(n):
        th, a = math.radians(th0+k*dth), math.radians(a0+k*da)
        u = unit([math.sin(a)*math.cos(th), math.sin(th), math.cos(a)*math.cos(th)])
        out.append((m0+dm*k+np.array([grade*k*k, 0, 0]), u, math.radians(s0+k*ds)))
    return out


def lift_distance(t):
    return t['D']+3.+(float(t['rr'][0])+2*EDGE_R+t.get('lift_pad',0.) if TEE_STAND else 0.)


def escape_corridor_points(t):
    """Conservative shaft-only corridor after clearing the full guide.
    Includes upright and gravity-rest shafts; never enlarge the seating bore.
    """
    shaft=t['rr']<8. # T grip radius is 9 mm; all current shafts are smaller.
    ends=np.vstack([t['pts'][shaft][[0,-1]],t['pts_up'][shaft][[0,-1]]])+t['u']*lift_distance(t)
    ends=np.vstack([ends,ends+np.array([0.,240.,0.])])
    radius=float(t['rr'][0])+C_SWEEP+.2
    cube=np.array([[x,y,z] for x in (-radius,radius) for y in (-radius,radius) for z in (-radius,radius)])
    return (ends[:,None,:]+cube[None,:,:]).reshape(-1,3)


class Layout:
    def __init__(self, v):
        self.v = np.asarray(v, float)
        tx, hx, tt = self.v[:13], self.v[13:26], self.v[26:]
        self.tools = []
        for kind, data, p in (() if TONLY else (('torx', comb.TORX, tx), ('hex', comb.HEX, hx))):
            for k, (m, u, psi) in enumerate(row(p, 9)):
                if kind == 'torx':
                    r = data[k]['point_to_point']/2; L = data[k]['overall']-1.2*data[k]['point_to_point']-2
                    bore = r+comb.CLEAR; name = data[k]['name']
                else:
                    r = data[k]['across_flats']/math.sqrt(3); L = data[k]['straight_length']; bore = comb.hex_bore(k)
                    name = '%g' % data[k]['across_flats']
                D = socket_depth(data[k]['point_to_point'] if kind == 'torx' else data[k]['across_flats'], u[2])
                if kind == BACK and DEEP_BACK:         # owner: 'hide the long bois a little deeper in the back'
                    D += max(0., self.v[38]+k*self.v[39])  # x[38], x[39]: extra seat depth at the small end, per key
                arm = arm_dir(u, psi)
                dn = np.array([0, 0, -1.])+u*u[2]
                if ARM_GRAVITY and np.linalg.norm(dn) > .02:  # the short arm hangs downhill: its gravity rest
                    arm = dn/np.linalg.norm(dn)
                pts, rr = lkey_cloud(m, u, D, L, data[k]['short_arm_assumed'], r, arm)
                self.tools.append(dict(set=kind, name=name, mouth=m, u=u, D=D, tip=m-u*D, pts=pts, rr=rr, bore=bore, arm=arm, L=L))
        # T-handles: tips on a line, axis from (a, phi), grip turned by psi (as optimize_pattern 'row')
        t0, dt = np.array(tt[0:3]), np.array(tt[3:6]); a0, da, p0, dp, s0, ds = tt[6:12]
        # owner, 2026-10-08: 'let's go equal spacing' (of the grips). Each handle is longer than the last, so equal
        # angle steps spread the grips; x[40] bends the angle steps (deg per k^2), x[41] grades the socket pitch
        # (mm per k^2 along the row)
        dda = self.v[40] if len(self.v) > 40 else 0.; tg = self.v[41] if len(self.v) > 41 else 0.
        d3a = self.v[42] if len(self.v) > 42 else 0.     # and x[42] a cubic term, so both ends can even out
        for k, (af, over, bar) in enumerate(TEE):
            a, ph = math.radians(a0+k*da+k*k*dda+k**3*d3a), math.radians(p0+k*dp)
            u = unit([math.sin(a)*math.cos(ph), math.sin(ph), math.cos(a)*math.cos(ph)])
            r = af/math.sqrt(3); D = socket_depth(TEE_SEAT_SIZE[k], u[2])
            tip = t0+dt*k+unit(dt)*tg*k*k
            if DEEP_TEE and len(self.v) > 44:          # owner: small T-handles sunk below the hex keys' grab zone:
                ex = max(0., self.v[43]-k*self.v[44])  # x[43] extra seat depth for T2, x[44] less per size; the mouth
                D += ex; tip = tip-u*ex                # stays put, the socket and the tool go deeper
            m = tip+u*D
            top = tip+u*(over-BAR_R)
            tier = 0
            if TEE_STAND:
                # Two staggered rows, small tools above large tools. x[26:38]:
                # grip origin xyz, pitch, tier dx/dy/dz, tilt, lean, bar turn,
                # upper-row count, per-grip z step. Derive tips from grip centres
                # so different catalogue lengths cannot distort equal spacing.
                gx, gy, gz, pitch, dx, dy, dz, tilt, lean, turn, count, grade = tt[:12]
                count = int(round(count))
                if not 2 <= count <= len(TEE)-2:
                    raise ValueError('each stand tier needs at least two tools')
                tier = int(k < count); j = k if tier else k-count
                ph, a = math.radians(tilt), math.radians(lean)
                u = unit([math.sin(a)*math.cos(ph), math.sin(ph), math.cos(a)*math.cos(ph)])
                top = np.array([gx-j*pitch+tier*dx, gy+tier*dy, gz+j*grade+tier*dz])
                tip = top-u*(over-BAR_R); D = socket_depth(TEE_SEAT_SIZE[k], u[2]); m = tip+u*D
                if tier:turn=self.v[40]
            b0 = unit(np.cross(u, [0, 1, 0])); psi = math.radians((turn if TEE_STAND else s0+k*ds)+TPSI_OFF[k])
            bd = unit(b0*math.cos(psi)+np.cross(u, b0)*math.sin(psi))
            pts, rr = cat([seg(tip, top, r), seg(top-bd*(bar/2-BAR_R), top+bd*(bar/2-BAR_R), BAR_R)])
            self.tools.append(dict(set='tee', name=TEE_NAMES[k], mouth=m, u=u, D=D, tip=tip, pts=pts, rr=rr, bore=r+comb.CLEAR+.15, top=top, bar=bd, af=af))
            if TEE_STAND:
                self.tools[-1]['rail'] = f'tee:{tier}'
                self.tools[-1]['lift_pad'] = max(0., self.v[38+tier])
        for t in self.tools:
            q = t['pts']-t['tip']; ax = q@t['u']
            t['guide_mm'] = land(t['D'])
            t['main'] = np.linalg.norm(q-np.outer(ax, t['u']), axis=1) < .5      # long arm / shaft, before tipping
            _, pd, _, _ = rest_pose(dict(t, floor_deg=0.))
            pd = pd if pd is not None else np.array([0, -1., 0])
            t['floor_p'], t['floor_n'], t['floor_deg'], t['floor_depth'] = floor_plane(t, pd)
            t['pinch'], t['pinch_dir'], cocked, t['u_rest'] = rest_pose(t)
            t['seat'] = t['pinch'] > PINCH_RATIO
            t['pts_up'] = t['pts']                     # upright and centred: where drawing it out starts
            if COCK:
                t['pts'] = cocked
        self.bosses = [boss_cloud(t['tip'], t['mouth'], t['u'], t['bore']+WALL) for t in self.tools]
        # the CAD's rails: per set, hull of the socket barrels swept 50 deg down-and-back in the LEFT-cheek
        # print (+x is down), trimmed at the board; as half-space sets for an exact convex distance
        from scipy.spatial import ConvexHull
        d50 = np.array([math.sin(math.radians(50)), -math.cos(math.radians(50)), 0.])
        self.rails = []
        self.rail_groups = [(s_, [t for t in self.tools if t.get('rail', t['set']) == s_])
                            for s_ in (('tee:0', 'tee:1') if TEE_STAND else SETS)]
        for s_, tools in self.rail_groups:
            _, P = rail_points(tools, s_, [])      # with the label lip, as the CAD
            lam = (P[:, 1].max()-BOARD+2)/math.cos(math.radians(50))
            Q = np.vstack([P, P+d50*lam])
            hq = Q[ConvexHull(Q).vertices]
            th_ = np.linspace(0, 2*math.pi, 12, endpoint=False)
            bic = np.vstack([np.c_[np.zeros(12), EDGE_R*np.cos(th_), EDGE_R*np.sin(th_)],
                             [[EDGE_R*math.tan(math.radians(50)), 0, 0], [-EDGE_R*math.tan(math.radians(50)), 0, 0]]])
            Q = (hq[:, None, :]+bic[None, :, :]).reshape(-1, 3); H = ConvexHull(Q)       # as the CAD's edge rounding
            self.rails.append((H.equations, Q.min(axis=0)-15, Q.max(axis=0)+15))
        self.escape_corridors=[ConvexHull(escape_corridor_points(t)).equations for t in self.tools] if TEE_STAND else []

    def body_sdf(self, p):
        d = np.full(len(p), 1e9)
        for eq, lo, hi in self.rails:
            sel = np.all((p >= lo) & (p <= hi), axis=1)
            if sel.any():
                d[sel] = np.minimum(d[sel], (p[sel]@eq[:, :3].T+eq[:, 3]).max(axis=1))
        d=np.minimum(d,p[:,1]-(BOARD+PLATE_T))
        for eq in self.escape_corridors:
            cut=(p@eq[:,:3].T+eq[:,3]).max(axis=1)
            d=np.maximum(d,-cut)
        return d


ESC = {'forward': np.array([0, 1., 0]), 'up-forward': unit([0, 1, .4]), 'axis': None}


ROBUST = os.environ.get('SHORT_ROBUST', '0') == '1'
ROBUST_ALT = os.environ.get('SHORT_ROBUST_ALT', '0') == '1'   # neighbours turned opposite ways (costs ~15 mm depth)
ARM_GRAVITY = os.environ.get('SHORT_ARM_GRAVITY', '1') == '1'
# Hand space (owner, 2026-10-08: 'equal hand space around that middle set above and below'): clear distance from
# the hex keys to the Torx keys above and to the T-handles below, each at least HAND mm and the two equal.
HAND = float(os.environ.get('SHORT_HAND', 0))


def hand_gaps(T):
    """Clear distance from the middle tier's keys to the back row's and to the T-handles (keys 'back', 'tee')."""
    out = {}
    hp, hr = cat([(t['pts'], t['rr']) for t in T if t['set'] == MIDDLE])
    for s_ in (BACK, 'tee'):
        op, orr = cat([(t['pts'], t['rr']) for t in T if t['set'] == s_])
        d, i = cKDTree(op).query(hp, k=8)
        out['back' if s_ == BACK else 'tee'] = float(np.min(d-hr[:, None]-orr[i]))
    return out
# Rest pose (owner, 2026-10-08: tools whose own torque pinches them in the bore). A tool's weight tips it about
# the mouth lip until its tip bears on the far side. Where that pinch's friction beats the slide down the bore
# (PINCH_RATIO > 0.8) a plain floor would let it hang. So every floor slopes FLOOR_DEG from square, low on the
# pinch side: the tilted tip rests on the slope by its trailing corner, and the same sideways pinch that held it
# now slides it down the slope, i.e. deeper, into the low corner against the flared wall. (A pocket that juts out
# sideways at the floor does not work with a rigid shank: the shank meets the wall above the pocket first and
# rests on that edge, a contact square to the tool.) The stored pose is the tool in that corner.
COCK = os.environ.get('SHORT_COCK', '1') == '1'
PINCH_RATIO, FLOOR_DEG = .8, 30.
LABEL_CAP = 5.88                                         # Fillaprint capital height at w = 0.42 (14 w)
MIDDLE = os.environ.get('SHORT_MIDDLE', 'hex')
DEEP_BACK = os.environ.get('SHORT_DEEP_BACK', '0') == '1'
TEE_EQUAL = float(os.environ.get('SHORT_TEE_EQUAL', 0))     # target grip-centre spacing, mm (0: off)
DEEP_TEE = os.environ.get('SHORT_DEEP_TEE', '0') == '1'
GRAB = float(os.environ.get('SHORT_GRAB', 0))   # T grips at least this far below the back row's grab zone (0: off)


def grab_gaps(T):
    """Per T-handle: vertical clearance from the top of its grip to the bottom of the back-row keys' grab zone
    (short arm plus the top 25 mm of the long arm) within 30 mm sideways; None where no key is above."""
    G = []
    for t in T:
        if t['set'] != BACK:
            continue
        top = np.max(t['pts'][:, 2]); m = (~t['main']) | (t['pts'][:, 2] > top-25)
        G.append(np.c_[t['pts'][m], t['rr'][m]])
    G = np.vstack(G); out = []
    for t in T:
        if t['set'] != 'tee':
            continue
        bar = t['pts'][~t['main']]; gx = bar[:, 0]; gz = float(np.max(bar[:, 2]))+BAR_R
        near = G[(G[:, 0] > gx.min()-30) & (G[:, 0] < gx.max()+30)]
        out.append(float(np.min(near[:, 2]-near[:, 3]))-gz if len(near) else None)
    return out
BACK = 'torx' if MIDDLE == 'hex' else 'hex'
_TOP, _FRONT = (np.array([0, .42, .91]), 1), (np.array([0, .95, .31]), -1)
LIP = {BACK: _TOP, MIDDLE: _FRONT, 'tee': _FRONT}
# The guide has no flare or separate rounded seating chamber.


def land(depth):
    """Actual straight guide, excluding only the shallow entrance chamfer."""
    return depth-ENTRY_LEAD_MM


def flare(depth):
    return 0.


def rot(P, c, k, ang):
    k = k/np.linalg.norm(k); q = P-c
    return c+q*math.cos(ang)+np.cross(k, q)*math.sin(ang)+np.outer(q@k, k)*(1-math.cos(ang))


def rest_pose(t):
    """Pinch ratio, pinch direction (where the tip bears) and the tipped point cloud."""
    u = t['u']; m = t['mouth']; w = t['rr']**2
    c = (t['pts']*w[:, None]).sum(0)/w.sum(); g = np.array([0, 0, -1.])
    Mp = np.cross(c-m, g); Mp = Mp-u*(Mp@u); nM = np.linalg.norm(Mp)
    gax = max(-(g@u), 1e-6); gperp = np.linalg.norm(g-u*(g@u))
    ratio = MU*(2*nM/t['D']+gperp)/gax
    if nM < 1e-9:
        return ratio, None, t['pts'], u
    k = Mp/nM; tipd = np.cross(k, -u); tipd /= np.linalg.norm(tipd)
    # pivot on the mouth lip: the mouth end shifts by the clearance away from the pinch side, the tip swings into
    # the flare and the seat; 0.1 mm off every wall, and lifted so the tilted flat tip clears the floor
    r_tool = float(t['rr'][0]); c_m, c_t = clearances(t)
    x_c = c_t+flare(t['D'])                           # tip centre's sideways reach at the floor (0.1 off the wall)
    ang = (c_m+x_c)/t['D']; ta = math.tan(math.radians(t['floor_deg']))
    # trailing corner 0.1 mm above the sloped floor (floor plane: see floor_plane)
    z_c = t['D']+r_tool*ta+(x_c-r_tool*math.cos(ang))*ta-r_tool*math.sin(ang)
    P = rot(t['pts'], m, k, ang)-tipd*c_m-u*(z_c-t['D'])
    return ratio, tipd, P, rot(u[None, :], np.zeros(3), k, ang)[0]


def clearances(t):
    """Straight-guide lateral clearance, with 0.02 mm reserve in the rest-pose screen."""
    if t['set']=='tee':
        c=max(TEE_HEX_C-.02,0.)
    else:
        c=max(t['bore']-float(t['rr'][0])-.02,0.)
    return c,c


def chamber_r(t):
    """Circumscribing guide radius; there is no widening chamber."""
    if t['set']=='tee':return (t['af']+2*TEE_HEX_C)/math.sqrt(3)
    return t['bore']


def floor_plane(t, pinch):
    """Square floor normal to the shaft at the prescribed burial depth."""
    return t['mouth']-t['u']*t['D'],t['u'],0.,t['D']


def rail_points(tools, set_name, labels=None):
    """A rail's outline before the 50 deg sweep: a ring round each socket at its mouth and past its deepest floor
    point, plus (with labels) the flat label lip. Shared by the study and the CAD (build_short.rail)."""
    P = []
    for t in tools:
        u = t['u']; R = t['bore']+WALL
        P += [ring_pts(t['mouth']-u*(t['floor_depth']+FLOOR+1), u, chamber_r(t)+WALL), ring_pts(t['mouth'], u, R)]
    P = np.vstack(P); rings = P.copy()
    if labels is not None:
        # owner: labels on the human side (hex, T: a flat lip under the mouths, facing out); the back row (Torx) is
        # the exception: on top, behind each mouth. The lip is the rail's support plane in direction nL.
        t0, side = LIP[set_name.split(':')[0]]
        r = np.asarray(tools[-1]['tip'])-np.asarray(tools[0]['tip']); r /= np.linalg.norm(r)
        nL = t0-(t0@r)*r; nL /= np.linalg.norm(nL)
        upL = np.array([0, 0, 1.])-nL*nL[2]
        if np.linalg.norm(upL) < .3:
            upL = np.array([0, -1., 0])-nL*nL[1]
        upL /= np.linalg.norm(upL); rgL = np.cross(upL, nL)
        h = float((P@nL).max()); extra = []
        for t in tools:
            m = np.asarray(t['mouth']); pk = m+nL*(h-m@nL)
            wt = 4.2*len(t['name'].lstrip('T'))
            c = pk+upL*side*(t['bore']+2.+LABEL_CAP/2+2.5)
            labels.append(dict(text=t['name'].lstrip('T'), centre=c, n=nL, up=upL, right=rgL))
            for a_ in (-1, 1):
                for b_ in (-1, 1):
                    q = c+rgL*a_*(wt/2+2.5)+upL*b_*(LABEL_CAP/2+2.)
                    extra += [q, q-nL*6.]
        P = np.vstack([P, np.array(extra)])
    return rings, P


def evaluate(v, detail=False, wd=5.):
    """With SHORT_ROBUST=1 the T-handle penalties also cover every handle turned by its bore's play
    (all one way, all the other, and alternating), so a handle left anywhere in its play still clears."""
    if not ROBUST:
        return _evaluate(v, detail, wd)
    global TPSI_OFF
    play = np.array([tee_play_deg(t[0]) for t in TEE]); alt = np.array([(-1)**k for k in range(len(TEE))])
    out = _evaluate(v, True, wd); extra = 0.
    try:
        for sgn in ((play, -play, play*alt, -play*alt) if ROBUST_ALT else (play, -play)):
            TPSI_OFF = sgn
            extra += sum(_evaluate(v, True, wd)[3].values())
    finally:
        TPSI_OFF = np.zeros(len(TEE))
    tot, depth, body_h, pen, rep, Lo = out
    pen = dict(pen); pen['turn'] = extra
    tot += 10*extra
    return (tot, depth, body_h, pen, rep, Lo) if detail else tot


def _evaluate(v, detail=False, wd=5.):
    Lo = Layout(v)
    T = Lo.tools; n = len(T)
    allp = np.vstack([t['pts'] for t in T]); allr = np.concatenate([t['rr'] for t in T])
    bp = np.vstack([b[0] for b in Lo.bosses]); br = np.concatenate([b[1] for b in Lo.bosses])
    ztop = max(float(np.max(allp[:, 2]+allr)), float(np.max(bp[:, 2]+br)))
    zk = ztop+SHELF_GAP

    def shelf(p, r):
        a = SHELF_DEPTH+C_SHELF-(p[:, 1]-r); b = p[:, 2]+r-(zk-C_SHELF)
        m = np.minimum(a, b); return float(np.sum(m[m > 0]))
    pen = dict(store=0., sweep=0., env=0., order=0.)
    trees = []
    for i, t in enumerate(T):
        parts = [(o['pts'], o['rr']) for j, o in enumerate(T) if j != i]
        op, orr = cat(parts); trees.append((cKDTree(op), orr, orr.max()))
    rep = []

    def body_pen(t, p, r, c):
        """Rail/plate penetration, ignoring the tool's own socket (points still inside its bore line)."""
        own = np.zeros(len(p), bool)
        for a_ in (t['u'], t.get('u_rest', t['u'])):     # the CAD cuts the opening up the socket axis and the rest lean
            q = p-t['mouth']; ax = q@a_; rad = np.linalg.norm(q-np.outer(ax, a_), axis=1)
            own |= (ax < 150.) & (rad < t['bore']+1.5)    # the CAD's opening and entry ring: bore + 1.6 (L) or more (T)
        pen_ = np.maximum(0, r+c-Lo.body_sdf(p)); pen_[own] = 0
        return float(pen_.sum())
    for i, t in enumerate(T):
        tree, orr, rmax = trees[i]
        pen['store'] += .5*hit_tree(tree, orr, rmax, t['pts'], t['rr'], C_STORE)
        pen['store'] += body_pen(t, t['pts'], t['rr'], C_STORE)
        pen['store'] += float(np.sum(np.maximum(0, BOARD+C_STORE-(t['pts'][:, 1]-t['rr']))))
        # drawing it out starts by straightening it upright, past its neighbours at rest
        pen['sweep'] += hit_tree(tree, orr, rmax, t['pts_up'], t['rr'], C_STORE)
        lift_mm = lift_distance(t)
        lift = t['u']*lift_mm
        sp, sr = sweep(t['pts'], t['rr'], lift, max(2, int(lift_mm/STEP)+1))
        base = hit_tree(tree, orr, rmax, sp, sr, C_SWEEP)+shelf(sp, sr)+body_pen(t, sp, sr, C_SWEEP)
        best, which = 1e9, None
        for name, e in ESC.items():
            dvec = (t['u'] if e is None else e)*240.
            escape_n = max(25, int(math.ceil(240./float(os.environ.get('SHORT_ESCAPE_STEP', 10.))))+1) if TEE_STAND else 25
            ep, er = sweep(t['pts']+lift, t['rr'], dvec, escape_n)
            c = hit_tree(tree, orr, rmax, ep, er, C_SWEEP)+shelf(ep, er)+body_pen(t, ep, er, C_SWEEP)
            if c < best:
                best, which = c, name
            if c == 0:
                break
        pen['sweep'] += base+best
        rep.append(dict(set=t['set'], name=t['name'], D=round(t['D'], 1), escape=which, lift_pen=round(base, 2), esc_pen=round(best, 2)))
        if TEE_STAND:
            rep[-1]['lift_mm'] = float(lift_mm)
    # order: small -> big from the user's left within each set (mouth x decreasing)
    for s_ in ('torx', 'hex', 'tee'):
        groups = [ts for name, ts in Lo.rail_groups if name.split(':')[0] == s_]
        xs = [] if TEE_STAND else [t['mouth'][0] for t in T if t['set'] == s_]
        pen['order'] += sum(max(0., xs[i+1]-xs[i]+4.) for i in range(len(xs)-1))
        if TEE_STAND:
            pen['order'] += sum(max(0., b['mouth'][0]-a['mouth'][0]+4.) for ts in groups for a, b in zip(ts, ts[1:]))
    # holder envelope: socket centres inside the rack width (walls are trimmed at the board and the ends in CAD);
    # the holder's height is the sockets' span (the receiver sits within it), on the bed in the cheek print
    for t in T:
        for q in (t['tip'], t['mouth']):
            pen['env'] += 5*max(0., abs(q[0])-(HALF-t['bore']-2.))+5*max(0., BOARD+2.-(q[1]-t['bore']))
        fl = t['tip']-t['u']*FLOOR                      # socket floor clear of the receiver plate (5.4 mm) everywhere
        pen['env'] += 5*max(0., BOARD+5.6-(fl[1]-t['bore']))
    for s_ in ('torx', 'hex'):
        xs = [t['mouth'][0] for t in T if t['set'] == s_] or [0.]
        pen['env'] += max(0., SPREAD-(max(xs)-min(xs)))
    zlo = float(np.min(bp[:, 2]-br)); zhb = float(np.max(bp[:, 2]+br))
    pen['env'] += max(0., (zhb-zlo)-H_MAX)*5
    pen['env'] += float(np.sum(np.maximum(0, np.abs(allp[:, 0])+allr-v_xenv)))
    if GRAB > 0:
        pen['grab'] = .2*sum(max(0., GRAB-g) for g in grab_gaps(T) if g is not None)
    if TEE_EQUAL > 0:
        groups = [ts for name, ts in Lo.rail_groups if name.split(':')[0] == 'tee']
        g = np.concatenate([np.linalg.norm(np.diff([t['top'] for t in ts], axis=0), axis=1) for ts in groups])
        pen['grip'] = float(np.sum(np.abs(g-TEE_EQUAL)))*.2
    if HAND > 0:
        hg = hand_gaps(T)
        pen['hand'] = max(0., HAND-hg['back'])+max(0., HAND-hg['tee'])+.5*abs(hg['back']-hg['tee'])
    depth = max(float(np.max(allp[:, 1]+allr)), float(np.max(bp[:, 1]+br)))
    body_h = float(np.max(bp[:, 2]+br)-np.min(bp[:, 2]-br))
    total = wd*depth+.15*body_h+10*sum(pen.values())
    if detail:
        return total, depth, body_h, pen, rep, Lo
    return total


v_xenv = float(os.environ.get('XENV', 165))
