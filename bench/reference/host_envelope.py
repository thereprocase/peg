"""Continuous board-front envelope for a host attached to the peg anchor.

This checks an input pose path, not whether changed peg geometry follows that
path. The default report belongs only to the existing round motion study.
Units are mm and degrees. No third-party packages are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NUMERICAL_TOLERANCE_MM = 1e-9


def _poses(poses):
    result = []
    for pose in poses:
        q = (pose['y'], pose['z'], pose['theta_deg']) if isinstance(pose, dict) else pose
        if len(q) != 3 or not all(math.isfinite(float(v)) for v in q):
            raise ValueError('Each pose must contain three finite coordinates')
        if not -90 < float(q[2]) < 90:
            raise ValueError('Board-front envelope requires tilt strictly between -90 and 90 degrees')
        result.append((float(q[0]), float(q[1]), math.radians(float(q[2]))))
    if len(result) < 2:
        raise ValueError('At least two poses are required')
    return result


def _pose_dict(q):
    return dict(y=q[0], z=q[1], theta_deg=math.degrees(q[2]))


def _lerp(a, d, u):
    return tuple(a[i] + u*d[i] for i in range(3))


def _critical_points(derivative, cuts):
    """Find every root when derivative is monotone between supplied cuts."""
    cuts = sorted(set([0.0, 1.0] + [u for u in cuts if 0 < u < 1]))
    points = list(cuts)
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        flo, fhi = derivative(lo), derivative(hi)
        if flo == 0:
            points.append(lo)
        if fhi == 0:
            points.append(hi)
        if flo*fhi >= 0:
            continue
        for _ in range(64):
            mid = (lo + hi)/2
            fm = derivative(mid)
            if fm == 0:
                lo = hi = mid
                break
            if flo*fm < 0:
                hi = mid
            else:
                lo, flo = mid, fm
        points.append((lo + hi)/2)
    return sorted(set(points))


def _linear_zero(a, d):
    return [-a/d] if d else []


def required_setback(poses, physical_height, seated_y=None, seated_z=None):
    """Minimum physical front-face setback at one installed height.

    For each path pose, cos(theta)*Y - sin(theta)*Z + pose.y >= 0.
    With cos(theta)>0 this becomes Y >= Z*tan(theta)-pose.y/cos(theta).
    The maximum is evaluated over every continuous, linearly interpolated
    pose segment. The first pose supplies the seated translations by default.
    """
    path = _poses(poses)
    sy = path[0][0] if seated_y is None else float(seated_y)
    sz = path[0][1] if seated_z is None else float(seated_z)
    z = float(physical_height)-sz
    best = (-math.inf, None, None)
    for index, (a, b) in enumerate(zip(path[:-1], path[1:])):
        d = tuple(b[i]-a[i] for i in range(3))
        def derivative(u):
            y, _, theta = _lerp(a, d, u)
            return d[2]*(z-y*math.sin(theta))-d[0]*math.cos(theta)
        # The derivative numerator has derivative -dtheta^2*y*cos(theta).
        # Splitting at y=0 therefore makes it monotone on each subinterval.
        for u in _critical_points(derivative, _linear_zero(a[0], d[0])):
            q = _lerp(a, d, u)
            value = (z*math.sin(q[2])-q[0])/math.cos(q[2])
            if value > best[0]:
                best = (value, q, index)
    return dict(physical_height_above_upper_hole_mm=float(physical_height),
                design_z_mm=z, required_design_y_mm=best[0],
                required_installed_setback_mm=best[0]+sy,
                limiting_pose=_pose_dict(best[1]), segment_index=best[2])


def max_flush_height(poses, installed_setback=0.0):
    """Maximum top height for a sharp vertical host front on this path.

    Nonnegative installation tilt is required for this upper-height cap.
    The host front plane is at installed_setback when seated.
    """
    path = _poses(poses)
    if any(q[2] < 0 for q in path):
        raise ValueError('Maximum upper height helper requires nonnegative tilt')
    y = float(installed_setback)-path[0][0]
    best = (math.inf, None, None)
    for index, (a, b) in enumerate(zip(path[:-1], path[1:])):
        d = tuple(b[i]-a[i] for i in range(3))
        def derivative(u):
            qy, _, theta = _lerp(a, d, u)
            return d[0]*math.sin(theta)-d[2]*(qy*math.cos(theta)+y)
        # Derivative numerator derivative = dtheta^2*qy*sin(theta).
        # Tilt is nonnegative, so its only interior sign change is at qy=0.
        for u in _critical_points(derivative, _linear_zero(a[0], d[0])):
            q = _lerp(a, d, u)
            if abs(q[2]) < 1e-14:
                front = y+q[0]
                if front < -NUMERICAL_TOLERANCE_MM:
                    raise ValueError('Requested front plane penetrates board at zero tilt')
                # Include the limiting value at a zero-angle endpoint.
                value = d[0]/d[2] if abs(front) < 1e-14 and d[2] else math.inf
            else:
                value = (y*math.cos(q[2])+q[0])/math.sin(q[2])
            if value < best[0]:
                best = (value, q, index)
    return dict(installed_setback_mm=float(installed_setback), design_front_y_mm=y,
                maximum_design_top_z_mm=best[0] if math.isfinite(best[0]) else None,
                maximum_physical_height_above_upper_hole_mm=(best[0]+path[0][1]) if math.isfinite(best[0]) else None,
                limiting_pose=_pose_dict(best[1]) if best[1] else None,
                segment_index=best[2], contact_at_limit=True)


def certify_host_polygon(poses, vertices_yz):
    """Continuously certify that a polygon stays in front of the full board.

    All vertices are design-coordinate (Y,Z) points; arbitrary X width is
    allowed. A linear functional reaches its minimum at a polygon vertex,
    including for nonconvex polygons. This envelope is sufficient for a board
    with holes, and exact for the requirement to remain wholly in front.
    Zero-clearance contact is allowed within the stated numerical tolerance.
    """
    path = _poses(poses)
    vertices = [tuple(map(float, v)) for v in vertices_yz]
    if len(vertices) < 3 or any(len(v) != 2 or not all(math.isfinite(x) for x in v) for v in vertices):
        raise ValueError('Supply at least three finite Y/Z vertices')
    best = (math.inf, None, None, None)
    evaluations = 0
    for vi, (y, z) in enumerate(vertices):
        for index, (a, b) in enumerate(zip(path[:-1], path[1:])):
            d = tuple(b[i]-a[i] for i in range(3))
            def derivative(u):
                _, _, theta = _lerp(a, d, u)
                return d[0]-d[2]*(y*math.sin(theta)+z*math.cos(theta))
            # Second derivative is -dtheta^2*(y*cos(theta)-z*sin(theta)).
            # Split at all its zeros, making the first derivative monotone.
            cuts = []
            if d[2]:
                base = math.atan2(y, z)
                for k in range(-2, 3):
                    cuts.append((base+k*math.pi-a[2])/d[2])
            for u in _critical_points(derivative, cuts):
                q = _lerp(a, d, u)
                value = y*math.cos(q[2])-z*math.sin(q[2])+q[0]
                evaluations += 1
                if value < best[0]:
                    best = (value, q, index, vi)
    return dict(passed=best[0] >= -NUMERICAL_TOLERANCE_MM,
                minimum_board_front_clearance_mm=best[0],
                limiting_pose=_pose_dict(best[1]), segment_index=best[2],
                limiting_vertex_index=best[3], vertices_design_yz_mm=vertices,
                numerical_tolerance_mm=NUMERICAL_TOLERANCE_MM,
                method='Continuous extrema at segment endpoints and every stationary point; monotone derivative intervals and 64-step bisection.',
                evaluated_candidates=evaluations, arbitrary_x_width=True,
                zero_clearance_contact_allowed=True)


def make_report(motion_file=ROOT/'round_motion_results.json', top_design_z=None,
                physical_lip_height=5.0):
    motion_file = Path(motion_file)
    raw = motion_file.read_bytes()
    motion = json.loads(raw)
    poses = motion['removal_poses']
    p = motion['parameters']
    if top_design_z is None:
        top_design_z = float(physical_lip_height)-poses[0]['z']
    y0 = p['front_gap']
    polygon = [(y0, p['spine_top']-p['spine_height']),
               (p['spine_depth'], p['spine_top']-p['spine_height']),
               (p['spine_depth'], top_design_z), (y0, top_design_z)]
    verification = motion.get('verification', {})
    return dict(
        schema_version=1,
        motion_input=dict(file=motion_file.relative_to(ROOT).as_posix() if motion_file.is_relative_to(ROOT) else str(motion_file), sha256=hashlib.sha256(raw).hexdigest(),
                          name=motion.get('name'), reported_passed=verification.get('passed')),
        scope='Host envelope on the supplied anchor motion path only. Changed pegs, locator depth, cam, board dimensions or motion require corresponding motion evidence and a regenerated envelope.',
        coordinates=dict(design='Anchor design Y/Z coordinates', installed='First removal pose; physical heights measured from upper hole center',
                         seated_pose=poses[0]),
        inequality='cos(theta)*Y - sin(theta)*Z + pose.y >= 0 at every interpolated pose',
        envelope='Y_min(Z) = max_path((sin(theta)*Z - pose.y)/cos(theta))',
        envelope_scope='Exact for keeping the host wholly in front of the board plane; conservative for the perforated board because it takes no credit for holes. Valid for arbitrary host width in X.',
        flush_front_height_limit=max_flush_height(poses),
        example_setbacks=[required_setback(poses, h) for h in [10, 20, 30, 50, 100]],
        proposed_sharp_host=dict(top_design_z_mm=top_design_z,
                                 top_physical_height_above_upper_hole_mm=top_design_z+poses[0]['z'],
                                 board_facing_corner_radius_mm=0.0,
                                 certificate=certify_host_polygon(poses, polygon),
                                 after_bearing_release_certificate=certify_host_polygon(poses[1:], polygon)),
        assumptions=[
            'Piecewise linear interpolation of Y, Z, and rotation angle exactly as in the input motion evidence.',
            'Rigid host fused to anchor; translation in Y/Z and rotation about X only.',
            'Sharp board-facing corner; no credit is taken for the existing 0.65 mm spine fillet.',
            f'The limit permits tangency during motion; the selected sharp lip is {top_design_z+poses[0]["z"]:g} mm above the upper hole center when seated.',
            'Envelope checks geometry only; no gravity preload, friction, printer accuracy, load rating, or physical fit claim.',
            'A stepped or sloped host back can follow the envelope; a single vertical front plane must use the maximum required setback over its full height.'
        ], numerical_tolerance_mm=NUMERICAL_TOLERANCE_MM)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion', type=Path, default=ROOT/'round_motion_results.json')
    parser.add_argument('--output', type=Path, default=ROOT/'host_envelope.json')
    parser.add_argument('--top-design-z', type=float)
    parser.add_argument('--physical-lip-height', type=float, default=5.0)
    args = parser.parse_args()
    report = make_report(args.motion, args.top_design_z, args.physical_lip_height)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(output=str(args.output), flush_front_height_limit=report['flush_front_height_limit'],
                          sharp_host_passed=report['proposed_sharp_host']['certificate']['passed']), indent=2))
