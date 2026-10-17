"""Worst-case dimensional closure budgets using recorded nominal OCC distances."""
from pathlib import Path
import json,hashlib,csv
P=Path(__file__).parent;O=P/'engineering-v10-results';src=O/'clearance_distances.json'
original=json.loads(src.read_text());rows=[]
def budget(gap,per_part):return gap-2*per_part
assert abs(budget(.5,.1)-.3)<1e-12 and budget(.2,.1)==0 and budget(.1,.1)<0
for pose in original['checks']:
 assert hashlib.sha256(Path(pose['file']).read_bytes()).hexdigest()==pose['sha256']
 for pair in pose['checks']:
  for error in [0,.025,.05,.075,.1,.125,.15,.2,.25,.3,.4,.5]:
   left=budget(pair['distance_mm'],error)
   rows.append({'source':pose['file'],'source_sha256':pose['sha256'],'pair':pair['pair'],'side':pair['side'],'nominal_gap_mm':pair['distance_mm'],'assumed_normal_error_each_part_mm':error,'remaining_gap_lower_bound_mm':left,'positive_clearance_budget':left>1e-9})
summary=[]
for pair in sorted({r['pair'] for r in rows}):
 gap=min(r['nominal_gap_mm'] for r in rows if r['pair']==pair)
 summary.append({'pair':pair,'minimum_recorded_gap_mm':gap,'equal_per_part_error_must_be_strictly_below_mm':gap/2,'budget_at_plusminus_0_2_mm_each':budget(gap,.2),'extra_nominal_gap_for_0_4mm_closure_plus_0_1mm_reserve_mm':max(0,.5-gap)})
out={'status':'complete','case_count':len(rows),'source_evidence_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'unit_checks':'pass','summary':summary,'cases':rows,'limits':['Reanalysis of recorded local CAD minimum distances, not new measured parts or deformed contact','Errors are assumed maximum surface displacements along the closing direction, not GD&T specifications or demonstrated process capability','No probability or production yield estimated','Negative remaining gap means lack of guaranteed clearance, not proof of a jam','A 0.1 mm residual reserve is illustrative, not a validated friction, dirt, thermal or wear allowance','Clearance increases can alter alignment, play, strength and locking; no CAD change was made']}
(O/'tolerance_budget_expanded.json').write_text(json.dumps(out,indent=2))
with (O/'tolerance_budget_expanded.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'cases':len(rows),'summary':summary},indent=2))
