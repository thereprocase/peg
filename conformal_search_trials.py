"""Bounded experimental path searches; failure does not prove impossibility."""
from __future__ import annotations

import argparse
import heapq
import json
import math
from pathlib import Path
import time

import numpy as np

from conformal_motion import ConformalStudy
from round_motion import RoundStudy, tf

ROOT = Path(__file__).resolve().parent


class FastSearchStudy(ConformalStudy):
    """Use the same conservative clipped X slabs, without distance work."""
    def __init__(self, overrides=None, slabs=192, clearance=0.0, omit_nose=False):
        super().__init__(overrides, slabs, clearance)
        if omit_nose:
            # Optimistic diagnostic only: omit both lower conical additions.
            # Any found trajectory must be checked against actual complete CAD.
            lower = self.contract['conformal_bearing']['lands'][1]
            rear = lower['rear_y']
            self.locator_points[:, [0, 3], 0] = rear
            self.extra_points[slabs:2 * slabs, 0, 0] = rear
            self.extra_points[slabs:2 * slabs, 3, 0] = rear
    def collision(self, q, real=False):
        if RoundStudy.collision(self, q, real):
            return True
        p = self.p
        t = p['board_thickness']
        a = math.radians(q[2]); c, s = math.cos(a), math.sin(a)
        xy = self.extra_points @ np.array([[c, s], [-s, c]]) + q[:2]
        R = p['hole_diameter'] / 2 - (0 if real else p['clearance'])
        h = np.sqrt(np.maximum(0, R * R - self.extra_outer ** 2))
        lo, hi = self.extra_rows - h, self.extra_rows + h
        yy, zz = xy[:, :, 0], xy[:, :, 1]
        candidates = [np.where((yy >= -t) & (yy <= 0), zz, np.nan)]
        yn, zn = np.roll(yy, -1, axis=1), np.roll(zz, -1, axis=1)
        for wall in [-t, 0]:
            with np.errstate(divide='ignore', invalid='ignore'):
                u = (wall - yy) / (yn - yy)
                section = zz + u * (zn - zz)
            candidates.append(np.where((u >= 0) & (u <= 1), section, np.nan))
        sections = np.concatenate(candidates, axis=1)
        zmin = np.min(np.where(np.isnan(sections), np.inf, sections), axis=1)
        zmax = np.max(np.where(np.isnan(sections), -np.inf, sections), axis=1)
        return bool(np.any(np.isfinite(zmin) & ((zmin < lo - 1e-10) | (zmax > hi + 1e-10))))


def search(study, step=.025, angle_step=.125, seconds=20, base=None):
    base = np.asarray(base if base is not None else [-study.p['front_gap'] + .03, 0, 0], dtype=float)
    scale = np.array([step, step, angle_step])
    cache, best, previous = {}, {(0, 0, 0): 0.0}, {(0, 0, 0): None}
    queue = [(0.0, 0.0, (0, 0, 0))]
    moves = [(y, z, a) for y in [-1, 0, 1] for z in [-1, 0, 1] for a in [-1, 0, 1] if (y, z, a) != (0, 0, 0)]
    started = time.monotonic()

    def pose(n):
        return base + np.asarray(n) * scale

    def valid(n):
        q = pose(n)
        if not (-.4 <= q[0] <= 18 and -.4 <= q[1] <= 5 and 0 <= q[2] <= 42):
            return False
        if n not in cache:
            cache[n] = not study.collision(q)
        return cache[n]

    status, path = 'exhausted', None
    if not valid((0, 0, 0)):
        status = 'blocked_start'
        queue = []
    while queue:
        if time.monotonic() - started > seconds:
            status = 'timeout'
            break
        _, cost, n = heapq.heappop(queue)
        if cost != best[n]:
            continue
        q = pose(n)
        if tf(study.upper, q).bounds[0] > 1:
            path = []
            while n is not None:
                path.append(pose(n).tolist())
                n = previous[n]
            path.reverse()
            status = 'path_found'
            break
        for move in moves:
            nn = tuple(n[i] + move[i] for i in range(3))
            if not valid(nn):
                continue
            new_cost = cost + math.sqrt(move[0] ** 2 + move[1] ** 2 + (.5 * move[2]) ** 2)
            if new_cost < best.get(nn, math.inf):
                best[nn] = new_cost
                previous[nn] = n
                heapq.heappush(queue, (new_cost + max(0, 14 / step - nn[0]), new_cost, nn))
    free = np.array([pose(n) for n, ok in cache.items() if ok])
    return {'status': status, 'elapsed_seconds': round(time.monotonic() - started, 3),
            'tested_nodes': len(cache), 'free_nodes': sum(cache.values()), 'base_pose': base.tolist(),
            'free_pose_minima': free.min(axis=0).tolist() if len(free) else None,
            'free_pose_maxima': free.max(axis=0).tolist() if len(free) else None,
            'translation_step_mm': step, 'angle_step_deg': angle_step,
            'waypoints': path, 'scope': 'Conservative node search only; segments and exact seating are not certified. Bounded failure is not proof of impossibility.'}


def run(seconds=20, omit_nose=False, spine_top=None):
    trials = [
        ({}, .025, .125), ({}, .01, .1),
        ({'pull_clearance': .60}, .025, .125),
        ({'pull_clearance': .70}, .025, .125),
        ({'pull_clearance': .85}, .025, .125),
    ]
    suffix = ('_optimistic' if omit_nose else '') + (f'_top{spine_top:g}' if spine_top is not None else '')
    out = ROOT / 'cad' / 'conformal' / f'conformal_search{suffix}_trials.json'
    reports = []
    for overrides, step, angle in trials:
        if spine_top is not None:
            overrides = overrides | {'spine_top': spine_top}
        study = FastSearchStudy(overrides, slabs=192, omit_nose=omit_nose)
        result = search(study, step, angle, seconds)
        result['overrides'] = overrides
        result['lower_nose_omitted_for_diagnostic'] = omit_nose
        reports.append(result)
        out.write_text(json.dumps({'trials': reports}, indent=2) + '\n',encoding='utf-8',newline='\n')
        print(json.dumps({k: v for k, v in result.items() if k not in ['waypoints', 'scope']}), flush=True)
        if result['waypoints']:
            break
    return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--omit-nose', action='store_true')
    parser.add_argument('--spine-top', type=float)
    args = parser.parse_args()
    run(args.seconds, args.omit_nose, args.spine_top)
