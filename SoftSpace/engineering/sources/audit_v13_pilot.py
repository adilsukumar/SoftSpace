import json,hashlib,time
from audit_v12_ocp import P,load,check,common,mass
O=P/'engineering-v13-results';cad=json.loads((O/'cad_report.json').read_text());old=json.loads((P/'engineering-v12-results'/'cad_report.json').read_text());rows=[]
for row in cad['sizes']:
 start=time.time();parts,control=load(row);changed={k for k in parts if any(s in k for s in ['Fork','LockPin','ServiceCap','CapBolt','CapNut']) and not k.endswith(('ForkPin','ForkPinCap'))};groups={k:i+1 if k in changed else 0 for i,k in enumerate(parts)};r=check(parts,groups)
 source=next(s for s in old['sizes'] if s['size']==row['size']);prior,_=load(source);inherit=[]
 for name in ['Band','CrownPad','LeftTongue','RightTongue','LeftCup','RightCup','LeftMainFoam','RightMainFoam','LeftCarrier','RightCarrier','LeftContinuousCover','RightContinuousCover']:
  v=mass(prior[name]);v2=mass(parts[name]);c=common(prior[name],parts[name]);inherit.append({'part':name,'source_volume_mm3':v,'candidate_volume_mm3':v2,'common_mm3':c,'pass':abs(v-v2)<.01 and abs(v-c)<.01})
 rows.append({'size':row['size'],'source_sha256':row['sha256'],'solid_validity_checks':control,'nominal_changed_pair_check':r,'unchanged_component_checks':inherit,'seconds':time.time()-start});print(json.dumps({'size':row['size'],'nominal_pass':r['pass'],'overlaps':r['overlaps'],'unchanged_checks':[(x['part'],x['pass']) for x in inherit]}),flush=True)
out={'sizes':rows,'scope':'All V13 solids valid; changed-body pairs checked against all bodies. Unchanged V12 nominal pairs rely on their recorded source audit. Coincident component-common failures are kept as failures, not claimed equivalence.'};(O/'pilot_audit.json').write_text(json.dumps(out,indent=2))
