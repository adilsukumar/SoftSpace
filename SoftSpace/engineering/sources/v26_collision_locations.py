from pathlib import Path
import json,sys
P=Path(r'${WORKSPACE}');sys.path.insert(0,str(P/'cad-validation-libraries'))
from audit_v14_motion import load,rotate,bounds,mass,BRepAlgoAPI_Common,BRepGProp,GProp_GProps
O=P/'engineering-v26-results';row=json.loads((O/'child_large_candidate_cad.json').read_text());parts,_=load(row);records=[]
for angle in [25,27.5]:
 op=BRepAlgoAPI_Common(rotate(parts['RightFork'],0,row['pivot_z_mm'],angle),parts['RightTongue']);assert op.IsDone();s=op.Shape();p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);pt=p.CentreOfMass();records.append(dict(angle_deg=angle,intersection_mm3=mass(s),bounds_mm=list(bounds(s)),centre_mm=[pt.X(),pt.Y(),pt.Z()]))
(O/'collision_locations.json').write_text(json.dumps(records,indent=2));print(records)
