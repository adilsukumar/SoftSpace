import json,math,hashlib
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';f=O/'final_available_data_screen.json';s=json.loads(f.read_text());assert hashlib.sha256(Path(s['reference_snapshot']).read_bytes()).hexdigest()==s['reference_snapshot_sha256'];fixtures=json.loads((O/'test_register.json').read_text());assert len(s['material_cases'])==500 and len(s['pivot_fit_cases'])==288 and len(s['retention_cases'])==216
for r in s['material_cases']:
 assert all(math.isfinite(r[k]) and r[k]>0 for k in ['reference_modulus_MPa','reference_tensile_yield_MPa','scaled_weighted_displacement_mm','scaled_sampled_centroid_stress_MPa']);assert abs(r['reference_yield_to_sampled_stress_ratio']*r['scaled_sampled_centroid_stress_MPa']-r['reference_tensile_yield_MPa'])<1e-8
 assert abs(r['force_for_same_reference2000_fixture_movement_N']-r['primary_force_N']*r['reference_modulus_MPa']/2000)<1e-9
for r in s['pivot_fit_cases']:
 expected=.15-r['each_diameter_error_bound_mm']-r['relative_axis_error_bound_mm']-r['assumed_radial_swelling_or_coating_mm'];assert abs(expected-r['remaining_radial_clearance_mm'])<1e-12;assert r['positive_margin']==(expected>1e-9)
for r in s['retention_cases']:assert abs(r['remaining_holding_margin_Nmm']-(r['assumed_holding_torque_Nmm']-r['quasistatic_moment_Nmm']))<1e-10
for r in s['CAD_metrology']:
 assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];assert abs(r['measured_saved_disc_axial_height_mm']-.3625)<1e-6;assert abs(r['measured_saved_nut_axial_height_mm']-3.2)<1e-6;assert abs(r['bolt_tip_protrusion_beyond_saved_nut_mm'])<1e-6;assert abs(r['nominal_bolt_nut_axial_overlap_at_reference_free_height_mm']-3.0125)<1e-6
out=dict(source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),material_scaling_identity_checks=500,pivot_bound_checks=288,retention_margin_checks=216,CAD_source_and_dimension_checks=6,all_recorded_checks_pass=True,physical_measurements_performed=0,product_validation_passed=False);(O/'final_screen_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
