"""Pack v3 with the frozen, browser-reviewed v1 renderer and camera."""
import sys,json
from pathlib import Path
from rectangular_funnel_viewer_v1 import main as pack

def main():
 pack()
 d=Path(sys.argv[2]);p=d/'index.html';s=p.read_text().replace('Rectangular tool funnel · prototype','Rectangular tool funnel v3 · upright prototype').replace('One rectangular funnel · two bench tools','Upright rectangular funnel · two bench tools').replace('Supports required; no slice qualification.','Flat bottom on bed; peg supports still need review. No slice qualification.')
 s=s.replace("distance=$('empty').checked?175:","distance=$('empty').checked?Math.max(both?250:175,(both?150:85)/aspect*1.45):")
 s=s.replace("$('reset').onclick=()=>reset();","$('empty').oninput=()=>reset(false);$('reset').onclick=()=>reset();")
 p.write_text(s)
 meta=json.loads((d/'models.json').read_text());meta.update(version=3,print_pose='upright',bottom_z=-64);(d/'models.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
