"""Geometric clamp-tip reach only; no thread, friction or holding-force claim."""
from pathlib import Path
import sys,json,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';n=json.loads((O/'cad_native_report.json').read_text());rows=[]
for size in [r['name'] for r in n['sizes']]:
 f=Path(next(f for f in n['files'] if '_'+size+'_' in f and f.endswith('.step') and 'Extension' not in f));gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(f));occ.synchronize();vols=gmsh.model.getEntities(3)
 for side in [-1,1]:
  tongues=[dt for dt in vols if (lambda b:abs(b[2]-61)<1e-5 and abs(b[5]-134)<1e-5 and abs(b[1]+8)<1e-5 and abs(b[4]-8)<1e-5 and (b[0]+b[3])*side>0)(gmsh.model.getBoundingBox(*dt))]
  knobs=[dt for dt in vols if (lambda b:abs(b[2]-94.5)<1e-5 and abs(b[5]-103.5)<1e-5 and abs(b[1]-8)<1e-5 and abs(b[4]-16)<1e-5 and (b[0]+b[3])*side>0)(gmsh.model.getBoundingBox(*dt))]
  assert len(tongues)==len(knobs)==1
  for ext in range(0,31,5):
   copy=occ.copy(knobs);occ.translate(copy,0,0,ext-15);occ.synchronize();distance=occ.getDistance(*copy[0],*tongues[0])[0]
   rows.append({'size':size,'side':side,'extension_mm':ext,'clamp_axis_z_mm':99+ext-15,'clamp_to_tongue_distance_mm':distance,'geometric_reach_pass':distance<1e-5,'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest()});occ.remove(copy,recursive=True);occ.synchronize()
 gmsh.finalize();print(size,'clamp reach checked',flush=True)
out={'status':'complete','case_count':len(rows),'all_geometric_reach_pass':all(r['geometric_reach_pass'] for r in rows),'cases':rows,'limits':['Ideal CAD stem meets tongue at the front face; no physical clamp force is computed','No thread, torque, friction, creep, tip wear or holding-force validation','Intended0–30mm range only; maximum actual mechanical travel and stop retention still need testing']}
(O/'lock_reach_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(rows),'all_geometric_reach_pass':out['all_geometric_reach_pass']}))
