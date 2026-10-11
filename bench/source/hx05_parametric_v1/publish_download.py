"""Preserve the parametric-download section when the green gallery rebuilds."""
from pathlib import Path
import json,hashlib

def install(root):
    root=Path(root)
    directory=root/'docs/gallery/key-fan/stacked/green'
    metadata=directory/'parametric.json'
    if not metadata.exists(): return
    data=json.loads(metadata.read_text())
    start='<!-- HX05 PARAMETRIC START -->'
    end='<!-- HX05 PARAMETRIC END -->'
    page=directory/'index.html';text=page.read_text()
    if start in text:
        a,rest=text.split(start,1);_,b=rest.split(end,1);text=a+b
    section=f'''{start}<section id="parametric"><h2>Edit this rack in FreeCAD</h2><p><a href="{data['bundle_url']}"><strong>Download the native parametric FreeCAD bundle</strong></a></p><p>Extract the ZIP and run <code>SETUP_HX05.FCMacro</code> once in FreeCAD. It installs the included generator module and opens the FCStd. Save a personal copy, then edit yellow cells in <strong>01_GlobalParameters</strong> or <strong>02_KeyLayout</strong> and press F5 to recompute.</p><p>Control fit, lead-ins, vents, base rounds and gussets globally; adjust each key’s sleeve length, upward angle, out-of-plane splay, handle rotation and tip position. The approved rear mount stays fixed. The document contains native solids, linked features and spreadsheets; the included module is needed for custom-feature recomputation.</p><p>The default geometry matches the approved rack. Parameter edits and save/reopen were checked in FreeCAD 1.1.3. Edited layouts need renewed clearance and printing checks. This is editable CAD, not a sliced print job.</p><p><a href="{data['fcstd_url']}">FCStd only (install the bundled module first)</a> · <a href="parametric.json">Validation and file hashes</a></p></section>{end}'''
    text=text.replace('<img src="HX05C-hero.jpg"',section+'<img src="HX05C-hero.jpg"',1)
    page.write_text(text,encoding='utf-8')
    receipt=root/'publication/green-fan-v1-review.json'
    rows=json.loads(receipt.read_text())
    for p in (page,metadata):
        rows[str(p.relative_to(root))]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    receipt.write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__': install(Path(__file__).resolve().parents[3])
