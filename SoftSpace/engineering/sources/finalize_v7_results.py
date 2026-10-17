from pathlib import Path
import json
p=Path(__file__).parent;o=p/'engineering-v7-results';j=json.loads((o/'solid_v7_summary.json').read_text())
c=next(c for c in j['cases'] if c['size']=='adult_medium');r=json.loads((o/'adult_medium_h1.5.json').read_text());a=c['meshes'][-1];c['meshes'].append(r)
c['stress_relative_mesh_change']=abs(r['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1);c['deflection_relative_mesh_change']=abs(r['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1)
c['stress_gate_5pct']=c['stress_relative_mesh_change']<.05;c['deflection_gate_5pct']=c['deflection_relative_mesh_change']<.05
j['all_stress_mesh_gates_pass']=all(c['stress_gate_5pct'] for c in j['cases']);j['all_deflection_mesh_gates_pass']=all(c['deflection_gate_5pct'] for c in j['cases'])
(o/'solid_v7_summary.json').write_text(json.dumps(j,indent=2));print('V7 stress and deflection mesh gates',j['all_stress_mesh_gates_pass'],j['all_deflection_mesh_gates_pass'])
