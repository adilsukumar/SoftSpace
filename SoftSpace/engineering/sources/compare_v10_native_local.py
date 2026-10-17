"""Compare the actual native and local band solids by OCC shared volume."""
from pathlib import Path
import sys,json,hashlib
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'));import gmsh
O=P/'engineering-v10-results';report=json.loads((O/'cad_native_report.json').read_text());assert report['status']=='complete';rows=[]
for row in report['sizes']:
 name=row['name'];native=Path(next(f for f in report['files'] if '_'+name+'_' in f and f.endswith('.step') and 'Extension' not in f));local=P/('OwnPassiveDefender_V10Local_'+name+'.step')
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ
 bands=[];volumes=[];bounds=[]
 for file in [native,local]:
  before=set(gmsh.model.getEntities(3));occ.importShapes(str(file));occ.synchronize();added=set(gmsh.model.getEntities(3))-before
  found=[dt for dt in added if (lambda b:b[0]<-75 and b[3]>75 and 81.99<b[2]<82.01 and b[4]-b[1]<30)(gmsh.model.getBoundingBox(*dt))]
  assert len(found)==1,(name,found);band=found[0];bands.append(band);volumes.append(occ.getMass(*band));bounds.append(gmsh.model.getBoundingBox(*band))
 common,_=occ.intersect([bands[0]],[bands[1]]);shared=sum(occ.getMass(*dt) for dt in common if dt[0]==3);difference=abs(sum(volumes)-2*shared);gmsh.finalize()
 r={'size':name,'native':str(native),'local':str(local),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'local_sha256':hashlib.sha256(local.read_bytes()).hexdigest(),'volumes_mm3':volumes,'shared_mm3':shared,'symmetric_difference_mm3':difference,'bounds_mm':bounds,'pass':difference<.01};rows.append(r);print(json.dumps(r),flush=True)
out={'status':'complete','all_pass':all(r['pass'] for r in rows),'cases':rows,'threshold_mm3':.01,'limit':'Band geometry comparison only. The numerical results retain the original local source hashes and quarter-symmetry approximation; this does not validate physical materials or contacts.'}
(O/'native_local_band_comparison.json').write_text(json.dumps(out,indent=2))
