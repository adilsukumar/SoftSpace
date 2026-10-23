"""Evidence inventory and closure of executed V21 checks, with open work retained."""
from pathlib import Path
import json,csv,hashlib,math
P=Path(__file__).resolve().parent;O=P/'engineering-v21-results'
motion=[json.loads(f.read_text()) for f in sorted(O.glob('*_motion.json'))];assert len(motion)==6
contact=json.loads((O/'contact_envelope.json').read_text());stress=json.loads((O/'interior_stress_recovery.json').read_text());scalar=json.loads((O/'separate_scalar_controls.json').read_text())
checks=[
 ('Final six size geometry','Completed finite checks','V19 final-CAD reports and V21 motion','No loaded deformation or manufacturing capability'),
 ('Midpoint folding and unequal sliders','Completed finite checks','V21 six motion JSON files','2.5 degree midpoints and selected unequal extensions; no continuous certificate'),
 ('Carry envelope','Completed arithmetic','V21 motion bounding volume ratios','No travel bag fit, handling or pinch qualification'),
 ('Reference cushion STEP bodies','Completed geometry checks','V20 CAD_verification.json','No Sony mounting skirt'),
 ('Cushion numerical integration','Completed with failures recorded','V21 all_v20_exact_area_comparison.csv','334 old rows exceed selected 1 percent; maximum 3.35 percent'),
 ('Wider glasses position sensitivity','Completed assumed scenarios','V21 wider_position_scenarios.csv','Local and global pressure risks remain; no population probability'),
 ('Separate scalar controls','Completed numerical controls','V21 separate_scalar_controls.json','Same reduced physics'),
 ('Joint equilibrium and displacement','Completed limited model','V20 saved_audit_rerun.json and V19 statuses','Not complete bolt or worn assembly'),
 ('Peak stress refinement','FAILED chosen comparison','V21 interior_stress_recovery.json','Software work remains: local mesh quality, stress location and contact/bearing idealization review; do not substitute a mean stress pass'),
 ('Friction retention and fit limits','Completed assumed arithmetic','V21 mechanical_limits.json','Supplier process, friction and spring preload require data; higher preload/clearance is not automatically acceptable'),
 ('Headband material screening','Prior conditional screens complete','V11 material_families.csv and V16 materials_reference_screen.json','Not every material or grade tested; final grade and process not selected'),
 ('Foam cover and full worn contact','INPUT AND MODEL GATED','V20 and V21 reduced screens only','Need traceable material curves, membrane/seam geometry, friction and head geometry; then full nonlinear contact'),
 ('Heat and moisture','Prior uncalibrated proxy only','engineering-final-results/environment_summary.json','Actual permeability, sweat and assembled thermal parameters unknown'),
 ('Incoming and outgoing sound','Prior acoustic proxies only','V7 acoustic_p2_summary.json and V20 slit illustration','No actual worn seal or pad transfer impedance; cannot claim dB or ANC preservation'),
 ('Drop fatigue creep cleaning','INPUT AND MODEL GATED','V19 handoff forms','Need grade, process, time dependent properties, joint details and acceptance criteria; no simulated durability pass'),
 ('Sony mounting interface','DIMENSION GATED','V20 internet_sources.json','Public envelope and attachment instructions do not define exact skirt/groove'),
 ('Manufacturing assembly and seams','DESIGN GATED','V19 prototype-handoff and V20 design_parameters.json','Threads are envelopes; locking, tool access, seam and bond details need supplier definition'),
 ('Sensory acceptance and comfort','REQUIRES PEOPLE','Report physical test plan','Software cannot establish autistic user preferences or acceptance'),
 ('Market superiority and price','NOT ESTABLISHED','Dated report market sources','No every-market-headphone comparison or current supplier quotes'),
 ('Report native pagination','UNVERIFIED','Report QA logs','Approximate previews are not native Word rendering')]
with (O/'test_scope_register.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['test','status','evidence','limit_or_next_input']);w.writerows(checks)
result=dict(date='2026-10-24',CAD_revisions={'standalone':'V19 unchanged','Flex':'V20 three reference bodies unchanged'},executed_V21_round_complete=True,all_possible_software_testing_complete=False,
 remaining_software_only_issue='Joint peak stress is not mesh stable. Local mesh quality, stress location and contact/bearing idealizations require further numerical review before a strength claim. This is not solely a missing-hardware-input problem.',
 all_product_simulations_complete=False,physical_tests=0,manufacturing_release=False,
 motion=dict(sizes=6,additional_samples=sum(len(r['cases']) for r in motion),recommended_sample_failures=sum(not c['pass'] for r in motion for c in r['cases'] if c['phase']!='simultaneous fold diagnostic'),simultaneous_diagnostic_failures=sum(r['diagnostic_failures'] for r in motion),bounding_ratios={r['size']:r['folded_to_wear_bounding_volume_ratio'] for r in motion}),
 contact=dict(exact_comparisons=contact['exact_area_comparisons'],old_grid_outside_1_percent=contact['comparisons_exceeding_chosen_1_percent'],wider_cases=contact['wider_scenario_count'],scalar_checks=len(scalar['cases'])),
 stress=dict(saved_solutions=8,peak_comparisons=8,failed_peak_comparisons=sum(not c['chosen_5_percent_comparison_pass'] for c in stress['mesh_comparisons'])),
 decision='Material coupons and model-specific reference-pad measurements can inform future models. Do not claim full software closure, mechanical strength, validated comfort, a final foam winner or Sony fit; do not order production tooling.')
(O/'review_status.json').write_text(json.dumps(result,indent=2))
matrix=O/'refinement/matrix_review.json'
if matrix.exists():
 finer=json.loads(matrix.read_text());result['finer_joint_matrix']=finer;result['remaining_software_only_issue']=('The selected finer interior-point comparisons passed. A fully resolved fastener, bearing and surface-stress model is still outside this reference fixture; no all-software or strength release.' if finer['all_selected_finer_peak_comparisons_pass'] else 'Some finer peak comparisons remain above the chosen gate. Retain this numerical limitation and do not claim strength.')
 (O/'review_status.json').write_text(json.dumps(result,indent=2))
text='''# Software review on 24 October 2026

This V21 round adds checks to the unchanged SoftSpace V19 headset and SoftSpace Flex V20 reference cushions. It does not finish all possible software work. The most important new result is a failed peak-stress refinement comparison that remains software work, as well as the material and mounting inputs already missing.

## What changed

Six sizes were checked at folding midpoints between the old 5 degree samples, at selected unequal slider settings, and at four simultaneous folding positions. These are finite rigid checks, not continuous motion or pinch safety proof. Read the six JSON files for every pass and failure and the source STEP hashes.

All 11,664 V20 cushion rows were compared with closed-form elliptical areas. 334 exceeded the chosen 1 percent numerical comparison, with a maximum difference of 3.35 percent. The 12 selected V20 checks were true but did not establish accuracy of every row. V21 uses exact areas and explicit force-root brackets; the original CSV is preserved.

The wider assumed-position study has 126,360 cases, covering arm centres from -10 to 40 mm at 2 mm increments, widths 3/5/8 mm and zone heights 12/18/24/32/100 mm. Other force, foam, cover and protrusion assumptions are the same as V20. 127 selected rows were verified with independently implemented adaptive integration and a scalar root; this checks implementation, not realism. No random population sampling or probability is implied.

The 18 and 32 mm zones can raise local pressure when the arm misses them. A 100 mm zone avoids that local increase in eligible cases but still has 780 peak-pressure increases elsewhere and four model-detachment cases. That 100 mm zone is a computational alternative only, with no new STEP release or final material selection. No patch is declared a winner. The cover is a parallel-stiffness hypothesis, not a real membrane. Model detachment is not a measured seal gap or an acoustic result.

Eight saved V19 joint solutions were postprocessed at 27 interior points per element. Centroid values were reproduced. All eight peak comparisons between the two existing meshes exceeded the chosen 5 percent gate, with changes about 5 to 57 percent. Displacement checks do not establish peak-stress convergence. The following finer-mesh section records four new equilibrium solves. No material-strength pass is claimed. Further numerical work on mesh quality, stress locations and contact/bearing idealizations remains open; it cannot honestly be relabelled as only a physical-testing requirement.

Hinge and fit formulas were inverted to show conditional limits. At the assumed lowest friction and equivalent static 3g loading, the earlier mass screen needs about 206 N preload. This is not a permitted setting: actual friction, locking, spring curve and stresses must be checked. A nominal 4.3 mm bore supports the tight allocated errors but not the broad raw-error scenario. Enlarging to 4.7 mm would satisfy only that arithmetic clearance target and change bearing behaviour; CAD was not changed blindly.

## Scope and remaining work

The accompanying test_scope_register.csv covers geometry, folding, fit, structural calculations, materials, contact, sound, heat, durability, manufacturing and user acceptance. It identifies completed screens, failed comparisons, missing inputs and tests that need people. Prior acoustic/thermal models belong to earlier idealized geometries and are not current-headset performance tests. Not every possible material, headphone or head shape has been tested.

No all-software-complete, zero-leakage, clinically helpful, strongest, cheapest or market-superiority claim is supported. No production tooling is released. Small traceable material samples and exact reference-pad dimensions are useful inputs, but this review does not force the user to buy hardware or treat unresolved numerical issues as solved.

## Reproduce

Use the repository engineering prepare_workspace.py tool and recorded dependencies. From that workspace run v21_contact_envelope.py, v21_verify_and_limits.py, run_v21_motion.py, v21_stress_recovery.py and v21_compile_review.py. The motion script uses original STEP hashes and the existing positive-control OCC import procedure. The stress script reads the eight existing NPZ files without modifying them. New source/output hashes are recorded in the publication manifest.
'''
(O/'README.md').write_text(text,encoding='utf-8');print(json.dumps(result,indent=2))
if matrix.exists():
 finer=json.loads(matrix.read_text());current='''
## Additional finer joint matrix

The four representative joint/load cases now have an optimized 1.9 mm result. The original failed 3.0 to 2.3 mm comparisons above remain recorded. Read refinement/matrix_review.json for all new comparisons and their exact pass/fail status. The final accepted route uses projected Anderson acceleration of the original fixed-point contact equations with direct-LU inner solves. The child outward run uses mixed acceleration and matches the saved unaccelerated reference field; the other three use full projected acceleration. A separate Newton warm-start control is retained as an implementation check only. Failed mesh and stopped performance/solver experiments remain in the logs and solver_experiments.json; they are not passes.

These isolated joint fixtures come from the V19 ParallelDisc geometry, not a complete loaded final AssemblyPrototype. They use E=3500 MPa, nu=0.35, 140 N preload, friction 0.2 and +/-2 N side load. The peak check samples 27 interior points; it is not a globally bounded surface/contact-edge stress or a resolved bolt/thread/bearing model. A numerical comparison pass does not supply a real material allowable stress, durability or a manufactured joint qualification.
'''
 if finer['all_selected_finer_peak_comparisons_pass']:current+='\nAll selected finer peak comparisons passed the chosen 5 percent gate. This resolves the recorded sampled-peak comparison within this reference model; broader structural qualification remains open.\n'
 else:current+='\nSome finer peak comparisons did not pass. Further numerical work remains before relying on peak stress.\n'
 (O/'README.md').write_text(text+current,encoding='utf-8')

# Final executed results and explicit current gate failures.
finer=json.loads((O/'refinement/matrix_review.json').read_text())
compact=[json.loads(f.read_text()) for f in sorted(O.glob('*_compact.json'))];assert len(compact)==6
result['finer_joint_matrix']=finer
result['stress']['finer_passed']=sum(v['chosen_5_percent_comparison_pass'] for r in finer['cases'] for v in r['stress'])
result['stress']['finer_failed']=8-result['stress']['finer_passed']
result['remaining_software_only_issue']='Adult fork sampled peaks still change by 27.52 and 28.31 percent between 2.3 and 1.9 mm. No reliable peak or strength claim. Hotspot diagnostics document locations and mesh quality; a resolved contact/edge geometry model and further targeted refinement remain open.'
result['compact_poses']={r['size']:dict(angles=r['chosen']['angles'],folded_to_wear_box_volume_ratio=r['chosen']['box_volume_mm3']/math.prod(r['nominal_box_mm']),tested_candidates=len(r['trials']),path_samples=r['chosen']['samples']) for r in compact}
result['calculation_dates']=['2026-10-23','2026-10-24']
result['CAD_revisions']['standalone']='V19 part shapes unchanged; V21 carrying pose STEP exports added'
(O/'review_status.json').write_text(json.dumps(result,indent=2))
checks=[(a, '6 passed and 2 FAILED chosen finer comparison' if a=='Peak stress refinement' else b, 'V21 refinement/matrix_review.json and hotspot_diagnostics.json' if a=='Peak stress refinement' else c, 'Adult fork peaks change 27.52 and 28.31 percent; stress remains unresolved' if a=='Peak stress refinement' else d) for a,b,c,d in checks]
checks.extend([('Compact carrying pose search','Six selected sampled paths passed','V21 six compact JSON and STEP exports','Ranked 625 candidates per size until first passing path; no continuous or pinch certificate'),('Joint family geometry','12 canonical part comparisons passed','V21 joint_family_geometry.json','Same isolated geometry within family; not full worn load equivalence'),('Older heat proxy equation','216 analytic comparisons passed','V21 thermal_proxy_control.json','155 assumed rows saturated; no current product cooling claim'),('Stress hotspot diagnostics','Completed diagnostic postprocessing','V21 hotspot_diagnostics.json','Location and quality context only; do not replace failed peak comparisons with quantiles')])
with (O/'test_scope_register.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['test','status','evidence','limit_or_next_input']);w.writerows(checks)
p=O/'README.md';t=p.read_text();t+='\n## Final review on 24 October\n\nSix of eight finer sampled-peak comparisons pass. The adult fork still changes 27.52 percent outward and 28.31 percent inward, so the peak-stress check remains failed. All four displacement comparisons change less than 0.63 percent and pass separately; final force-balance errors are below 7e-10 N. These do not erase the peak failure. Hotspot locations, curved-element condition numbers, energy and volume-weighted quantiles are recorded in hotspot_diagnostics.json. Quantiles are diagnostic context, never substitute pass criteria. Proximity to a nominal contact boundary does not prove a singularity.\n\nAll six sizes have a smaller carrying pose. Each search ranked 625 candidate angle pairs, rejected actual collisions, and stopped at the first passing endpoint and left-first path sampled every 2.5 degrees. Six pose-only STEP exports reimport as 42 solids with matching volume. Part shapes are unchanged. The 12 canonical joint-part comparisons within the adult/child families pass; this does not transfer whole-headset worn loads. The older heat proxy matched its analytic equation in 216 rows, but 155 assumed moisture rows saturated. This is no cooling-performance validation.\n\nThe finite V21 review is complete. All possible software testing is not complete. Remaining software work includes the adult fork peak prediction, detailed fastener/contact and manufactured geometry, actual material curves, full worn contact, calibrated acoustics and thermal models, and exact Sony mounting geometry. These need defined inputs; arbitrary extra simulated cases would not establish real performance. Both products remain development concepts, not manufacturing-ready or proven beneficial.\n\nAccepted reproduction sources include v21_anderson_matrix.py (mixed child source archived in solver-sources), v21_matrix_review.py, v21_hotspot_diagnostics.py, v21_family_equivalence.py, v21_compact_pose.py and run_v21_compact.py. Replaying equilibrium and geometry searches can take hours. Read solver_experiments.json for stopped and rejected attempts.\n';p.write_text(t,encoding='utf-8')
