"""Shared update: retain failures and avoid an all-software-complete claim."""
import json
def add_v21(d,P,new_page,para,table,picture):
 O=P/'engineering-v21-results'
 if not (O/'review_status.json').exists():return
 r=json.loads((O/'review_status.json').read_text());c=json.loads((O/'contact_envelope.json').read_text());s=json.loads((O/'interior_stress_recovery.json').read_text())
 new_page(d,'V21 Additional software review')
 para(d,'24 October 2026 review of calculations from 23 and 24 October. The added checks found useful passes and important failures. All possible software work is not finished. The first joint peak-stress comparisons failed; the following pages record the finer-mesh investigation and its exact scope. Material, mounting and whole-product performance remain unverified.')
 para(d,'Part shapes remain SoftSpace V19 and SoftSpace Flex V20; V21 adds carrying pose STEP exports. We added '+str(r['motion']['additional_samples'])+' rigid motion samples across all six headset sizes. These include folding positions between the old 5 degree steps, unequal left and right slider positions, and selected simultaneous folding positions. The checks use the saved final STEP files and record their hashes.')
 table(d,['Size','Folded box volume compared with wear box'],[[name.replace('_',' '),format(100*ratio,'.1f')+' percent'] for name,ratio in r['motion']['bounding_ratios'].items()],[2.2,4.7])
 para(d,'All the added recommended-path samples and simultaneous-fold diagnostics passed the existing interference gate. A smaller bounding box is useful for carrying, but this does not test a travel bag, fingers near a hinge, friction, loaded deformation or continuous motion between samples.')
 para(d,'The test register now separates completed finite checks, failed numerical comparisons, missing measurements and tests that need people. A large number of calculations is not a probability that either product will work.')
 new_page(d,'V21 Glasses positions change the result')
 para(d,'The exact-area calculation checked all 11,664 old cushion rows. 334 differed by more than the chosen 1 percent comparison, with a maximum difference of 3.35 percent. The earlier 12 selected comparisons were correct, but they did not establish accuracy for every row. The old results remain saved; the new position screen uses exact elliptical areas.')
 picture(d,'V21_position_screen','Calculated pressure changes across a wider assumed arm-height range. These are foam-column calculations, not measured pressure or comfort.',6.55)
 table(d,['Zone height','Eligible cases with local pressure increase','Largest local increase'],[[str(z)+' mm',str(v['local_increases']),format(v['max_local_increase_percent'],'.2f')+' percent'] for z,v in c['zone_results'].items()],[1.25,3.9,1.75])
 para(d,'The study has 126,360 cases. Glasses-arm centres range from 10 mm below to 40 mm above pad centre, at 2 mm steps. All values are assumptions, not a distribution of real users. Cases above the chosen 40 percent compression cutoff are flagged. A separately written integration and scalar root checked 127 selected rows successfully.')
 para(d,'A 100 mm tall computational zone avoided the local increase in the eligible cases, but 780 cases increased peak pressure elsewhere and four showed model detachment. There is no final winner. This taller zone is a numerical alternative only; the three V20 STEP bodies are unchanged. Model detachment does not directly predict sound leakage.')
 new_page(d,'V21 The first joint stress comparison failed')
 para(d,'We recovered stresses at 27 interior points in each element of eight saved joint solutions. The old centre-point values were reproduced. Peak stress changed substantially between the two existing meshes. All eight comparisons exceeded our chosen 5 percent check. This is a failed numerical refinement check, not evidence that an actual part broke.')
 table(d,['Load and size','Part','Peak change between meshes'],[[('Outward' if x['direction']=='quadratic-contact' else 'Inward')+' '+x['size'].replace('_',' '),x['component'],format(x['change_percent'],'.1f')+' percent'] for x in s['mesh_comparisons']],[3.3,1.3,2.3])
 para(d,'The earlier stable displacement checks remain true. They cannot be used as evidence for stable peak stress. These failures triggered a finer-mesh investigation. Neither a material-strength margin nor fatigue life is established. Averaging stress would not make these original peak comparisons pass.')
 para(d,'The hinge calculation also shows why settings matter. The old assumed worst moving-side mass needs about 206 N preload at friction 0.1 and equivalent static 3g. That is not an approved assembly setting. The catalogue reference point is not a full allowable spring-load curve; increasing preload also changes part stress.')
 para(d,'For the 4 mm pin and 4.3 mm bore, the tight allocated errors leave 0.06 mm radial margin. The broad assumed raw errors leave minus 0.15 mm. A larger bore changes bearing behaviour, so we have not changed it blindly. Controlled finishing and real dimensional capability must be specified.')
 trial=O/'refinement/trial.json'
 if trial.exists():
  tr=json.loads(trial.read_text());para(d,'An extra 1.9 mm child large mesh trial has '+str(tr['nodes'])+' nodes. Trial status: '+tr['status']+'. The first unoptimized curved mesh had an invalid element and was rejected. The saved trial and failure log document the correction attempt; no result here is a full product-strength pass.')
 matrix=O/'refinement/matrix_review.json'
 if matrix.exists():
  f=json.loads(matrix.read_text());new_page(d,'V21 Finer joint results')
  para(d,'We added optimized 1.9 mm meshes for the child large and adult small representative joints, under outward and inward loads. The table compares the new interior-point peaks with the 2.3 mm results. The failed earlier comparisons remain in the history.')
  table(d,['Size and load','Tongue peak change','Fork peak change'],[[x['size'].replace('_',' ')+' '+x['direction'],format(x['stress'][0]['change_percent'],'.2f')+' percent',format(x['stress'][1]['change_percent'],'.2f')+' percent'] for x in f['cases']],[3.3,1.8,1.8])
  para(d,('All eight selected finer peak comparisons passed the chosen 5 percent check.' if f['all_selected_finer_peak_comparisons_pass'] else 'Six of eight finer peak checks pass. The adult fork changes by 27.52 percent outward and 28.31 percent inward, so those two checks still fail.')+' The displacement comparisons and force balance are recorded separately. These checks concern selected computed quantities, not the strength of a real part.')
  para(d,'Projected Anderson acceleration solved the original contact equations. Its child outward displacement field matched the saved unaccelerated direct reference. Its final force residual is checked independently of iteration progress. The model still uses an assumed PA66 stiffness of 3500 MPa, friction 0.2, 140 N prescribed preload and a 2 N side load in either direction.')
  para(d,'These are isolated joint fixtures extracted from V19 ParallelDisc geometry. They do not model the full final AssemblyPrototype, resolved bolt and thread contact, actual bearing clearance, creep or fatigue. Peaks are sampled at 27 interior points per element; surface and contact-edge peaks are not globally bounded.')
  para(d,'Hotspot locations and curved-element quality were also inspected. Their proximity to boundaries does not prove a singularity. Quantiles do not replace failed peak checks. The rejected mesh and stopped solver experiments are retained. A stopped experiment has no equilibrium pass. The final accepted route and raw solutions are identified in refinement/matrix_review.json and solver_experiments.json.')
 new_page(d,'V21 What is still open')
 table(d,['Topic','Current evidence and remaining work'],[
 ['Peak joint stress','Read the finer comparison page for the current status. Surface peaks, real material strength and full fastener contact remain unqualified.'],
 ['Full worn contact','Reduced models only. Need actual foam, cover, seams, head geometry, friction and headband force.'],
 ['Sound and ANC','Earlier acoustic proxies only. Need actual pad transfer properties and worn seal; no dB or ANC benefit is established.'],
 ['Heat and moisture','Earlier assumed-property models only. Actual permeability and thermal inputs are missing.'],
 ['Drop and life','No calibrated drop, fatigue, creep, cleaning or ageing result. Grade, process, joint details and criteria are missing.'],
 ['Sony mounting','Published outer size and groove instructions do not define the exact skirt and groove.'],
 ['Production details','Locking, tool access, tolerances, cover seam and bonding are not manufacturing released.'],
 ['Comfort and sensory acceptance','Requires voluntary feedback from intended users. No software result proves acceptance.']],[1.7,5.2])
 para(d,'This round is complete as a recorded set of checks. It does not close all software work, and it does not require us to pretend missing or failed tests passed. Small material coupons and reference-pad dimensions can improve later models, but no production batch or custom mounting tooling is released.')
 para(d,'An analytic temperature calculation matched the old one-node heat proxy within 0.00013 degrees C across 216 saved rows. That checks the equation implementation. In 155 of those assumed rows the moisture calculation reached saturation. This is an older proxy, not the current headset or a measured comfort result; the heat and moisture problem is not solved.')
 para(d,'Evidence: engineering-v21-results contains the motion logs, exact-area comparisons, wider position cases, separate scalar controls, stress recovery, mechanical limits and the complete test scope register. The two reports use the same evidence snapshot. No new market-price check or physical test was performed on this date.')
 compact=list(O.glob('*_compact.json'))
 if len(compact)==6:
  new_page(d,'V21 Carrying poses')
  para(d,'The old fold reduced the child medium bounding volume by less than 0.1 percent. We therefore searched additional positions of the existing parts. This changes the assembly pose only; the headband, cups and cushions were not reshaped.')
  rows=[]
  for path in sorted(compact):
   x=json.loads(path.read_text());chosen=x['chosen'];old=x['original_fold_box_mm'];wear=x['nominal_box_mm'];volume=lambda b:b[0]*b[1]*b[2]
   rows.append([x['size'].replace('_',' '),format(100*volume(old)/volume(wear),'.1f')+' percent',format(100*volume(chosen['box_mm'])/volume(wear),'.1f')+' percent' if chosen else 'No better passing candidate',str(chosen['angles']) if chosen else 'None'])
  table(d,['Size','Old folded volume relative to wear','New candidate volume relative to wear','Angles in degrees'],rows,[1.55,1.9,2.1,1.35])
  para(d,'Each size search ranked 625 angle pairs at 5 degree increments up to 120 degrees. Candidates were tested in order until the first passing endpoint and sampled path. A selected candidate also passed left-first path samples every 2.5 degrees. Saved STEP poses were reimported and checked for 42 solids and matching volume.')
  para(d,'This is a finite geometric carrying check. It does not prove a continuous path, finger safety, friction holding, loaded clearance or real bag fit. If a size has no selected candidate, its existing V19 pose remains the reference. The complete search trials and source hashes are saved.')
