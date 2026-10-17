"""Neighboring width sensitivity around each calibrated size; not population coverage."""
import json
from pathlib import Path
import numpy as np
import screening as s
import contact_membrane_fem as m
import extendable_study as e
ROOT=Path(__file__).parent;OUT=ROOT/'engineering-v5-results'
recipes=json.loads((ROOT/'extendable-recipes.json').read_text());rows=[]
for recipe in recipes:
    base=next(h for h in s.HEADS if h['name']==recipe['name']);R=recipe['band_halfspan_mm']
    rr,_=e.solve(recipe['family'],R,15,base['width_mm']+5+70-2*R+2,steps=30)
    x=np.array([0]+[r['opening_mm'] for r in rr['history']]);y=np.array([0]+[r['force_per_cup_N'] for r in rr['history']])
    for delta in [-5,5]:
        head=dict(base,width_mm=base['width_mm']+delta);F=2
        for it in range(35):
            c,_=m.solve(head,force=F,contour=recipe['contour_fraction'])
            opening=head['width_mm']+70-2*R-2*c['absolute_approach_mm']
            target=float(np.interp(opening,x,y))
            if abs(target-F)<2e-4:break
            F=(F+target)/2
        else:raise RuntimeError('Width sensitivity equilibrium failed')
        c.update(size=recipe['name'],breadth_delta_mm=delta,synthetic_head_breadth_mm=head['width_mm'])
        rows.append(c)
    print(recipe['name'],'neighbor width checks complete',flush=True)
(OUT/'size_overlap_summary.json').write_text(json.dumps({'cases':rows,'limitations':['Only +/-5 mm breadth, fixed synthetic curvature, nominal extension/modulus','Not anatomical coverage or an acceptable clamping-force criterion']},indent=2))
