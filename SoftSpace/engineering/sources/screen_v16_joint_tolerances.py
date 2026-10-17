"""Bounded-error geometric fit screen; no manufacturing capability is assumed."""
from pathlib import Path
import json,hashlib,math,itertools,csv,sys
P=Path(__file__).parent;O=P/'engineering-v16-results';s=json.loads((O/'selected_candidates.json').read_text());cases=[];sizes=[]
for r in s['sizes']:
 assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
 d=r['dimensions'];radius=12 if r.get('layout','lower').startswith('upper') else math.sqrt(125);clear=(d['index_hole_diameter_mm']-d['locking_pin_diameter_mm'])/2
 backlash=math.degrees(2*math.asin(clear/(2*radius)))
 sizes.append({'variant':r['variant'],'source':r['file'],'source_sha256':r['sha256'],'index_radius_mm':radius,'nominal_radial_clearance_mm':clear,'nominal_one_sided_rotation_until_contact_deg':backlash})
 for t,pos,angle in itertools.product([0,.01,.025,.05,.1],[0,.025,.05,.1],[0,.1,.25,.5,1]):
  drift=2*radius*math.sin(math.radians(angle)/2);remaining=clear-t-pos-drift
  cases.append({'variant':r['variant'],'each_diameter_error_bound_mm':t,'relative_center_error_bound_mm':pos,'angular_error_bound_deg':angle,'angular_center_shift_mm':drift,'worst_case_remaining_radial_clearance_mm':remaining,'positive_geometric_fit_margin':remaining>1e-9})
interfaces=[]
for name,hole,pin in [('Index hole and pin',2.3,2.2),('Cross drill and rivet shaft',.85,.8),('Knob bore and stem',2.3,2.2),('Rivet head recess and formed head',1.3,1.2)]:
 for t,pos in itertools.product([0,.01,.025,.05,.1],[0,.01,.025,.05,.1]):
  margin=(hole-pin)/2-t-pos;interfaces.append({'interface':name,'hole_diameter_mm':hole,'insert_diameter_mm':pin,'each_diameter_error_bound_mm':t,'relative_center_error_bound_mm':pos,'minimum_radial_fit_margin_mm':margin,'positive_geometric_fit_margin':margin>1e-9})
# Analytic unit controls, including contact and both signs of an offset.
assert abs(2*12*math.sin(math.radians(math.degrees(2*math.asin(.05/24)))/2)-.05)<1e-12
assert abs((2.3-2.2)/2-.05)<1e-12
out={'revision':'V16 additional bounded joint tolerance screen','geometry_changed':False,'sizes':sizes,'case_count':len(cases),'cases':cases,'positive_margin_cases':sum(c['positive_geometric_fit_margin'] for c in cases),'interface_case_count':len(interfaces),'interface_cases':interfaces,'limits':['Errors are illustrative bounds, not measured process capabilities or probabilities','Error vectors are conservatively aligned in the unfavorable direction; failing a bound does not prove every real assembly fails','Zero margin means ideal contact and is not counted as usable clearance','Cylinders and axes are rigid and parallel; no surface finish, chamfer capture, friction, swelling, wear or pin return force is solved','Nominal backlash excludes pivot and guide clearance, elasticity and stop surfaces','No manufacturing tolerance or product qualification is granted']}
(O/'joint_tolerance_screen.json').write_text(json.dumps(out,indent=2))
with (O/'joint_tolerance_cases.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cases[0].keys());w.writeheader();w.writerows(cases)
sys.path.insert(0,str(P/'solver-libraries'));import matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(8,4));x=[0,.01,.025,.05,.075,.1]
for radius,label in [(math.sqrt(125),'Child lower plate'),(12,'Adult upper plate')]:
 ax.plot(x,[math.degrees(2*math.asin(max(0,.05-t)/(2*radius))) for t in x],marker='o',label=label)
ax.set(xlabel='Error bound on each diameter in mm',ylabel='Remaining one sided rotation in degrees',title='Nominal index fit is sensitive to small errors');ax.grid(alpha=.2);ax.legend();fig.text(.5,.02,'Assumes zero centre error. Zero on the plot means no positive clearance budget. Not a measured production result.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.06,1,1));fig.savefig(P/'documents/images/V16_joint_tolerances.png',dpi=150);plt.close(fig)
print(json.dumps({'cases':len(cases),'positive_margin_cases':out['positive_margin_cases'],'interfaces':len(interfaces),'one_sided_nominal_rotation_deg':[r['nominal_one_sided_rotation_until_contact_deg'] for r in sizes]}))
