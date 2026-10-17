"""Sequential V12 band fixture meshes; no parallel heavy solves."""
import json,hashlib
from v12_full_width_band import run,P,O
cad=json.loads((O/'cad_report.json').read_text());cases=[]
for row in cad['sizes']:
 size=row['size'];meshes=[]
 for h in [2.5,2.0,1.5,1.25,1.0]:
  path=O/(size+'_full_width_h'+str(h)+'.json')
  r=json.loads(path.read_text()) if path.exists() else run(size,h)
  assert r['source_sha256']==row['sha256'];meshes.append(r)
  if len(meshes)>=2:
   a,b=meshes[-2:];dc=abs(b['compliance_mm_per_N']/a['compliance_mm_per_N']-1);sc=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1)
   if dc<.05 and sc<.05:break
 c={'size':size,'meshes':meshes,'compliance_relative_mesh_change':dc,'sampled_peak_stress_relative_mesh_change':sc,'chosen_compliance_5percent_gate':dc<.05,'chosen_sampled_peak_stress_5percent_gate':sc<.05};cases.append(c);(O/'band_sizes_partial.json').write_text(json.dumps(cases,indent=2));print(json.dumps({'finished_size':size,'meshes':[r['mesh_max_mm'] for r in meshes],'displacement_change':dc,'sampled_stress_change':sc}),flush=True)
out={'status':'complete six-size ideal actual-width band fixture study','cases':cases,'all_chosen_mesh_comparisons_pass':all(r['chosen_compliance_5percent_gate'] and r['chosen_sampled_peak_stress_5percent_gate'] for r in cases),'limits':['Actual V12 wider guides, but homogeneous E2000MPa nu0.35 and ideal symmetry datum restraints','2N guide-bottom traction does not model complete worn contact or clamp, tongue and lock forces','A chosen mesh comparison is not a continuum stress bound, material qualification, comfort result or durability pass']};(O/'band_sizes_summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({'sizes':len(cases),'all_chosen_mesh_comparisons_pass':out['all_chosen_mesh_comparisons_pass']}),flush=True)
