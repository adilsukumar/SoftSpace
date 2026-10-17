import json
def add_v17(d,P,new_page,para,table,picture,is_glasses,link=None):
 O=P/'engineering-v17-results';f=O/'test_register.json'
 if not f.exists():return
 s=json.loads(f.read_text());new_page(d,'V17 Pin entry trials')
 para(d,'Project status: V17 two size entry pilots with V16 six size candidates and V10 native archives.')
 para(d,'V16 exposed a small clearance budget at the locking index. V17 changes only the child large and adult small pilots. Their index holes grow from 2.3 to 2.5 mm. A 0.3 mm entry cone opens to 3.1 mm at the rear face. The straight bearing land becomes 2.7 mm long instead of 3 mm. The pin, cap, housing and spring space are unchanged.')
 rows=[]
 c=json.loads((O/'entry_option_comparison.json').read_text())
 for r in c['cases']:
  if r['layout']=='Child lower':
   a=next(x for x in c['cases'] if x['layout']=='Adult upper' and x['hole_diameter_mm']==r['hole_diameter_mm']);rows.append([str(r['hole_diameter_mm']),f"{r['nominal_radial_clearance_mm']:.3f}",f"{r['nominal_one_sided_index_rotation_deg']:.3f} / {a['nominal_one_sided_index_rotation_deg']:.3f}",f"{r['illustrative_remaining_margin_mm']:.4f} / {a['illustrative_remaining_margin_mm']:.4f}"])
 table(d,['Hole mm','Radial clearance mm','Child and adult play each way in degrees','Child and adult remaining margin mm'],rows,[.8,1.3,2.3,2.5])
 para(d,'The comparison assumes opposite diameter errors of 0.025 mm on each part, a relative centre error of 0.1 mm and an angular error of 0.1 degrees, aligned unfavourably. These are chosen comparison inputs, not supplier capability or approved requirements. The 2.5 mm option is the smallest of the four tested diameters with positive margin in both layouts. Its remaining margin is only about 0.0055 and 0.0041 mm. It is an experiment, not an optimised final size.')
 picture(d,'V17_entry_sections','Actual sections through the wearing pin axes. The picture shows the local entry and straight land, not spring centering or a measured return force.',5.5)
 new_page(d,'V17 Recorded geometry and component checks')
 table(d,['Pilot','Sequence samples','Valid solids'],[[r['size'].replace('_',' '),str(r['motion_samples']),str(r['valid_solids'])] for r in s['pilots']],[2.5,2.2,2.2])
 para(d,f"The two pilots passed {s['motion_samples']} sampled adjustment, release, folding and pin-return poses. The records also include {s['index_blocking_queries']} attempted index rotations and {s['retention_blocking_queries']} retention escape queries, which produced the intended geometric blocking. Both saved STEP files passed independent reimport and per-part volume checks. This is not a continuous motion, assembly-force or durability pass.")
 e=s['entry_queries'];para(d,f"The {e['case_count']} local entry queries agree with the intended geometry. A fully inserted pin with 0.14 mm sideways offset stays clear, while 0.16 mm causes interference. An offset tip can enter the wide mouth but then collide deeper in the cone or straight land. The chamfer does not by itself make a misaligned pin seat.")
 if s.get('mechanics'):
  rows=[]
  for m in s['mechanics']:
   r=m['meshes'][-1];rows.append([m['size'].replace('_',' '),f"{r['weighted_load_direction_displacement_mm']:.4f}",f"{r['max_von_mises_centroid_MPa']:.2f}",'Pass' if m['mesh_comparison_pass'] else 'Not passed'])
  table(d,['Separate tongue fixture','Fine displacement mm','Fine sampled stress MPa','Mesh comparison'],rows,[2.0,1.6,1.7,1.6])
  para(d,'These are separate ideal component fixtures. Each stem is truncated and fixed at z 82 mm, with assumed modulus 2000 MPa and Poisson ratio 0.35. The assumed folded-hole load is 11.63 N for child large and 10.83 N for adult small. It acts only on the straight hole land. Straight-sided quadratic tetrahedra approximate curved surfaces with facets. The entry cone has no centering force or friction model. Mesh comparison and saved-array checks do not qualify the complete joint or actual material.')
 para(d,'The wider hole triples the nominal radial clearance but also triples the index contribution to rotational play. The shorter straight land reduces the area available for bearing. The unchanged housing and cap still guide the stem through smaller clearances, and their alignment remains a separate constraint. We have not established real spring return, tolerance capability, wear, contamination resistance, pinch clearance or child access.')
 para(d,'V17 has two local STEP pilots only. V16 remains the latest six size CAD candidate and native Fusion archives remain V10. Previous whole-headset and material screens do not automatically transfer to the changed plates. Physical sound reduction, wearer comfort, sensory acceptance, durability and cost remain unvalidated.')
 if is_glasses:para(d,'The Sony WH CH720N replacement cushion is unchanged. These pin-entry trials concern the separate standalone defender. Sony mounting measurements and actual fit, seal, pressure, leakage and ANC comparisons remain outstanding.')
 if (O/'digital_closeout.json').exists():
  contact=json.loads((O/'pin_contact_and_return.json').read_text());spring=json.loads((O/'spring_design_tradeoff.json').read_text())
  new_page(d,'V17 Loaded pin contact and spring return')
  para(d,'The latch is on hold for production. Unloaded geometry and component mesh passes do not establish reliable pin return when the joint carries a sideways load. The new calculation bends a 2.2 mm pin against two guides with a gap and elastic wall contact. It is a one plane beam model, not full three dimensional joint contact.')
  para(d,'The guide surfaces were extracted from both saved pilot solids. In common local coordinates, the rear guide runs from y minus 32 to minus 21 mm, and the front guide from minus 12.999 to minus 10 mm. The folded hole load acts at y minus 6.35 mm. The assumed elastic modulus is 193000 MPa. Guide stiffness, clearance and external load are varied; their actual manufactured values are not known.')
  para(d,'Ninety contact cases passed their force and moment balance checks. Controls include an exact overhanging beam example, reversed loading and three meshes for each layout. The selected mesh comparisons pass the chosen 5 percent limit. An initial mesh created a very short near duplicate interval and poor conditioning; accepted results use a corrected mesh split at each geometric boundary.')
  picture(d,'V17_contact_return','Reduced static contact and assumed Coulomb drag. The plot is a diagnostic calculation, not a measured return force or physical joint rating.',5.8)
  normal=spring['comparison_contact_normal_sum_N'];pre=contact['spring_reference']['wear_preload_N']
  table(d,['Chosen comparison at 2 N side load','Force N'],[['Earlier illustrative spring preload',f'{pre:.3f}'],['Guide drag at friction 0.1 plus other drag 0.1 N',f'{.1*normal+.1:.3f}'],['Guide drag at friction 0.3 plus other drag 0.1 N',f'{.3*normal+.1:.3f}']],[4.9,2.0])
  para(d,'The 1080 drag and preload comparisons have 180 positive assumed margins. That count is not a probability or a predicted factory yield. Sliding drag is estimated from static guide reactions; no actual withdrawal or return path, surface pressure, collar, cross hole or chamfer centering is solved. The result identifies a risk to measure, not a proven failure in a real product.')
  new_page(d,'V17 Spring trade offs and completion decision')
  para(d,'The 300 alternative spring designs vary wire diameter, coil diameter, active turns and free length. The screen also includes assumed dimensional errors, a 10 percent rate range, 1.5 mm permanent length loss, a 0.5 mm reserve above solid height and an approximate coil diameter increase. Typical 301 full hard wire data are a reference, not a manufactured spring allowable.')
  if link:
   link(d,'Ulbrich 301 wire reference data',spring['sources'][0]);link(d,'Lee Spring design considerations',spring['sources'][1])
  para(d,'Sixteen designs meet the chosen envelope, static reference, return and pull criteria with zero guide friction. None meets them all at assumed guide friction of 0.1, 0.3 or 0.6 under the 2 N side load comparison. The 3 N pull limit is an illustrative engineering choice; it has not been approved by autistic users or established as a comfort or dexterity threshold. This finite search does not prove that every possible spring or latch architecture fails.')
  para(d,'The spring CAD is still a space reservation. No actual coil ends, spring seating, lateral stability, fatigue or manufacturing process has been qualified. A coupled three dimensional joint analysis needs credible materials, friction, support stiffness, fasteners, torque and load requirements. Additional arbitrary simulations cannot establish those missing inputs.')
  table(d,['Workstream','Current status','Evidence still needed'],[
   ['Six size geometry','V16 sampled checks pass','V17 is two pilots only; native Fusion remains V10'],
   ['V17 component and reduced contact models','Chosen numerical checks pass','Complete joint and actual material correlation'],
   ['Loaded spring return','Production hold','Measured pull, return, drag, spring rate and set'],
   ['Headband and full worn fit','Conditional studies only','Actual clamp force, heads and contact materials'],
   ['Foam cover and glasses zone','Reference screens only','Compression recovery, stretch, friction and actual frames'],
   ['Sound reduction and outgoing leakage','No physical pass','Matched acoustic tests with repeated seating'],
   ['Comfort heat and sensory acceptance','No physical pass','Voluntary feedback and climate measurements'],
   ['Drop cycles cleaning and ageing','Not performed','Actual assembled samples and reviewed test loads'],
   ['Sony WH CH720N fit','Measurements deferred','Original mounting dimensions and host comparisons'],
   ['Manufacturing and final price','Not released','Process capability, assembly proof and supplier quotes']],[2.0,1.7,3.2])
  para(d,'The package includes a 28 workstream completion matrix and blank measurement records. The recorded assessment is complete; the whole product is not. The next step is to measure pin return and guide drag with actual parts, then decide whether to change the spring, guide or latch architecture. Material calibration and Sony mounting measurements must precede model specific and physical performance claims.')
  if is_glasses:para(d,'The production hold above concerns the standalone latch. The replacement cushion remains a separate candidate and still needs Sony mounting measurements, calibrated pad materials and physical fit and acoustic tests.')
