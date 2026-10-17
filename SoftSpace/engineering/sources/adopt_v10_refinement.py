"""Adopt only a completed finer solve with source and numerical checks."""
from pathlib import Path
import sys,json,hashlib,math
P=Path(__file__).parent;O=P/'engineering-v10-results';size=sys.argv[1];h=float(sys.argv[2]);r=json.loads((O/(size+'_h'+str(h)+'.json')).read_text());s=json.loads((O/'solid_v10_summary.json').read_text())
assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];assert r['minimum_adaptive_Jacobian_mm3']>0 and r['minimum_quadrature_jacobian_mm3']>0 and r['relative_free_residual']<1e-5
rx=r['reaction_sum_N'];assert math.sqrt((rx[0]+1)**2+rx[1]**2+rx[2]**2)<1e-5
c=next(c for c in s['cases'] if c['size']==size);old=c['meshes'][-1];assert h<old['mesh_max_mm']
c['meshes'].append(r);ds=abs(r['max_von_mises_centroid_MPa']/old['max_von_mises_centroid_MPa']-1);du=abs(r['guide_mean_x_displacement_mm']/old['guide_mean_x_displacement_mm']-1)
c.update(stress_relative_mesh_change=ds,deflection_relative_mesh_change=du,stress_gate_5pct=ds<.05,deflection_gate_5pct=du<.05)
s.update(all_stress_comparisons_pass=all(c['stress_gate_5pct'] for c in s['cases']),all_deflection_comparisons_pass=all(c['deflection_gate_5pct'] for c in s['cases']))
(O/'solid_v10_summary.json').write_text(json.dumps(s,indent=2));print(json.dumps({'size':size,'mesh_mm':h,'stress_change':ds,'displacement_change':du,'stress_pass':ds<.05}),flush=True)
