"""Publish the fit-v4 trial overlay while preserving HX04 v2 as labelled history.
No G-code or full-rack geometry is changed by this page update.
"""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[1]
B=R/'bench/reviews/tee-fit-v4-guide40'
D=R/'docs/gallery/key-fan'
TAG='tee-fit-v4-2026-10-09'
REL=f'https://github.com/thereprocase/peg/releases/download/{TAG}/'
BUNDLE='tee-fit-v4__native-source-and-checks.zip'


def receipt(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)


def apply():
    dst=D/'fit-v4';dst.mkdir(parents=True,exist_ok=True)
    mesh='HX05-fit-v4__left-end__print.stl';shutil.copyfile(B/mesh,dst/mesh)
    report=json.loads((B/'fit-v4-check.json').read_text());export=json.loads((B/'export-check.json').read_text())
    assert report['guide_policy'].startswith('max(40') and export['closed_mesh'] and export['mesh_components']==4
    for q in report['pieces']:assert q['straight_guide_mm']>=40 and q['clearance_per_flat_mm']==.19
    (dst/'checks.json').write_text(json.dumps(dict(geometry=report,exports=export,physical_fit='Pending',slicing='Pending',supersedes='original HX04 v2 socket fit coupon'),indent=2)+'\n',encoding='utf-8',newline='\n')
    header='''<header><nav><a href="../../">Product groups</a><a href="../current-pegs/?family=repro">Repro collection</a></nav><h1>Key fan fit revision</h1><p>Longer straight shaft guides, increased hex clearance and vented floors and flat-to-flat T-handle alignment.</p><p class="status">Fit coupon v4 · prototype. Native geometry checks pass; slicing and physical fit are pending. The archived HX04 v2 rack below retains its older seats.</p></header>'''
    section=f'''<!-- FIT_V4_BEGIN --><section id="fit-coupon-v4"><h2>Fit coupon v4: 40 mm minimum shaft hug</h2><p>The shaft is guided by a straight six-flat bore for at least <strong>40 mm</strong>, increasing to <strong>8× shaft size</strong> for larger tools. The <strong>0.8 mm entrance chamfer is additional</strong>; the floor is square with a <strong>1 mm through vent</strong> in each block. There is no rounded or flared seating chamber.</p><p>Hex clearance is <strong>0.19 mm per flat</strong> (0.38 mm total across flats). The 5 mm key gets a <strong>5.38 mm AF bore</strong>. The T-bar runs <strong>flat-to-flat</strong>. This adds 0.18 mm total clearance to v3, which printed snug. These are CAD targets; printed dimensions remain to be checked.</p><p><strong><a href="fit-v4/{mesh}" download>Download the new coupon STL</a></strong> · <a href="{REL}HX05-fit-v4.FCStd">FreeCAD document</a> · <a href="{REL}HX05-fit-v4__left-end__print.step">STEP</a> · <a href="{REL}{BUNDLE}">Native CAD, source and checks ZIP</a></p><model-viewer id="fit-coupon-viewer" src="fit-v4/coupon.glb" camera-controls camera-orbit="65deg 65deg auto" interaction-prompt="none" alt="Four revised socket blocks with full straight hex guides: L2, T2.5, T5 and T10" style="height:380px"></model-viewer><table><thead><tr><th>Block</th><th>Bore AF</th><th>Shaft hug</th><th>Burial including entrance</th></tr></thead><tbody><tr><td>L2 F19</td><td>2.38 mm</td><td>40.0 mm</td><td>40.8 mm</td></tr><tr><td>T2.5 F19</td><td>2.88 mm</td><td>40.0 mm</td><td>40.8 mm</td></tr><tr><td>T5 F19</td><td>5.38 mm</td><td>40.0 mm</td><td>40.8 mm</td></tr><tr><td>T10 F19</td><td>10.38 mm</td><td>80.0 mm</td><td>80.8 mm</td></tr></tbody></table><p>A 6 mm shaft gets 48 mm of hug; an 8 mm shaft gets 64 mm. F19 labels mean flat-to-flat and 0.19 mm clearance per flat.</p><h3>Prepare and test</h3><p>The STL is already arranged on the left end, matching the holder's print direction. Use your actual printer and filament profile, apply its calibrated compensation and inspect the hex roofs and supports before printing. No G-code is supplied. These blocks have no mounting pegs.</p><p>The previous <a href="https://github.com/thereprocase/peg/releases/tag/tee-fit-v3-2026-10-09">v3 coupon</a> printed snug and remains available as history. Check that each tool reaches the floor, compare the small key's rocking and check the 5 mm key's rotational stop and return feel. The 5 mm CAD bore allows about ±8.7° rotation; it is a clearance fit. At this requested allowance, the 2 mm key can rotate fully in its 2.38 mm bore; the 2.5 mm key allows about ±26.1°. Native solid, floor, rotational-stop and export checks are in <a href="fit-v4/checks.json">the new coupon evidence</a>. Print quality, fit and loads remain unqualified.</p><h3>Why the original coupon changed</h3><p>The owner's HX04 v2 print allowed roughly 15° of rocking in the 2 mm L-key and a complete turn in both 5 mm tests. Its short neck, deep entrance and widened chamber did not provide enough effective guidance. This coupon tests the replacement before applying its fit to a complete rack.</p></section><!-- FIT_V4_END -->'''
    p=D/'index.html';text=p.read_text()
    text=re.sub(r'<header>.*?</header>',header,text,count=1,flags=re.S)
    text=re.sub(r'<!-- FIT_V3_BEGIN -->.*?<!-- FIT_V3_END -->','',text,flags=re.S)
    text=re.sub(r'<!-- FIT_V4_BEGIN -->.*?<!-- FIT_V4_END -->','',text,flags=re.S)
    if 'id="hx04-v2-archive"' not in text:
        text=text.replace('<article>','<details id="hx04-v2-archive"><summary>Archived HX04 v2 rack and original coupon</summary><article><p class="status">Historical geometry and computational evidence. The owner’s socket-fit trial failed; this full rack has not yet adopted the new guide geometry.</p>',1)
        text=text.replace('</footer>','</footer></details>',1)
    text=text.replace('</header>','</header>'+section,1)
    text=text.replace('<model-viewer src="loaded.glb','<model-viewer id="rack-viewer" src="loaded.glb')
    text=text.replace('<h2>How the sockets hold the tools</h2>','<h2>Original socket design (superseded)</h2>')
    text=text.replace('Jiggling tools walk in, not out. Every bore has a short straight neck, then widens slightly toward a floor sloped 30° low on the side the tool’s own weight tips toward, so a tool pinched by its weight slides deeper instead of hanging.','The original design used a short neck, a widened chamber and a sloped floor. Owner testing found inadequate centering and rotational restraint; that seating approach is superseded by the straight-guide trial above.')
    text=text.replace('<strong>Print the fit coupon first</strong>','<strong>Original v2 coupon (history)</strong>').replace('<strong>Full part:</strong>','<strong>Archived full part (older seats):</strong>')
    text=text.replace('The full part assumes corners.','This archived full part assumes corners; the owner has since confirmed flat-to-flat handles.')
    text=text.replace('review.js?v=2','review.js?v=fit3-20261009')
    text=text.replace('<title>Three-tier key fan · Repro</title>','<title>Key fan · 40 mm guide fit coupon · Repro</title>')
    p.write_text(text,encoding='utf-8',newline='\n')
    p=D/'review.js';p.write_text(p.read_text().replace("document.querySelector('model-viewer')","document.querySelector('#rack-viewer')"),encoding='utf-8',newline='\n')
    p=D/'checks.json';ev=json.loads(p.read_text());ev['physical_tests']='Original socket-fit coupon failed owner expectations; revised fit-v4 trial pending';ev['fit_revision']=dict(version=4,coupon='fit-v4/checks.json',guide_minimum_mm=40,guide_size_ratio=8,clearance_per_flat_mm=.19,handle_axis='flat-to-flat',full_rack='Archived HX04 v2 retains earlier socket geometry');p.write_text(json.dumps(ev,indent=1)+'\n',encoding='utf-8',newline='\n')
    p=R/'docs/gallery/current-pegs/catalog.json';catalog=json.loads(p.read_text());part=next(q for q in catalog['parts'] if q['id']=='HX04');part['notes']['status']='Socket fit revision · new coupon v4';part['notes']['qualification']='Owner coupon print revealed excessive small-key rocking and full rotation of the 5 mm tests. Use the revised 40 mm guide coupon on the detail page. This archived full rack retains the earlier seats; new coupon physical fit and slicing are pending.';part['extra_downloads']=[dict(label='New 40 mm guide fit coupon and archived HX04 rack',url='../key-fan/?v=3#fit-coupon-v4')];p.write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8',newline='\n')
    p=R/'publication/current-pegs-v1-additions.json';entries=json.loads(p.read_text());entries['catalog.json']=receipt(R/'docs/gallery/current-pegs/catalog.json');p.write_text(json.dumps(entries,indent=2)+'\n',encoding='utf-8',newline='\n')
    (R/'publication/key-fan-v2-additions.json').write_text(json.dumps({q.name:receipt(q) for q in sorted(D.iterdir()) if q.is_file() and q.name!='part-hx04__v1__left-cheek__fit-pf02c9-hoop5__print.stl'},indent=2)+'\n',encoding='utf-8',newline='\n')
    (R/'publication/tee-fit-v4-page-additions.json').write_text(json.dumps({q.relative_to(R).as_posix():receipt(q) for q in sorted(dst.iterdir()) if q.is_file()},indent=2)+'\n',encoding='utf-8',newline='\n')


def package(out):
    out.mkdir(parents=True,exist_ok=True)
    source=R/'bench/source/tee_racks_v1'
    paths=[source/'fit_coupon_v4.py',source/'study/socket_policy.py',source/'fonts/Fillaprint-Regular.ttf',source/'fonts/OFL.txt',source/'tools/check_fit_coupon.py',source/'tools/setup_freecad_linux.sh']
    check=json.loads((B/'fit-v4-check.json').read_text())
    names=['README.md','fit-v4-check.json','export-check.json','HX05-fit-v4.FCStd','HX05-fit-v4__left-end__print.step','HX05-fit-v4__left-end__print.stl']+[q['id']+'__installed.step' for q in check['pieces']]
    paths += [B/name for name in names]
    entries={p.relative_to(R).as_posix():p.read_bytes() for p in paths}
    manifest={n:dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)) for n,b in entries.items()}
    entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    with zipfile.ZipFile(out/BUNDLE,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(entries.items()):z.writestr(name,data)
    for name in ('HX05-fit-v4.FCStd','HX05-fit-v4__left-end__print.step','HX05-fit-v4__left-end__print.stl'):
        shutil.copyfile(B/name,out/name)
    assets=json.loads((R/'publication/release-assets.json').read_text());downloads=json.loads((R/'publication/release-downloads.json').read_text())
    for p in out.iterdir():
        assets[p.name]=receipt(p);downloads['key-fan/fit-v4/'+p.name]=REL+p.name
    (R/'publication/release-assets.json').write_text(json.dumps(assets,indent=2)+'\n',encoding='utf-8',newline='\n')
    (R/'publication/release-downloads.json').write_text(json.dumps(downloads,indent=2)+'\n',encoding='utf-8',newline='\n')
    js=R/'docs/gallery/release-downloads.js';before,tail=js.read_text().split('const links=',1);_,end=json.JSONDecoder().raw_decode(tail)
    js.write_text(before+'const links='+json.dumps(downloads,separators=(',',':'))+tail[end:],encoding='utf-8',newline='\n')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path);a=ap.parse_args();apply()
    if a.package:package(a.package)
    print('Updated key-fan fit coupon v4 overlay')
