import json,hashlib,math
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v12-results'
cad=json.loads((O/'cad_report.json').read_text());motion=json.loads((O/'ocp_motion_audit.json').read_text());step=json.loads((O/'STEP_verification.json').read_text());fork=json.loads((O/'fork_mechanics_summary.json').read_text());spring=json.loads((O/'pin_spring_screen.json').read_text());band=json.loads((O/'band_sizes_summary.json').read_text());controls=json.loads((O/'kernel_controls.json').read_text())
assert motion['all_pass'] and motion['case_count']==216 and step['all_pass'] and step['case_count']==18 and controls['all_pass']
for r in step['cases']:assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
checks=[]
for c in band['cases']:
 for r in c['meshes']:
  assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256'];work=r['ideal_load_per_full_side_N']*r['guide_weighted_x_displacement_mm'];err=abs(work-2*r['strain_energy_Nmm'])/abs(work);balance=math.sqrt(sum(v*v for v in [r['reaction_sum_N'][0]+2,*r['reaction_sum_N'][1:]]));passed=err<1e-6 and balance<1e-6 and r['relative_free_residual']<1e-6 and r['minimum_adaptive_Jacobian_mm3']>0
  checks.append({'size':c['size'],'mesh_max_mm':r['mesh_max_mm'],'source_sha256':r['source_sha256'],'work_energy_relative_error':err,'reaction_balance_error_N':balance,'pass':passed})
assert all(c['pass'] for c in checks)
out={'updated':'2026-10-14','revision':'V12 local STEP candidate','native_Fusion_revision':'V10','product_validation_complete':False,'tests':[
 {'test':'Six-size CAD export','status':'Pass recorded geometry checks','result':'18 local STEP files,32 positive-volume solids each including spring-space envelopes'},
 {'test':'Independent rigid motion','status':'Pass sampled checks','result':'216 poses;42 adjustment,24 release,150 folding; not continuous loaded motion'},
 {'test':'Collision-query controls','status':'18 known embedded/disjoint cases pass','result':'Coincident fork copy/equivalence comparisons still fail and are not accepted as a geometry-transfer proof'},
 {'test':'Wider guide tolerance arithmetic','status':'Positive under one assumed error budget','result':'0.6mm nominal minus0.4mm relative closure leaves0.2mm; not factory validation'},
 {'test':'Band stiffness and sampled stress mesh comparison','status':'Pass' if band['all_chosen_mesh_comparisons_pass'] else 'Some comparisons fail','result':'Six V12 ideal fixtures,with earlier failed coarse stress comparisons retained'},
 {'test':'Band numerical algebra checks','status':'Pass','result':str(len(checks))+' saved meshes; residual,work energy,reaction balance,source identity and positive Jacobians'},
 {'test':'Fork calculations','status':'Two examples pass chosen mesh and algebra checks','result':'Four quadratic FE solves; ideal fixed pivot-bore fixture; not full joint contact'},
 {'test':'Fork material and load screen','status':'80 conditional cases complete','result':'Adult20N fixture stress about132MPa exceeds all8 listed plastic typical yield references'},
 {'test':'Pin and spring calculations','status':'Conditional equations complete','result':'36 pin and162 spring cases; no fatigue,set,friction or reliable-return pass'},
 {'test':'Latch manufacturing assembly','status':'Unfinished design','result':'Integral housing needs a specified assembly/service route,retained cap/head and fastening design'},
 {'test':'Complete joint and worn contact','status':'Unvalidated','result':'Final fasteners,torque,friction,actual foam,cover,heads and glasses inputs required'},
 {'test':'Physical durability comfort and acoustics','status':'Not performed','result':'No prototype,fall,fold-cycle,ageing,wearer,real isolation or outgoing-music test'},
 {'test':'Sony WH CH720N replacement fit','status':'Measurements deferred by user','result':'Generic pad remains unchanged and not claimed compatible'},
 {'test':'Price manufacturing and market superiority','status':'Not demonstrated','result':'No production quotes,tolerance capability or matched physical competitor test'}],
 'band_mesh_algebra_audits':checks,'evidence_sha256':{name:hashlib.sha256((O/name).read_bytes()).hexdigest() for name in ['cad_report.json','ocp_motion_audit.json','STEP_verification.json','kernel_controls.json','fork_mechanics_summary.json','pin_spring_screen.json','band_sizes_summary.json']}}
(O/'test_register.json').write_text(json.dumps(out,indent=2))
note='''# V12 status and retained failures

This is an engineering candidate, not a manufacturing release or finished product.

The integral latch housing and captive collared pin need a specified assembly and servicing process. A removable retained cap/head or split housing must be designed and rechecked. The spring is only an allocated envelope, not a final actual coil. Final screws, torque, friction, stops, wear and pinch access are not qualified.

The first STEP-part matching bounds were too strict for loose BSpline bounding boxes; the recorded drift is an identification issue, not a clearance acceptance tolerance. The first released envelopes used anisotropic dilation and failed expected volume conservation by about0.994mm3 per assembly. Exact cylindrical reconstruction replaces those envelopes. Initial files remain in initial-dilation-exports.

Coincident independent imports and deep geometric copies of forks gave empty common volumes. The originals passed validity and self-common checks; known embedded/disjoint cubes, including rotated pairs, passed18 controls. The final216-pose audit uses located original OCP shapes. No fork family-equivalence pass is claimed from the failed coincident comparison. The earlier interrupted gmsh motion batch is preliminary and is superseded by the recorded independent audit.

Coarse band stress comparisons that exceeded5percent are retained before refinement. A final stable pair does not bound continuum corner stress or qualify manufactured strength. The two fork fixtures are ideal component examples, not complete joints. At20N illustrative adult side load, their linearly scaled sampled stress exceeds the typical yield references of all8 listed plastics. Pin and spring static reference ratios do not prove fatigue life, return reliability or drop resistance.

Physical comfort, sensory acceptance, acoustics, ageing and durability require measured materials and samples. The Sony pad mount dimensions remain deferred. No universal preference, zero leakage, unbreakable, lowest-price, absent-Indian-competition or market-superiority claim is established. Native Fusion files remain V10; V12 files are local STEP candidates.
'''
(O/'REVIEW.md').write_text(note)
doc=P/'documents'/'document_status.json'
if doc.exists():
 s=json.loads(doc.read_text());s['latest_study']={'revision':'V12','native_Fusion_revision':'V10','STEP_files':18,'rigid_motion_samples':216,'band_fixtures':6,'fork_fixture_examples':2,'pin_cases':36,'spring_cases':162,'fork_grade_load_cases':80,'manufacturing_release':False,'physical_validation_complete':False};doc.write_text(json.dumps(s,indent=2))
print(json.dumps({'STEP_files':18,'motion_samples':216,'band_mesh_audits':len(checks),'all_recorded_band_algebra_pass':True,'manufacturing_release':False}))
