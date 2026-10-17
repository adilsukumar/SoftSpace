import sys,json,hashlib,csv
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v17-results';sys.path.insert(0,str(P/'solver-libraries'));import numpy as np
c=json.loads((O/'pin_contact_and_return.json').read_text());s=json.loads((O/'spring_design_tradeoff.json').read_text());d=json.loads((O/'digital_closeout.json').read_text());audits=[]
for row in c['source_geometry']['rows']:
 assert hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()==row['source_sha256']
 for h in [1,.5,.25]:
  f=O/(row['size']+'_pin_contact_h'+str(h)+'.npz')
  with np.load(f) as a:
   y=a['y'];u=a['u'];r=a['reaction'];force=a['force'][::2];fb=float(abs((r+force).sum()));mb=float(abs((r+force)@y));finite=all(np.isfinite(a[k]).all() for k in ['y','u','reaction','force']);assert finite and fb<1e-5 and mb<1e-4
  audits.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'force_balance_error_N':fb,'moment_balance_error_Nmm':mb,'pass':True})
assert c['contact_case_count']==90 and c['return_case_count']==1080 and len(s['cases'])==300 and all(r['equilibrium_pass'] for r in c['cases']);assert not d['product_complete'] and not d['manufacturing_release'] and len(d['workstreams'])==28
out={'arrays_checked':len(audits),'audits':audits,'contact_controls_pass':all(r['pass'] for r in c['controls']),'selected_contact_refinements_pass':all(r['chosen_5percent_comparison_pass'] for r in c['refinements']),'manufacturing_release':False,'scope':'Source identity and independent saved-array equilibrium checks; not physical validation'};(O/'closeout_verification.json').write_text(json.dumps(out,indent=2))
f=O/'physical-test-records';f.mkdir(exist_ok=True);target=f/'loaded_pin_return_measurements.csv'
if not target.exists():
 with target.open('w',newline='') as file:csv.writer(file).writerow(['sample_id','CAD_revision','pin_material_grade_lot','guide_material_grade_lot','spring_part_number_lot','temperature_C','relative_humidity_percent','cycle_count','reviewed_transverse_load_N','measured_spring_free_length_mm','measured_seated_length_mm','measured_released_length_mm','measured_spring_only_seated_force_N','measured_spring_only_released_force_N','measured_spring_removed_breakaway_drag_N','measured_combined_pull_force_N','measured_return_force_N','full_engagement_observed','return_delay_seconds','residual_pin_travel_mm','measurement_uncertainty','notes'])
print(json.dumps({'saved_arrays_verified':len(audits),'source_geometry_matched':True,'test_record_has_no_results':True,'product_complete':False}))
