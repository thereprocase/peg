"""Conservative motion bounds for the added conformal bearing segments.

Every additional X slab encloses the true curved patch at its inner edge and
uses the smaller hole section at its outer edge. Rotation about X preserves
the slabs. The untouched round core retains its existing capsule bound.
"""
from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
import time

import numpy as np

from conformal_anchor import contract
from round_motion import RoundStudy, contact_certificate, pose_dict

ROOT = Path(__file__).resolve().parent


class ConformalStudy(RoundStudy):
    def __init__(self, overrides=None, slabs=192, clearance=0.0, geometry_contract=None):
        self.contract = geometry_contract or contract(overrides)
        p = self.contract['parameters'] | {'clearance':clearance}
        super().__init__(p,slabs=slabs)
        b = self.contract['conformal_bearing']
        R = b['radius_mm']
        edges = np.linspace(0,b['arc_width_mm']/2,slabs+1)
        bottom = -np.sqrt(R*R-edges[:-1]**2)
        top = b['chord_z_relative_to_hole_mm']
        polys, outer, rows = [], [], []
        for land in b['lands']:
            z = land['center_z']
            rear, front = land['rear_y'], land['front_y']
            # Ignoring lower chamfer conservatively encloses the additional nose.
            if land['name'] == 'lower':
                rear -= p['locator_chamfer']
            arr = np.empty((slabs,4,2))
            arr[:,0,0] = rear; arr[:,1,0] = front
            arr[:,2,0] = front; arr[:,3,0] = rear
            arr[:,0:2,1] = (z+bottom)[:,None]
            arr[:,2:4,1] = z+top
            polys.append(arr)
            outer.append(edges[1:])
            rows.append(np.full(slabs,0 if land['name']=='upper' else -p['pitch']))
        self.extra_points = np.concatenate(polys)
        self.extra_outer = np.concatenate(outer)
        self.extra_rows = np.concatenate(rows)
        self.radius = max(self.radius,float(np.linalg.norm(self.extra_points,axis=2).max()))

    def extra_distance(self,q,real=False):
        p = self.p
        t = p['board_thickness']
        a = math.radians(q[2]); c,s = math.cos(a),math.sin(a)
        xy = self.extra_points @ np.array([[c,s],[-s,c]]) + q[:2]
        R = p['hole_diameter']/2-(0 if real else p['clearance'])
        h = np.sqrt(np.maximum(0,R*R-self.extra_outer**2))
        lo,hi = self.extra_rows-h,self.extra_rows+h
        yy,zz = xy[:,:,0],xy[:,:,1]
        candidates = [np.where((yy>=-t)&(yy<=0),zz,np.nan)]
        yn,zn = np.roll(yy,-1,axis=1),np.roll(zz,-1,axis=1)
        for wall in [-t,0]:
            with np.errstate(divide='ignore',invalid='ignore'):
                u = (wall-yy)/(yn-yy)
                section = zz+u*(zn-zz)
            candidates.append(np.where((u>=0)&(u<=1),section,np.nan))
        sections = np.concatenate(candidates,axis=1)
        zmin = np.min(np.where(np.isnan(sections),np.inf,sections),axis=1)
        zmax = np.max(np.where(np.isnan(sections),-np.inf,sections),axis=1)
        if np.any(np.isfinite(zmin)&((zmin<lo-1e-10)|(zmax>hi+1e-10))):
            return 0.0
        dy = np.maximum.reduce([-t-yy,yy,np.zeros_like(yy)])
        dl,du = np.maximum(zz-lo[:,None],0),np.maximum(hi[:,None]-zz,0)
        vertex = np.min(np.minimum(dy*dy+dl*dl,dy*dy+du*du))
        corners = np.stack([np.column_stack([np.full(len(h),-t),lo]),
                            np.column_stack([np.zeros(len(h)),lo]),
                            np.column_stack([np.full(len(h),-t),hi]),
                            np.column_stack([np.zeros(len(h)),hi])],axis=1)
        edges = np.roll(xy,-1,axis=1)-xy
        delta = corners[:,:,None,:]-xy[:,None,:,:]
        fac = np.sum(delta*edges[:,None,:,:],axis=3)/np.sum(edges*edges,axis=2)[:,None,:]
        dd = delta-np.clip(fac,0,1)[:,:,:,None]*edges[:,None,:,:]
        return float(np.sqrt(min(vertex,np.min(np.sum(dd*dd,axis=3)))))

    def collision(self,q,real=False):
        return super().collision(q,real) or self.extra_distance(np.asarray(q),real)<=1e-8

    def clear_distance(self,q,real=False):
        return min(super().clear_distance(q,real),self.extra_distance(np.asarray(q),real))


def screen_baseline(count=200,slabs=192):
    from round_verify_cad import sample_poses
    source = json.loads((ROOT/'round_motion_results.json').read_text())
    study = ConformalStudy(slabs=slabs)
    # Contact poses need a separate exact certificate; finite slab bounds
    # deliberately cannot represent conformal zero clearance at seating.
    poses = sample_poses(source['removal_poses'][1:],count)
    failed = []
    for i,q in enumerate(poses):
        if study.collision(q):
            failed.append({'index':i,'pose':q,
                           'round_core':super(ConformalStudy,study).collision(q),
                           'extra_clearance_bound_mm':study.extra_distance(np.asarray(q))})
    return {'scope':'Conservative sampled screen of original free path; exact contact excluded.',
            'samples':len(poses),'slabs_per_half':slabs,'radial_reserve_mm':0,
            'passed':not failed,'failed_poses':failed}


def seating_certificate(study,a,b):
    """Exact zero-angle translation sweep of core and circular bearing caps.

    Every X section of a lower circular cap extends from -h to -H, where
    h = sqrt(R^2-X^2) and H = R cos(angle/2). An upward shift dz fits the
    circular bore whenever 0 <= dz <= 2H: its bottom stays above -h and
    its top remains below +h. Linear translation attains these extrema
    at endpoints. The conical nose is a subset of the full-radius cap.
    """
    if a[2]!=0 or b[2]!=0:
        raise ValueError('Exact seating certificate only covers pure translations')
    g=study.contract; p=g['parameters']
    half_height=-g['conformal_bearing']['chord_z_relative_to_hole_mm']
    lifts=[q[1]+p['seat_drop'] for q in [a,b]]
    min_lift,max_lift=min(lifts),max(lifts)
    upper_margin=2*half_height-max_lift
    core=contact_certificate(study,a,b)
    core['passed']=bool(core['passed'])
    passed=core['passed'] and min_lift>=-1e-9 and upper_margin>=-1e-9
    return {'passed':bool(passed),'start':list(a),'end':list(b),'round_core_exact_sweep':core,
            'minimum_arc_lift_mm':min_lift,'maximum_arc_lift_mm':max_lift,
            'minimum_arc_half_height_mm':half_height,
            'arc_upper_boundary_margin_mm':upper_margin,
            'method':'Exact round-core translation sweep plus full-width circular-cap containment inequalities; linear lift extrema occur at endpoints.',
            'intended_contact_allowed':True}


def certify_candidate(output=None, slabs=768, max_seconds=180):
    """Recheck the original round trajectory against the current complete model."""
    output=Path(output or ROOT/'cad/conformal/conformal_motion_results.json')
    baseline=ROOT/'round_motion_results.json'
    gpath=ROOT/'cad/conformal/conformal_120_geometry.json'
    spath=ROOT/'cad/conformal/conformal_120.step'
    data=json.loads(baseline.read_text(encoding='utf-8'))
    g=json.loads(gpath.read_text(encoding='utf-8'))
    study=ConformalStudy(slabs=slabs,geometry_contract=g)
    poses=np.array([[q[k] for k in ['y','z','theta_deg']] for q in data['removal_poses']])
    seated=np.array([g['seated_pose'][k] for k in ['y','z','theta_deg']])
    if not np.array_equal(poses[0],seated):
        raise ValueError('Baseline path does not begin at the current seated pose')
    contact=seating_certificate(study,poses[0],poses[1])
    if not contact['passed']:
        raise ValueError(f'Exact seating segment failed: {contact}')
    report={'name':'conformal_120_default_3p94','parameters':g['parameters'],
            'geometry_contract':g,'removal_poses':[pose_dict(q) for q in poses],
            'install_poses':[pose_dict(q) for q in poses[::-1]],
            'trajectory':'Original round removal waypoints, reverified against the complete conformal model without path adjustments.',
            'verification':{'passed':False,'complete':False,'exact_seating_certificates':[contact],
                            'continuous_free_motion_certificates':[],
                            'x_slabs_per_half':slabs,'radial_bore_clearance_reserved_mm':0.0,
                            'lower_nose_ignored_conservatively':True},
            'source_sha256':{path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in [baseline,gpath,spath,Path(__file__),ROOT/'conformal_anchor.py',ROOT/'round_motion.py',ROOT/'round_anchor.py']},
            'scope':'Continuous ideal rigid geometry clearance, including exact final contact. The conformal arcs have zero nominal radial gap; this study reserves no additional radial bore clearance. No print or load qualification.'}
    started=time.monotonic()
    for i,(a,b) in enumerate(zip(poses[1:-1],poses[2:])):
        if time.monotonic()-started > max_seconds:
            report['verification']['timeout']=True
            break
        certificate=study.certify(a,b)
        report['verification']['continuous_free_motion_certificates'].append({'segment_index':i+1,**certificate})
        report['elapsed_seconds']=round(time.monotonic()-started,3)
        output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        if not certificate['passed']:
            print(json.dumps({'failed_segment':i+1,'certificate':certificate}),flush=True)
            return report
        print(f'Certified {i+1}/{len(poses)-2} free segments',flush=True)
    certs=report['verification']['continuous_free_motion_certificates']
    complete=len(certs)==len(poses)-2
    report['verification'].update(passed=complete and all(c['passed'] for c in certs),complete=complete,
                                  total_interval_certificates=sum(c.get('leaves',0) for c in certs))
    report['summary']={'maximum_install_tilt_deg':float(poses[:,2].max()),
                       'maximum_lift_above_seated_mm':float(poses[:,1].max()-poses[0,1]),
                       'nominal_lip_mm':g['host_interface']['nominal_flush_lip_height_above_upper_hole_mm']}
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certify',action='store_true')
    parser.add_argument('--slabs',type=int,default=768)
    parser.add_argument('--max-seconds',type=float,default=180)
    args=parser.parse_args()
    if args.certify:
        result=certify_candidate(slabs=args.slabs,max_seconds=args.max_seconds)
        print(json.dumps({'verification_passed':result['verification']['passed'],
                          'elapsed_seconds':result.get('elapsed_seconds')},indent=2))
    else:
        result=screen_baseline(slabs=args.slabs)
        out=ROOT/'cad/conformal/conservative_path_screen.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({**result,'failed_poses':result['failed_poses'][:3]},indent=2))
