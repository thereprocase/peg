import FreeCAD as A,Part,Mesh,json,sys,hashlib,math
from pathlib import Path
out=Path(sys.argv[1]);shape=Part.Shape();shape.read(str(out/'installed.step'));assert shape.isValid() and len(shape.Solids)==1
meshes={}
for name in ('installed.stl','print.stl'):
 m=Mesh.Mesh(str(out/name));assert m.isSolid() and m.Volume>0
 parts=m.getSeparateComponents();signed=[]
 for part in parts:
  points,faces=part.Topology;origin=points[0]
  signed.append(math.fsum((points[a]-origin).dot((points[b]-origin).cross(points[c]-origin)) for a,b,c in faces)/6)
 assert sum(v>0 for v in signed)==1 and len(parts)==len(shape.Shells), 'mesh shells differ from the one CAD solid'
 assert abs(sum(signed)-shape.Volume)/shape.Volume<.005
 meshes[name]=dict(closed=m.isSolid(),connected_surfaces=m.countComponents(),material_solids=1,internal_cavity_shells=len(parts)-1,signed_shell_volumes_mm3=signed,volume_mm3=sum(signed),relative_volume_error=abs(m.Volume-shape.Volume)/shape.Volume,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest())
(out/'native-export-check.json').write_text(json.dumps(dict(freecad=A.Version(),occ=Part.OCC_VERSION,native_valid=shape.isValid(),native_solids=len(shape.Solids),volume_mm3=shape.Volume,step_sha256=hashlib.sha256((out/'installed.step').read_bytes()).hexdigest(),meshes=meshes,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='native reload and closed-mesh checks; exact withdrawals, installation, FEA, slicing and physical fit pending'),indent=2)+'\n')
print(out.name,'native STEP and both closed meshes pass')
