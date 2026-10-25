from pathlib import Path
import json,sys
P=Path(r'${WORKSPACE}');sys.path.insert(0,str(P/'cad-validation-libraries'))
from audit_v14_motion import load,common,rotate,moved,recipes
O=P/'engineering-v26-results';row=json.loads((P/'engineering-v19-results/child_large_cad_report.json').read_text());parts,valid=load(row);R=recipes['child_large']['band_halfspan_mm'];fork=moved(parts['RightFork'],(-R,0,0));tongue=moved(parts['RightTongue'],(-R,0,0));samples=[]
for angle in [0,20,22.5,25,27.5,30,60]:samples.append(dict(angle_deg=angle,intersection_mm3=common(rotate(fork,0,row['pivot_z_mm'],angle),tongue)))
(O/'baseline_local_motion_control.json').write_text(json.dumps(dict(source_CAD_sha256=row['sha256'],samples=samples,scope='Original V19 ParallelDisc whole tongue and fork. Nominal local pose, no folding extension or assembly.'),indent=2));print(samples)
