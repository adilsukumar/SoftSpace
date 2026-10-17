import json

def add_v15(d,P,new_page,para,table,picture,link,is_glasses):
 O=P/'engineering-v15-results';f=O/'adult_small_retention_cad.json'
 if not f.exists():return
 r=json.loads(f.read_text());audit=O/'adult_small_retention_audit.json';a=json.loads(audit.read_text()) if audit.exists() else None
 new_page(d,'V15 Knob retention experiment')
 para(d,'V15 is one adult small retention pilot. It adds an intended M2 threaded metal knob and a separate hex jam nut to the V14 release stem. The earlier knob only had an unretained matching bore. Countertightening the nut against the knob gives us a defined retention method to develop. It has not passed pullout, loosening, repeated release or child access tests.')
 para(d,'The knob is 8 mm across and 4 mm long. Its intended thread allocation is 3 mm, with a 1 mm rear counterbore. The separate nut is 4 mm across flats and 1.6 mm long. The male thread envelope is 6 mm long. The nominal nut to shoulder and shoulder to cap gaps are each 0.4 mm. These are design dimensions, not measured manufacturing tolerances.')
 if (P/'documents/images/V15_retention_section.png').exists():picture(d,'V15_retention_section','Exact section of the adult small pilot. The coloured outlines come from saved STEP geometry. Thread helices and flank contact are not modelled.',6.2)
 if a:
  para(d,f"The saved pilot contains {a['solid_count']} solids. Its {a['case_count']} recorded release and slider endpoint checks "+('passed.' if a['all_pass'] else 'include failures.')+' These check geometric clearance outside the cosmetic thread allocations. They do not prove threaded engagement or a safe complete mechanism. No V15 six size motion pass or folding pass is inferred from them.')
 para(d,'The intended thread is M2 with 0.4 mm pitch, using proposed 6g external and 6H internal tolerances. A Bossard technical guide lists these general tolerance fields and the M2 dimensions. A supplier drawing, thread runout, gauges, coating, final material grade, real wrench access and a controlled tightening process are still required. The smooth thread envelopes in the STEP file cannot replace these details.')
 link(d,'Bossard metric thread dimensions and tolerances','https://www.bossard.com/au-en/knowledge-hub/resources/technical-information/metric-iso-threads/')
 if is_glasses:
  para(d,'This retention experiment belongs to the standalone ear defender. The Sony WH CH720N replacement cushion is unchanged. Its original mounting dimensions remain deferred by the user; fit, retention, pressure, incoming noise, outgoing music and ANC effects remain untested. The separate pad product does not inherit a benefit from this knob change.')
  new_page(d,'V15 Shared packing and retention limits')
 else:new_page(d,'V15 Child packing search')
 searches=sorted([json.loads(p.read_text()) for p in O.glob('child_*_packing_search.json')],key=lambda r:['child_small','child_medium','child_large'].index(r['size']))
 if searches:
  review_file=O/'packing_review.json';review=json.loads(review_file.read_text()) if review_file.exists() else None
  rows=[]
  for s in searches:
   b=next((r for r in review['sizes'] if r['size']==s['size']),None) if review else None
   change='Review pending' if b is None else f"{abs(b['change_from_retracted_unfolded_percent']):.2f} percent "+('larger' if b['change_from_retracted_unfolded_percent']>=0 else 'smaller')
   rows.append([s['size'].replace('_',' '),str(s['ranked_pose_count']),str(len(s['shortlisted_pose_checks'])),change])
  table(d,['Size','Boxes ranked','Endpoints checked','Best recorded fold against retracted unfolded'],rows,[1.5,1.1,1.3,3.0])
  para(d,'This search moves the existing V14 parts; it does not create a new child headband. It ranks 30 625 combinations per size using two slider positions from 0 to 30 mm and two cup angles from 0 to 120 degrees. Only a finite shortlist gets actual solid intersection checks. We stop at the first clear endpoint in that shortlist. Ranking boxes is not a collision pass or a proof of the best possible fold.')
  para(d,'We compare the first clear new endpoint with the already checked V14 folded endpoint and keep the smaller recorded box. A worse new endpoint is rejected. The fully retracted unfolded baseline is included so that retracting the sliders cannot be presented as a folding benefit. These endpoint checks do not prove a new path to the pose. The original V14 sampled path evidence remains separate. The selected child packing goal is still unresolved.')
  if (P/'documents/images/V15_child_packing.png').exists():picture(d,'V15_child_packing','Source matched V14 clear endpoints are retained when the new search endpoint is worse. Positive bars mean more box volume than simply retracting the headset.',6.2)
  para(d,'The fold search holds both release pins 6 mm back, as in the earlier V14 motion study. It does not show that a real spring would hold that state after we let go, or that the cups latch safely for storage. A stable released or folded storage mechanism remains a design task. A clear displayed fold is not yet a usable carrying mode.')
 path=O/'child_large_path_audit.json'
 if path.exists():
  p=json.loads(path.read_text())
  if not is_glasses:new_page(d,'V15 Child large folding sequence')
  para(d,f"The improved child large endpoint has {p['case_count']} recorded adjustment, release and folding samples. The complete sampled sequence "+('passed.' if p['new_complete_sampled_path_pass'] else 'did not pass.')+' With the headband fixed, the left slider goes to 0 mm and the right to 20 mm. Both release pins are held 6 mm back. The left cup turns 30 degrees first, then the right turns 60 degrees. This order is part of the checked sequence.')
  para(d,'The exported box is about 247.0 by 81.6 by 171.1 mm. It is 5.24 percent smaller in volume than the nominal 15 mm slider pose and 3.93 percent smaller than the fully retracted unfolded pose. This is a modest geometric improvement for child large. Child small and medium still have no useful recorded improvement. The stable storage, pinch, physical handling and durability limits remain open.')
  verification=O/'STEP_verification.json'
  if verification.exists():
   v=json.loads(verification.read_text());para(d,f"The {v['case_count']} new STEP reimports "+('passed' if v['all_pass'] else 'include failures')+' solid count, validity and volume checks. The improved child large export also matched the intended box dimensions. These checks cover storage of the geometry, not a physical product.')
  if not is_glasses and (P/'documents/images/V15_child_large_fold.png').exists():picture(d,'V15_child_large_fold','The same V14 child large surfaces before and after the newly checked rigid transforms. Equal display scale. The right picture holds the release pins back.',6.2)
 loads=O/'retention_load_screen.json'
 if is_glasses:new_page(d,'V15 Remaining retention and product tests')
 if loads.exists():
  s=json.loads(loads.read_text());required=[r['required_yield_for_factor_two_MPa'] for r in s['cases']]
  para(d,f"The retention screen calculates {s['case_count']} assumed combinations of root diameter, tightening torque, nut factor and external pull. A simple solid rod model gives required yield strengths from {min(required):.1f} to {max(required):.1f} MPa for a chosen factor of two. This range is not an approved torque, material selection or thread strength rating. Thread stripping, real flank contact, stress concentration, actual jam nut load sharing, fatigue and loosening are excluded.")
 para(d,'The new knob projects farther behind the cap and adds two separate small nuts to the headset. These changes can increase bulk and complicate assembly. The V14 folding results cannot be transferred to V15 without checking the new geometry. Child access to loose parts and pinch points remains open. We have not selected this retention pilot as a final product design.')
 para(d,'At the V15 stage, V14 was the latest six size CAD candidate and V15 was a local STEP experiment for one size. The later V16 section records the next changes. Native editable Fusion archives remain V10. Real material data, complete joint analysis and physical comfort, acoustic and durability work are still needed.')
