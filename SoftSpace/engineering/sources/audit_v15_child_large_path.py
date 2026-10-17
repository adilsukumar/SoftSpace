"""Check the improved V14 child-large endpoint using two discrete fold orders."""
import json
from audit_v14_motion import P,load,check,moved,rotate,unlocked,recipes
O=P/'engineering-v15-results';s=json.loads((O/'child_large_packing_search.json').read_text());best=s['best_clear_endpoint'];assert best and best['pass'];cad=json.loads((P/'engineering-v14-results/cad_report.json').read_text());row=next(r for r in cad['sizes'] if r['size']=='child_large');assert row['sha256']==s['source_sha256'];parts,controls=load(row);R=recipes['child_large']['band_halfspan_mm'];el,er=best['extension_mm'];L,T=best['angles_deg'];assert [el,er,L,T]==[0,20,30,60]
left=[k for k in parts if k.startswith('Left') and k not in ['LeftTongue','LeftForkPin','LeftForkPinCap','LeftSliderKnob']];right=[k for k in parts if k.startswith('Right') and k not in ['RightTongue','RightForkPin','RightForkPinCap','RightSliderKnob']];lt=['LeftTongue','LeftForkPin','LeftForkPinCap'];rt=['RightTongue','RightForkPin','RightForkPinCap']
def pose(extl,extr,stroke=0,la=0,ra=0):
 b=unlocked(parts,R,stroke)
 return {k:moved(rotate(v,-R,65,-la),(0,0,15-extl)) if k in left else moved(rotate(v,R,65,ra),(0,0,15-extr)) if k in right else moved(v,(0,0,15-extl)) if k in lt else moved(v,(0,0,15-extr)) if k in rt else v for k,v in b.items()}
out={'revision':'V15 new path experiment on unchanged V14 child-large CAD','source':row['file'],'source_sha256':row['sha256'],'cases':[],'positive_solid_controls':controls,'limits':['Discrete5degree5mm and2mmrelease samples, not continuous or deformable loaded motion','Pin release held6mm during folding; no stable folded latch or spring return mechanism qualified','No new V15 retention-pilot geometry used; this is V14 child-large only']}
def sample(phase,extl,extr,stroke=0,la=0,ra=0,order=None):
 q=pose(extl,extr,stroke,la,ra)
 if phase=='adjustment':g={k:1 if k.startswith('Left') and not k.endswith('SliderKnob') else 2 if k.startswith('Right') and not k.endswith('SliderKnob') else 0 for k in q}
 elif phase=='release':g={k:i+1 if k.endswith(('LockPin','PullKnob','SpringSpace')) else 0 for i,k in enumerate(q)}
 else:g={k:1 if k in left else 2 if k in right else 3 if k in lt else 4 if k in rt else 0 for k in q}
 r=check(q,g);r.update(phase=phase,extension_mm=[extl,extr],stroke_mm=stroke,angles_deg=[la,ra],order=order);out['cases'].append(r);(O/'child_large_path_checkpoint.json').write_text(json.dumps(out,indent=2));print(json.dumps({'phase':phase,'angles':[la,ra],'pass':r['pass'],'order':order}),flush=True);return r['pass']
prefix=True
for e in [10,5,0]:
 if not sample('adjustment',e,15):prefix=False;break
if prefix:prefix=sample('adjustment',0,20)
if prefix:
 for stroke in [0,2,4,6]:
  if not sample('release',0,20,stroke):prefix=False;break
paths=[]
if prefix:
 for order,angles in [('left first',[(a,0) for a in range(0,L+1,5)]+[(L,a) for a in range(5,T+1,5)]),('right first',[(0,a) for a in range(0,T+1,5)]+[(a,T) for a in range(5,L+1,5)])]:
  passed=True
  for la,ra in angles:
   if not sample('folding',0,20,6,la,ra,order):passed=False;break
  paths.append({'order':order,'complete_sampled_path_pass':passed})
  if passed:break
out.update(prefix_pass=prefix,path_orders=paths,new_complete_sampled_path_pass=prefix and any(r['complete_sampled_path_pass'] for r in paths),case_count=len(out['cases']));(O/'child_large_path_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'case_count':len(out['cases']),'sampled_path_pass':out['new_complete_sampled_path_pass']}))
