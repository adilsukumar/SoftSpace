from pathlib import Path
import json,time
P=Path(__file__).resolve().parent
from audit_v14_motion import load
O=P/'engineering-v24-results';rows=[]
for size in ['child_large','adult_small']:
 row=json.loads((P/'engineering-v19-results/final-CAD'/f'{size}_cad_report.json').read_text());start=time.time();parts,controls=load(row);assert len(parts)==42 and all(c['pass'] for c in controls);rows.append(dict(size=size,solids=len(parts),source_sha256=row['sha256'],all_recorded_geometry_controls_pass=True,seconds=time.time()-start))
(O/'motion_loader_replay.json').write_text(json.dumps(dict(cases=rows,scope='Actual relocated primary OCP reader and its existing validity/self-common controls; no new motion path or whole-product clearance claim.'),indent=2));print(rows)
