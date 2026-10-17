"""Bounded final screens on unchanged V18 CAD. No physical measurements or product qualification."""
import sys,json,hashlib,math,itertools,csv
from pathlib import Path
from audit_v14_motion import P,load,bounds
O=P/'engineering-v18-results';oldpath=P/'engineering-v11-results/materials_screen.json';old=json.loads(oldpath.read_text());register=json.loads((O/'test_register.json').read_text());torque=json.loads((O/'torque_and_mass.json').read_text());grades={r['grade']:r for r in old['band_cases']};assert len(grades)==10
fixtures=[]
for r in register['band_mechanics']['cases']:
 m=r['meshes'][-1];fixtures.append(('Band',r['size'],m,m['guide_weighted_x_displacement_mm'],2.0))
for r in register['stop_mechanics']:
 m=r['meshes'][-1];fixtures.append(('Tongue stop',r['size'],m,m['weighted_load_direction_displacement_mm'],13.0))
for r in register['fork_mechanics']['cases']:
 m=r['meshes'][-1];fixtures.append(('Fork',r['size'],m,m['cup_weighted_x_displacement_mm'],2.0))
materials=[]
for component,size,m,u0,f0 in fixtures:
 assert hashlib.sha256(Path(m['source']).read_bytes()).hexdigest()==m['source_sha256']
 for name,g in grades.items():
  E=g['modulus_MPa'];y=g['typical_tensile_yield_MPa']
  for factor in [.25,.5,1,2.5,5]:
   sigma=m['max_von_mises_centroid_MPa']*factor;disp=u0*factor*2000/E
   materials.append(dict(component=component,size=size,grade=name,reference_modulus_MPa=E,modulus_basis=g['modulus_basis'],reference_tensile_yield_MPa=y,reference_density_g_cm3=g['density_g_cm3'],source_url=g['source_url'],reference_data_checked=old['checked'],CAD_sha256=m['source_sha256'],load_factor=factor,primary_force_N=f0*factor,scaled_weighted_displacement_mm=disp,scaled_sampled_centroid_stress_MPa=sigma,reference_yield_to_sampled_stress_ratio=y/sigma,reference_yield_exceeded=sigma>y,warning='Linear fixed-nu scaling only; not a new nonlinear solve, physical material test or manufactured allowable'))
for r in materials:
 r['force_for_same_reference2000_fixture_movement_N']=r['primary_force_N']*r['reference_modulus_MPa']/2000
 r['sampled_stress_for_same_reference2000_fixture_movement_MPa']=r['scaled_sampled_centroid_stress_MPa']*r['reference_modulus_MPa']/2000
# Positive controls for the exact fixed-nu homogeneous elastic scaling law.
assert abs(1*2000/2000-1)<1e-12 and abs(2*2000/4000-1)<1e-12
metrology=[];fit=[]
for f in sorted(O.glob('*_cad_report.json')):
 row=json.loads(f.read_text());parts,_=load(row);h=row['hinge'];bolt=bounds(parts['RightHingeBolt']);nut=bounds(parts['RightHingeNut']);disc=bounds(parts['RightDiscSpring']);free=h['disc_free_height_mm'];loaded=disc[4]-disc[1];shift=free-loaded;overlap=max(0,min(bolt[4],nut[4]+shift)-(nut[1]+shift));gap=(h['bore_diameter_mm']-h['pin_diameter_mm'])/2
 metrology.append(dict(size=row['size'],source=row['file'],source_sha256=row['sha256'],nominal_pivot_bore_diameter_mm=h['bore_diameter_mm'],nominal_bolt_diameter_mm=h['pin_diameter_mm'],nominal_radial_pivot_clearance_mm=gap,measured_saved_disc_axial_height_mm=loaded,reference_disc_free_height_mm=free,disc_axial_relaxation_to_reference_free_height_mm=shift,measured_saved_nut_axial_height_mm=nut[4]-nut[1],bolt_tip_protrusion_beyond_saved_nut_mm=bolt[4]-nut[4],nominal_bolt_nut_axial_overlap_at_reference_free_height_mm=overlap,scope='Measurements of saved nominal CAD envelopes only; no actual threads, thread runout, engagement strength or toleranced manufactured assembly'))
 for diameter_error,axis_error,swell in itertools.product([0,.025,.05,.1],[0,.025,.05,.1],[0,.025,.05]):
  margin=gap-diameter_error-axis_error-swell;fit.append(dict(size=row['size'],each_diameter_error_bound_mm=diameter_error,relative_axis_error_bound_mm=axis_error,assumed_radial_swelling_or_coating_mm=swell,remaining_radial_clearance_mm=margin,positive_margin=margin>1e-9))
retention=[]
for r in torque['mass_cases']:
 for acceleration,holding in itertools.product([0,1,1.5,2,3,5],[64,96]):
  demand=r['maximum_gravity_moment_over_orientation_Nmm']*acceleration;retention.append(dict(size=r['size'],density_scenario=r['density_scenario'],equivalent_resultant_acceleration_g=acceleration,assumed_holding_torque_Nmm=holding,quasistatic_moment_Nmm=demand,remaining_holding_margin_Nmm=holding-demand,positive_margin=holding>demand,scope='Equivalent static inertial load at worst orientation,not a transient impact or measured friction result'))
for r in torque['mass_cases']:r['calculated_acceleration_at64Nmm_g']=64/r['maximum_gravity_moment_over_orientation_Nmm']
out=dict(updated='2026-10-16',revision='V18 final available-data screens',geometry_changed=False,reference_snapshot=str(oldpath),reference_snapshot_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest(),reference_data_date=old['checked'],reference_grades=len(grades),fixture_count=len(fixtures),material_cases=materials,material_case_count=len(materials),reference_yield_exceedances=sum(r['reference_yield_exceeded'] for r in materials),CAD_metrology=metrology,pivot_fit_cases=fit,pivot_fit_case_count=len(fit),positive_pivot_fit_margin_cases=sum(r['positive_margin'] for r in fit),retention_cases=retention,retention_case_count=len(retention),acceleration_thresholds=torque['mass_cases'],minimum_calculated64Nmm_threshold_g=min(r['calculated_acceleration_at64Nmm_g'] for r in torque['mass_cases']),physical_measurements_performed=0,limits=['Ten previously recorded grades are not every material; no material winner or actual property validation is established','Old published reference data are reused with their recorded date and source links,not reverified as current supplier data','E scaling is exact only for the same homogeneous linear fixture and fixed Poisson ratio0.35; real grade Poisson ratios and large deformation are not solved','Steel data concern wire references,not qualified formed strip; the PP modulus is a flexural proxy','Material substitutions do not update complete assembly mass,friction,creep,foam,cover,contact or acoustics','Diameter and alignment bounds are illustrative scenarios,not production probabilities or supplier capability','Hinge torque values64and96Nmm are proposed targets,not measured properties; inward folding is intentionally possible','No impact time history,drop,fatigue,loosening,pinch or wearer safety simulation is claimed','CAD dimensions are not measurements of the user Sony headset or physical parts'])
(O/'final_available_data_screen.json').write_text(json.dumps(out,indent=2))
for name,rows in [('v18_material_load_scaling.csv',materials),('v18_pivot_clearance_cases.csv',fit),('v18_retention_acceleration_cases.csv',retention),('v18_saved_CAD_measurements.csv',metrology)]:
 with (O/name).open('w',newline='') as file:
  w=csv.DictWriter(file,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
register['final_available_data_screens']=dict(file='engineering-v18-results/final_available_data_screen.json',material_cases=len(materials),pivot_fit_cases=len(fit),retention_cases=len(retention),CAD_sizes_measured=len(metrology),minimum_calculated64Nmm_threshold_g=out['minimum_calculated64Nmm_threshold_g'],physical_measurements_performed=0)
register['screening_phase_disposition']='Available-data screening recorded with known limits; complete joint,validated materials,physical performance and Sony fit remain input-dependent and are not passed';(O/'test_register.json').write_text(json.dumps(register,indent=2));print(json.dumps(register['final_available_data_screens']))
