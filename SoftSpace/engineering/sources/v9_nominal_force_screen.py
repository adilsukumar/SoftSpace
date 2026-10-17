"""Hybrid screen: actual nominal CAD band linear compliance plus scalar pad model.
No slider lock/contact or worn scalp mechanics. Synthetic inputs only.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,csv,sys
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import contact_membrane_fem as m,screening as s
O=P/'engineering-v9-results';ss=json.loads((O/'solid_v9_summary.json').read_text())
assert ss['status']=='complete','Six native band mesh cases required'
recipes={r['name']:r for r in json.loads((P/'engineering-v8-results'/'lower_crown_summary.json').read_text())['recipes']}
rows=[]
for c in ss['cases']:
    name=c['size'];head=next(h for h in s.HEADS if h['name']==name);recipe=recipes[name]
    r=c['meshes'][-1];compliance=2*r['guide_mean_x_displacement_mm']/r['load_per_full_side_N']
    for E in [1500,2000,2500]:
        F=2.;stiffness=(E/2000)/compliance
        for it in range(60):
            cc,_=m.solve(head,force=F,contour=1,foam_multiplier=1)
            opening=head['width_mm']+70-2*recipe['band_halfspan_mm']-2*cc['absolute_approach_mm']
            if opening<0:raise RuntimeError('Required band opening became negative')
            target=stiffness*opening
            if abs(target-F)<.0002:break
            F=(F+target)/2
        else:raise RuntimeError('Hybrid force equilibrium failed '+name)
        cc.update(E_MPa=E,extension_mm=15,opening_mm=opening,linear_band_compliance_mm_per_N=compliance*2000/E,scaled_band_stress_MPa=r['max_von_mises_centroid_MPa']*F/2,equilibrium_mismatch_N=abs(target-F),native_STEP_sha256=c['source_sha256'])
        rows.append(cc)
    print(name,'nominal hybrid cases complete',flush=True)
j={'status':'complete','case_count':len(rows),'cases':rows,'model':'Native nominal V9 quadratic band compliance coupled iteratively to scalar membrane/foam contact','limits':['Nominal 15 mm setting only; no adjusted joint compliance','Linear elastic band and ideal guide loads; no joint friction or locking','35 mm mount offset per side assumed, matching earlier synthetic fit screen','Synthetic heads, foam law and cover tension; no scalp contact','Point pressure peaks unvalidated; no comfort or sealing threshold']}
(O/'nominal_force_screen.json').write_text(json.dumps(j,indent=2))
with (O/'nominal_force_screen.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'cases':len(rows),'force_range_N':[min(r['force_N'] for r in rows),max(r['force_N'] for r in rows)],'compression_range_mm':[min(r['max_compression_mm'] for r in rows),max(r['max_compression_mm'] for r in rows)]}))
