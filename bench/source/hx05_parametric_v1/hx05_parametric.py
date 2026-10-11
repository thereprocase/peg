"""HX05 native FreeCAD features. Requires only FreeCAD and Python's stdlib."""
import math
import FreeCAD as App
import Part
V = App.Vector

def value(obj, name):
    x = getattr(obj, name)
    return float(x.Value if hasattr(x, 'Value') else x)

def unit(v):
    if v.Length < 1e-12:
        raise ValueError('Zero direction vector')
    return v / v.Length

def ring(center, axis, radius, count=20):
    axis = unit(axis)
    a = unit(axis.cross(V(1, 0, 0) if abs(axis.x) < .9 else V(0, 1, 0)))
    b = axis.cross(a)
    return [center + (a * math.cos(2*math.pi*i/count) + b * math.sin(2*math.pi*i/count))*radius for i in range(count)]

def hull(points):
    """Incremental convex hull, with coplanar triangles merged into CAD faces."""
    pts = list({tuple(round(c, 10) for c in p): p for p in points}.values())
    first = min(range(len(pts)), key=lambda i: pts[i].x)
    second = max(range(len(pts)), key=lambda i: (pts[i]-pts[first]).Length)
    edge = pts[second]-pts[first]
    third = max(range(len(pts)), key=lambda i: edge.cross(pts[i]-pts[first]).Length)
    normal = unit(edge.cross(pts[third]-pts[first]))
    fourth = max(range(len(pts)), key=lambda i: abs(normal.dot(pts[i]-pts[first])))
    tetra = [first, second, third, fourth]
    if len(set(tetra)) != 4:
        raise ValueError('Gusset hull collapsed; check tool position and radius')
    inside = sum((pts[i] for i in tetra), V()) / 4
    def face(a, b, c):
        n = unit((pts[b]-pts[a]).cross(pts[c]-pts[a]))
        if n.dot(inside-pts[a]) > 0:
            b, c, n = c, b, -n
        return a, b, c, n, -n.dot(pts[a])
    faces = [face(first,second,third), face(first,fourth,second), face(first,third,fourth), face(second,fourth,third)]
    for index, point in enumerate(pts):
        if index in tetra:
            continue
        visible = [f for f in faces if f[3].dot(point)+f[4] > 1e-7]
        if not visible:
            continue
        edges = {}
        for f in visible:
            for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
                key = tuple(sorted((a,b)))
                if key in edges:
                    del edges[key]
                else:
                    edges[key] = (a,b)
        faces = [f for f in faces if f not in visible]
        faces.extend(face(a,b,index) for a,b in edges.values())
    groups = []
    for a,b,c,n,d in faces:
        same = next((g for g in groups if (g[0]-n).Length < 1e-6 and abs(g[1]-d) < 1e-5), None)
        if same is None:
            groups.append([n,d,{a,b,c}])
        else:
            same[2].update((a,b,c))
    surfaces = []
    for n,d,indices in groups:
        points = [pts[i] for i in sorted(indices)]
        center = sum(points,V()) / len(points)
        a = unit(points[0]-center); b = n.cross(a)
        projected=sorted(((p-center).dot(a),(p-center).dot(b),i) for i,p in enumerate(points))
        def cross2(o,a,b):
            return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lower=[]; upper=[]
        for point in projected:
            while len(lower)>=2 and cross2(lower[-2],lower[-1],point)<=1e-8: lower.pop()
            lower.append(point)
        for point in reversed(projected):
            while len(upper)>=2 and cross2(upper[-2],upper[-1],point)<=1e-8: upper.pop()
            upper.append(point)
        points=[points[p[2]] for p in lower[:-1]+upper[:-1]]
        try:
            surfaces.append(Part.Face(Part.makePolygon(points+[points[0]])))
        except Part.OCCError:
            surfaces.extend(Part.Face(Part.makePolygon([points[0],points[i],points[i+1],points[0]])) for i in range(1,len(points)-1))
    shape = Part.Solid(Part.Shell(surfaces))
    if shape.Volume < 0:
        shape.reverse()
    if not shape.isValid():
        raise ValueError('Invalid convex hull; restore the last valid parameter values')
    return shape

def frame(key):
    p = key.Parameters
    up = value(key,'UpAngle'); out = value(key,'OutOfPlane')
    if value(p,'MinimumUpAngle') < 10:
        raise ValueError('Minimum upward angle must remain at least 10 degrees')
    if value(p,'AFClearance') < 0 or value(p,'LeadDepth') <= 0 or value(p,'LeadOpening') <= 0:
        raise ValueError('Clearance must be nonnegative and lead-in dimensions positive')
    if up < value(p,'MinimumUpAngle')-1e-9 or up >= 90:
        raise ValueError('%s: upward angle must be at least %g degrees and below 90' % (key.Label,value(p,'MinimumUpAngle')))
    y = math.sin(math.radians(out)); z = math.sin(math.radians(up))
    if out <= 0 or y*y+z*z >= 1:
        raise ValueError('%s: incompatible upward/out-of-plane angles' % key.Label)
    u = V(math.sqrt(1-y*y-z*z),y,z)
    flat = unit(V(u.z,0,-u.x)); roll = math.radians(value(key,'HandleRoll'))
    b = flat*math.cos(roll)+u.cross(flat)*math.sin(roll)
    tip = V(value(key,'TipX'),value(key,'TipY'),value(key,'TipZ'))
    guide = value(key,'GuideLength'); lead = value(p,'LeadDepth')
    if guide < 40 or guide+lead >= value(key,'ToolLength')-18:
        raise ValueError('%s: guide must be >=40 mm and leave room below the handle' % key.Label)
    radius = value(key,'OuterRadius')
    if radius < (value(key,'NominalAF')+value(p,'AFClearance')+2*value(p,'LeadOpening'))/math.sqrt(3)+1:
        raise ValueError('%s: increase the outer radius to retain at least 1 mm at the lead-in' % key.Label)
    if value(p,'VentDiameter') <= 0 or value(p,'FloorDepth') < value(p,'VentDiameter')+.5:
        raise ValueError('Floor must exceed vent diameter by at least 0.5 mm')
    return tip,u,b,tip+u*(guide+lead)

def hexwire(center,u,b,af):
    side = u.cross(b); radius = af/math.sqrt(3)
    points = [center+(b*math.cos(math.pi/6+i*math.pi/3)+side*math.sin(math.pi/6+i*math.pi/3))*radius for i in range(6)]
    return Part.makePolygon(points+[points[0]])

def halfspace(center,u,b):
    side = u.cross(b)
    points = [center+(b*sx+side*sy)*1000 for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(u*2000)

def capsule(a,b,r):
    return Part.makeCylinder(r,(b-a).Length,a,unit(b-a)).multiFuse([Part.makeSphere(r,a),Part.makeSphere(r,b)]).removeSplitter()

def cavity_parts(key):
    p=key.Parameters
    tip,u,b,m=frame(key);floor=value(p,'FloorDepth')
    af = value(key,'NominalAF')+value(p,'AFClearance'); lead = value(p,'LeadDepth')
    bore = Part.Face(hexwire(tip,u,b,af)).extrude(u*(value(key,'ToolLength')+value(key,'GuideLength')+lead))
    entrance = Part.makeLoft([hexwire(m-u*lead,u,b,af),hexwire(m,u,b,af+2*value(p,'LeadOpening'))],True,True)
    elbow = tip-u*(floor/2); vent = value(p,'VentDiameter')/2
    axial = Part.makeCylinder(vent,floor/2+.06,tip+u*.03,-u)
    escape = unit(V(0,1,0)-u*u.y)
    radial = Part.makeCylinder(vent,500,elbow,escape)
    return [bore,entrance,axial,radial]

class Generator:
    def __init__(self, obj):
        obj.Proxy = self
    def dumps(self):
        return None
    def loads(self, state):
        pass
    def execute(self, obj):
        if not App.GuiUp: print('HX05 recompute:',obj.Name,flush=True)
        try:
            self.build(obj)
            obj.LastError = ''
        except Exception as exc:
            obj.LastError = str(exc)
            obj.Shape = Part.Shape()
            raise
    def build(self, obj):
        p = obj.Parameters
        kind = obj.Kind
        if kind == 'SocketCut':
            raw=obj.Base.Shape.copy().cut(obj.Tool.Shape.copy())
            if not raw.isValid():
                raw=obj.Base.Shape.copy()
                for cutter in cavity_parts(obj.Key): raw=raw.cut(cutter)
            if not raw.isValid(): raw=obj.Base.Shape.copy().cut(obj.Tool.Shape.copy(),1e-6)
            if not raw.isValid(): raw.fix(1e-7,1e-7,1e-6)
            reduced=raw.copy().removeSplitter()
            obj.Shape=reduced if reduced.isValid() else raw
            if not obj.Shape.isValid() or len(obj.Shape.Solids)!=1:
                raise ValueError('Socket cut failed; restore the last valid parameter values')
            return
        if kind == 'Stock':
            keys = obj.Keys
            front = max(q.y for key in keys for q in ring(frame(key)[3],frame(key)[1],value(key,'OuterRadius'),32))
            half = value(p,'HalfWidth'); bottom = value(p,'PlateBottom')
            s = Part.makeBox(2*half,front-5,-bottom,V(-half,5,bottom))
            r = value(p,'BaseCornerRadius')
            if r > 0:
                s = s.makeFillet(r,[e for e in s.Edges if e.BoundBox.XLength>2*half-.01])
            for key in keys:
                tip,u,b,m = frame(key)
                s = s.cut(halfspace(m-u*.05,u,b)).removeSplitter()
            obj.Shape = s
            return
        tip,u,b,m = frame(obj if kind == 'Key' else obj.Key)
        key = obj if kind == 'Key' else obj.Key
        radius = value(key,'OuterRadius'); floor = value(p,'FloorDepth')
        if kind == 'Key':
            top = tip+u*(value(key,'ToolLength')-9)
            shaft = Part.Face(hexwire(tip,u,b,value(key,'NominalAF'))).extrude(top-tip)
            grip = capsule(top-b*(value(key,'HandleLength')/2-9),top+b*(value(key,'HandleLength')/2-9),9)
            obj.Axis = u; obj.BarAxis = b; obj.Mouth = m
            obj.Shape = Part.makeCompound([shaft,grip])
        elif kind in ('Sleeve','Gusset'):
            ends = ring(tip-u*floor,u,radius)+ring(m,u,radius)
            if kind == 'Sleeve':
                obj.Shape = hull(ends+[V(q.x,5,q.z) for q in ends])
            else:
                spread = value(p,'GussetSpread'); back = value(p,'GussetBedward')
                roots = [V(q.x-back,5,q.z+sign*spread) for q in ends for sign in (-1,1)]
                s = hull(ends+roots)
                half = value(p,'HalfWidth'); bottom = value(p,'PlateBottom')
                s = s.common(Part.makeBox(2*half,1000,-bottom,V(-half,5,bottom)))
                obj.Shape = s.cut(halfspace(m-u*.10,u,b)).removeSplitter()
        elif kind == 'Entry':
            af = value(key,'NominalAF')+value(p,'AFClearance')+2*value(p,'LeadOpening')
            obj.Shape = Part.Face(hexwire(m,u,b,af)).extrude(u*500)
        elif kind == 'Cavity':
            parts=cavity_parts(key)
            raw=parts[0].multiFuse(parts[1:])
            reduced=raw.copy().removeSplitter()
            obj.Shape=reduced if reduced.isValid() else raw
            if not obj.Shape.isValid():
                # A compound of valid cutting solids is also a valid cutter;
                # SocketCut can apply its four parts sequentially.
                obj.Shape=Part.makeCompound(parts)
        else:
            raise ValueError('Unknown HX05 feature kind: '+kind)
