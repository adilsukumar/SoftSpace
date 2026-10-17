from solid_band_v7 import run,OUT
import json,traceback,time
j={'status':'running','cases':[],'model':'Linear elastic CAD crown and guides, rounded entry, ideal2N/side load','limitations':['Actual material unknown; E2000MPa and nu0.35 hypotheses','Slider locking/contact and nonlinear assembled fit not simulated','Stable stress does not establish material strength or comfort']}
try:
 for size in ['child_small','child_medium','child_large','adult_small','adult_medium','adult_large']:
  rows=[run(size,h) for h in [3,2]]
  if size=='child_small':rows.append(json.loads((OUT/'child_small_h1.5.json').read_text()))
  a,b=rows[-2:];du=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1);ds=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
  j['cases'].append({'size':size,'meshes':rows,'deflection_relative_mesh_change':du,'stress_relative_mesh_change':ds,'deflection_gate_5pct':du<.05,'stress_gate_5pct':ds<.05})
  (OUT/'solid_v7_summary.json').write_text(json.dumps(j,indent=2));print(size,'mesh_change',du,ds,flush=True)
 j['status']='complete'
except Exception:j['status']='error';j['error']=traceback.format_exc();print(j['error'])
(OUT/'solid_v7_summary.json').write_text(json.dumps(j,indent=2))
