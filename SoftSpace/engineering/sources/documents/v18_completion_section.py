import json
def add_completion(d,P,new_page,para,table,picture,is_glasses):
 O=P/'engineering-v18-results';f=O/'fork_mechanics_summary.json'
 if not f.exists():return
 s=json.loads(f.read_text());register=json.loads((O/'test_register.json').read_text());new_page(d,'V18 Final component checks')
 para(d,'The fork between the cup and folding hinge now has its own component test. This adds evidence for a part that was missing from the earlier V18 fixtures. It does not replace the complete joint, worn fit or acoustic tests.')
 picture(d,'V18_fork_fixtures','Actual saved finite element boundaries. Colours show adjacent element centroid stress on the undeformed fork; they are not measured surface stress.',5.8)
 rows=[]
 for r in s['cases']:
  m=r['meshes'][-1];rows.append([r['size'].replace('_',' '),f"{m['cup_weighted_x_displacement_mm']:.4f}",f"{m['max_von_mises_centroid_MPa']:.2f}",f"{100*r['sampled_stress_change_fraction']:.2f}%",'Pass' if r['chosen_5percent_mesh_comparison_pass'] else 'Not passed'])
 table(d,['Fork fixture','Cup movement mm','Sampled stress MPa','Last stress change','Chosen mesh gate'],rows,[1.7,1.3,1.5,1.3,1.1])
 para(d,'The two pivot bore surfaces are fully fixed. A uniform total force of 2 N acts along X on the two cup pin bores. Downward forces of about 4.8 N in the child fixture and 5.4 N in the adult fixture act over the two stop patches. These loads balance the moment around the folding axis. They are a different load case from the earlier 13 N tongue stop fixture and must not be combined as if they solved one assembly.')
 para(d,'The material is still assumed: elastic modulus 2000 MPa and Poisson ratio 0.35. Straight sided quadratic tetrahedra approximate the curved surfaces. Actual bearing pressure, bolt preload, washer friction, guide flexibility and stop contact are not solved. Numerical support reactions are not real pressure measurements.')
 new_page(d,'V18 Testing decision and remaining inputs')
 total=register['solver_array_audits_total'];para(d,'The current V18 component assessment is recorded. There are now '+str(total)+' saved solver array audits across the band, tongue stop and fork fixtures. Source hashes, work and energy, force balance, fixed displacements, finite values, residuals and positive elements were checked. A mesh comparison pass means that selected calculated outputs changed by less than our chosen limit. It does not mean that a real product passed a strength or comfort test.')
 if any(len(r['meshes'])>2 for r in s['cases']):para(d,'The first child fork stress comparison exceeded the chosen 5 percent limit. A finer mesh was added and the final comparison is reported above. The earlier result remains in the evidence. Refinement was used to check this particular output, not to certify every local stress or remove the need for a physical test.')
 table(d,['Work still needed','Input or test needed','Status'],[[r['workstream'],r['prerequisite'],r['status']] for r in register['remaining_product_validation']],[1.7,3.9,1.3])
 para(d,'The next useful step is a measured bench prototype, followed by corrected material models and assembled tests. We cannot honestly mark sound reduction, leakage, comfort, heat, fatigue or sensory acceptance as passed using the current unknown properties. Complete joint contact and manufacturing details also remain open. This is not a finished or released product.')
 if is_glasses:para(d,'The Sony WH CH720N pad still needs the original mounting dimensions, which the user will measure later. The fork results concern the separate defender. They do not add a model specific fit, glasses pressure, ANC or leakage result.')
 else:para(d,'Both reports share this decision. The separate Sony WH CH720N cushion remains a generic candidate until the original pad and mount are measured. No acoustic or comfort advantage over market products has been demonstrated.')
