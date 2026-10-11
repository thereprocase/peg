"""Build the portable document from the approved layout and native body."""
from pathlib import Path
import sys,json,math
import FreeCAD as A,Part
import hx05_parametric as H
V=A.Vector
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
layout=json.loads(Path(sys.argv[2]).read_text());rack=next(r for r in layout['racks'] if r['id']=='HX05C')
reference=Part.Shape();reference.read(sys.argv[3])
doc=A.newDocument('HX05C_Parametric')
readme=doc.addObject('App::TextDocument','START_HERE');readme.Label='START HERE — editing guide'
readme.Text='''HX05C / Bondhus 13190 inch fan — parametric native document

Open SETUP_HX05.FCMacro once from the extracted bundle to install the small
feature module. Later, open this FCStd normally. No NumPy/SciPy is required.

EDIT YELLOW CELLS in 01_GlobalParameters and 02_KeyLayout. Dimensions use mm;
angles use deg. Press F5 (Recompute) after changes. Rebuilds can take several minutes.
Guide lengths are straight engagement; the lead-in is additional.
UpAngle is measured upward from horizontal from seated tip toward handle.
OutOfPlane measures shaft splay away from the pegboard; HandleRoll=0 makes
the T-bar parallel to the board. Tip X/Y/Z locate the seated shaft tip.

The original rear mount and plate are preserved as an explicit fixed native
feature. Width/height and peg geometry are intentionally not spreadsheet inputs.
The fan body, socket cuts, funnels, vents, tools and gussets recompute.
Select FinalHolder for export. Select the ReferenceTools group and press Space
to show the catalogue tool envelopes. Press 0 for axonometric, V,F to fit.

Named sleeve/gusset/cavity generators feed native Union/entrance Cut features
and robust socket Cut features with a geometric fallback for difficult seams.
Do not edit generated Shapes. Edit the sheets or replace individual features.
Invalid angles/guide/radius inputs give an error instead of silently clamping.

The supplied defaults are checked against the approved native solid. Changes
invalidate the previous clearance/print evidence. Recheck access, collisions,
installation, support placement and print envelope after edits. This is not a
sliced job. Previous slice needed a blocker in the 9/64 socket.
'''
global_sheet=doc.addObject('Spreadsheet::Sheet','GlobalParameters');global_sheet.Label='01_GlobalParameters — edit yellow cells'
layout_sheet=doc.addObject('Spreadsheet::Sheet','KeyLayout');layout_sheet.Label='02_KeyLayout — edit yellow cells'
params=doc.addObject('App::FeaturePython','Parameters');params.Label='Resolved global parameters (from spreadsheet)'
rows=[('AFClearance',.38,'mm','Total hex clearance across flats'),('LeadDepth',3.,'mm','Axial lead-in depth'),('LeadOpening',1.5,'mm','Opening added per flat'),('FloorDepth',3.,'mm','Material below seated tip'),('VentDiameter',1.,'mm','Air outlet diameter'),('BaseCornerRadius',8.,'mm','Tip-face corner rounds'),('GussetSpread',12.,'mm','Extra root width on EACH side'),('GussetBedward',16.,'mm','Root extension toward print bed'),('MinimumUpAngle',10.,'deg','Minimum upward key angle')]
for col,text in [('A','Parameter'),('B','Value'),('C','Meaning')]:global_sheet.set(col+'1',text)
for i,(name,val,unit,description) in enumerate(rows,2):
 global_sheet.set('A'+str(i),name);global_sheet.set('B'+str(i),f'={val:.12g} {unit}');global_sheet.setAlias('B'+str(i),name);global_sheet.set('C'+str(i),description)
 global_sheet.setBackground('B'+str(i),(1.,.95,.70))
 params.addProperty('App::PropertyAngle' if unit=='deg' else 'App::PropertyLength',name,'From spreadsheet',description)
 params.setExpression(name,'GlobalParameters.'+name)
 params.setEditorMode(name,1)
params.addProperty('App::PropertyLength','HalfWidth','Fixed mount');params.HalfWidth=108.;params.setEditorMode('HalfWidth',1)
params.addProperty('App::PropertyDistance','PlateBottom','Fixed mount');params.PlateBottom=min(t['tip'][2]-t['outer_radius']-6 for t in rack['tools']);params.setEditorMode('PlateBottom',1)
mount=doc.addObject('Part::Feature','ApprovedMount');mount.Label='03_FIXED — approved peg interface and backplate'
mount.Shape=reference.common(Part.makeBox(2000,1005.55,2000,V(-1000,-1000,-1000))).removeSplitter()
assert mount.Shape.isValid() and len(mount.Shape.Solids)==1
mount.addProperty('App::PropertyString','Scope','Provenance');mount.Scope='Exact native backplate/pegs extracted from 9a9e695; protected from fan parameter edits';mount.setEditorMode('Scope',1)
groups={}
for name,label in [('ReferenceTools','Reference tools — Space to show/hide'),('AdditiveFeatures','Additive sleeve and gusset features'),('CuttingTools','Socket / lead-in / vent cutting tools'),('BooleanHistory','Native Boolean feature history')]:
 groups[name]=doc.addObject('App::DocumentObjectGroup',name);groups[name].Label=label

def feature(name,label,kind,key=None):
 o=doc.addObject('Part::FeaturePython',name);o.Label=label
 o.addProperty('App::PropertyString','Kind','Internal');o.Kind=kind;o.setEditorMode('Kind',2)
 o.addProperty('App::PropertyLink','Parameters','Inputs');o.Parameters=params
 o.addProperty('App::PropertyString','LastError','Status');o.setEditorMode('LastError',1)
 if key:
  o.addProperty('App::PropertyLink','Key','Inputs');o.Key=key
 H.Generator(o)
 return o
headers=['Key','Guide mm','Up deg','Out deg','Roll deg','Tip X mm','Tip Y mm','Tip Z mm','Outer R mm','Nominal AF mm','Tool length mm','T-bar length mm']
for i,h in enumerate(headers):layout_sheet.set(chr(65+i)+'1',h)
keys=[];adds=[mount];entries=[];cavities=[]
for i,t in enumerate(sorted(rack['tools'],key=lambda t:t['af']),2):
 tag=t['name'].replace('/','_');key=feature('Key_'+tag,t['name']+' — angles, length and reference tool','Key');keys.append(key);groups['ReferenceTools'].addObject(key)
 u=V(*t['axis']);b=V(*t['bar_axis']);flat=H.unit(V(u.z,0,-u.x));roll=math.degrees(math.atan2(b.dot(u.cross(flat)),b.dot(flat)))
 settings=[('GuideLength',t['guide'],'mm'),('UpAngle',math.degrees(math.asin(u.z)),'deg'),('OutOfPlane',math.degrees(math.asin(u.y)),'deg'),('HandleRoll',roll,'deg'),('TipX',t['tip'][0],'mm'),('TipY',t['tip'][1],'mm'),('TipZ',t['tip'][2],'mm'),('OuterRadius',t['outer_radius'],'mm'),('NominalAF',t['af'],'mm'),('ToolLength',t['overall'],'mm'),('HandleLength',t['bar'],'mm')]
 layout_sheet.set('A'+str(i),t['name'])
 for j,(name,val,unit) in enumerate(settings,1):
  cell=chr(65+j)+str(i);alias='K'+tag+'_'+name
  layout_sheet.set(cell,f'={val:.15g} {unit}');layout_sheet.setAlias(cell,alias);layout_sheet.setBackground(cell,(1.,.95,.70))
  key.addProperty('App::PropertyAngle' if unit=='deg' else 'App::PropertyDistance',name,'From KeyLayout')
  key.setExpression(name,'KeyLayout.'+alias);key.setEditorMode(name,1)
 for name in ('Axis','BarAxis','Mouth'):key.addProperty('App::PropertyVector',name,'Derived');key.setEditorMode(name,1)
 for kind in ('Sleeve','Gusset','Entry','Cavity'):
  f=feature(kind+'_'+tag,t['name']+' — '+kind.lower(),kind,key)
  groups['AdditiveFeatures' if kind in ('Sleeve','Gusset') else 'CuttingTools'].addObject(f)
  (adds if kind in ('Sleeve','Gusset') else entries if kind=='Entry' else cavities).append(f)
stock=feature('RoundedStock','Rounded filled tip base','Stock');stock.addProperty('App::PropertyLinkList','Keys','Inputs');stock.Keys=keys;groups['AdditiveFeatures'].addObject(stock)
# Preserve the original Boolean order for stable exact comparison.
order={t['name']:i for i,t in enumerate(rack['tools'])}
adds=[mount,stock]+sorted(adds[1:],key=lambda f:(order[f.Key.Label.split(' — ')[0]],0 if f.Kind=='Sleeve' else 1))
entries.sort(key=lambda f:order[f.Key.Label.split(' — ')[0]]);cavities.sort(key=lambda f:order[f.Key.Label.split(' — ')[0]])
fused=doc.addObject('Part::MultiFuse','BodyUnion');fused.Label='Union — mount, base, sleeves and gussets';fused.Shapes=adds;fused.Refine=True;groups['BooleanHistory'].addObject(fused)
previous=fused
for i,cutter in enumerate(entries+cavities):
 final=i==len(entries+cavities)-1
 name='FinalHolder' if final else 'Cut_'+str(i+1).zfill(2)
 label='FINAL HOLDER — export this' if final else 'Cut — '+cutter.Label
 if i<len(entries):
  cut=doc.addObject('Part::Cut',name);cut.Label=label;cut.Refine=True
 else:
  cut=feature(name,label,'SocketCut',cutter.Key)
  cut.addProperty('App::PropertyLink','Base','Inputs');cut.addProperty('App::PropertyLink','Tool','Inputs')
 cut.Base=previous;cut.Tool=cutter
 if not final:groups['BooleanHistory'].addObject(cut)
 previous=cut
for sheet in (global_sheet,layout_sheet):sheet.setStyle('A1:L1','bold');sheet.setColumnWidth('A',170)
global_sheet.setColumnWidth('B',120);global_sheet.setColumnWidth('C',300)
for col in 'BCDEFGHIJKL':layout_sheet.setColumnWidth(col,115)
print('Recomputing native document',flush=True)
doc.recompute()
# Keep a native cut unrefined if OCC cannot simplify its coincident edges.
for o in doc.Objects:
 if o.TypeId=='Part::Cut' and 'Invalid' in o.State:
  print('Retry native cut without refinement',o.Name,o.getStatusString(),flush=True)
  o.Refine=False
  doc.recompute()
errors=[(o.Name,str(o.State)) for o in doc.Objects if 'Invalid' in o.State or (hasattr(o,'LastError') and o.LastError)]
if errors:
 for o in doc.Objects:
  if 'Invalid' in o.State: print(o.Name,o.getStatusString(),getattr(o,'LastError',''),flush=True)
if errors: doc.saveAs(str(out/'FAILED_DIAGNOSTIC.FCStd'))
assert not errors,errors
assert previous.Shape.isValid() and len(previous.Shape.Solids)==1,'Final native solid invalid'
for o in doc.Objects:
 if hasattr(o,'Shape'):o.Visibility=False
previous.Visibility=True
doc.recompute()
path=out/'HX05C_13190_parametric_v1.FCStd';doc.saveAs(str(path));previous.Shape.exportBrep(str(out/'rebuilt.brep'))
print('SAVED',path,'volume',previous.Shape.Volume,'objects',len(doc.Objects),flush=True)
# Verify the editable construction reproduces the approved solid.
diff=previous.Shape.cut(reference).Volume+reference.cut(previous.Shape).Volume
result=dict(valid=previous.Shape.isValid(),solids=len(previous.Shape.Solids),volume_mm3=previous.Shape.Volume,reference_volume_mm3=reference.Volume,symmetric_difference_mm3=diff,objects=len(doc.Objects),native_booleans=11,robust_socket_cuts=10,parameter_sheets=2,feature_module='hx05_parametric.py',reference_commit='9a9e69581e6b9389d27edd8eb4484b41f02f2abd',scope='Default shape equivalence; edited layouts require new clearance and printing checks.')
(out/'build-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert diff<.1,('Default geometry differs from approved body',diff)
print(json.dumps(result,indent=2),flush=True)
