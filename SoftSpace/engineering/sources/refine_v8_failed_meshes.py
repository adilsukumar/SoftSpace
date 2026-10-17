from solid_band_v8 import run,OUT
import json,traceback
j=json.loads((OUT/'solid_v8_summary.json').read_text())
try:
 for c in j['cases']:
  if c['stress_gate_5pct']:continue
  a=c['meshes'][-1];b=run(c['size'],1.5);c['meshes'].append(b)
  c['stress_relative_mesh_change']=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1);c['deflection_relative_mesh_change']=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1)
  c['stress_gate_5pct']=c['stress_relative_mesh_change']<.05;c['deflection_gate_5pct']=c['deflection_relative_mesh_change']<.05
  (OUT/'solid_v8_summary.json').write_text(json.dumps(j,indent=2));print(c['size'],'refined stress change',c['stress_relative_mesh_change'],flush=True)
 j['all_stress_mesh_gates_pass']=all(c['stress_gate_5pct'] for c in j['cases']);j['all_deflection_mesh_gates_pass']=all(c['deflection_gate_5pct'] for c in j['cases'])
except Exception:j['refinement_error']=traceback.format_exc();print(j['refinement_error'])
(OUT/'solid_v8_summary.json').write_text(json.dumps(j,indent=2))
