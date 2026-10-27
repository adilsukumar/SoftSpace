from pathlib import Path
import json,sys,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'cad-validation-libraries'))
from audit_v14_motion import load,check,common,mass
O=P/'engineering-v27-results';out=[]
for zh in [18,32]:
 row=json.loads((O/f'flex_zone{zh}_cad_report.json').read_text());parts,valid=load(row);r=check(parts);cover=parts['continuous_cover_reference'];control=common(cover,cover);assert abs(control-mass(cover))<.01
 out.append(dict(zone_height_mm=zh,source_CAD_sha256=row['sha256'],validity=valid,pair_intersection_check=r,cover_self_common_control_mm3=control,cover_volume_mm3=mass(cover),pass_geometry=all(x['pass'] for x in valid) and r['pass'],scope='Three valid solids, nominal nonoverlap and positive cover Boolean control. Continuous cover reference intentionally has no glasses slot. No worn sealing or Sony mount fit claim.'))
(O/'flex_geometry_audit.json').write_text(json.dumps(out,indent=2));assert all(x['pass_geometry'] for x in out);print('Both Flex references pass geometry checks')
