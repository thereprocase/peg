"""Reopen native documents, edit a sleeve/handle and Torx diameter, save again."""
from pathlib import Path
import sys,json
import FreeCAD as A,Part
import hx05_family as H
folder=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
model=next(folder.glob('HX05[AB]_*_matched_v1.FCStd'))
d=A.openDocument(str(model));keys=[o for o in d.Objects if getattr(o,'Kind','')=='Key']
assert len(keys)==8
assert all(isinstance(o.Proxy,H.Generator) for o in d.Objects if hasattr(o,'Kind'))
assert d.FinalHolder.Shape.isValid() and len(d.FinalHolder.Shape.Solids)==1
key=max(keys,key=lambda k:k.NominalDiameter.Value if k.RoundSocket else k.NominalAF.Value)
original=d.FinalHolder.Shape.copy();oldmouth=key.Mouth;oldbar=key.BarAxis
oldguide=key.GuideLength.Value;oldroll=key.HandleRoll.Value;oldcavity=d.getObject('Cavity_'+key.Name[4:]).Shape.Volume
oldmount=d.ApprovedMount.Shape.exportBrepToString()
d.KeyLayout.set('B9',f'={oldguide+1} mm');d.KeyLayout.set('E9',f'={oldroll+2} deg')
if key.RoundSocket:d.KeyLayout.set('M9',f'={key.NominalDiameter.Value+.1} mm')
print('Recompute edited',model.name,flush=True);d.recompute()
errors=[(o.Name,getattr(o,'LastError','')) for o in d.Objects if 'Invalid' in o.State or getattr(o,'LastError','')]
assert not errors,errors
assert d.FinalHolder.Shape.isValid() and len(d.FinalHolder.Shape.Solids)==1
assert abs(key.GuideLength.Value-oldguide-1)<1e-8 and abs((key.Mouth-oldmouth).Length-1)<1e-7
assert (key.BarAxis-oldbar).Length>.01
assert d.ApprovedMount.Shape.exportBrepToString()==oldmount
if key.RoundSocket:assert d.getObject('Cavity_'+key.Name[4:]).Shape.Volume>oldcavity
saved=out/model.name;d.saveAs(str(saved))
r=dict(filename=model.name,valid_single_solid=True,restored_features=len([o for o in d.Objects if hasattr(o,'Kind')]),guide_increment_mm=1,handle_roll_increment_degrees=2,round_diameter_increment_mm=.1 if key.RoundSocket else None,fixed_mount_unchanged=True,edited_volume_mm3=d.FinalHolder.Shape.Volume,freecad='.'.join(A.Version()[:3]))
(out/'edit-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
