"""Conditional nominal-setting band strength margins, not a material certificate."""
from pathlib import Path
import json,hashlib
P=Path(__file__).parent;O=P/'engineering-v10-results';s=json.loads((O/'solid_v10_summary.json').read_text());f=json.loads((O/'adjustment_force_screen.json').read_text());bands={c['size']:max(c['meshes'],key=lambda r:r['max_von_mises_centroid_MPa']) for c in s['cases']};rows=[];models=[('quarter_width',f,bands)]
if (O/'adjustment_force_full_width.json').exists():
 full=json.loads((O/'full_width_sizes_summary.json').read_text());ff=json.loads((O/'adjustment_force_full_width.json').read_text());fb={c['size']:max(c['meshes'],key=lambda r:r['max_von_mises_centroid_MPa']) for c in full['cases']};models.append(('actual_width_fixture',ff,fb))
for model,forces,lookup in models:
 for case in forces['cases']:
  if case['extension_mm']!=15:continue
  b=lookup[case['head'] if 'head' in case else case['name']]
  assert hashlib.sha256(Path(b['source']).read_bytes()).hexdigest()==b['source_sha256']
  sigma=b['max_von_mises_centroid_MPa']*case['force_N']/b.get('load_per_full_side_N',2)
  rows.append({'size':b['size'],'fixture_model':model,'E_MPa':case['E_MPa'],'extension_mm':15,'predicted_force_per_side_N':case['force_N'],'band_centroid_stress_scaled_MPa':sigma,'stress_reference_mesh_mm':b['mesh_max_mm'],'stress_reference':'Largest observed accepted-mesh centroid peak, not a proven continuum upper bound','strength_needed_for_margin_2_MPa':2*sigma,'strength_needed_for_margin_3_MPa':3*sigma,'source_sha256':b['source_sha256']})
out={'status':'complete conditional screen','cases':rows,'case_count':len(rows),'minimum_strength_for_margin_3_over_all_nominal_cases_MPa':max(r['strength_needed_for_margin_3_MPa'] for r in rows),'assumed_strength_options_MPa':[5,10,20,30,40],'limits':['Only nominal 15 mm adjustment; each ideal band fixture uses its own recorded reduced force screen','Largest observed accepted-mesh centroid stress is not a proven continuum peak bound','Linear elastic stress scaled by predicted force; unchanged Poisson ratio assumed','Assumed E and scalar pad input, not measured band force','Margins2 and3 are illustrative design targets, not a cited product standard','No measured yield strength, fatigue, creep, defects, pin bearing, clamp torque, drop impact or stress singularity allowance','No physical strength pass or failure is established; no wearer benefit is inferred']}
for strength in out['assumed_strength_options_MPa']:
 out.setdefault('strength_option_counts',[]).append({'assumed_strength_MPa':strength,'cases_with_margin_at_least_2':sum(strength>=r['strength_needed_for_margin_2_MPa'] for r in rows),'cases_with_margin_at_least_3':sum(strength>=r['strength_needed_for_margin_3_MPa'] for r in rows)})
(O/'conditional_strength_screen.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['cases','limits']}),flush=True)
