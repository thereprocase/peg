"""Editable slicer modifiers for the approved HX05 fan bodies. Stdlib + FreeCAD only."""
import math
import FreeCAD as App
import Part
from hx05_family import hull, ring, frame as family_frame, value, unit

def frame(key):
    if hasattr(key, "RoundSocket"):
        return family_frame(key)
    from hx05_parametric import frame as inch_frame
    return inch_frame(key)
V = App.Vector


def fuse(parts):
    parts = [p for p in parts if not p.isNull() and p.Volume > 1e-6]
    if not parts:
        raise ValueError('No modifier material')
    raw = parts[0].multiFuse(parts[1:]) if len(parts) > 1 else parts[0]
    if not raw.isValid():
        raise ValueError('Modifier union is invalid')
    refined = raw.copy().removeSplitter()
    return refined if refined.isValid() else raw


class DensityZone:
    def __init__(self, obj):
        obj.Proxy = self

    def dumps(self):
        return None

    def loads(self, state):
        pass

    def execute(self, obj):
        print('HX05 density:', obj.Name, flush=True)
        try:
            self.build(obj)
            obj.LastError = ''
        except Exception as exc:
            print('HX05 density failure:',obj.Name,repr(exc),flush=True)
            obj.LastError = str(exc)
            obj.Shape = Part.Shape()
            raise

    def build(self, obj):
        p = obj.DensityParameters
        role = obj.DensityRole
        body = obj.Holder.Shape
        box = body.optimalBoundingBox()
        if role == 'DraftedHolder':
            angle = value(p, 'MaximumExteriorOverhang')
            if not 0 < angle <= 30:
                raise ValueError('Exterior draft must be greater than zero and at most 30 degrees from print Z')
            slope = math.tan(math.radians(angle))
            mount = obj.Mount.Shape
            mb = mount.optimalBoundingBox()
            base_x = min(mb.XMin, min(q.x for key in obj.Keys for q in
                ring(frame(key)[0]-frame(key)[1]*value(key.Parameters,'FloorDepth'),frame(key)[1],value(key,'OuterRadius'),20)
                +ring(frame(key)[3],frame(key)[1],value(key,'OuterRadius'),20)))
            front = 5.0
            housings = []
            worst = 0.0
            for key in obj.Keys:
                tip, axis, bar, mouth = frame(key)
                radius = value(key, 'OuterRadius')
                start = tip - axis*value(key.Parameters, 'FloorDepth')
                points = ring(start, axis, radius, 20) + ring(mouth, axis, radius, 20)
                roots = []
                for q in points:
                    rise = max(0.0, q.x-base_x)
                    needed = max(0.0, q.y-front)/slope
                    x = max(base_x, q.x-needed)
                    y = max(front, q.y-slope*(q.x-x))
                    roots.append(V(x,y,q.z))
                    if y <= front+1e-7:
                        roots.append(V(base_x,y,q.z))
                    if x <= base_x+1e-7 and y > front:
                        roots.append(V(base_x,4.5,q.z))
                # Direct in-layer sleeve-to-plate attachment, backed by the
                # existing full-height plate. Density masks remain separate.
                radial = unit(V(0,0,1)-axis*axis.z)
                for q in [start, mouth-axis*value(key.Parameters,'LeadDepth')]:
                    for sign in (-1,1):
                        anchor = q+radial*(sign*radius)
                        for sx in (-1,1):
                            for sz in (-1,1):
                                root_z = max(value(key.Parameters,'PlateBottom'),min(0,anchor.z+sz*value(p,'RootWidth')/2))
                                roots.append(V(max(base_x+.5,min(mb.XMax-.5,anchor.x+sx*value(p,'RibWidth')/2)),4.5,root_z))
                                roots.append(V(base_x,4.5,root_z))
                housing = hull(points+roots)
                for f in housing.Faces:
                    c = f.CenterOfMass
                    if abs(c.x-base_x)<1e-5 or c.y<=front+1e-5:
                        continue  # bed contact and buried plate interface
                    n = f.normalAt(0,0)
                    if n.x < -1e-8:
                        overhang = math.degrees(math.atan2(-n.x,math.hypot(n.y,n.z)))
                        worst = max(worst,overhang)
                        if overhang>angle+1e-4:
                            raise ValueError('Exterior facet exceeds requested overhang: %.6f degrees; key %s; centre %s; normal %s; inside-positive %s'%(overhang,key.Label,c,n,housing.isInside(c+n*.01,1e-7,False)))
                housings.append(housing)
            rail = []
            if mb.XMin-base_x>1e-6:
                gap = mb.XMin-base_x
                foot_y = min(front-1.6,slope*gap)
                rail_points = [V(x,y,z) for x,ys in [(base_x,[foot_y,front]),(mb.XMin+.02,[0,front])]
                    for y in ys for z in [value(obj.Keys[0].Parameters,'PlateBottom'),0]]
                rail.append(hull(rail_points))
            raw = fuse([mount.copy()]+rail+housings)
            for cutter in obj.Cutters:
                raw = raw.cut(cutter.Shape.copy())
            refined = raw.copy().removeSplitter()
            obj.Shape = refined if refined.isValid() else raw
            if not obj.Shape.isValid() or len(obj.Shape.Solids)!=1:
                raise ValueError('Drafted holder must remain one connected solid')
            obj.MaximumCheckedOuterOverhang = worst
            return
        if role == 'StructuralHolder':
            parts = obj.EnvelopeParts if hasattr(obj, 'EnvelopeParts') else [p for p in obj.Core.Helpers if p.DensityRole != 'Mounts']
            outer = fuse([p.Shape for p in parts]).common(body)
            if not hasattr(obj, 'OuterShape'):
                obj.addProperty('Part::PropertyPartShape', 'OuterShape', 'Cached construction')
                obj.setEditorMode('OuterShape', 1)
            obj.OuterShape = outer
            obj.Shape = outer.fuse(obj.Mount.Shape)
            if not obj.Shape.isValid() or len(obj.Shape.Solids) != 1:
                raise ValueError('Structural holder must remain one connected solid')
            return
        if role == 'PrintCore':
            masks = next(p for p in obj.Core.Helpers if p.DensityRole == 'Mounts')
            roots = masks.Shape.common(obj.Holder.Mount.Shape)
            outer = obj.Holder.OuterShape if hasattr(obj.Holder, 'OuterShape') else fuse([p.Shape for p in obj.Holder.EnvelopeParts]).common(obj.Holder.Holder.Shape)
            obj.Shape = outer.fuse(roots)
            if not obj.Shape.isValid():
                raise ValueError('Clipped printable core invalid')
            return
        if role == 'SupportBlocker':
            parts = []
            for key in obj.Keys:
                tip, axis, bar, mouth = frame(key)
                kp = key.Parameters
                lead = value(kp, 'LeadDepth')
                # A small overlap with the socket skin suppresses roof supports;
                # these are slicer exclusions, never physical holder material.
                af = value(key, 'NominalAF') + value(kp, 'AFClearance') + .3
                if hasattr(key, 'RoundSocket') and key.RoundSocket:
                    af = value(key, 'NominalDiameter') + value(kp, 'AFClearance') + .3
                    def wire(q, size):
                        return Part.Wire([Part.makeCircle(size/2, q, axis)])
                else:
                    from hx05_parametric import hexwire
                    def wire(q, size):
                        return hexwire(q, axis, bar, size)
                wide = af + 2*value(kp, 'LeadOpening')
                parts.append(Part.makeLoft([wire(tip-axis*.2, af),
                    wire(mouth-axis*lead, af), wire(mouth, wide),
                    wire(mouth+axis*5, wide)], True, True))
            obj.Shape = Part.makeCompound(parts)
            if not obj.Shape.isValid():
                raise ValueError('Socket support blockers invalid')
            return
        if role == 'SolidCore':
            # True intersections mean the modifier cannot fill a socket or vent.
            raw = fuse([q.Shape for q in obj.Helpers]).common(body)
            refined = raw.copy().removeSplitter()
            obj.Shape = refined if refined.isValid() else raw
            if not obj.Shape.isValid():
                raise ValueError('Clipped modifier solid is invalid')
            obj.ZoneVolume = obj.Shape.Volume
            obj.BodyVolumeFraction = 100 * obj.Shape.Volume / body.Volume
            return
        if role == 'Foundation':
            depth = value(p, 'FoundationDepth')
            obj.Shape = Part.makeBox(depth, box.YLength+2, box.ZLength+2,
                                     V(box.XMin, box.YMin-1, box.ZMin-1))
            return
        if role == 'Mounts':
            # Native peg geometry beyond the board-side plate, plus local root discs.
            # This is an infill mask, so a simple envelope can cover every rear
            # peg without inheriting bearing-face tessellation seams. Orca
            # intersects this volume with the physical holder automatically.
            mb = obj.Mount.Shape.optimalBoundingBox()
            parts = [Part.makeBox(mb.XLength, -mb.YMin+.02, mb.ZLength,
                                 V(mb.XMin, mb.YMin, mb.ZMin))]
            radius = value(p, 'PegRootRadius')
            depth = value(p, 'RootDepth')
            for x in obj.PegColumns:
                for z in obj.PegRows:
                    parts.append(Part.makeCylinder(radius, depth, V(x, -.1, z), V(0,1,0)))
            # Top and bottom collector belts: dense only where the mount transfers loads.
            belt = value(p, 'CollectorHeight')
            for z in [max(obj.PegRows), min(obj.PegRows)]:
                parts.append(Part.makeBox(box.XLength, depth, belt,
                                         V(box.XMin, -.1, z-belt/2)))
            obj.Shape = fuse(parts)
            return
        parts = []
        for key in obj.Keys:
            tip, axis, bar, mouth = frame(key)
            radius = value(key, 'OuterRadius')
            floor = value(key.Parameters, 'FloorDepth')
            if role == 'Sockets':
                start = tip-axis*floor
                parts.append(Part.makeCylinder(radius+.02, (mouth-start).Length+.03,
                                                start, axis))
            elif role == 'Ribs':
                radial = unit(V(0,0,1)-axis*axis.z)
                width = value(p, 'RibWidth')
                root_width = value(p, 'RootWidth')
                reach = value(p, 'RootFanout')
                for sign in (-1,1):
                    points = []
                    for q in [tip-axis*floor, mouth-axis*value(key.Parameters,'LeadDepth')]:
                        shell = q + radial*(sign*(radius-width/3))
                        root = V(shell.x, 5.0, shell.z+sign*reach)
                        for sx in (-1,1):
                            for sz in (-1,1):
                                points.append(shell+V(sx*width/2,0,sz*width/2))
                                points.append(root+V(sx*width/2,0,sz*root_width/2))
                    parts.append(hull(points))
            else:
                raise ValueError('Unknown density role')
        obj.Shape = fuse(parts)
