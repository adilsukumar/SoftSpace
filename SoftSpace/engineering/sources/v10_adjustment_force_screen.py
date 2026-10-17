"""Reduced compliance screen across extension settings, not full assembly contact.
Actual changed band and ideal clamped slider segment compliances in series.
"""
import os,sys,json,csv,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import contact_membrane_fem as m,screening as s
O=P/'engineering-v10-results';full_width='full' in sys.argv;ss=json.loads((O/('full_width_sizes_summary.json' if full_width else 'solid_v10_summary.json')).read_text());sl=json.loads((O/'slider_compliance.json').read_text())
assert ss['status']=='complete' and sl['all_compliance_comparisons_pass'],'Completed band and slider comparisons required'
if full_width:assert ss['all_compliance_comparisons_pass'],'Completed actual-width stiffness comparisons required'
recipes={r['name']:r for r in json.loads((P/'engineering-v8-results'/'lower_crown_summary.json').read_text())['recipes']}
sliders={c['extension_mm']:c['meshes'][-1] for c in sl['cases']};rows=[]
for c in ss['cases']:
 name=c['size'];head=next(h for h in s.HEADS if h['name']==name);recipe=recipes[name];band=c['meshes'][-1]
 if hashlib.sha256(Path(band['source']).read_bytes()).hexdigest()!=band['source_sha256']:raise RuntimeError('Band source changed')
 band_full_opening_compliance=2*band['compliance_mm_per_N'] if full_width else 2*band['guide_mean_x_displacement_mm']/band['load_per_full_side_N']
 for ext in [0,15,30]:
  for E in [1500,2000,2500]:
   slider=sliders[ext];full_compliance=(band_full_opening_compliance+2*slider['tip_compliance_mm_per_N'])*2000/E
   F=2
   for it in range(60):
    cc,_=m.solve(head,force=F,contour=1,foam_multiplier=1)
    opening=head['width_mm']+70-2*recipe['band_halfspan_mm']-2*cc['absolute_approach_mm']
    if opening<0:raise RuntimeError('Required band opening negative')
    target=opening/full_compliance
    if abs(F-target)<.0002:break
    F=(F+target)/2
   else:raise RuntimeError('Reduced equilibrium failed '+name)
   cc.update(extension_mm=ext,E_MPa=E,opening_mm=opening,band_full_opening_compliance_mm_per_N=band_full_opening_compliance*2000/E,one_slider_compliance_mm_per_N=slider['tip_compliance_mm_per_N']*2000/E,total_full_opening_compliance_mm_per_N=full_compliance,equilibrium_mismatch_N=abs(F-target),band_source_sha256=band['source_sha256'])
   rows.append(cc)
 print(name,'adjustment force cases complete',flush=True)
j={'status':'complete','case_count':len(rows),'cases':rows,'model':'Scalar series-compliance screen: quarter-symmetry V10 band plus ideal clamped exposed CAD tongue, coupled to scalar membrane/foam','limits':['Quarter symmetry mirrors the front-only clamp bore; full-width band comparison remains open','No guide end moment/rotation coupling; not a monolithic assembled model','Same synthetic head width at each extension; vertical worn-head fit omitted','Clamp friction, pin bearing and actual locking not solved','35mm mounting offset each side remains assumed','Assumed materials, foam law and cover tension; point pressure peaks unvalidated','No comfort, strength or sound-seal threshold']}
if full_width:
 j['model']='Scalar series-compliance screen: actual full front-to-rear width X-half band fixture plus ideal clamped slider, coupled to scalar membrane/foam'
 j['limits'][0]='Actual front-only bore retained; ideal crown fixture and uniform guide traction, not full worn-assembly contact'
stem='adjustment_force_full_width' if full_width else 'adjustment_force_screen'
(O/(stem+'.json')).write_text(json.dumps(j,indent=2))
with (O/(stem+'.csv')).open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'cases':len(rows),'force_range_N':[min(r['force_N'] for r in rows),max(r['force_N'] for r in rows)],'compression_range_mm':[min(r['max_compression_mm'] for r in rows),max(r['max_compression_mm'] for r in rows)]}))
