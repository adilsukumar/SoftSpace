from acoustic_p2_refinement import solve,O
import json,traceback
j={'status':'running','meshes':[],'comparisons':[],'limitations':['Same hypothetical wall/cavity physics as V6','Quarter symmetry; uniform incident excitation','Area-integrated receiver replaces nodal mean','No material or wearer validation']}
try:
 for family in ['verification','child','adult']:
  values=[]
  for h in [6,4.5]:
   v=solve(family,h);values.append(v);j['meshes'].append({k:u for k,u in v.items() if k!='rows'});(O/'acoustic_p2_summary.json').write_text(json.dumps(j,indent=2))
  a,b=values;diff=[abs(x['model_pressure_transfer_db']-y['model_pressure_transfer_db']) for x,y in zip(a['rows'],b['rows'])]
  comp={'family':family,'max_mesh_difference_db':max(diff),'gate_1db':max(diff)<1}
  if family=='verification':comp.update(max_exact_complex_error=max(r['relative_complex_error'] for r in b['rows']),gate_exact_1pct=max(r['relative_complex_error'] for r in b['rows'])<.01)
  j['comparisons'].append(comp);(O/'acoustic_p2_summary.json').write_text(json.dumps(j,indent=2));print(comp,flush=True)
 j['status']='complete'
except Exception:j['status']='error';j['error']=traceback.format_exc();print(j['error'])
(O/'acoustic_p2_summary.json').write_text(json.dumps(j,indent=2))
