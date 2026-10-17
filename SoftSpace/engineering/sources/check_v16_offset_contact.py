"""Validate the analytic radial clearance against original OCP index geometry."""
import json,math
from audit_v14_motion import P,load,common,moved,recipes
O=P/'engineering-v16-results';selected=json.loads((O/'selected_candidates.json').read_text());cases=[]
for row in selected['sizes']:
 parts,_=load(row);upper=row.get('layout','lower').startswith('upper');direction=(1,0,0) if upper else (5/math.sqrt(125),0,10/math.sqrt(125))
 for prefix in ['Left','Right']:
  for offset in [-.06,-.04,0,.04,.06]:
   v=common(moved(parts[prefix+'LockPin'],tuple(offset*d for d in direction)),parts[prefix+'Tongue']);expected=abs(offset)>.05
   cases.append({'variant':row['variant'],'side':prefix,'offset_mm':offset,'interference_mm3':v,'expected_interference':expected,'matches_analytic':v>1e-5 if expected else v<1e-5})
 out={'case_count':len(cases),'all_match':all(r['matches_analytic'] for r in cases),'cases':cases,'scope':'Wear position pin versus tongue only. Confirms nominal radial fit equation at sampled offsets; not a tolerance or spring-return qualification.'};(O/'offset_contact_validation_partial.json').write_text(json.dumps(out,indent=2))
 print(row['variant'],out['all_match'],flush=True)
(O/'offset_contact_validation.json').write_text(json.dumps(out,indent=2));assert out['all_match']
