"""Publish only review images and numerical receipts; no new print downloads."""
from pathlib import Path
import sys,json,shutil,hashlib,html
ROOT=Path(__file__).resolve().parents[3]
B=Path(sys.argv[1]);D=ROOT/'docs/gallery/key-fan/stacked';R=ROOT/'bench/reviews/stacked-fans-v1'
D.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
layout=json.loads((B/'layout.json').read_text());access=json.loads((B/'access.json').read_text());native=json.loads((B/'tight-native/native.json').read_text());sweeps=json.loads((B/'tight-native/sweep-check.json').read_text())
assert access['passed']
for name in ('layout.json','access.json','spacing.json','density.json'):shutil.copyfile(B/name,R/name)
for name in ('native.json','sweep-check.json'):shutil.copyfile(B/'tight-native'/name,R/name)
images=[]
shutil.copyfile(B/'renders/sections.png',D/'sections.png')
for p in sorted((B/'renders').glob('*.jpg')):
 if p.stem.split('-')[0] in ('HX05A','HX05B','HX05C','stack','empty'):
  shutil.copyfile(p,D/p.name);images.append(p.name)
rows=[];cards=[]
previous={'HX05C':(248.,250.61559795555635),'HX05B':(234.,212.71615127348775),'HX05A':(250.,181.13024740551631)}
comparisons=[]
for r in native['racks']:
 ident=r['id'];lo,hi,y0,y1,z0,z1=r['bounds'];size=[hi-lo,y1-y0,z1-z0]
 oldw,oldh=previous[ident]
 comparisons.append(dict(id=ident,previous_width_mm=oldw,previous_height_mm=oldh,width_mm=size[0],height_mm=size[2],holder_front_envelope_reduction_percent=100*(1-size[0]*size[2]/(oldw*oldh))))
 name={'HX05A':'33034 Torx · 8 tools','HX05B':'13189 metric · 8 tools','HX05C':'13190 inch · 10 tools'}[ident]
 rows.append(f'<tr><th>{name}</th><td>{oldw:.0f} → {size[0]:.0f}</td><td>{size[1]:.1f}</td><td>{size[2]:.1f}</td></tr>')
 cards.append(f'<section id="{ident}"><h2>{name}</h2><img src="{ident}-hero.jpg" alt="Native {name} fan with reference tools" width="1200" height="850"><details><summary>Front and plan views</summary><img loading="lazy" src="{ident}-front.jpg" alt="{name} front view" width="1200" height="700"><img loading="lazy" src="{ident}-plan.jpg" alt="{name} plan view" width="1200" height="600"></details></section>')
minimum=min(min(x['stored_bound'],x['withdrawal_bound'],x['hand_bound']) for x in access['records'])
status='The conservative native axial socket-release and grasp checks pass.' if sweeps['passed'] else 'The native sweep review has unresolved contacts; these models are not ready to print.'
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stacked Bondhus fans · Repro</title><style>body{margin:0;background:#f5f3ec;color:#222;font:18px/1.55 system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:24px}a{color:#126657}h1,h2{line-height:1.15}img{display:block;width:100%;height:auto;border-radius:14px;background:#ece9df;margin:18px 0}section{margin:38px 0}table{width:100%;border-collapse:collapse;font-size:16px}th,td{text-align:left;padding:10px;border-bottom:1px solid #ccc}summary{cursor:pointer;color:#126657}.note{border-left:5px solid #247b6d;padding:16px;background:#e0eee7}.stack{max-width:540px;margin:auto}.small{font-size:15px}</style></head><body><main><nav><a href="../final/">Previous final models</a> · <a href="../">Fit tests</a></nav><h1>Stacked Bondhus fans</h1><p class="note"><strong>Denser fan revision.</strong> Small keys tuck individually into the spaces above and behind the larger tools. The longer shafts retain their independent angles and staggered ends. Contact-limited placement keeps the separate tip, funnel and hand-clearance rules below.</p><p><a href="#HX05B">Metric</a> · <a href="#HX05C">Inch</a> · <a href="#HX05A">Torx</a> · <a href="#stack">Vertical stack</a></p>'''
page+='<p>Holder width is down 26% for inch, 21% for metric and 46% for Torx. The metric holder is 16.5 mm taller; the inch holder is 11.5 mm shorter. All three have smaller front bounding areas. This is a checked compact arrangement, not a claim of a global packing optimum.</p>'
page+=''.join(cards)
pitches=[hi['z']-lo['z'] for lo,hi in zip(layout['racks'],layout['racks'][1:])]
stack_text=f"Inch to metric: {pitches[0]:.1f} mm ({pitches[0]/25.4:.0f} rows). Metric to Torx: {pitches[1]:.1f} mm ({pitches[1]/25.4:.0f} rows)."
page+=f'''<section><h2>Three distinct clearance rules</h2><ul><li><strong>Near the buried ends:</strong> approximately 1 mm between the steel shaft envelopes. Socket clearance consumes part of this distance; the shared plastic web widens as the shafts diverge.</li><li><strong>At each entrance:</strong> the full chamfer adds 3 mm along the shaft and opens 1.5 mm per flat. Mouth envelopes have a separate 2 mm spacing target.</li><li><strong>At the handles:</strong> the axial socket-release stroke and a 50 mm diameter grasp envelope are checked with the other tools left in place.</li></ul><p>The selected 3C / 5C fit remains +0.38 mm total across flats. Straight engagement remains max(40 mm, 8× shaft size), plus the lead-in, with a square stop and 1 mm vent. Other sizes and new print angles need their own fit confirmation. Torx guides use circular catalogue envelopes and have no demonstrated rotational registration.</p></section><section id="stack"><h2>Vertical stack</h2><p>Inch below metric below Torx. {stack_text} Each gap is calculated separately for the represented tools and socket-release strokes. The previous layout used 228.6 mm at both levels; the narrower arrangement needs two extra rows at the lower gap.</p><img class="stack" loading="lazy" src="stack-hero.jpg" alt="Three populated fans stacked vertically" width="800" height="1300"><details><summary>Empty holders</summary><img class="stack" loading="lazy" src="empty-stack-hero.jpg" alt="Three native holders without tools" width="800" height="1300"></details><table><caption>Native holder envelope, mm; includes rear mounting projections, excludes tools</caption><thead><tr><th>Set</th><th>Width: old → new</th><th>Depth</th><th>Height</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section><section><h2>Native cross-sections</h2><img loading="lazy" src="sections.png" alt="Native plastic and shaft sections at 45 mm from the mounting face" width="1440" height="624"></section><section><h2>Review evidence</h2><p>The stored-tool, grasp and axial-release envelope screen passes for all 26 tools. {status} Native solid validity and stored tool/body overlap are checked during construction. Tool shapes are catalogue envelopes with an assumed 18 mm grip diameter, not measured manufacturer geometry.</p><p>The subsequent free-hand removal maneuver is not modelled. Thin-web printability, supports, whole-rack installation motion, stiffness and physical load capacity remain unqualified. Previous FEA and installation evidence do not transfer. This page provides renders, not approved print files.</p><p><a href="review.json">Review results</a> · <a href="https://github.com/thereprocase/peg/tree/hx05/bench/source/stacked_fans_v1">Construction source</a></p></section></main></body></html>'''
(D/'index.html').write_text(page,encoding='utf-8')
(D/'review.json').write_text(json.dumps(dict(layout_sha256=hashlib.sha256((B/'layout.json').read_bytes()).hexdigest(),pitch_mm=layout['pitch'],pitches_mm=pitches,density_comparison=comparisons,tool_hand_access_passed=access['passed'],native_sweeps=sweeps,native=[{k:r[k] for k in ('id','valid','solids','stored_overlap_mm3','bounds','cavity_gaps')} for r in native['racks']]),indent=2)+'\n')
receipts={}
for base in (D,R,ROOT/'bench/source/stacked_fans_v1'):
 for p in sorted(base.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:receipts[str(p.relative_to(ROOT))]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(ROOT/'publication/stacked-fans-v1-review.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('Published review files',len(receipts),'site bytes',sum(p.stat().st_size for p in D.iterdir() if p.is_file()))
