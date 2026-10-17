"""Prove geometry equality before sharing component fixture results within a family."""
import json
from audit_v14_motion import P,load,moved,mass,common,recipes
O=P/'engineering-v18-results';rows={json.loads(f.read_text())['size']:json.loads(f.read_text()) for f in O.glob('*_cad_report.json')};records=[]
for family,reference in [('child','child_large'),('adult','adult_small')]:
 ref,_=load(rows[reference]);rr=recipes[reference]['band_halfspan_mm']
 for size,row in rows.items():
  if not size.startswith(family):continue
  parts,_=load(row);R=recipes[size]['band_halfspan_mm']
  for name in ['RightTongue','RightFork']:
   a=moved(parts[name],(-R,0,0));b=moved(ref[name],(-rr,0,0));v=common(a,b);va=mass(a);vb=mass(b);records.append(dict(size=size,part=name,reference=reference,source_sha256=row['sha256'],reference_sha256=rows[reference]['sha256'],volume_a=va,volume_b=vb,common_mm3=v,pass_result=max(abs(va-v),abs(vb-v))<.01))
old=json.loads((P/'engineering-v12-results/cad_report.json').read_text())
for size,row in rows.items():
 if not size.startswith('child'):continue
 prior=next(r for r in old['sizes'] if r['size']==size);a,_=load(row);b,_=load(prior);v=common(a['Band'],b['Band']);va=mass(a['Band']);vb=mass(b['Band']);records.append(dict(size=size,part='Band',reference='V12 same size',source_sha256=row['sha256'],reference_sha256=prior['sha256'],volume_a=va,volume_b=vb,common_mm3=v,pass_result=max(abs(va-v),abs(vb-v))<.01))
out=dict(records=records,all_pass=len(records)==15 and all(r['pass_result'] for r in records),scope='Volume intersection of original located valid solids. Only listed component geometry transfers, never complete worn fit or joint performance.');(O/'component_equivalence.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
