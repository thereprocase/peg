from pathlib import Path
import json,numpy as np
source=Path('bench/source/hx05_density_v1/genetic.py');scope={'__file__':str(source.resolve())};exec(source.read_text().split('rng=np.random.default_rng')[0],scope)
rows=[]
for ident in ['HX05C','HX05B','HX05A']:
 model=scope['Model'](ident);model.solve(np.ones(len(model.edges)),.35)
 flags=[dict(case=label,numerical_regularization_fraction=float(fr),resolved=bool(fr<.01)) for label,fr in zip(model.labels,model.last_regularization_fraction)]
 rows.append(dict(id=ident,cases=flags));print(ident,flags,flush=True)
Path('.local-runtime/hx05-density-v1/lattice-quality.json').write_text(json.dumps(dict(models=rows,scope='Cases dominated by numerical regularization are unresolved by this coarse lattice, not physical strength evidence.'),indent=2)+'\n')
