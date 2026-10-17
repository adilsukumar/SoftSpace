import sys,json,hashlib
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
reports=[json.loads((P/n).read_text()) for n in ['cad_v9_adult_small_first.json','cad_v9_report.json'] if (P/n).exists()]
sizes={};files=[]
for r in reports:
 for s in r['sizes']:sizes[s['name']]=s
 for f in r['files']:
  if f not in files:files.append(f)
checks=[]
for name in files:
 f=Path(name)
 if f.suffix!='.step':continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(f));gmsh.model.occ.synchronize()
 bodies=gmsh.model.getEntities(3);volume=sum(gmsh.model.occ.getMass(*dt) for dt in bodies);gmsh.finalize()
 checks.append({'file':str(f),'solids':len(bodies),'volume_mm3':volume,'pass':len(bodies)==28 and volume>0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
out={'status':'complete' if len(sizes)==6 and len(checks)==18 and all(c['pass'] for c in checks) else 'partial','sizes':list(sizes.values()),'files':files,'STEP_checks':checks,'all_available_STEP_pass':all(c['pass'] for c in checks),'replacements':'V8 replacement pads unchanged; no V9-specific pad or leakage test'}
(P/'engineering-v9-results'/'native_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':out['status'],'sizes':list(sizes),'STEPs':len(checks),'available_pass':out['all_available_STEP_pass']}))
