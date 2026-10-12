"""Compare candidates only against matching material and boundary baselines."""
import json, math
from pathlib import Path

rows=[]
for folder in sorted(Path('.').glob('HX05*')):
    results=[json.loads(p.read_text()) for p in (folder/'results').glob('*.json')]
    bases={(r['layer_stiffness_ratio'],r['bulk_stiffness_ratio'],r['support']):r for r in results if r['clock_deg']==0}
    for r in results:
        base=bases.get((r['layer_stiffness_ratio'],r['bulk_stiffness_ratio'],r['support']))
        if base is None: continue
        reference={v['case']:v for v in base['loads']}
        compliance=[v['compliance']/reference[v['case']]['compliance'] for v in r['loads']]
        stress=[v['normalized_layer_index_p99']/reference[v['case']]['normalized_layer_index_p99'] for v in r['loads']]
        rows.append(dict(rack=r['id'],clock_deg=r['clock_deg'],ratio=r['layer_stiffness_ratio'],bulk=r['bulk_stiffness_ratio'],support=r['support'],budget_error=r['budget_error_fraction'],width_mm=r['rib_width_mm'],compliance_geomean=math.exp(sum(map(math.log,compliance))/len(compliance)),compliance_worst_ratio=max(compliance),layer_index_geomean=math.exp(sum(map(math.log,stress))/len(stress)),layer_index_worst_ratio=max(stress),max_residual=max(v['residual_relative'] for v in r['loads'])))
Path('comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:
    print(f"{r['rack']} clock={r['clock_deg']:g} rz={r['ratio']:g} budget={r['budget_error']:.3%} C(mean/worst)={r['compliance_geomean']:.3f}/{r['compliance_worst_ratio']:.3f} layer(mean/worst)={r['layer_index_geomean']:.3f}/{r['layer_index_worst_ratio']:.3f}")
