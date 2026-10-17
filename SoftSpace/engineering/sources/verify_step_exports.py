import sys,json
from pathlib import Path
p=Path(__file__).parent;sys.path.insert(0,str(p/'solver-libraries'))
import gmsh
j=json.loads((p/'cad_v6_report.json').read_text());poses=json.loads((p/'cad_v6_pose_exports.json').read_text())
files=[f for f in j['files'] if f.endswith('.step') and 'Extension' not in f]+poses['files']
results=[]
for path in files:
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.occ.importShapes(path);gmsh.model.occ.synchronize()
 volumes=gmsh.model.getEntities(3);expected=4 if 'ReplacementCushion' in path else 28
 mass=sum(gmsh.model.occ.getMass(d,t) for d,t in volumes)
 results.append({'file':path,'solid_count':len(volumes),'expected_count':expected,'total_volume_mm3':mass,'pass':len(volumes)==expected and mass>0});gmsh.finalize()
report={'status':'complete','all_pass':all(r['pass'] for r in results),'exports':results}
(p/'cad_v6_step_verification.json').write_text(json.dumps(report,indent=2));print('Verified',len(results),'STEP exports; all pass',report['all_pass'])
