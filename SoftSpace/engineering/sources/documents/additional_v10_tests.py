"""Shared report section for extra V10 travel and tolerance checks."""
import json

def add_section(d,P,new_page,para,table,is_glasses):
 O=P/'engineering-v10-results'
 path=O/'intermediate_travel_audit.json'
 if not path.exists():return
 travel=json.loads(path.read_text());tol=json.loads((O/'tolerance_budget_expanded.json').read_text())
 assert travel['status']=='complete'
 new_page(d,'Additional travel and tolerance checks')
 para(d,'We checked '+str(travel['pose_count'])+' standalone V10 poses: all six sizes at 0, 5, 10, 15, 20, 25 and 30 mm extension. '+('All sampled poses passed' if travel['all_pass'] else 'Some poses did not pass')+' the nominal rigid-body overlap check at a 0.01 cubic mm threshold. This covers more positions than the earlier endpoint audit. It does not prove continuous clearance between samples or clearance when the band bends.')
 para(d,'The band, crown pad and two clamp knobs moved as one group. All 28 solids were covered. Pairs within the same rigid group were checked once per size and reused because their relative positions do not change. The CAD source hashes are recorded. The results use local geometry calculations on the native STEP exports; no new Fusion simulation or physical test was run.')
 table(d,['Pair','Smallest gap','Remaining gap with 0.2 mm error per part'],[[r['pair'],f"{r['minimum_recorded_gap_mm']:.3f} mm",f"{r['budget_at_plusminus_0_2_mm_each']:.3f} mm"] for r in tol['summary']],[1.8,1.5,3.6])
 para(d,'The expanded tolerance budget has '+str(tol['case_count'])+' calculations over 12 assumed error levels. It reuses the recorded minimum distances. For the guide and slider tongue, equal errors must each stay below 0.109 mm to guarantee any positive gap under this simplified rule. At 0.2 mm per part the gap budget is negative. This means manufacturing clearance is not established; it does not prove that every real slider will jam.')
 para(d,'An illustrative 0.2 mm error per part plus a 0.1 mm remaining gap would need at least 0.500 mm nominal clearance. The current minimum would need about 0.283 mm more. This is a design input to investigate, not an approved production tolerance. Increasing the gap also needs checks for play, alignment, strength and locking. The CAD has not been changed by this test.')
 para(d,('For the Sony replacement cushion, the pad geometry and host fit remain unchanged. These standalone headband checks do not measure the Sony clamp force or validate our pad. ' if is_glasses else '')+'Native Word page layout remains unverified. These results are separate from real comfort, sensory acceptance, sound reduction and leakage tests.')
 new_page(d,'Tests that still need inputs or physical samples')
 table(d,['Test group','What is still needed','Current outcome'],[
 ['Foam and cover','Compression and recovery curves, cover stretch, friction and seam construction','Assumed models only'],
 ['Worn contact and fit','Measured heads, glasses paths, joint behaviour and nonlinear contact','No validated worn assembly result'],
 ['Band and locks','Material strength, creep and fatigue; real clamp threads, friction and torque','Conditional strength screen only'],
 ['Adjustment and retention','Clearance specification, stops, pull-out and repeated adjustment tests','Sampled rigid travel passes; retention open'],
 ['Heat and moisture','Measured material data and timed warm humid wear trials','Earlier model cases saturated'],
 ['Sound and leakage','Real cup, seal and material properties; acoustic fixture and repeated fitting','No measured attenuation or leakage pass'],
 ['Sony WH CH720N','Original pad mount, cup, vent and frame measurements','User will measure later'],
 ['Wearer feedback','Voluntary trials with autistic users and glasses wearers','Comfort and acceptance untested'],
 ['Manufacturing and cost','Supplier samples, dimensional capability and quotes','Production readiness and price unproven']],[1.4,3.65,1.85])
 para(d,'The saved test register separates finished calculations from tests needing inputs. We cannot complete the physical tests in CAD. We will use the measured inputs to replace assumptions and compare the original, uniform and softer-zone pads on the same headphone. Until then there is no claim that our product is better than a market product.')
 para(d,'Shared update on 14 October 2026: added intermediate slider positions and the expanded tolerance budget to both reports. Earlier failures remain recorded. Source records: intermediate_travel_audit.json and tolerance_budget_expanded.json.')
 stop_path=O/'stop_onset_audit.json'
 if stop_path.exists():
  stop=json.loads(stop_path.read_text());over=json.loads((O/'overtravel_audit.json').read_text())
  new_page(d,'Slider stop contact and unfinished validation')
  para(d,'The native V10 slider already has an outboard shoulder that obstructs the guide during overtravel. We removed the two clamp knobs in the numerical model to represent an unlocked assembly, then imposed six axial positions from 30 to 75 mm in each size. These are diagnostic poses outside the intended range, not positions we recommend using.')
  table(d,['Check','Recorded finding','Meaning'],[
   ['36 overtravel poses','Guide and tongue overlap at imposed 40, 50 and 60 mm settings in all six sizes','The existing shoulder creates a rigid geometric obstruction'],
   ['12 contact onset searches','Contact begins near 31.000 mm on both sides of every size','About 1 mm beyond the intended 30 mm range'],
   ['Numerical bracket','Contact threshold located within 0.001 mm intervals','Numerical location only; not manufactured accuracy'],
   ['Imposed 70 and 75 mm poses','Shapes are beyond the stop and separated axially','Not a reachable pull-out path: intervening positions clash'],
   ['Stop strength and retention','Not tested under load','No pull-out force or durability rating']], [1.35,3.05,2.5])
  para(d,'The contact search used exact CAD minimum distances. It did not solve the stress or deformation when the shoulder is pulled against the guide. The stop can exist geometrically and still need strengthening. We need the chosen material, manufacturing method and proof-load requirement before validating this part.')
  para(d,'Locking remains separate. The saved clamp knobs are shape placeholders. A loaded clamp test needs the final thread and insert geometry, tightening torque, contact friction and wear behaviour. Full worn-contact work also needs measured foam and cover properties, head shapes and the real glasses contact path. The earlier ideal headband-force studies do not replace those inputs.')
  para(d,'For the replacement pad route, these are standalone defender results. Sony WH-CH720N mount fit, original clamp force, acoustic response and ANC behaviour remain untested. Its original pad and groove still need measurement. The current generic cushion has not been changed by these checks.')
  para(d,'Physical validation remains unfinished: real compression and recovery, locking and pull-out, repeated adjustment, drops, cleaning and ageing, timed heat and moisture, incoming noise, outgoing playback and voluntary comfort trials. The test register identifies these as open. No software run can establish a real material curve or a wearer preference without measurements.')
  para(d,'Shared update on 14 October 2026: added stop geometry and overtravel evidence to both reports. Sources: overtravel_audit.json and stop_onset_audit.json. The CAD revision remains V10; no geometry was edited in this batch.')
