"""Pack the new holder review; frozen model inputs remain read-only."""
import argparse,json,sys,shutil,hashlib
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tool_models'))
from engineering_viewer_v2 import smooth_crease
LIFT_MM=150
OUT_MM=0
ROUTE=dict(waypoints_mm=[[0,0,0],[0,0,LIFT_MM]],mode="vertical",lift_mm=LIFT_MM)

def main():
 p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('output',type=Path);p.add_argument('--empty-only',action='store_true');a=p.parse_args();d=a.build;o=a.output;o.mkdir(parents=True,exist_ok=True)
 c=json.loads((d/'candidate.json').read_text());poses=[] if a.empty_only else json.loads((d/'poses.json').read_text());desc=[];inputs={}
 global LIFT_MM,ROUTE
 LIFT_MM=max((r['lift_mm'] for r in poses),default=150)
 ROUTE=dict(waypoints_mm=[[0,0,0],[0,0,LIFT_MM]],mode='vertical',lift_mm=LIFT_MM)
 def pack(path,name,color,role,case,offset=0):
  m=trimesh.load_mesh(path,process=True);v,n,f=smooth_crease(m)
  file=name+'.bin';(o/file).write_bytes(np.c_[v,n].astype('<f4').tobytes()+np.array(f,dtype='<u4').tobytes())
  desc.append(dict(file=file,vertices=len(v),indices=f.size,color=color,role=role,case=case));inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
 pack(d/(c['name']+'__installed.stl'),'holder',[.83,.62,.25],'holder','all')
 for pose in poses:
  ident=pose['tool'];model=Path('bench/reviews')/(ident+'-engineering-model-v2');meta=json.loads((model/'cad.json').read_text());basis=np.array(pose['basis']);off=np.array(pose['translation']);turn=Rotation.from_euler('z',meta['parameters']['opening_sign']*pose['opening_deg'],degrees=True).as_matrix()
  for part in meta['parts']:
   source=model/(part['name']+'.stl')
   if part['role']=='coil' and pose['opening_deg']:source=model/f"coil-open-{pose['opening_deg']}.stl"
   m=trimesh.load_mesh(source,process=True);rot=basis@(turn if part['role']=='moving' else np.eye(3));m.vertices=np.asarray(m.vertices)@rot.T+off
   v,n,f=smooth_crease(m);file=pose['id']+'-'+part['name']+'.bin'
   (o/file).write_bytes(np.c_[v,n].astype('<f4').tobytes()+np.array(f,dtype='<u4').tobytes())
   desc.append(dict(file=file,vertices=len(v),indices=f.size,color=part['color'],role='tool',case=pose['id']));inputs[str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()
 for src,dst in [(d/'editable.FCStd','holder.FCStd'),(d/c['print_file'],'holder-print.stl')]:shutil.copy2(src,o/dst)
 (o/'models.json').write_text(json.dumps(dict(meshes=desc,poses=poses,spacing_mm=50.8,lift_mm=LIFT_MM,out_mm=OUT_MM,route=ROUTE,downloads=dict(native='holder.FCStd',print='holder-print.stl')),indent=2)+'\n')
 shutil.copy2(Path(__file__).with_suffix('.html'),o/'index.html')
 (o/'packing.json').write_text(json.dumps(dict(inputs=inputs,scope='Complete frozen CAD tessellations transformed into seating poses; normals only smoothed. Coil at recorded0/+10 poses included. One holder geometry reused for both instances.'),indent=2)+'\n')
if __name__=='__main__':main()
