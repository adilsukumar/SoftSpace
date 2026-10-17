"""Sequential actual-width band compliance checks for all six CAD sizes."""
from pathlib import Path
import json,hashlib,math
import v10_full_width_band as b
P=Path(__file__).parent;O=P/'engineering-v10-results';cases=[]
for size in ['adult_small','child_small','child_medium','child_large','adult_medium','adult_large']:
 rows=[];change=None
 for h in [2.0,1.5,1.25]:
  f=O/(size+'_full_width_h'+str(h)+'.json')
  r=json.loads(f.read_text()) if f.exists() else b.run(size,h)
  assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']
  assert r['minimum_adaptive_Jacobian_mm3']>0 and r['relative_free_residual']<1e-5
  rx=r['reaction_sum_N'];assert math.sqrt((rx[0]+2)**2+rx[1]**2+rx[2]**2)<1e-5
  rows.append(r)
  if len(rows)>1:
   change=abs(rows[-1]['compliance_mm_per_N']/rows[-2]['compliance_mm_per_N']-1)
   if change<.05:break
 c={'status':'complete','size':size,'meshes':rows,'compliance_relative_mesh_change':change,'compliance_gate_5pct':change<.05,'limits':rows[-1]['limits']};cases.append(c)
 (O/(size+'_full_width_summary.json')).write_text(json.dumps(c,indent=2))
 out={'status':'complete' if len(cases)==6 else 'partial','cases':cases,'all_compliance_comparisons_pass':all(c['compliance_gate_5pct'] for c in cases),'limit':'Actual-width ideal fixture stiffness study; no scalp, guide or locking contact and no measured material properties. Not an isolated symmetry comparison with the earlier quarter model.'}
 (O/'full_width_sizes_summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({'size':size,'compliance_change':change,'pass':change<.05,'completed_sizes':len(cases)}),flush=True)
