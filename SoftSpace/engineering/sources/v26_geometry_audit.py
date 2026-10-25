from pathlib import Path
import json,sys,hashlib,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'cad-validation-libraries'))
from audit_v14_motion import load,common,rotate
O=P/'engineering-v26-results';row=json.loads((O/'child_large_candidate_cad.json').read_text());parts,controls=load(row);fork=parts['RightFork'];tongue=parts['RightTongue'];samples=[]
for angle in [i*2.5 for i in range(25)]:
 v=common(rotate(fork,0,row['pivot_z_mm'],angle),tongue);samples.append(dict(angle_deg=angle,intersection_mm3=v,passed=v<.01))
stops=[]
for angle in [-.1,-1]:
 v=common(rotate(fork,0,row['pivot_z_mm'],angle),tongue);stops.append(dict(angle_deg=angle,intersection_mm3=v,blocking_detected=v>1e-5))
out=dict(date='2026-10-25',source_CAD_sha256=row['sha256'],solids=2,validity_controls=controls,folding_samples=samples,wearing_stop_samples=stops,sampled_local_motion_pass=all(r['passed'] for r in samples),stop_blocking_pass=all(r['blocking_detected'] for r in stops),scope='Only cropped local tongue and fork under rigid nominal geometry. 25 discrete samples 0 to 60 degrees; no full headset folding, continuous collision, tolerances, loading or pinch qualification.')
(O/'local_motion_audit.json').write_text(json.dumps(out,indent=2));print({k:out[k] for k in ['solids','sampled_local_motion_pass','stop_blocking_pass']})
