import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,csv
import extendable_study as e,contact_membrane_fem as m,screening as s
p=Path(__file__).parent;o=p/'engineering-v8-results';base=json.loads((o/'lower_crown_summary.json').read_text());rows=[]
for recipe in base['recipes']:
 name=recipe['name'];family=recipe['family'];head=next(h for h in s.HEADS if h['name']==name);e.CONFIG[family]['band_arch_height']=recipe['arch_height_mm']
 for ext in [0,15,30]:
  for E in [1500,2000,2500]:
   F=2
   for it in range(30):
    cc,_=m.solve(head,force=F,contour=1,foam_multiplier=1);opening=head['width_mm']+70-2*recipe['band_halfspan_mm']-2*cc['absolute_approach_mm'];band,_=e.solve(family,recipe['band_halfspan_mm'],ext,opening,E=E)
    target=band['force_per_cup_N']
    if abs(F-target)<.0002:break
    F=(F+target)/2
   else:raise RuntimeError('V8 material/contact equilibrium failed')
   cc.update(E_MPa=E,extension_mm=ext,opening_mm=opening,max_elastic_stress_MPa=band['max_elastic_stress_MPa'],equilibrium_mismatch_N=abs(F-target));rows.append(cc)
 print(name,'54-case sensitivity progress',len(rows),flush=True)
 (o/'material_sensitivity_partial.json').write_text(json.dumps(rows,indent=2))
summary={'status':'complete','case_count':len(rows),'cases':rows,'model':'Current lower-crown recipe, nonlinear planar beam, scalar membrane/foam contact','limitations':['Assumed modulus/foam/tension/head values','No scalp contact,3D slider friction or real material curves','Point pressure peaks unvalidated; no comfort threshold']}
(o/'material_sensitivity.json').write_text(json.dumps(summary,indent=2))
with (o/'material_sensitivity.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
