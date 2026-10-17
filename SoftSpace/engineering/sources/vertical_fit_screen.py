"""Synthetic coronal head/crown clearance; not 3D scalp-contact validation.
Worn planar band shapes retain the V5 lateral compression assumptions.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,csv
from pathlib import Path
import numpy as np
import extendable_study as e
p=Path(__file__).parent;o=p/'engineering-v7-results'
data=json.loads((p/'engineering-v5-results'/'extendable_summary.json').read_text())
rows=[];shapes=[]
for recipe in data['recipes']:
 name=recipe['name'];family=recipe['family'];width=recipe['reference_head_width_mm'];cap_t=recipe['band_thickness_mm']
 for ext in [0,15,30]:
  case=next(c for c in data['cases'] if c['head']==name and c['extension_mm']==ext and c['E_MPa']==2000)
  result,xy=e.solve(family,recipe['band_halfspan_mm'],ext,case['opening_mm'])
  # Model tongue pin sits at65mm above cushion center. Cap endpoints are30+ext higher.
  xy[:,1]+=65+30+ext
  cap=xy[8:-8];normal=np.column_stack([-np.gradient(cap[:,1]),np.gradient(cap[:,0])]);normal/=np.linalg.norm(normal,axis=1)[:,None]
  inside=cap-normal*(cap_t/2+5);center=len(inside)//2
  shapes.append({'size':name,'extension_mm':ext,'band_inner_crown_height_mm':float(inside[center,1]),'pad_inner_curve_mm':inside.tolist(),'width_mm':width})
  heights=[105,115,125,135,145] if family=='child' else [130,140,150,160,170]
  for H in heights:
   mask=abs(inside[:,0])<width/2;head_z=H*np.sqrt(1-(inside[mask,0]/(width/2))**2)
   gap=inside[mask,1]-head_z;minimum=float(gap.min());crown_gap=float(inside[center,1]-H)
   status='rigid band intersection possible' if minimum<-5 else ('pad compression geometric candidate' if minimum<=0 else 'no crown contact in this free shape')
   rows.append({'size':name,'family':family,'extension_mm':ext,'synthetic_width_mm':width,'synthetic_height_above_ear_mm':H,'comparison_force_N':case['force_N'],'crown_gap_mm':crown_gap,'minimum_vertical_gap_mm':minimum,'classification':status})
 with (o/'vertical_fit_partial.json').open('w') as f:json.dump({'rows':rows,'shapes':shapes},f)
 print(name,'height screen complete',flush=True)
summary={'status':'complete','case_count':len(rows),'synthetic_height_ranges_mm':{'child':[105,145],'adult':[130,170]},'rows':rows,'shapes':shapes,
 'limitations':['Hypothetical heights; not anthropometric percentiles','Coronal ellipse only; no fore-aft depth/pinna/skin geometry','Band shape solved under lateral endpoint displacement without scalp load','5mm crown padding is geometric allowance, not known compression-force behavior','Negative gap needs coupled scalp contact, positive gap needs fit reassessment; neither is a wearable pass/fail certificate']}
(o/'vertical_fit_summary.json').write_text(json.dumps(summary,indent=2))
with (o/'vertical_fit.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('Recorded',len(rows),'synthetic head-height comparisons')
