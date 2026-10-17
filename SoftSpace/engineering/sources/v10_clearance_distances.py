"""OCC minimum distances and a hypothetical relative error budget.
This is a nominal geometry check, not a manufacturing tolerance specification.
"""
from pathlib import Path
import sys,json,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';v=json.loads((O/'cad_local_report.json').read_text());rows=[]
for name in v['files']:
 path=Path(name);gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(path));occ.synchronize()
 bodies=gmsh.model.getEntities(3);bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies}
 band=next(dt for dt,b in bounds.items() if b[0]<-75 and b[3]>75 and 66.99<b[2]<97.01 and b[4]-b[1]<30)
 forks=[dt for dt,b in bounds.items() if abs(b[2]-31)<.01 and abs(b[5]-79)<.01 and b[3]-b[0]>20]
 tongues=[dt for dt,b in bounds.items() if abs(b[2]-61)<.01 and abs(b[5]-134)<.01 and abs(b[1]+8)<.01 and abs(b[4]-8)<.01]
 pins=[dt for dt,b in bounds.items() if abs((b[2]+b[5])/2-65)<.01 and b[4]-b[1]>35 and b[3]-b[0]<5]
 knobs=[dt for dt,b in bounds.items() if abs(b[1]-8)<.01 and abs(b[4]-16)<.01 and abs((b[5]-b[2])-9)<.01]
 if any(len(g)!=2 for g in [forks,tongues,pins,knobs]):raise RuntimeError('Ambiguous hardware groups '+path.name)
 def side(dt):return 1 if bounds[dt][0]+bounds[dt][3]>0 else -1
 checks=[]
 for label,a,b in [('guide to tongue',band,t) for t in tongues]+[('guide to pivot pin',band,t) for t in pins]+[('knob to fork',k,next(f for f in forks if side(f)==side(k))) for k in knobs]:
  result=occ.getDistance(*a,*b);distance=result[0]
  budgets=[{'assumed_error_each_part_mm':e,'worst_relative_closure_mm':2*e,'remaining_distance_lower_bound_mm':distance-2*e,'clearance_guaranteed_by_this_simple_budget':distance>2*e} for e in [.1,.2,.4]]
  checks.append({'pair':label,'side':side(b),'distance_mm':distance,'nearest_points_mm':list(result[1:]),'hypothetical_budgets':budgets})
 gmsh.finalize();rows.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks});print(path.name,'minimum clearance checks saved',flush=True)
j={'status':'complete','checks':rows,'method':'OCC exact shape minimum-distance query, no surface display mesh','limits':['Nominal undeformed shape only','The assumed per-part errors are examples, not verified factory capabilities','Negative remaining budget means clearance is not guaranteed, not a proved physical jam','Friction, roughness, thermal expansion, loads and assembly variation are omitted']}
(O/'clearance_distances.json').write_text(json.dumps(j,indent=2))
print(json.dumps({'minimums_mm':{label:min(c['distance_mm'] for r in rows for c in r['checks'] if c['pair']==label) for label in ['guide to tongue','guide to pivot pin','knob to fork']}}))
