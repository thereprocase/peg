"""Read-only coarse scan guide frame. Does not supply vertices to the CAD generator."""
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tool_traces'))
from knipex_scan_preview_v1 import read_glb

BASES={'knipex':('knipex-flush-cuts-trace-v1','knipex-flush-cuts-scan-2026-10-04'),
       'klein':('klein-strips-trace-v1','klein-strips-scan-2026-10-04')}


def source(ident):
    old,src=BASES[ident];old=Path('bench/reviews')/old;src=Path('bench/reference/solder-tools')/src
    meta=json.loads((old/'trace.json').read_text())
    raw,faces,uv,_,j=read_glb(src/'model.glb',texture=False)
    # Table fit removes the former rivet-cap slope from the manufactured tool frame.
    a,b,c=meta['table_plane'];z=np.array([-a,1,-b]);z/=np.linalg.norm(z)
    oldbasis=np.array(meta['basis_rows']);measure=np.array(meta['measurement_axis_tool'])@oldbasis
    x=measure-z*np.dot(measure,z);x/=np.linalg.norm(x);y=np.cross(z,x);basis=np.array([x,y,z])
    scale=meta['mm_per_source_unit'];origin=np.array(meta['raw_origin'])+np.array(meta['centred_frame_origin'])
    v=(raw-origin)@basis.T*scale
    v[:,2]+=3.75 if ident=='knipex' else 4.0
    labels=np.load(old/'source-face-labels.npz');lab=labels['labels']
    return v,faces,uv,lab,src/j['images'][0]['uri'],dict(
        raw_origin=origin.tolist(),basis_rows=basis.tolist(),mm_per_source_unit=scale,
        vertical_pivot_cap_offset_mm=3.75 if ident=='knipex' else 4.0,
        frame_note='Table-normal manufacturing frame, caliper direction projected in table plane, primary rivet center. Removes noisy domed-cap plane tilt; alignment is approximate.',
        source=str(src/'model.glb'),trace_metadata=str(old/'trace.json'),face_labels=str(old/'source-face-labels.npz'),
        label_legend=labels['legend'].tolist())

if __name__=='__main__':
    for ident in BASES:
        v,f,uv,l,tex,meta=source(ident);print(ident,meta['label_legend'])
        selected=np.unique(f[l>0]);q=v[selected]
        for x in [0,20,40,60,80,100,120]:
            slab=q[np.abs(q[:,0]-x)<1.5]
            if len(slab):print(x,np.round(np.quantile(slab[:,1:],[.025,.5,.975],axis=0),2).tolist())
