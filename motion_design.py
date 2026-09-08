"""Reproducible parametric pegboard anchor geometry and rigid-body motion study.

Coordinates: X across holes; Y toward user; Z up. Board front Y=0,
rear Y=-board_thickness. Hole centers (X,Z)=(0,0),(0,-pitch).
Extrude make_profile(parameters) from X=-width/2 to +width/2.
Dependencies: numpy, shapely. All dimensions millimeters; angles degrees.
"""
from __future__ import annotations
import math, json, heapq
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely.affinity import affine_transform

DEFAULTS=dict(board_thickness=3.94,hole_diameter=6.35,pitch=25.4,width=4.0,
    neck_height=3.6,spine_depth=4.5,spine_height=34.6,pull_clearance=.47,elbow_offset=None,
    tongue_run=5.0,tongue_rise=3.0,locator_depth=2.3,locator_height=3.0,
    hole_clearance=.10,front_gap=.15,seat_drop=.12)

def get_parts(params=None):
    p=DEFAULTS | (params or {})
    if not (p['hole_diameter']>p['width']>0):raise ValueError('hole_diameter must exceed positive width')
    if min(p[k] for k in ['board_thickness','neck_height','spine_depth','spine_height','locator_height','locator_depth','tongue_run','tongue_rise'])<=0:raise ValueError('All dimensions must be positive')
    t=p['board_thickness'];h=p['neck_height'];pitch=p['pitch']
    hc=math.sqrt(p['hole_diameter']**2-p['width']**2)/2
    if h>=2*(hc-p['hole_clearance']):raise ValueError('Neck section does not fit circular hole with requested margin')
    z0=-hc+h/2+p['seat_drop']
    m=p['tongue_rise']/p['tongue_run'];r=h/2
    if p['elbow_offset'] is None:
        p['elbow_offset']=p['pull_clearance']-p['front_gap']-(2*hc-r)/m+r*math.sqrt(1+1/m**2)
    neckrear=-t-p['elbow_offset']
    hook=LineString([(1.4,z0),(neckrear,z0),(neckrear-p['tongue_run'],z0+p['tongue_rise'])]).buffer(h/2,quad_segs=12,cap_style=1,join_style=1)
    spine=box(p['front_gap'],4.2-p['spine_height'],p['spine_depth'],4.2).buffer(-.65,quad_segs=8).buffer(.65,quad_segs=8)
    zlow=-pitch+z0;lh=p['locator_height']/2; chamfer=min(.7,p['locator_depth']*.35,lh*.6)
    loc=Polygon([(.6,zlow-lh),(-p['locator_depth']+chamfer,zlow-lh),(-p['locator_depth'],zlow-lh+chamfer),(-p['locator_depth'],zlow+lh-chamfer),(-p['locator_depth']+chamfer,zlow+lh),(.6,zlow+lh)])
    complete=unary_union([hook,spine,loc])
    if complete.geom_type!='Polygon' or not complete.is_valid:raise ValueError('Dimensions produce disconnected/invalid anchor')
    return p,{'hook':hook,'spine':spine,'locator':loc,'complete':complete},z0

def make_profile(params=None):
    """Return closed-solid exterior vertices [(y,z),...] without repeated endpoint."""
    return np.asarray(get_parts(params)[1]['complete'].exterior.coords[:-1]).tolist()

def transformed(poly,pose):
    y,z,a=pose;c=math.cos(math.radians(a));s=math.sin(math.radians(a))
    return affine_transform(poly,[c,-s,s,c,y,z])

def pose_json(p,stage='threading'):
    return dict(y=round(float(p[0]),8),z=round(float(p[1]),8),theta_deg=round(float(p[2]),8),stage=stage)

class Study:
    def __init__(self,p=None):
        self.p,self.parts,self.z0=get_parts(p); self.poly=self.parts['complete'];p=self.p
        self.half=math.sqrt(p['hole_diameter']**2-p['width']**2)/2
        self.obs=self.obstacles(self.half-p['hole_clearance'])
        self.real_obs=self.obstacles(self.half)
        self.radius=max(math.hypot(y,z) for y,z in self.poly.exterior.coords)
        self.cache={}
    def obstacles(self,h):
        pitch=self.p['pitch'];t=self.p['board_thickness']
        return unary_union([box(-t,-100,0,-pitch-h),box(-t,-pitch+h,0,-h),box(-t,h,0,100)])
    def collision(self,pose,real=False):
        return transformed(self.poly,pose).intersection(self.real_obs if real else self.obs).area>1e-9
    def distance(self,pose): return transformed(self.poly,pose).distance(self.real_obs)
    def gridsearch(self,step=.05,astep=.25):
        """A* removal with simultaneous lift/tip/translation for a snug throat."""
        base=(-self.p['front_gap']+.03,0,0)
        start=(0,0,0);q=[(0,0,start)];prev={start:None};best={start:0};self.cache={}
        def pose(n):return(n[0]*step+base[0],n[1]*step+base[1],n[2]*astep)
        def valid(n):
            if not(-10<=n[0]<=int(30/step) and -int(2/step)<=n[1]<=int(12/step) and 0<=n[2]<=int(65/astep)):return False
            if n not in self.cache:self.cache[n]=transformed(self.poly,pose(n)).distance(self.obs)>.003
            return self.cache[n]
        if not valid(start):return None
        moves=[(dy,dz,da) for dy in [-1,0,1] for dz in [-1,0,1] for da in [-1,0,1] if(dy,dz,da)!=(0,0,0)]
        while q:
            _,cost,n=heapq.heappop(q)
            if cost!=best[n]:continue
            if transformed(self.poly,pose(n)).bounds[0]>1:
                out=[]
                while n is not None:out.append(pose(n));n=prev[n]
                return out[::-1]
            for d in moves:
                nn=tuple(n[i]+d[i] for i in range(3))
                if not valid(nn):continue
                nc=cost+math.sqrt(d[0]**2+d[1]**2+(.5*d[2])**2)
                if nc<best.get(nn,1e100):
                    best[nn]=nc;prev[nn]=n
                    heapq.heappush(q,(nc+max(0,14/step-nn[0]),nc,nn))
        return None
    def sampled_segment_clear(self,a,b,max_movement=.10):
        a=np.asarray(a,float);b=np.asarray(b,float)
        disp=np.linalg.norm(b[:2]-a[:2])+self.radius*math.radians(abs(b[2]-a[2]))
        n=max(1,math.ceil(disp/max_movement))
        # Keep the deliberately reserved hole allowance in all free-motion shortcuts.
        return all(transformed(self.poly,a+(b-a)*u/n).distance(self.obs)>.002 for u in range(n+1))
    def simplify(self,path):
        out=[path[0]];i=0
        while i<len(path)-1:
            j=len(path)-1
            while j>i+1 and not self.sampled_segment_clear(path[i],path[j]):j-=1
            out.append(path[j]);i=j
        return out
    def certify_segment(self,a,b,depth=0):
        """Conservative continuous sweep certificate via midpoint distance bound.

        For ALL intermediate poses, Hausdorff displacement from midpoint is <=
        |delta_translation|/2 + 2*R*sin(|delta_angle|/4). If midpoint obstacle
        distance exceeds this quantity, entire segment is collision-free.
        Otherwise bisect; no result relies solely on sampled frames.
        """
        a=np.asarray(a,float);b=np.asarray(b,float);m=(a+b)/2
        bound=np.linalg.norm(b[:2]-a[:2])/2+2*self.radius*math.sin(math.radians(abs(b[2]-a[2]))/4)
        dist=transformed(self.poly,m).distance(self.obs)
        if dist>bound+1e-9:
            return {'passed':True,'leaves':1,'lower_clearance_mm':dist-bound,'max_bound_mm':bound}
        if depth>=22 or self.collision(m):return {'passed':False,'pose':m.tolist(),'depth':depth}
        l=self.certify_segment(a,m,depth+1);r=self.certify_segment(m,b,depth+1)
        if not l['passed'] or not r['passed']:return {'passed':False,'left':l,'right':r}
        return {'passed':True,'leaves':l['leaves']+r['leaves'],'lower_clearance_mm':min(l['lower_clearance_mm'],r['lower_clearance_mm']),'max_bound_mm':max(l['max_bound_mm'],r['max_bound_mm'])}
    def translation_sweep(self,a,b):
        """Exact polygonal sweep for fixed-angle linear translation, incl contact."""
        a=np.asarray(a,float);b=np.asarray(b,float)
        if abs(a[2]-b[2])>1e-10:raise ValueError('Pure translation only')
        pa=transformed(self.poly,a);pb=transformed(self.poly,b);d=b[:2]-a[:2]
        polys=[pa,pb];pts=np.asarray(pa.exterior.coords)
        for u,v in zip(pts[:-1],pts[1:]):
            q=Polygon([u,v,v+d,u+d])
            if q.area>1e-12:polys.append(q)
        sweep=unary_union(polys)
        area=sweep.intersection(self.real_obs).area
        return {'passed':area<1e-8,'intersection_area_mm2':area,'method':'exact edge-quadrilateral union for pure translation; zero-clearance contact allowed'}
    def first_collision(self,fn,maxq,step=.01):
        prev=0
        for q in np.arange(step,maxq+step/2,step):
            if self.collision(fn(float(q)),real=True):
                lo=prev;hi=float(q)
                for _ in range(35):
                    mid=(lo+hi)/2
                    if self.collision(fn(mid),real=True):hi=mid
                    else:lo=mid
                return (lo+hi)/2
            prev=float(q)
        return None
    def build(self,name):
        path=self.gridsearch()
        if path is None:raise RuntimeError(f'No path for {name}')
        search_states=len(self.cache);simple=self.simplify(path)
        # A fully clear staging pose lets the operator establish angle before approaching.
        staging=(max(28,simple[-1][0]+12),simple[-1][1],simple[-1][2])
        level=(staging[0],staging[1],0)
        contact=(-self.p['front_gap'],-self.p['seat_drop'],0)
        removal=[contact]+simple+[staging,level]
        certs=[self.certify_segment(a,b) for a,b in zip(removal[1:-1],removal[2:])]
        seating=self.translation_sweep(contact,simple[0])
        if not all(c['passed'] for c in certs) or not seating['passed']:raise RuntimeError('Continuous motion certificate failed')
        sampled=[]
        for j,(a,b) in enumerate(zip(removal[:-1],removal[1:])):
            a=np.asarray(a,float);b=np.asarray(b,float)
            travel=np.linalg.norm(b[:2]-a[:2])+self.radius*math.radians(abs(b[2]-a[2]))
            n=max(1,math.ceil(travel/.025))
            for k in range(n):sampled.append(a+(b-a)*k/n)
        sampled.append(np.asarray(removal[-1]))
        collisions=sum(self.collision(q,real=True) for q in sampled)
        pull=self.first_collision(lambda q:(contact[0]+q,contact[1],0),10,.01)
        lift=self.first_collision(lambda q:(contact[0],contact[1]+q,0),8,.01)
        # Rotate upper anchor outwards around the bottom edge of the flat spine land.
        pivot=np.array([self.p['front_gap'],4.2-self.p['spine_height']+.65])
        def rock(q):
            a=-math.radians(q);c=math.cos(a);s=math.sin(a)
            rp=np.array([c*pivot[0]-s*pivot[1],s*pivot[0]+c*pivot[1]])
            trans=np.array(contact[:2])+pivot-rp
            return (trans[0],trans[1],-q)
        rocking=self.first_collision(rock,12,.005)
        mins=[transformed(self.poly,q).bounds[0] for q in sampled]
        backside=max(0,-self.p['board_thickness']-min(mins))
        stages=[]
        for i,q in enumerate(removal):
            stage='release bearing contact' if i<=1 else 'tip and lift' if i<len(removal)-3 else 'withdraw tongue' if i==len(removal)-3 else 'clear approach' if i==len(removal)-2 else 'free in front'
            stages.append(pose_json(q,stage))
        install=[]
        for i,q in enumerate(stages[::-1]):
            q=dict(q)
            q['stage']='free in front' if i==0 else 'set insertion angle' if i==1 else 'thread upper tongue' if i==2 else 'rotate down and engage lower locator' if i<len(stages)-2 else 'align' if i==len(stages)-2 else 'seat on bore and face'
            install.append(q)
        return {'name':name,'parameters':self.p,'install_poses':install,'removal_poses':stages,
          'summary':{'upper_neck_center_z_mm':self.z0,'effective_bore_half_height_mm':self.half,'maximum_install_tilt_deg':max(q[2] for q in removal),'maximum_lift_mm':max(q[1] for q in removal)-contact[1],
          'rear_wall_clearance_required_mm':backside,'straight_outward_travel_until_stop_mm':pull,'straight_lift_until_stop_mm':lift,'outward_rocking_about_lower_land_deg':rocking,'rocking_pivot_yz':pivot.tolist(),
          'retaining_overlap_above_effective_bore_mm':self.z0+self.p['tongue_rise']+self.p['neck_height']/2+contact[1]-self.half,
          'section_area_mm2':self.p['width']*self.p['neck_height'],'section_modulus_mm3':self.p['width']*self.p['neck_height']**2/6},
          'verification':{'passed':collisions==0 and seating['passed'] and all(c['passed'] for c in certs),'astar_validity_checks':search_states,'raw_astar_waypoints':len(path),'simplified_waypoints':len(removal),
          'dense_verification_frames':len(sampled),'dense_max_point_travel_mm':.025,'colliding_frames':collisions,'continuous_free_motion_certificates':certs,'contact_segment_certificate':seating,
          'reserved_bore_half_height_clearance_mm':self.p['hole_clearance'],'continuous_free_motion_uses_shrunk_bores':True,'assumptions':['Perfect cylindrical bores, flat rigid board, exact polygonal printed geometry.','Constant X width; no yaw or roll. Effective circular-bore height exactly accounts for full width.','Clearance study includes complete upper hook, lower locator, and spine.','Physical contact has zero intended gap at final seating; certified free threading reserves hole_clearance in bore half-height.','No FEA, fatigue, creep, extrusion error, board breakout, or physical load testing.','Attached mount geometry can obstruct the verified path and must be checked separately.']}}

def generate(outdir=None):
    out=Path(outdir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    variants=[('default_3p94',{}),('stock_4p19',{'board_thickness':4.19}),('nominal_3_16',{'board_thickness':4.7625}),('true_1_4',{'board_thickness':6.35}),('lowes_white_9_32_holes',{'board_thickness':3.94,'hole_diameter':7.14375})]
    results=[]
    for name,p in variants:
        result=Study(p).build(name);results.append(result)
        print(name,result['summary'],result['verification']['passed'],flush=True)
    p,parts,z0=get_parts()
    geom={'parameters':p,'width':p['width'],'profile_yz':make_profile(p),'parts_yz':{k:np.asarray(v.exterior.coords[:-1]).tolist() for k,v in parts.items() if k!='complete'},
       'coordinate_system':{'units':'mm','board_front_y':0,'board_rear_y':'-board_thickness','upper_hole_center_z':0,'lower_hole_center_z':'-pitch','extrusion_x':['-width/2','width/2'],'rotation':'yprime=cos(theta)*y-sin(theta)*z+pose.y; zprime=sin(theta)*y+cos(theta)*z+pose.z'},'upper_neck_center_z':z0,
       'variants':[{k:r[k] for k in ['name','parameters']}|{'profile_yz':make_profile(r['parameters'])} for r in results]}
    report={'study':'Planar rigid-body insertion/removal and interference study','variants':results,'passed':all(r['verification']['passed'] for r in results),
       'continuous_method':'Midpoint shape distance to obstacle exceeds maximum rigid displacement over each certified interval; recursively bisected. Pure-translation contact segment uses exact swept polygon union. Reverse traversal inherits identical swept volume.'}
    (out/'geometry.json').write_text(json.dumps(geom,indent=2));(out/'motion_results.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':generate()
