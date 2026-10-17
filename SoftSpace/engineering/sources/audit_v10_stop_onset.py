"""Locate first guide/tongue stop contact along nominal axial extension."""
from pathlib import Path
import json,sys,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';native=json.loads((O/'cad_native_report.json').read_text());rows=[]
for size in native['sizes']:
 name=size['name'];source=Path(next(f for f in native['files'] if '_'+name+'_' in f and f.endswith('.step') and 'Extension' not in f))
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(source));occ.synchronize();bodies=gmsh.model.getEntities(3);bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in bodies}
 band=[dt for dt,b in bounds.items() if b[0]<-75 and b[3]>75 and abs(b[2]-82)<1e-5 and b[4]-b[1]<30];assert len(band)==1
 tongues=[dt for dt,b in bounds.items() if abs(b[2]-61)<1e-5 and abs(b[5]-134)<1e-5 and abs(b[1]+8)<1e-5 and abs(b[4]-8)<1e-5];assert len(tongues)==2
 for tongue in tongues:
  def distance(ext):
   copy=occ.copy(band);occ.translate(copy,0,0,ext-15);occ.synchronize();gap=occ.getDistance(*copy[0],*tongue)[0];occ.remove(copy,recursive=True);occ.synchronize();return gap
  lo,hi=30.,40.;gap30=distance(lo);assert gap30>1e-6 and distance(hi)<=1e-6
  queries=2
  while hi-lo>.001:
   mid=(lo+hi)/2;queries+=1
   if distance(mid)>1e-6:lo=mid
   else:hi=mid
  rows.append({'size':name,'side':-1 if sum(bounds[tongue][::3])<0 else 1,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'nominal_extension30_gap_mm':gap30,'last_noncontact_extension_mm':lo,'first_contact_extension_mm':hi,'bracket_width_mm':hi-lo,'distance_contact_threshold_mm':1e-6,'queries':queries,'overtravel_from30_mm':[lo-30,hi-30]})
 gmsh.finalize();print(name,'two stop-contact brackets located',flush=True)
out={'status':'complete','case_count':len(rows),'cases':rows,'all_brackets_within_0_001mm':all(r['bracket_width_mm']<=.001 for r in rows),'method':'OCC minimum distance queries and binary search between 30 and 40 mm for each tongue against translated native STEP band. Monotonic first closure is assumed in this local bracket; the 40 to 60 mm intersection audit independently shows the shoulder obstruction.','limits':['Geometric contact only; no contact force, stress, deformation, wear, load capacity or safety factor','No dimensional or angular variation','The 0.001 mm bracket is numerical localisation, not manufactured accuracy','The existing stop shoulder is retained; no CAD change made']}
(O/'stop_onset_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(rows),'first_contact_range_mm':[min(r['first_contact_extension_mm'] for r in rows),max(r['first_contact_extension_mm'] for r in rows)]}),flush=True)
