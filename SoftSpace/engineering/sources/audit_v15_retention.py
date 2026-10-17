"""Original-shape geometry checks for the adult-small retention experiment."""
import sys,json,math
from audit_v14_motion import P,load,check,moved,unlocked,rotate,recipes,bounds,mass
O=P/'engineering-v15-results';size=sys.argv[1];row=json.loads((O/(size+'_retention_cad.json')).read_text());parts,validity=load(row);R=recipes[size]['band_halfspan_mm'];cases=[]
for stroke in [0,2,4,6]:
 q=unlocked(parts,R,stroke)
 for prefix in ['Left','Right']:q[prefix+'ReleaseJamNut']=moved(parts[prefix+'ReleaseJamNut'],(0,-stroke,0))
 r=check(q);r.update(phase='release',stroke_mm=stroke);cases.append(r);print(json.dumps({'phase':'release','stroke':stroke,'pass':r['pass']}),flush=True)
# Retraction and extension geometry includes the longer new rear knob and nut.
for extension in [0,30]:
 q={k:moved(s,(0,0,extension-15)) if k in ['Band','CrownPad','LeftSliderKnob','RightSliderKnob'] else s for k,s in parts.items()}
 r=check(q);r.update(phase='slider endpoint',extension_mm=extension);cases.append(r)
out={'revision':'V15 adult-small retention pilot','source':row['file'],'source_sha256':row['sha256'],'solid_count':len(parts),'validity':validity,'cases':cases,'case_count':len(cases),'all_pass':all(r['pass'] for r in cases),'limits':['Cosmetic thread envelopes cannot prove flank contact thread strength or assembly torque','No all-six-size V15 or folding path pass is inferred','Actual nut locking and child small-part access remain unvalidated']}
(O/(size+'_retention_audit.json')).write_text(json.dumps(out,indent=2));print(json.dumps({'case_count':len(cases),'all_pass':out['all_pass']}))
