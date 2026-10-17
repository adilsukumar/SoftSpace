import sys,json,hashlib
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import gmsh
j=json.loads((p/'cad_v8_report.json').read_text());assert j['status']=='complete' and len(j['recipes'])==6
results=[]
for filename in j['files']:
 f=Path(filename)
 if f.suffix!='.step':continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(str(f));gmsh.model.occ.synchronize()
 volumes=gmsh.model.getEntities(3);volume=sum(gmsh.model.occ.getMass(d,t) for d,t in volumes);gmsh.finalize()
 expected=4 if 'ReplacementCushion' in f.name else 28
 results.append({'file':str(f),'solids':len(volumes),'expected':expected,'volume_mm3':volume,'pass':len(volumes)==expected and volume>0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
report={'status':'complete','all_pass':all(r['pass'] for r in results),'checks':results};(p/'engineering-v8-results'/'STEP_verification.json').write_text(json.dumps(report,indent=2));print('Checked',len(results),'STEP exports; all pass',report['all_pass'])
