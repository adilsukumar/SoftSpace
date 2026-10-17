from pathlib import Path
import json,hashlib
P=Path(__file__).parent;O=P/'engineering-v9-results';v=json.loads((O/'native_verification.json').read_text());cases=[]
for s in v['sizes']:
 size=s['name'];meshes=[]
 for f in O.glob(size+'_h*.json'):
  r=json.loads(f.read_text())
  if 'mesh_max_mm' in r:meshes.append(r)
 meshes.sort(key=lambda r:r['mesh_max_mm'],reverse=True)
 if len(meshes)<2:continue
 a,b=meshes[-2:];ds=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1);du=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1)
 source=sorted(f for f in P.glob('OwnPassiveDefender_V9_'+size+'_*.step') if 'Extension' not in f.name)[-1]
 cases.append({'size':size,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'meshes':meshes,'stress_relative_mesh_change':ds,'deflection_relative_mesh_change':du,'stress_gate_5pct':ds<.05,'deflection_gate_5pct':du<.05})
j={'status':'complete' if len(cases)==6 else 'partial','native_sizes_exported':len(v['sizes']),'structural_cases_checked':len(cases),'cases':cases,'all_available_stress_comparisons_pass':all(c['stress_gate_5pct'] for c in cases),'limitations':['Only ideal linear elastic crown and guide model; E2000MPa and nu0.35 assumed','No measured yield/creep/fatigue allowable, slider contact or locking','Two successive meshes within5% is a numerical comparison, not absolute error validation','No new pad, leakage or sensory evidence']}
(O/'solid_v9_summary.json').write_text(json.dumps(j,indent=2));print(json.dumps({'status':j['status'],'cases':[(c['size'],c['stress_relative_mesh_change'],c['deflection_relative_mesh_change']) for c in cases]}))
