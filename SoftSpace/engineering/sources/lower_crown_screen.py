"""Recalibrate reduced force and evaluate shorter crown profiles before CAD."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,math
import numpy as np
import extendable_study as e
import contact_membrane_fem as m
import screening as screening
p=Path(__file__).parent;o=p/'engineering-v8-results';o.mkdir(exist_ok=True)
e.CONFIG['adult']['band_arch_height']=40;e.CONFIG['child']['band_arch_height']=25
source=json.loads((p/'extendable-recipes.json').read_text());recipes=[];cases=[];height_rows=[]
for recipe in source:
 name=recipe['name'];family=recipe['family'];head=next(h for h in screening.HEADS if h['name']==name)
 contact,_=m.solve(head,force=2,contour=1,foam_multiplier=1)
 spread=head['width_mm']+70-2*contact['absolute_approach_mm'];lo=(spread-70)/2;hi=(spread-1)/2
 for _ in range(16):
  R=(lo+hi)/2;r,_=e.solve(family,R,15,spread-2*R)
  if r['force_per_cup_N']>2:lo=R
  else:hi=R
 R=(lo+hi)/2;new=dict(recipe,band_halfspan_mm=R,arch_height_mm=e.CONFIG[family]['band_arch_height']);recipes.append(new)
 for ext in [0,15,30]:
  F=2
  for it in range(30):
   cc,_=m.solve(head,force=F,contour=1,foam_multiplier=1);opening=head['width_mm']+70-2*R-2*cc['absolute_approach_mm'];r,xy=e.solve(family,R,ext,opening)
   target=r['force_per_cup_N']
   if abs(F-target)<.0002:break
   F=(F+target)/2
  else:raise RuntimeError('Coupled fit failed')
  cc.update(extension_mm=ext,opening_mm=opening,band_halfspan_mm=R,arch_height_mm=e.CONFIG[family]['band_arch_height']);cases.append(cc)
  xy[:,1]+=65+30+ext;cap=xy[8:-8];normal=np.column_stack([-np.gradient(cap[:,1]),np.gradient(cap[:,0])]);normal/=np.linalg.norm(normal,axis=1)[:,None];inner=cap-normal*(recipe['band_thickness_mm']/2+8);center=len(inner)//2
  heights=range(105,146,5) if family=='child' else range(120,156,5)
  for H in heights:
   mask=abs(inner[:,0])<head['width_mm']/2;gaps=inner[mask,1]-H*np.sqrt(1-(inner[mask,0]/(head['width_mm']/2))**2);gap=float(gaps.min())
   height_rows.append({'size':name,'family':family,'extension_mm':ext,'head_height_mm':H,'crown_inner_height_mm':float(inner[center,1]),'minimum_vertical_gap_mm':gap,'candidate_contact':-5<=gap<=0})
 print(name,'R',round(R,2),'crown heights',[round(r['crown_inner_height_mm'],1) for r in height_rows if r['size']==name and r['head_height_mm']==min(heights)],flush=True)
 (o/'lower_crown_partial.json').write_text(json.dumps({'recipes':recipes,'cases':cases,'height_cases':height_rows},indent=2))
report={'status':'complete','recipes':recipes,'cases':cases,'height_cases':height_rows,'limitations':['Synthetic coronal ellipses and heads; not a population fit certification','Height varies only0/15/30mm in this screen; continuous fit interpolation not established','Scalp contact and crown pressure not included; only free-shape clearance','Crown padding8mm is an unmeasured geometric hypothesis','Force2N is a comparison target, not an autistic comfort limit']}
(o/'lower_crown_summary.json').write_text(json.dumps(report,indent=2));(p/'lower-crown-recipes.json').write_text(json.dumps(recipes,indent=2))
