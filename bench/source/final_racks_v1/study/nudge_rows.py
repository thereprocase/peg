"""Owner, 2026-10-08: nudge a layout with some parameters frozen (default: the whole T fan; argv[4] = frozen
indices, e.g. the T fan angles 32,33,34,35) to clear the stretch's clashes."""
import json, sys, time
import numpy as np
from scipy.optimize import minimize
import short as S
src, out, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
x = np.array(json.load(open(src))['x']); t0 = time.time()
FROZEN = [int(i) for i in sys.argv[4].split(',')] if len(sys.argv) > 4 else list(range(26, 38))
free = [i for i in range(len(x)) if i not in FROZEN]
# multi-start (farm): NUDGE_SEED > 0 jitters the free parameters before the local search
_seed = int(__import__('os').environ.get('NUDGE_SEED', 0))
if _seed:
    _rng = np.random.default_rng(_seed); _j = float(__import__('os').environ.get('NUDGE_JITTER', .03))
    x[free] = x[free]+_rng.normal(0, 1, len(free))*np.maximum(np.abs(x[free])*_j, _j*10)
best = [1e18, x[free].copy()]
GAP = None                                     # argv[5]: reference layout whose T grip-to-grip gaps are a floor
if len(sys.argv) > 5:                          # (owner: 'less fan, not more snug')
    _T = [t for t in S.Layout(json.load(open(sys.argv[5]))['x']).tools if t['set'] == 'tee']
    GAP = np.linalg.norm(np.diff([t['top'] for t in _T], axis=0), axis=1)


VERT = float(__import__('os').environ.get('NUDGE_VERT', 0))    # weight on the loaded rack's height


def vert(v):
    """Loaded height: top of the tallest stored tool to the bottom of the holder."""
    Lo = S.Layout(v)
    top = max(float(np.max(t['pts'][:, 2]+t['rr'])) for t in Lo.tools)
    bot = min(float(np.min(b[0][:, 2]-b[1])) for b in Lo.bosses)
    return top-bot


def gap_pen(v):
    if GAP is None:
        return 0.
    T = [t for t in S.Layout(v).tools if t['set'] == 'tee']
    g = np.linalg.norm(np.diff([t['top'] for t in T], axis=0), axis=1)
    return float(np.sum(np.maximum(0, GAP-g)))


def full(p):
    v = x.copy(); v[free] = p; return v
class Done(Exception): pass
def g(p):
    v = full(p); tot, d, bh, pen = S.evaluate(v, True)[:4]
    val = d+.1*bh+1000*(sum(pen.values())+gap_pen(v))+VERT*vert(v)
    if val < best[0]:
        best[0] = val; best[1] = p.copy()
    if time.time()-t0 > secs:
        raise Done
    return val
try:
    minimize(g, x[free], method='Nelder-Mead', options=dict(maxiter=100000, adaptive=True, initial_simplex=None))
except Done:
    pass
v = full(best[1]); tot, d, bh, pen, rep, Lo = S.evaluate(v, True)
print(round(d, 1), round(bh, 1), 'vert %.1f' % vert(v), 'gap short %.2f' % gap_pen(v), {k: round(float(q), 2) for k, q in pen.items()})
for r in rep:
    if r['lift_pen'] or r['esc_pen']:
        print(' ', r)
json.dump(dict(x=list(map(float, v)), rep=rep, depth=d, body_h=bh, pen={k: float(q) for k, q in pen.items()}), open(out, 'w'), indent=1)
