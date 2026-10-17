"""Package current CAD and evidence without treating open checks as passes."""
from pathlib import Path
import json,hashlib,zipfile,shutil
P=Path(__file__).parent;O=P/'engineering-v10-results'
native=json.loads((O/'cad_native_report.json').read_text());pairs=json.loads((O/'native_all_pose_pairs.json').read_text());bands=json.loads((O/'native_local_band_comparison.json').read_text());stress=json.loads((O/'solid_v10_summary.json').read_text());archives=json.loads((O/'native_archive_reopen.json').read_text())
assert native['status']=='complete' and pairs['all_pass'] and bands['all_pass'] and archives['status']=='complete'
from audit_v10_source_identity import audit as audit_source_identity
source_identity=audit_source_identity()
full=json.loads((O/'adult_small_full_width_summary.json').read_text())
full_sizes=json.loads((O/'full_width_sizes_summary.json').read_text()) if (O/'full_width_sizes_summary.json').exists() else None
full_force=json.loads((O/'adjustment_force_full_width.json').read_text()) if (O/'adjustment_force_full_width.json').exists() else None
strength=json.loads((O/'conditional_strength_screen.json').read_text()) if (O/'conditional_strength_screen.json').exists() else None
quarter_pass=sum(c['stress_gate_5pct'] for c in stress['cases'])
actual_changes=[abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1) for c in full_sizes['cases']] if full_sizes else []
actual_pass=sum(v<.05 for v in actual_changes)
review=f"""# V10 CAD candidates and recorded numerical checks

Updated 14 October 2026. This package records concept geometry and calculations. It does not establish comfort, sound reduction, sensory acceptance, pain prevention, market superiority, zero leakage or production readiness.

The mechanical calculations use local Python, Gmsh and SciPy on the saved STEP geometry. Runtime versions are recorded in runtime_versions.json. Library installations remain in the local project and are not bundled in this ZIP.

All six native Fusion candidates were exported as six F3D archives and 18 nominal/endpoint STEP poses. Each STEP contains 28 solids and passes the all-body intersection audit at a 0.01 mm3 overlap tolerance. Each F3D was reopened in Fusion and its V10 component contained 28 solids. Native and local band shapes agree within the 0.01 mm3 volume comparison tolerance. Source hashes are saved.

Current CAD hashes also match the files used in the recorded checks. archive_integrity.json is an earlier inventory: its reopening flags were recorded before the native reopening check, and its Python reader could not verify an unsupported compression method. native_archive_reopen.json records the later Fusion reopening results. The outer deliverable ZIP receives a separate CRC and file-hash check.

The wider V9 audit found shortest-setting guide/pivot-pin clashes in all six sizes and extra knob/fork clashes in the child sizes. Earlier selected-body checks had omitted these parts. V10 trims the guide bottoms by 2 mm and raises the clamp bores and knobs by 4 mm. The intended slider range remains 0 to 30 mm. Nominal selected gaps are 0.217157 mm for guide/tongue, 1 mm for guide/pin and 0.5 mm for knob/fork. These are CAD gaps, not proven factory tolerances. The clamp reach audit checks 84 positions geometrically; it does not prove locking or retention.

Changed-guide quarter-band sampled stress comparisons meet the chosen 5% limit in {quarter_pass} of six sizes. All six guide-displacement comparisons meet that limit. The earlier adult-medium 8.37% and 18% changes remain in history. The quarter model mirrors the front-only bore onto the rear wall. Its nominal geometric approximation remains even after numerical refinement.

The separate actual-width ideal-fixture study covers {len(actual_changes)} of six sizes. Its sampled stress comparisons meet 5% in {actual_pass} of those sizes. Guide compliance and stress are reported separately; displacement stability alone is not peak-stress stability. The actual-width model retains the real front-only bore, but its crown restraints and surface loading differ from the quarter model. It does not isolate symmetry error or solve the worn assembly.

Slider segment checks use consistent surface loads at 0, 15 and 30 mm adjustment. The reduced force screens combine ideal band/slider compliance with scalar foam/cover contact and synthetic heads. They omit real guide rotations, clamp friction, pin bearing and scalp contact. All material properties and mounting offsets remain assumed. They do not establish a comfort or sound-seal threshold.

The invalid first adult-large quarter mesh and earlier memory, export, load and solver failures are retained. Accepted element-quality, residual and force-balance checks are numerical evidence, not physical verification. Last-two-mesh peak comparisons are not absolute continuum error bounds.

Sony WH-CH720N is the selected replacement-pad host. The user owns it and will measure its mount later. The generic pad is not claimed compatible. Host force, mounting dimensions, driver/vent geometry, incoming noise, outgoing music, response, ANC and wearer comfort remain untested. Existing replacement-pad competitors are recorded in both reports; no superiority or confirmed Indian market absence is claimed.

Remaining work includes measured foam/cover/band properties, real locking and retention, joints and worn-head contact, manufacturing tolerances, thermal/moisture checks, calibrated acoustic comparisons and voluntary sensory feedback. These dependencies prevent a finished commercial-product claim.

Both Word reports were updated together. Their structure and approximate previews were checked. Native Word pagination remains unverified: desktop control returned unavailable elements and activation failures, followed by GetCursorPos Access is denied (0x80070005).
"""
if full_force:
 review+=f"\nThe actual-width reduced force screen contains {full_force['case_count']} assumed-input cases. The older quarter-fixture screen remains separately recorded.\n"
if strength:
 review+=f"\nThe conditional nominal-setting material screen contains {strength['case_count']} cases. A sampled-stress margin of 3 would require up to {strength['minimum_strength_for_margin_3_over_all_nominal_cases_MPa']:.3f} MPa under these assumptions. It uses the largest observed accepted-mesh centroid peak, not a proven continuum upper bound. Margins of 2 and 3 are illustrative; no measured yield, creep, fatigue or durability pass follows.\n"
travel_path=O/'intermediate_travel_audit.json'
if travel_path.exists():
 travel=json.loads(travel_path.read_text());tolerance=json.loads((O/'tolerance_budget_expanded.json').read_text())
 review+=f"\nAdditional V10 check: {travel['pose_count']} sampled rigid slider poses cover six sizes at 5 mm intervals. All pass: {travel['all_pass']}. Within-group pairs use rigid-transform invariance after their first check. This is not continuous swept-volume clearance or loaded contact. The {tolerance['case_count']}-case expanded dimensional budget does not establish manufacturing clearance: the guide/tongue 0.217157 mm nominal gap cannot guarantee clearance at assumed 0.2 mm normal error per part. No CAD revision was made. test_register.json lists unresolved tests and their prerequisites. Timing fields are elapsed wall time and may include interruption; they are not CPU benchmarks.\n"
if (O/'stop_onset_audit.json').exists():
 stop=json.loads((O/'stop_onset_audit.json').read_text())
 review+=f"\nFurther stop check: {stop['case_count']} guide/tongue contact searches locate an existing stop shoulder near 31 mm extension in all six sizes, roughly 1 mm beyond the intended range. The 36 imposed overtravel poses include blocking intersections at 40 to 60 mm. Separated imposed shapes beyond those intersections do not show a reachable extraction path. Stop strength, loaded retention and locking remain untested; no geometry was changed.\n"
(O/'REVIEW.md').write_text(review,encoding='utf-8');items={}
def add(f,n):items[n]=f
for value in native['files']:add(Path(value),'CAD/native/'+Path(value).name)
local=json.loads((O/'cad_local_report.json').read_text())
for value in local['files']:add(Path(value),'CAD/local/'+Path(value).name)
for f in O.iterdir():
 if f.suffix in ['.json','.csv','.npz','.md'] and '_partial' not in f.name:add(f,'evidence/'+f.name)
for f in (P/'documents').glob('*.docx'):add(f,'documents/'+f.name)
add(P/'documents'/'document_status.json','documents/document_status.json');add(P/'sony_ch720n_host.json','host/sony_ch720n_host.json');add(P/'sony_ch720n_market_comparison.json','host/sony_ch720n_market_comparison.json')
for name in ['audit_v9_all_pose_pairs.py','compare_v10_native_local.py','build_v10_local_candidates.py','solid_band_v10.py','solid_band_v9.py','run_v10_structure.py','audit_v10_numerics.py','audit_saved_v10_mesh_quality.py','v10_clearance_distances.py','audit_v10_band_symmetry.py','annotate_v10_scope.py','v10_slider_segment.py','quadratic_surface_load.py','v10_adjustment_force_screen.py','contact_membrane_fem.py','screening.py','v10_full_width_band.py','v10-variants.json','lower-crown-recipes.json','package_v10_verified.py']:
 add(P/name,'sources/'+name)
for name in ['GuideClearanceV10.py','VerifyV10Archives.py']:add(P/'CushionNext'/name,'sources/'+name)
for name in ['check_streamed_assembly.py','adopt_v10_refinement.py','v10_conditional_strength_screen.py','run_v10_full_width_sizes.py','refine_v10_actual_width_stress.py','audit_v10_lock_reach.py','render_v10_numerical_summary.py','record_v10_environment.py','finalize_v10_evidence_and_reports.py','audit_v10_source_identity.py']:add(P/name,'sources/'+name)
add(P/'engineering-v9-results'/'all_pose_pairs.json','prior-V9/all_pose_pairs.json');add(P/'engineering-v9-results'/'REVIEW.md','prior-V9/REVIEW.md')
for name in ['audit_v10_intermediate_travel.py','v10_tolerance_budget.py','finalize_v10_additional_tests.py']:
 add(P/name,'sources/'+name)
for name in ['audit_v10_overtravel.py','audit_v10_stop_onset.py']:
 add(P/name,'sources/'+name)
add(P/'documents'/'additional_v10_tests.py','sources/additional_v10_tests.py')
manifest={'status':'Native V10 CAD candidates; structural and physical checks remain open','native_CAD_files':len(native['files']),'local_STEP_files':len(local['files']),'native_STEP_all_pair_pass':pairs['all_pass'],'archives_reopened':len(archives['archives']),'band_geometry_agreement':bands['all_pass'],'all_stress_comparisons_pass':stress['all_stress_comparisons_pass'],'files':[{'path':n,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for n,f in items.items()]}
manifest['actual_width_fixture']={'completed_sizes':len(full_sizes['cases']),'status':full_sizes['status'],'all_recorded_compliance_comparisons_pass':full_sizes['all_compliance_comparisons_pass']} if full_sizes else {'status':'not recorded'}
if full_sizes:
 manifest['actual_width_fixture']['sampled_stress_comparisons_passing']=actual_pass
 manifest['actual_width_fixture']['stress_refinement_status']=full_sizes.get('stress_refinement_status','not recorded')
 manifest['actual_width_fixture']['all_sampled_stress_comparisons_pass']=len(actual_changes)==6 and actual_pass==6
manifest['actual_width_reduced_force_cases']=full_force['case_count'] if full_force else 0
manifest['CAD_file_identity']={'files':source_identity['unique_CAD_files'],'all_match':source_identity['all_match']}
target=P/'EarDefender_V10_Native_CAD_and_Recorded_Checks.zip'
if target.exists():
 history=P/'package-history';history.mkdir(exist_ok=True)
 latest=history/'EarDefender_V10_before_additional_travel_tests.zip'
 if not latest.exists():shutil.copy2(target,latest)
 before_stop=history/'EarDefender_V10_before_stop_tests.zip'
 if not before_stop.exists():shutil.copy2(target,before_stop)
 previous=history/'EarDefender_V10_before_20261014_final_refinement.zip'
 if not previous.exists():shutil.copy2(target,previous)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,f in items.items():z.write(f,n)
 z.writestr('manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for row in manifest['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'integrity':'pass','status':manifest['status']}))
