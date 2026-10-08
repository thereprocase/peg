"""HX04 fit coupon (owner, 2026-10-08): cut from the final CAD so it is the real geometry, printed the same way
(on the user's left end, same profile, same solid-infill zones).

  * End slice: everything at installed x >= SLICE_X (the left end, which is the print bed face), plus a local
    tower that keeps the T3 socket whole. It carries the left peg-hook column, so it hangs on the board, and holds
    Torx T10/T15, hex 1.5/2 and T-handles T2 (sunk), T2.5 (unclocked) and T3 (clocked, the most pinched tool).
  * Blocks, each cut round one socket with a flat face on the bed side and its name debossed on top:
    T5 C (keyed to the hex corners, as built), T5 F (keyed to the flats), TX30. A fit test: print it at the
    plain 20% infill (tools/quickslice.py); the solid zones are for the full part.
Run with FreeCAD's Python and the build env (SHORT_*, HX4S_*):  python coupon.py <out dir>
"""
from pathlib import Path
import json, math, sys
import numpy as np
import FreeCAD as A
import Part
sys.argv = [sys.argv[0]]+sys.argv[1:]
import build_short as BS
V = A.Vector
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
SLICE_X = 88.
SLICE_ZMIN = -205.                                      # down to just under the T3 socket
g = BS.build(True)
body, Lo, receiver = g['shape'], g['Lo'], g['receiver']
zones = BS.solid_zones(Lo, receiver, body)
T = {(t['set'], t['name']): t for t in Lo.tools}
bb = body.BoundBox


def socket_box(t, pad=6.):
    """Axis-aligned box round a socket: mouth (plus 3 mm) to past its deepest floor point, padded."""
    u = np.asarray(t['u']); m = np.asarray(t['mouth']); R = BS.SH.chamber_r(t)+BS.WALL+pad
    P = np.vstack([m+u*3., m-u*(t['floor_depth']+BS.FLOOR+2.)])
    lo, hi = P.min(axis=0)-R, P.max(axis=0)+R
    return Part.makeBox(*(hi-lo), V(*lo))


def holes_for(t, tbar):
    """The socket cutters of one tool (as build_short.build), with a chosen T-bar clocking."""
    old = BS.TBAR; BS.TBAR = tbar
    try:
        ax = BS.v(t['u']); m = BS.v(t['mouth']); hk = None
        if t['set'] == 'tee' and t['af'] >= BS.TEE_KEYED_MIN:
            hk = (t['af']+2*BS.SH.TEE_HEX_C, BS.v(t['bar']))
        parts = BS.socket(m, ax, t['bore'], t['D'], ring_w=1.6 if t['set'] != 'tee' else 2., hexkey=hk,
                          floor=(BS.v(t['floor_p']), BS.v(t['floor_n']), float(t['floor_depth'])))
        ur = BS.v(t['u_rest'])
        if ur.getAngle(ax) > 1e-3:
            parts.append(Part.Face(BS.teardrop(m, t['bore']+.8, ur)).extrude(ur*150.))
        return BS.B.union(parts)
    finally:
        BS.TBAR = old


def largest(s):
    s = s.removeSplitter()
    return max(s.Solids, key=lambda so: so.Volume) if len(s.Solids) > 1 else s


def label(shape, text, cap=4.):
    """Deboss `text` 0.6 mm into the piece's top face in the print (installed -x side)."""
    b = shape.BoundBox
    c = V(b.XMin, (b.YMin+b.YMax)/2, (b.ZMin+b.ZMax)/2)
    n = V(-1, 0, 0); up = V(0, 0, 1); right = up.cross(n)
    keep = BS.halfspace(c+V(.6, 0, 0), V(1, 0, 0))
    mk = BS.engrave(text, BS.size_for_cap(cap), c, right, up, n, .6, keep)
    t = shape.cut(mk)
    return t if t.isValid() and len(t.Solids) == 1 else shape


pieces = []
# --- end slice with a tower round T3 -----------------------------------------------------------------------
keep = Part.makeBox(bb.XMax-SLICE_X+1, bb.YLength+2, bb.ZMax-SLICE_ZMIN+1, V(SLICE_X, bb.YMin-1, SLICE_ZMIN))
keep = keep.fuse(socket_box(T[('tee', '3')], pad=4.))
sl = largest(body.common(keep))
pieces.append(('end slice', sl, zones.common(keep)))
# --- blocks ------------------------------------------------------------------------------------------------
for key, tbar, name in ((('tee', '5'), 'corners', 'T5 C'), (('tee', '5'), 'flats', 'T5 F'),
                        (('torx', 'T30'), None, 'TX30')):
    t = T[key]; box = socket_box(t, pad=3.)
    blk = body.common(box)
    if tbar == 'flats':                              # refill the as-built bore, cut the flats-keyed one
        blk = blk.fuse(holes_for(t, 'corners').common(box)).cut(holes_for(t, 'flats'))
    blk = largest(blk)
    pieces.append((name, label(blk, name), zones.common(box)))

# --- print pose and plate layout -----------------------------------------------------------------------------
report = []; bodies = []; zs = []; xoff = yoff = row_h = 0.
BED = 240.                                              # shelf-pack the pieces onto the plate
for name, s, z in pieces:
    pp, m = BS.print_pose(s); zp = z.copy(); zp.transformShape(m)
    b = pp.BoundBox
    if xoff > 0 and xoff+b.XLength > BED:
        xoff, yoff, row_h = 0., yoff+row_h+8., 0.
    shift = V(xoff-b.XMin, yoff-b.YMin, 0); pp.translate(shift); zp.translate(shift)
    xoff += b.XLength+8.; row_h = max(row_h, b.YLength)
    bodies.append(pp); zs.append(zp)
    report.append(dict(piece=name, volume_mm3=round(s.Volume), print_extent_mm=[round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)], solids=len(s.Solids)))
BS.B.mesh(Part.makeCompound(bodies), OUT/'print.stl')
BS.B.mesh(Part.makeCompound(zs), OUT/'print_solid.stl')
for name, s, z in pieces:                           # installed pose, one file per piece (T5 C and F overlap)
    BS.B.mesh(s, OUT/('installed_'+name.replace(' ', '_')+'.stl'))
Part.makeCompound([p[1] for p in pieces]).exportStep(str(OUT/'coupon_installed.step'))
(OUT/'coupon.json').write_text(json.dumps(dict(pieces=report, slice_x_mm=SLICE_X, tbar_default=BS.TBAR), indent=1), encoding='utf-8', newline='\n')
print(json.dumps(report, indent=1))
