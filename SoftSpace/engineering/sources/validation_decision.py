"""Evidence-based validation decision. No new simulations or changed acceptance limits."""
from pathlib import Path
import json,csv,hashlib
P=Path(__file__).resolve().parent;O=P/'validation-decision';O.mkdir(exist_ok=True)
read=lambda p:json.loads((P/p).read_text(encoding='utf-8-sig'))
r=read('engineering-v26-results/review_status.json');f=read('engineering-v20-results/design_parameters.json');m=read('engineering-v26-results/relieved/local_motion_audit.json')
assert not r['all_product_software_testing_complete'] and not f['measured_Sony_dimensions']
assert r['variant_A']['mesh_passes']==2 and len(r['variant_A']['folding_failures'])==2 and r['variant_B']['accepted_fields']==0
assert len(m['folding_samples'])==25 and m['sampled_local_motion_pass'] and m['stop_blocking_pass']
for case in r['cases']:
 path=P/'engineering-v26-results'/f"{case['size']}_h{case['mesh_size_mm']}_{case['direction']}.npz"
 assert hashlib.sha256(path.read_bytes()).hexdigest()==case['raw_sha256']
for variant in ['', 'relieved/']:
 c=read('engineering-v26-results/'+variant+'child_large_candidate_cad.json');assert hashlib.sha256(Path(c['file']).read_bytes()).hexdigest()==c['sha256']
gates=[
 ['S1','SoftSpace','Whole joint strength','UNRESOLVED','A tongue mesh checks fail; B has no accepted equilibrium field','A complete motion compatible joint and reliable solved fields','Retain the existing numerical checks; qualify actual loads and hardware','engineering-v26-results/review_status.json'],
 ['S2','SoftSpace','Full assembly folding and fit','NOT VERIFIED FOR NEW CANDIDATE','B passes 25 local rigid positions only; main headset unchanged','Integrate accepted parts in six assemblies with tolerances','Local finite samples are not continuous loaded assembly qualification','engineering-v26-results/relieved/local_motion_audit.json'],
 ['B1','Both','Foam and cover contact','INPUT AND MODEL GAP','Reduced assumption based screens and manufacturer points only','Selected grade compression loading and unloading curves cover tension seams friction and head geometry','Define acceptable pressure fit and compression range before prediction','engineering-v25-results/manufacturer_input_review.json'],
 ['F1','SoftSpace Flex','Sony pad mounting','DIMENSION GAP','Published pad envelope; assumed opening; no exact mount verification','Traceable groove skirt carrier geometry and tolerances from drawing supplier or reference part','Fit retention and seal checks on the actual mounting design','engineering-v20-results/design_parameters.json'],
 ['B2','Both','Sound reduction leakage and sound changes','NOT VALIDATED','No calibrated complete product acoustic result','Finished seal geometry and appropriate frequency dependent material and host inputs','Define attenuation leakage and host sound criteria before simulation','engineering-v26-results/remaining_test_register.csv'],
 ['B3','Both','Heat and moisture','NOT VALIDATED','Earlier reduced assumed scenarios do not qualify the product','Selected material thermal moisture properties and defined environment','Define acceptable temperature and humidity behaviour before prediction','engineering-v26-results/remaining_test_register.csv'],
 ['B4','Both','Durability drop creep fatigue cleaning','NOT VALIDATED','No calibrated complete assembly qualification','Final materials joints tolerances load history aging and cleaning exposure','Define lifetime misuse and cleaning requirements and then verify','engineering-v26-results/remaining_test_register.csv'],
 ['B5','Both','Wearer comfort and sensory acceptance','REQUIRES PEOPLE','No wearer evidence','Voluntary representative wearer evaluation including autistic participants','Software can screen designs but cannot establish personal sensory acceptance','AGENTS.md']]
with (O/'requirements.csv').open('w',newline='',encoding='utf-8') as fp:
 w=csv.writer(fp);w.writerow(['ID','Route','Requirement','Status','Existing evidence','Required inputs or design','Acceptance requirement','Evidence file']);w.writerows(gates)
evidence=['engineering-v26-results/review_status.json','engineering-v26-results/stress_comparisons.csv','engineering-v26-results/local_motion_audit.json','engineering-v26-results/relieved/local_motion_audit.json','engineering-v26-results/stronger_resource_stop.json','engineering-v20-results/design_parameters.json','engineering-v20-results/phase_status.json','engineering-v25-results/manufacturer_input_review.json','engineering-v24-results/relocation_source_audit.json']
index=[dict(path=p,sha256=hashlib.sha256((P/p).read_bytes()).hexdigest(),bytes=(P/p).stat().st_size) for p in evidence]
decision=dict(date='2026-10-25',review_complete=True,all_software_testing_complete=False,software_validation_passed=False,manufacturing_release=False,SoftSpace='NOT APPROVED unresolved joint strength and full product models',SoftSpace_Flex='NOT APPROVED unverified Sony mounting and full product models',accepted_V26_equilibrium_fields=2,accepted_V26B_equilibrium_fields=0,local_V26B_motion_samples=25,credit_control='No new physical-model sweeps or solver retries in this review; saved evidence reused',scope='Completed evidence assessment, not completion of missing tests, a product pass, or proof of physical safety.',evidence=index)
(O/'decision.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
(O/'README.md').write_text('''# Software validation decision

Review date: 25 October 2026. Both designs are NOT APPROVED for manufacturing release. The evidence assessment is complete; all software testing is not complete and neither product has passed full validation.

SoftSpace has unresolved joint stress prediction and no accepted strength field for the motion-corrected V26B candidate. Its 25 passing local motion samples do not establish complete headset folding. SoftSpace Flex still lacks verified Sony mounting geometry; published outside pad dimensions do not define the skirt and groove. Both routes lack complete qualified contact, acoustic, heat and durability models and inputs. Wearer acceptance needs people.

requirements.csv identifies the exact evidence, missing inputs or design, and acceptance requirement for every open gate. decision.json hashes the reviewed evidence. Earlier passing mathematical checks and failed experiments remain intact. Missing properties, mounting dimensions and acceptance criteria cannot be inferred by repeating the same assumed simulations. Testing every imaginable material or every market headphone is not a finite validation requirement; specific grades, supported models and operating conditions must be defined.

No new simulation campaign was run for this review, and no test limit was relaxed. Further computation should be tied to one changed design, newly qualified input or specific failed requirement. A completed review is not a substitute for the missing work. No comfort, no-leakage, acoustic performance, compatibility or durability claim is released.
''',encoding='utf-8')
print({k:decision[k] for k in ['review_complete','all_software_testing_complete','software_validation_passed','manufacturing_release']})
