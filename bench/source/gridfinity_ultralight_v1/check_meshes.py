"""Independent closed-mesh checks and geometry-only 3MF packaging; NumPy only."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import numpy as np

root=Path(sys.argv[1])
reports=[]
dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
for path in sorted(root.glob('GF*.stl')):
    raw=path.read_bytes()
    count=int.from_bytes(raw[80:84],'little')
    assert len(raw)==84+50*count
    triangles=np.frombuffer(raw,dtype=dtype,offset=84,count=count)['vertices'].astype(float)
    vertices,inverse=np.unique(triangles.reshape(-1,3),axis=0,return_inverse=True)
    faces=inverse.reshape(-1,3)
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    unique_edges,edge_inverse,counts=np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
    assert np.all(counts==2),path.name
    directions=np.where(edges[:,0]<edges[:,1],1,-1)
    assert np.all(np.bincount(edge_inverse,weights=directions)==0)
    areas=np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)/2
    assert np.all(areas>1e-10)
    volume=np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6
    assert volume>0
    if not path.stem.endswith('-print-inverted'):
        reports.append({'file':path.name,'triangles':count,'closed_edges':True,'consistent_winding':True,'positive_volume_mm3':volume,'sha256':hashlib.sha256(raw).hexdigest()})
        continue
    assert vertices[:,2].min()>=-1e-6
    vs=''.join(f'<vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>' for x,y,z in vertices)
    fs=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in faces)
    model=f'<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model" name="{path.stem}"><mesh><vertices>{vs}</vertices><triangles>{fs}</triangles></mesh></object></resources><build><item objectid="1"/></build></model>'
    target=path.with_suffix('.3mf')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',model)
    reports.append({'file':path.name,'triangles':count,'closed_edges':True,'consistent_winding':True,'positive_volume_mm3':volume,'bed_z_min':vertices[:,2].min(),'sha256':hashlib.sha256(raw).hexdigest(),'geometry_only_3mf':target.name})
(root/'MESH-CHECKS.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
